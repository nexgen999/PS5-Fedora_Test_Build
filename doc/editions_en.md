# The Fedora builds — catalogue

Every build is **one YAML file** in `distros/fedora/`. The workflow discovers them
automatically: adding a file is enough to get a new image and its archives, and every
edition built by one run lands in **a single release**. The image name and archive names
come from `image.name` inside the YAML.

- Graphical editor: [`editor_en.md`](editor_en.md)
- Builder internals: [`builder_en.md`](builder_en.md)
- GitHub Actions pipeline: [`ci_en.md`](ci_en.md)
- Troubleshooting: [`troubleshooting_en.md`](troubleshooting_en.md)
- Version française : [`editions_fr.md`](editions_fr.md)

## Overview table

| Edition | File | `image.name` | Packages | Desktop / session | Login |
|---|---|---|--:|---|---|
| Base | `image.yaml` | `ps5-fedora` | 194 | GNOME (Wayland) | GDM + autologin |
| Desktop | `fedora-desktop_edition.yaml` | `ps5-fedora-desktop_edition` | 181 | GNOME (Wayland) | GDM + autologin |
| Dev | `fedora-dev_edition.yaml` | `ps5-fedora-dev_edition` | 189 | GNOME (Wayland) | GDM + autologin |
| Gaming | `fedora-gaming_edition.yaml` | `ps5-fedora-gaming_edition` | 176 | GNOME (Wayland) | GDM + autologin |
| Test | `fedora-test_build.yaml` | `ps5-fedora-test_build` | 194 | GNOME (Wayland) | GDM + autologin |
| Minimal | `fedora-minimal_setup.yaml` | `ps5-fedora-minimal_setup` | 40 | none (CLI) | console / SSH |
| COSMIC | `fedora-cosmic_edition.yaml` | `ps5-fedora-cosmic_edition` | 137 | COSMIC (Wayland) | cosmic-greeter (greetd) |
| KDE | `fedora-kde_edition.yaml` | `ps5-fedora-kde_edition` | 137 | Plasma 6 (Wayland) | SDDM |
| Cinnamon | `fedora-cinnamon_edition.yaml` | `ps5-fedora-cinnamon_edition` | 145 | Cinnamon (X11) | LightDM + autologin |
| Budgie | `fedora-budgie_edition.yaml` | `ps5-fedora-budgie_edition` | 145 | Budgie (Wayland labwc, Xorg available) | SDDM + autologin |
| Sway | `fedora-sway_edition.yaml` | `ps5-fedora-sway_edition` | 137 | Sway (Wayland) | SDDM |
| Niri | `fedora-niri_edition.yaml` | `ps5-fedora-niri_edition` | 137 | Niri (Wayland) | SDDM |
| Miracle WM | `fedora-miraclewm_edition.yaml` | `ps5-fedora-miraclewm_edition` | 137 | Miracle WM (Wayland) | SDDM |

Package counts are what the **YAML lists** (what [`build.difference.md`](../build.difference.md)
shows). The alternative desktops (COSMIC, Plasma, Sway, Niri, Miracle WM) are installed
from their comps group in `post-packages`, so the final image contains far more than
those 137 packages.

## Shared Fedora base

Present in **every** Fedora image, whatever the edition:

- Fedora 45 x86_64 (`image.release: "45"`, `kojipkgs.fedoraproject.org`), rootfs built by
  distrobuilder.
- **PS5 kernel** compiled from `ps5-linux-patches` (tag `kernel-7.3.3-c8fe83a`, see
  `PATCHES_REF` in `build_image.sh`), packaged as `.rpm` and installed into the image from
  `/opt/rpms` in `post-files`.
- User `ps5` / password `ps5`, member of `wheel` with passwordless `sudo`, `root` locked
  (`passwd -l root`), SSH enabled (`PermitRootLogin no`, `PasswordAuthentication yes`).
- Networking: `NetworkManager`, `avahi`, `iw`/`wpa_supplicant`/`wireless-regdb`,
  `linux-firmware`, SSH.
- **Internal IW620 WiFi**: `ps5-iw620.service` copies the firmware from the ESP, unloads
  `moal` when needed and re-enables the radio.
- **Fan ON + Boost ON**: `ps5-performance.service` (oneshot) runs `ps5_control --fan on`
  then `--boost on`, built from `ps5-linux-tools`.
- Growable rootfs (`grow-rootfs.service`), zram = half the RAM with zstd, SELinux disabled.
- XWayland (`xorg-x11-server-Xwayland`) for X11 apps, polkit, portals, fonts,
  `bash-completion`.
- Every session is **Wayland**; there is no full X11 session.

Shared by all **except `minimal_setup`**:

- RPM Fusion free + nonfree and codecs (`ffmpeg`, `gstreamer1-plugins-bad-freeworld`,
  `gstreamer1-plugins-ugly`), Flathub, Balena Etcher, 32-bit Mesa drivers (Steam/i686).
- **PS5 Fedora Manager** (GTK4 app) installed under `/usr/share/applications`.

## GNOME family

These five builds share the desktop block (GNOME Shell + GDM) and the same autologin:
`/etc/gdm/custom.conf` with `AutomaticLogin=ps5`, plus the
`gnome-initial-setup-done` marker so the wizard is skipped on first boot.

### Base — `image.yaml` → `ps5-fedora` (194 packages)

The reference: full GNOME, GNOME apps, mobile connectivity (GSConnect, MTP, SSHFS,
ADB/Fastboot), printing/scanning, codecs, the full development toolchain and the gaming
stack (Steam, Decky Loader). It is the only edition carrying the GitHub **Latest** badge.

### Desktop — `fedora-desktop_edition.yaml` → 181 packages

GNOME + apps + codecs + mobile + printing, **without** the development toolchain (no
`gcc`/`cmake`/`gdb`/`rpm-build`/`python3-pip`) and without the gaming stack. The everyday
workstation pick.

### Dev — `fedora-dev_edition.yaml` → 189 packages

GNOME + full toolchain (`gcc`, `gcc-c++`, `gdb`, `cmake`, `meson`, `ninja`, `autoconf`,
`automake`, `libtool`, `rpm-build`, `python3-pip`, `python3-pyyaml`) plus printing,
**without** gaming. Pick it if you compile on the console.

### Gaming — `fedora-gaming_edition.yaml` → 176 packages

GNOME + Steam, Gamescope, MangoHud, GameMode, 32-bit Mesa and Decky Loader, without the
development toolchain. Pick it when the PS5 is a game console.

### Test — `fedora-test_build.yaml` → 194 packages

A complete copy of the base under another name, used to try a change without touching the
`ps5-fedora` image or archives.

## Alternative Wayland family (137 listed packages)

These five builds share an identical base: desktop infrastructure (portals, GVfs, polkit,
PipeWire/WirePlumber, Mesa, NetworkManager and plugins), printing/scanning, mobile
connectivity, the dev toolchain, FR/EN localisation + ibus, fonts, Firefox, Flatpak, and
the whole PS5 `post-files` (fan/boost, manager, kernel rpm, internal WiFi, zram).
**GNOME is entirely absent** (no `gnome-shell`, `gdm`, `nautilus`, `gnome-keyring`, no
GNOME apps).

The desktop is installed from a comps group in `post-packages`, then a Wayland session is
enabled with `ps5` autologin:

| Edition | Installation | Session / autologin |
|---|---|---|
| COSMIC | `@cosmic-desktop-environment` + `cosmic-greeter cosmic-session cosmic-settings` | `cosmic-greeter.service` (greetd), `[initial_session] command = "cosmic-session"` in `/etc/greetd/cosmic-greeter.toml` |
| KDE | `@kde-desktop-environment` + `sddm-wayland-plasma` | `sddm`, `/etc/sddm.conf.d/autologin.conf` → `Session=plasma` |
| Sway | `@sway-desktop-environment` + Waybar/foot/fuzzel/mako/grim/slurp, `xdg-desktop-portal-wlr`, `xwayland-satellite` | `sddm` (+ `sddm-wayland-sway`), `Session=sway` |
| Niri | `niri` + the same tooling | `sddm`, `Session=niri` |
| Miracle WM | `@miraclewm-desktop-environment` + the same tooling | `sddm`, `Session=miracle-wm` |

Worth knowing:

- Each edition checks that the session binary exists (`startplasma-wayland`, `sway`,
  `niri`, `miracle-wm`) and **fails loudly** otherwise: no desktop-less image.
- `xorg-x11-server-Xorg` is installed as a fallback for SDDM if it drops back to its X11
  greeter; X11 apps still run through XWayland.
- The value in `Session=` must match a file in `/usr/share/wayland-sessions/` (without
  `.desktop`). That line is what changes if you want another default session.
- Unlike the GNOME family, these builds do not install the Flatpak Extension Manager
  (a GNOME app).

How to choose: **KDE** for the Qt ecosystem and graphical settings, **COSMIC** for a
modern GNOME-like desktop, **Sway/Miracle WM** for i3-style tiling, **Niri** for
scrollable tiling.

## X11 / Budgie family (145 listed packages)

Two builds that start from the Wayland family base (portals, GVfs, PipeWire/WirePlumber,
Mesa, printing, dev toolchain, `gtk4`/`libadwaita`) and add the full X11 stack plus the
graphical polkit agent `pkexec` needs:

| Edition | Installation | Session / autologin |
|---|---|---|
| Cinnamon | `@cinnamon-desktop-environment` + `lightdm`/`slick-greeter`, `mate-polkit` | LightDM, `user-session=cinnamon` (X11 session), `ps5` autologin (`autologin` group) |
| Budgie | `@budgie-desktop-environment` + `budgie-desktop-apps`, SDDM, `mate-polkit` | SDDM, `Session=` detected in `/usr/share/wayland-sessions` (labwc) or `/usr/share/xsessions` |

- **X11 and XWayland**: `xorg-x11-server-Xorg`, the `amdgpu` driver and XWayland are
  installed in both editions. Cinnamon runs an X11 session like the Fedora spin; Budgie
  starts on Wayland (labwc) and runs X11 apps through XWayland.
- The session name is not hard-coded: `post-files` reads the installed `.desktop` files and
  writes the value into the display manager config
  (`/etc/lightdm/lightdm.conf.d/50-ps5-autologin.conf` or
  `/etc/sddm.conf.d/autologin.conf`).
- Each edition **fails loudly** if the desktop is missing: no image without a graphical
  session.

## Minimal — `fedora-minimal_setup.yaml` → 40 packages

No graphical session: SSH, NetworkManager (+ WiFi), PS5 kernel, fan/boost, internal WiFi,
zram, grow-rootfs, `git`/`make`/`gcc` (needed to build `ps5_control`), console fonts,
FR/EN localisation. No Flatpak, no codecs, no manager. A good server base or a bare
starting point.

## One-line chooser

| Need | Edition |
|---|---|
| Everything GNOME | Base (`ps5-fedora`) |
| GNOME workstation without dev tools | Desktop |
| Compile / develop | Dev |
| Play (Steam, MangoHud…) | Gaming |
| Try changes without touching the base | Test |
| Non-GNOME Wayland desktop | KDE, COSMIC, Sway, Niri or Miracle WM |
| Classic X11 desktop | Cinnamon |
| Budgie desktop (Wayland on labwc) | Budgie |
| Server / console only | Minimal |

## Building one edition

```bash
./build_image.sh --distro fedora --variant fedora-sway_edition
# -> output/ps5-fedora-sway_edition.img  (12 GB by default)
```

- `--variant` takes the **file name without `.yaml`**. An unknown variant lists the
  available editions and exits with an error.
- `--print-name` only prints the resolved image name (used by CI).
- `--img-size` changes the image size, `--clean` starts from scratch.
- Budget ~30 GB free: each edition keeps its chroot in
  `work/chroot-fedora-<edition>/` plus the 12 GB image.
- Through GitHub Actions everything builds automatically (see [`ci_en.md`](ci_en.md)); the
  *Run workflow* form lets you tick the editions to build, or use `variant` /
  `skip_editions`.

## Editing an edition

Two ways, both detailed in [`editor_en.md`](editor_en.md):

1. **Graphical editor** (`python3 tools/edition_editor.py`): tick/untick packages and
   `# --- … ---` blocks, add repositories, RPM packages, flatpaks, commands and scripts,
   then save the YAML and regenerate `build.difference.md`.
2. **By hand**: edit the YAML. Script blocks are delimited by `# --- Title ---` markers;
   keeping those markers lets the editor keep recognising them.

After a change, `git push` to `main` triggers a rebuild (unless the commit only touches
`tools/**`, `**.md` or `.gitignore`).

## Known limitations

- Images are **not signed** and the Fedora source verification is disabled
  (`skip_verification: true`): the chain relies on HTTPS and on the checksums published in
  each release.
- The `ps5` password is public: change it after the first boot if the machine is exposed.
- Only Cinnamon opens a full X11 session; the others run Wayland, where XWayland covers
  most X11 applications. The Xorg server ships in the GNOME family, Cinnamon and Budgie for
  the remaining cases.
- Old releases are pruned to 5 (`KEEP_RELEASES`, one release per run), and CI artifacts
  expire after 7 days.
