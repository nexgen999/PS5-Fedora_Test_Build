# PS5 Linux Image Builder

Builds bootable Linux USB images for PlayStation 5 using Docker containers. Supports Ubuntu 26.04, Arch, CachyOS (Gamescope + Steam), Fedora (GNOME), individually or as a multi-distro image with kexec switching.

## Documentation

- [`doc/editor_fr.md`](doc/editor_fr.md) / [`doc/editor_en.md`](doc/editor_en.md) — the graphical YAML editor: checkboxes, the additions tab, the build comparison
- [`doc/builder_fr.md`](doc/builder_fr.md) / [`doc/builder_en.md`](doc/builder_en.md) — how the builder works: kernel/rootfs/image stages, edition YAML anatomy, CI and releases

## Prerequisites

- Docker (with permission to run `--privileged` containers) — install as per your distro's instructions
- ~30GB free disk space for Ubuntu, Arch, or CachyOS

Once Docker is installed, add your user to the docker group and apply it without logging out:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

## Quick Start

```bash
# Build a single Ubuntu 26.04 image
./build_image.sh --distro ubuntu2604

OR

# Build CachyOS (Arch-based, Gamescope + Steam Big Picture)
./build_image.sh --distro cachyos

OR

OR

# Build Fedora (base edition: distros/fedora/image.yaml)
./build_image.sh --distro fedora

OR

# Build one Fedora edition (any YAML in distros/fedora/)
./build_image.sh --distro fedora --variant fedora-gaming_edition

OR

# Build a multi-distro image (ubuntu2604 + arch + cachyos)
./build_image.sh --distro all
```

The script auto-clones the kernel source, applies PS5 patches, compiles, and builds the image. Subsequent runs reuse cached artifacts automatically. Press Ctrl+C at any time to abort cleanly.

## Flash to USB

```bash
sudo dd if=output/ps5-ubuntu2604.img of=/dev/sdX bs=4M status=progress
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--distro` | `ubuntu2604`, `arch`, `cachyos`, `fedora`, or `all` | `ubuntu2604` |
| `--variant` | Edition YAML to build, i.e. `distros/<distro>/<variant>.yaml` (see [Fedora editions](#fedora-editions)) | `image` |
| `--kernel` | Path to kernel source directory | auto-clone version selected by PS5 patch set |
| `--img-size` | Disk image size in MB | `12000` (`32000` for `all`) |
| `--clean` | Remove all cached build artifacts and start fresh | off |
| `--kernel-only` | Build and package the kernel only, then exit | off |
| `--patches-ref` | Branch, tag, or commit SHA for patches | `v1.2` |

## Caching

The build automatically skips stages that have already completed:

- **Kernel source** — reused if `work/linux/` exists
- **Kernel packages** — reused if `.deb`/`.pkg.tar.zst` files exist in `linux-bin/`
- **Root filesystem** — reused if chroot directories are populated

Use `--clean` to wipe everything and rebuild from scratch. The build will also suggest `--clean` if a stage fails.

## Build Output

```
PS5 Linux Image Builder
=======================
  Distro:       all
                (ubuntu2604 arch cachyos)
  Image size:   32000MB
  Kernel src:   /path/to/work/linux

Stages:
  1. Kernel            cached
  2. Root filesystem   build
  3. Disk image        build

Logs: /path/to/build.log

  ✓ Kernel packages (cached)
  ✓ Build image builder image
  ⠹ Building arch rootfs
```

All verbose output goes to `build.log`. The terminal shows a spinner with live progress.

## Distributions

| Distro | Desktop | Kernel format | Init |
|--------|---------|---------------|------|
| Ubuntu 26.04 (Resolute) | GNOME | `.deb` | systemd |
| Arch | Sway | `.pkg.tar.zst` | systemd |
| CachyOS | Gamescope + Steam Big Picture (Arch + `[cachyos]` repo, no v3 migration in image build) | `.pkg.tar.zst` | systemd |
| Fedora | GNOME (Wayland) | `.rpm` | systemd |

## Fedora editions

Each build of `--distro fedora` is described by one YAML file in
`distros/fedora/`. The image name is read from `image.name` inside that YAML,
so every edition gets its own file, its own archives and its own release:

| Edition | YAML | Image | Content |
|---------|------|-------|---------|
| Base | `image.yaml` | `ps5-fedora` | Full desktop build (reference edition, owns the GitHub *Latest* badge) |
| Desktop | `fedora-desktop_edition.yaml` | `ps5-fedora-desktop_edition` | GNOME desktop without the dev toolchain or gaming stack |
| Gaming | `fedora-gaming_edition.yaml` | `ps5-fedora-gaming_edition` | GNOME + Steam, Gamescope, MangoHud, GameMode, 32-bit Mesa, Decky Loader |
| Dev | `fedora-dev_edition.yaml` | `ps5-fedora-dev_edition` | GNOME + full toolchain (gcc, cmake, meson, gdb, rpm-build, Python, git) |
| Minimal | `fedora-minimal_setup.yaml` | `ps5-fedora-minimal_setup` | CLI only (no graphical session): SSH, NetworkManager, kernel and hardware tooling |
| Test | `fedora-test_build.yaml` | `ps5-fedora-test_build` | Everything: desktop, mobile, print/scan, codecs, dev tools and gaming stack |

```bash
./build_image.sh --distro fedora --variant fedora-minimal_setup
# -> output/ps5-fedora-minimal_setup.img
```

### Adding a new edition

1. Copy an existing YAML, e.g. `cp distros/fedora/fedora-dev_edition.yaml distros/fedora/fedora-my_edition.yaml`.
2. Change `image.name` (that becomes the `.img`, the archives and the release tag prefix) and `image.description`, then edit the package list.
3. Nothing else to wire: the CI lists `distros/fedora/*.yaml` and builds, compresses and releases every file it finds.

`image.yaml` is also the edition used for the kernel-only job, so keep it as the base build.

Keep the runtime toolchain (`git`, `make`, `gcc`, `binutils`, `pkgconf`) in editions that install `ps5-linux-tools` during the build, and `steam`/`gamescope`/`mangohud`/`gamemode` are installed from RPM Fusion in `post-packages` for the gaming editions.

## Éditeur graphique d'éditions

`tools/edition_editor.py` lit `distros/fedora/image.yaml` et génère les autres YAML
sans recopier les scripts à la main :

```bash
sudo dnf install python3-tkinter          # une seule fois (Debian/Ubuntu : python3-tk)
python3 tools/edition_editor.py             # ouvre l'interface
python3 tools/edition_editor.py --check     # liste les groupes/blocs lus, sans GUI
python3 tools/edition_editor.py --difference  # régénère build.difference.md
```

- onglet **Paquets & blocs** : chaque groupe de `image.yaml` est listé, on décoche ce qu'on ne veut pas (avec une recherche) ; chaque section `# --- … ---` des actions est une case à cocher. Les blocs `[commun]` (kernel, WiFi, fan/boost, ps5_control, manager, RPM Fusion, Flathub, grow-rootfs, SELinux, utilisateur, zram) restent toujours inclus ;
- onglet **Ajouts** : pour enrichir une build avec ce qui n'existe pas dans `image.yaml` — dépôts supplémentaires, paquets RPM, applications Flatpak, commandes d'installation et scripts libres. Ordre d'exécution : dépôts → paquets → flatpaks → commandes (dans `post-packages`), puis scripts (fin de `post-files`) ;
- **Enregistrer** écrit `distros/fedora/<nom>.yaml`, nommé d'après `image.name`, et régénère `build.difference.md` ; le workflow buildera et releasera automatiquement le fichier.

### Comparatif des builds

`build.difference.md` (racine du dépôt) est généré à chaque enregistrement ou via le
bouton **Comparatif des builds**. Il contient : un tableau récapitulatif par build,
le tableau des paquets présents/absents build par build, le tableau des blocs de script,
et pour chaque édition la liste de ses ajouts (dépôts, paquets RPM, flatpaks, commandes,
scripts) ainsi que les paquets retirés par rapport à la base.

Charger une édition existante recharge ses cases. Si elle contient du script qui n'existe
pas dans `image.yaml`, les blocs sont verrouillés et ce script est recopié tel quel :
seuls les paquets, le nom et la description sont alors modifiables (rien n'est perdu).

## Releases

Every CI build publishes one release per edition:

- tag: `<image.name>-YYYY.MM.DD-HHMM` (UTC), e.g. `ps5-fedora-gaming_edition-2026.11.24-1830`
- assets: the 7z volumes of that edition (`ps5-<edition>.img.7z.001`, `.002`, ...)
- nothing is overwritten: a new build creates a new release, older ones are untouched
- the 5 newest releases of each edition are kept; older ones are pruned. Change `KEEP_RELEASES` in `.github/workflows/build-image.yml` to keep more.

## Multi-distro Image

`--distro all` builds a 32GB image with 4 partitions (one EFI boot partition plus three root filesystems):

| Partition | Type | Label | Content |
|-----------|------|-------|---------|
| p1 | FAT32 | boot | Shared kernel, per-distro initrds, kexec scripts |
| p2 | ext4 | ubuntu2604 | Ubuntu 26.04 rootfs |
| p3 | ext4 | arch | Arch rootfs |
| p4 | ext4 | cachyos | CachyOS rootfs |

The boot partition contains kexec scripts to switch between distros at runtime. Ubuntu 26.04 is the default boot target.

## Building the Kernel Standalone

Use `--kernel-only` to compile the PS5 kernel and produce installable packages without building a full disk image.

```bash
./build_image.sh --kernel-only                                # .deb (default)
./build_image.sh --kernel-only --distro all                   # .deb + .pkg.tar.zst
./build_image.sh --kernel-only --patches-ref main             # fetch from specific branch/tag
./build_image.sh --kernel-only --clean                        # wipe and rebuild from scratch
```

Output packages are written to `linux-bin/`. Install on a running PS5 Linux system:

```bash
sudo dpkg -i linux-bin/linux-ps5_*.deb
```

## PS5 Pro GPU Firmware

The kernel package installs `ps5-stage-gpu-firmware.service`. It only acts on a PS5 Pro, when ps5-linux-loader has dumped the Viola GPU firmware (`viola_*.bin`) to `/boot/efi/lib/firmware/amdgpu/` and the kernel's amdgpu can load it. Then it:

- copies the files to `/usr/lib/firmware/amdgpu/`
- rebuilds the initramfs and deploys it to the boot partition with `zz-update-boot`, or on Bazzite by copying it to `/boot/efi/initrd.img`

amdgpu uses the firmware from the next boot on. The service does nothing on other models, without the firmware, or on Batocera and SteamOS. Check it with `journalctl -u ps5-stage-gpu-firmware`.

## Directory Layout

```
build_image.sh                  # Image builder (also supports --kernel-only)
docker/
  kernel-builder/               # Kernel compilation container
  kernel-builder-arch/          # Repackages .deb kernel as .pkg.tar.zst
  image-builder/
    Dockerfile                  # Image building container (distrobuilder)
    entrypoint.sh               # Single-distro build logic
    entrypoint-multi.sh         # Multi-distro build logic
distros/
  ubuntu2604/                   # Ubuntu 26.04 (Resolute)
  arch/                         # Arch Linux
  cachyos/                      # CachyOS repos + Gamescope/Steam
  shared/                       # Kernel postinst hooks (single + multi)
boot/
  cmdline.txt                   # Kernel cmdline template (__DISTRO__ placeholder)
  vram.txt                      # VRAM allocation
  kexec-{ubuntu2604,arch,cachyos}.sh
work/                           # Build artifacts (auto-created)
linux-bin/                      # Compiled kernel packages
output/                         # Final .img files
```
