# Troubleshooting

Guide by symptom. Always start from the **first error** in the log: the ones after it are
almost always consequences.

- Build catalogue: [`editions_en.md`](editions_en.md)
- CI pipeline: [`ci_en.md`](ci_en.md)
- Local builder: [`builder_en.md`](builder_en.md)
- Version française : [`troubleshooting_fr.md`](troubleshooting_fr.md)

## Where to look

| Context | Place |
|---|---|
| Local build | terminal output + `build.log` (all the verbose detail) |
| CI | the red step log, then the run *Summary* |
| Installed system | `journalctl -b`, `systemctl --failed` on the PS5 |

## Local build

| Symptom | Cause | Fix |
|---|---|---|
| `permission denied` on `docker` | user not in the docker group | `sudo usermod -aG docker $USER` then `newgrp docker` |
| `Unknown edition 'x' for fedora` | the YAML does not exist | the message lists editions; `--variant` takes the name **without** `.yaml` |
| `dnf` fails on Steam/GameScope | packages installed before RPM Fusion | keep the block order: RPM Fusion first, gaming later |
| `ps5-linux-tools` fails to compile | `git`/`make`/`gcc` missing | add those packages to the edition (`minimal_setup` has them) |
| Inconsistent rootfs after an edit | stale `work/chroot-…` cache | rerun with `--clean` (wipes `work/`, `linux-bin/`, `cache/`, `output/`) |
| `no space left on device` | chroot + 12 GB image per edition | free space or lower `--img-size` |
| The kernel rebuilds every time | `linux-bin/*.rpm` missing | expected after `--clean`; otherwise the script reuses the existing `.rpm` |

## CI / GitHub Actions

| Symptom | Cause | Fix |
|---|---|---|
| Nothing starts after a push | `paths-ignore` (`tools/**`, `**.md`, `.gitignore`) | touch `distros/**` or dispatch the workflow manually |
| Only one edition is red, the others published | intended isolation | fix the YAML and rerun with `variant` |
| `::error::Edition X failed to build` | the `build` step failed | open the "Build X image" log: the first error is the cause |
| `Failed to enable unit: Unit x.service does not exist` | the script enables a service whose package is not installed | already handled by `enable_unit` (unit skipped); add the package to really enable it |
| `ERREUR: cosmic-session absent` / `sway absent` / `niri absent` / `miracle-wm absent` | comps group or package unavailable for that Fedora release | check `dnf environment list` / `dnf list` on Fedora 45, fix the name, rerun |
| `no .rpm produced in image/linux-bin` | kernel packaging failed | read the `kernel` job log; rerun after fixing |
| Kernel artifact `EACCES` | uploading the `linux-bin/staging/` tree (root-owned files) | never upload `linux-bin/`: the workflow copies the `.rpm` to `kernel-pkg/` |
| `An error has occurred during zip creation for the artifact` | same cause: `upload-artifact` zips unreadable files | keep the `kernel-pkg/` path |
| The `kernel` job does not recompile | valid cache (same patches tag and recipes) | intended; to force it, delete the `kernel-rpm-…` cache in Actions → Caches |
| `No build output for edition X; skipping its release` | failed build or missing artifact | fix the build; other editions' releases are unaffected |
| Release rejected / tag already exists | two runs very close on the same edition | the `concurrency` group serialises per edition; rerun if needed |
| The run takes long | 11 editions to build | the kernel is cached; builds run in parallel |

## YAML and the graphical editor

| Symptom | Cause | Fix |
|---|---|---|
| "locked mode" | the YAML has scripts absent from `image.yaml` (e.g. `minimal_setup`) | intended: scripts are kept verbatim, only packages and recognised blocks change |
| Additions are not written in locked mode | limitation of that mode | a warning is shown; edit the YAML by hand in that case |
| A block does not show up in the editor | missing `# --- Title ---` marker | add the marker above the block |
| `--check` does not list a block as `[commun]` | content differs from `image.yaml` | expected for an edition-specific block (it shows as `[optionnel]`) |
| `build.difference.md` looks stale | it is a generated file | run `python3 tools/edition_editor.py --difference` |

## On the PS5, once booted

| Symptom | Diagnosis | Lead |
|---|---|---|
| No graphical session | `systemctl --failed`, `journalctl -b -u sddm` | check that the greeter is enabled and the session exists |
| SDDM black screen | `journalctl -b -u sddm`, `ls /usr/share/wayland-sessions` | wrong session name in `autologin.conf`, or an X11 greeter without an X server: `sddm-wayland-sway` / `sddm-wayland-plasma` |
| COSMIC does not start | `systemctl status cosmic-greeter`, `cat /etc/greetd/cosmic-greeter.toml` | the greeter uses `greetd`; autologin is an `[initial_session]` block |
| GNOME asks for the setup wizard again | missing marker | `/home/ps5/.config/gnome-initial-setup-done` must exist |
| X11 apps do not start | `echo $XDG_SESSION_TYPE`, `ls /usr/bin/Xwayland` | XWayland is installed; check the `xorg-x11-server-Xwayland` package |
| No internal WiFi | `systemctl status ps5-iw620`, `dmesg | grep -i moal` | firmware expected in the ESP (`nxp/pcieuartiw620_combo_v1.bin`); `nmcli radio wifi on` |
| Fan/boost inactive | `systemctl status ps5-performance`, `ps5_control --fan on` | the binary is in `/usr/local/sbin/ps5_control`, oneshot service |
| PS5 Fedora Manager missing | `ls /usr/share/applications | grep -i ps5` | the install block is in `post-files`; `update-desktop-database` |
| Wrong resolution / no Vulkan | `vulkaninfo --summary` | Mesa AMD must be present; PS5 firmware issues are out of scope |

Useful diagnostics:

```bash
systemctl --failed
journalctl -b -p err
ls /usr/share/wayland-sessions/     # names usable in Session=
nmcli device status
ip -br addr
df -h /
free -h
```

## Archives and releases

| Symptom | Cause | Fix |
|---|---|---|
| Extraction fails | missing volume | download **all** `*.7z.00N` into one directory, then `7z x …001` |
| Checksum mismatch | interrupted download | compare with `meta/<image>.sha256` published in the release body |
| Old release disappeared | automatic pruning | `KEEP_RELEASES` = 5 per edition; get a newer one |
| No Latest badge on an edition | intended | only `image` (base) carries the badge |
