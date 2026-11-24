# How the builder works — `build_image.sh`

This repository builds bootable Linux USB images for the PlayStation 5 (a GPT disk
image you flash to a USB drive) by chaining Docker containers: compiling the PS5
kernel, building the distribution root filesystem, then assembling the disk image.

- Graphical YAML editor: [`editor_en.md`](editor_en.md)
- Version française : [`builder_fr.md`](builder_fr.md)

## Overview

```
build_image.sh --distro fedora --variant fedora-gaming_edition
        │
        ├─ 1. Kernel   : clone ps5-linux-patches + stable linux, apply the patches,
        │                compile, install modules into linux-bin/staging,
        │                then package as .rpm (fedora) / .deb / .pkg.tar.zst
        │
        ├─ 2. Rootfs   : distrobuilder build-dir distros/fedora/<edition>.yaml
        │                -> work/chroot-fedora-<edition>/  (dnf, files, scripts)
        │
        └─ 3. Image    : truncate + parted + mkfs + copy the rootfs
                         -> output/<image.name>.img
```

Everything verbose goes to `build.log`; the terminal shows one spinner line per stage.
The script runs with `set -e`: the first failing stage stops the build, and the final
message suggests `--clean` when the cache looks stale.

## Requirements

- Docker, allowed to run `--privileged` containers (`sudo usermod -aG docker $USER`
  then `newgrp docker`).
- ~30 GB free disk space (rootfs + kernel + a 12 GB image).
- The build runs as `linux/amd64` (`DOCKER_DEFAULT_PLATFORM` is exported).

## Usage

```bash
./build_image.sh                                        # Ubuntu 26.04 (default)
./build_image.sh --distro fedora                         # base edition (image.yaml)
./build_image.sh --distro fedora --variant fedora-dev_edition
./build_image.sh --distro all                            # 32 GB multi-distro image
./build_image.sh --kernel-only                           # kernel only, no image
```

| Option | Purpose | Default |
|---|---|---|
| `--distro` | `ubuntu2604`, `arch`, `cachyos`, `fedora`, `proxmox`, `debian`, `bazzite`, `bazzite-deck`, `batocera`, `all` | `ubuntu2604` |
| `--variant` | YAML stem in `distros/<distro>/` (without `.yaml`) | `image` |
| `--kernel` | already-cloned kernel source directory | auto (`work/linux`) |
| `--img-size` | disk image size in MB | `12000` (`32000` for `all`) |
| `--clean` | wipe every cache, then rebuild | off |
| `--clean-only` | wipe caches and exit | off |
| `--kernel-only` | compile and package the kernel, then exit | off |
| `--patches-ref` | PS5 patch branch/tag/SHA | tag defined in the script |
| `--print-name` | print the image name resolved from the YAML, then exit | off |

An unknown variant prints the available editions and exits with an error.

## The three stages

### 1. Kernel

1. `work/ps5-linux-patches` is shallow-cloned at `--patches-ref`.
2. The target version is read from the `# Linux/x.y.z …` header of the patch set's
   `.config`, then the matching stable kernel is shallow-cloned into `work/linux`.
3. All `*.patch` files are applied (`git apply --exclude=Makefile`) and the patch set
   `.config` is copied in.
4. The `ps5-kernel-builder` image compiles the kernel; every artifact goes to
   `linux-bin/staging/` (bzImage, System.map, modules, headers, plus `/etc` and
   `/usr/local` for the PS5 helpers: firmware, Bluetooth, …).
5. The package format depends on the distribution: `.rpm` (fedora/bazzite), `.deb`
   (ubuntu/debian/proxmox), `.pkg.tar.zst` (arch/cachyos), all three for `all`.
6. `linux-bin/VERSION` holds the kernel version (modules directory name).

### 2. Rootfs

`docker/image-builder/entrypoint.sh` fills `/tmp/build-staging` (`zz-update-boot` hook,
`fstab` with partition labels, `grow-rootfs`, kernel packages), then runs:

```bash
distrobuilder build-dir "$IMAGE_YAML" "$CHROOT" \
    --with-post-files --cache-dir /build/cache --cleanup=false
```

**The edition YAML drives this stage**: packages, files and actions. Distributions that
ship their own `distros/<distro>/build-rootfs.sh` (bazzite, batocera…) bypass
distrobuilder entirely.

The chroot is reused between runs when already populated; `--clean` resets it.

### 3. Disk image

- temporary file `output/.<name>.img.tmp` (`truncate` to `--img-size`);
- GPT layout: p1 ext4 (root, 500 MB → end), p2 FAT32 (ESP, 1 MB → 500 MB);
- `losetup` + `kpartx`, `mkfs.ext4 -L <distro>` and `mkfs.vfat -n boot`;
- copy the chroot, move `/boot/efi` onto the ESP partition;
- `cmdline.txt` (from `distros/<distro>/cmdline.txt` or `boot/cmdline.txt`, with
  `__DISTRO__` replaced by the label), `vram.txt`, `kexec.sh`;
- rename to `output/<image.name>.img`.

## Editions (YAML) and image name

Each Fedora build is described by a file `distros/fedora/<stem>.yaml`. The image name
comes from `image.name` inside that file:

| Edition | YAML | `image.name` |
|---|---|---|
| Base | `image.yaml` | `ps5-fedora` |
| Desktop | `fedora-desktop_edition.yaml` | `ps5-fedora-desktop_edition` |
| Gaming | `fedora-gaming_edition.yaml` | `ps5-fedora-gaming_edition` |
| Dev | `fedora-dev_edition.yaml` | `ps5-fedora-dev_edition` |
| Minimal | `fedora-minimal_setup.yaml` | `ps5-fedora-minimal_setup` |
| Test | `fedora-test_build.yaml` | `ps5-fedora-test_build` |

- `image.name` becomes the `.img`, the archive names and the release tag prefix.
- Without `image.name` the script falls back to `ps5-<distro>[-<variant>]`.
- Every edition has **its own chroot**: `work/chroot` for `image.yaml`,
  `work/chroot-<distro>-<variant>` otherwise. No cross-edition reuse.
- `--print-name` prints the resolved name (used by the workflow).

## Edition YAML anatomy

```yaml
image:
  name: ps5-fedora-gaming_edition     # -> output/ps5-fedora-gaming_edition.img
  distribution: fedora
  release: "45"
  description: Fedora GNOME + Gaming  # reused in the GitHub release
  architecture: x86_64

source:                               # where the rootfs comes from
  downloader: fedora-http
  url: https://kojipkgs.fedoraproject.org
  skip_verification: true

packages:
  manager: dnf
  update: true
  cleanup: true
  sets:
    - packages:
        # comment = group title in the editor
        - gnome-shell
        - gdm
      action: install

files:
  - path: /etc/hostname
    generator: hostname
  - path: /etc/fstab
    generator: copy
    source: /tmp/build-staging/fstab

actions:
  - trigger: post-unpack            # always executed in full
    action: |-
      #!/bin/bash
      set -eux
      dnf makecache || true

  - trigger: post-packages
    action: |-
      #!/bin/bash
      set -eux

      # --- RPM Fusion, Codecs & Flathub ---
      dnf install -y …rpmfusion-free-release…

      # --- Gaming stack (Steam, Gamescope, MangoHud, GameMode) ---
      dnf install -y steam gamescope mangohud gamemode
```

Key points:

- **Triggers** in use: `post-unpack`, `post-update`, `post-packages`, `post-files`.
- `# --- Title ---` comments split a trigger into blocks the editor can tick; without a
  marker the whole script is kept.
- Kernel packages are copied into `/opt/rpms` (a `copy` generator from
  `/tmp/build-staging/rpms`) and installed by a `post-packages` block.
- `steam`, `gamescope`, `mangohud`, `gamemode` must be installed **after** RPM Fusion
  (inside `post-packages`), otherwise `dnf` fails: those packages are not in the base
  Fedora repositories.
- `ps5-linux-tools` is compiled during the build: the `git`, `make`, `gcc` toolchain
  (plus `binutils`, `pkgconf`) must stay in the editions that use it.
- Blocks present in every build: kernel, internal WiFi, fan ON/boost ON, PS5 Fedora
  Manager, RPM Fusion, Flathub, grow-rootfs, SELinux, default user, zram.

## Adding an edition

**With the editor** (recommended): see [`editor_en.md`](editor_en.md), then `Save` —
the file lands in `distros/fedora/` and the comparison is regenerated.

**By hand**:

1. `cp distros/fedora/fedora-dev_edition.yaml distros/fedora/fedora-my_edition.yaml`
2. change `image.name` and `image.description`, adjust packages/scripts;
3. nothing else: the workflow lists `distros/fedora/*.yaml` and builds, compresses and
   publishes every file it finds.

`image.yaml` is also the base for the CI kernel job, so it must stay the complete
reference build.

## Continuous integration (GitHub Actions)

`.github/workflows/trigger-builds.yml` (`deploy`) runs `build-image.yml` on pushes to
`main` (except `tools/**`, `**.md`, `.gitignore`), on manual dispatch, or on a
`run-ci`-labelled pull request.

```
editions ──► kernel ──► build (matrix, one edition at a time) ──► release (matrix)
```

| Job | Role |
|---|---|
| `editions` | lists `distros/fedora/*.yaml` (or only `variant` when given) and builds the matrix |
| `kernel` | compiles the kernel **once**, copies the `.rpm` into `kernel-pkg/` and uploads the `kernel-rpm` artifact |
| `build` | per edition: download the `.rpm`, run `build_image.sh --variant <edition>`, verify the image, split it into 1.5 GiB 7z volumes (`7z -mx=4 -v1500m`) |
| `release` | publishes one release per edition with checksums, then prunes old ones |

- Tag: `<image.name>-YYYY.MM.DD-HHMM` in UTC, e.g.
  `ps5-fedora-gaming_edition-2026.11.24-1830`.
- Nothing is overwritten: each build creates a new tag.
- `KEEP_RELEASES: '5'` (in `build-image.yml`): only the 5 newest dated releases of each
  edition are kept, older ones are deleted (release + tag). The *Latest* badge is only
  set by the `image` edition.
- 7z volumes are 1.5 GiB to stay under GitHub's 2 GiB per-file limit.
- The `kernel` job copies the `.rpm` into a runner-owned directory before uploading:
  `linux-bin/` also holds the root-owned `staging/` tree written by the container, which
  `upload-artifact` cannot read.

## Outputs

| Path | Content |
|---|---|
| `output/<image.name>.img` | GPT disk image to flash |
| `output/*.img.7z.00*` | archives (CI) |
| `linux-bin/*.rpm` / `*.deb` / `*.pkg.tar.zst` | kernel packages |
| `linux-bin/VERSION` | version of the compiled kernel |
| `linux-bin/staging/` | intermediate kernel artifacts (not published) |
| `work/chroot[-…]/` | cached root filesystem |
| `build.log` | full build log |

Flash to a USB drive:

```bash
sudo dd if=output/ps5-fedora.img of=/dev/sdX bs=4M status=progress
```

For releases, download **every** volume, then extract the `.001`.

## Kernel only and multi-distro

```bash
./build_image.sh --kernel-only                     # .deb (default ubuntu)
./build_image.sh --kernel-only --distro fedora     # .rpm
./build_image.sh --kernel-only --distro all        # .deb + .pkg.tar.zst
```

`--distro all` builds a 32 GB image with four partitions (ESP + Ubuntu + Arch +
CachyOS) plus `kexec` scripts to switch distributions at boot.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `permission denied` on `docker` | `sudo usermod -aG docker $USER` then `newgrp docker` |
| `Unknown edition 'x' for fedora` | the YAML does not exist in `distros/fedora/`; the message lists editions |
| `dnf` fails on steam/gamescope | installed before RPM Fusion: move them later in `post-packages` |
| ps5-linux-tools fails to compile | `git`/`make`/`gcc` missing from the edition |
| inconsistent rootfs after edits | rerun with `--clean` (wipes `work/`, `linux-bin/`, `cache/`, `output/`) |
| "no space left on device" | free space: each edition keeps its chroot plus a 12 GB image |
| kernel artifact `EACCES` in CI | never upload all of `linux-bin/`: the workflow copies the `.rpm` first |
| nothing starts after a push | the workflow ignores `tools/**`, `**.md`, `.gitignore`: touch `distros/**` or dispatch `deploy` manually |

## File map

```
build_image.sh                     # orchestration (kernel, rootfs, image)
docker/kernel-builder/             # kernel compilation + .deb packaging
docker/kernel-builder-rpm/         # .rpm packaging (linux-ps5 spec)
docker/kernel-builder-arch/        # .pkg.tar.zst packaging
docker/image-builder/
  Dockerfile                       # distrobuilder, skopeo, umoci, parted…
  entrypoint.sh                    # single-distro build
  entrypoint-multi.sh              # multi-distro build
distros/fedora/*.yaml              # one edition per file
distros/fedora/build-rootfs.sh     # (when present) custom rootfs
distros/shared/                    # shared hooks (zz-update-boot…)
boot/                              # cmdline.txt, vram.txt, kexec.sh
tools/edition_editor.py            # graphical YAML editor
doc/                               # this documentation
```
