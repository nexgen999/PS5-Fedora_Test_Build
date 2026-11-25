# Comparaison des builds PS5 Fedora

Fichier généré par `tools/edition_editor.py` (bouton « Comparatif des builds » ou à chaque enregistrement d'une édition). Ne pas éditer à la main.

## Résumé

| Build | Image | Paquets | Blocs | Dépôts | Paquets ajoutés | Flatpaks | Scripts |
|---|---|--:|--:|--:|--:|--:|--:|
| `base` | `ps5-fedora` | 194 | 25 | 0 | 0 | 0 | 0 |
| `budgie_edition` | `ps5-fedora-budgie_edition` | 145 | 23 | 0 | 0 | 0 | 0 |
| `cinnamon_edition` | `ps5-fedora-cinnamon_edition` | 145 | 23 | 0 | 0 | 0 | 0 |
| `cosmic_edition` | `ps5-fedora-cosmic_edition` | 137 | 23 | 0 | 0 | 0 | 0 |
| `desktop_edition` | `ps5-fedora-desktop_edition` | 181 | 23 | 0 | 0 | 0 | 0 |
| `dev_edition` | `ps5-fedora-dev_edition` | 189 | 23 | 0 | 0 | 0 | 0 |
| `gaming_edition` | `ps5-fedora-gaming_edition` | 176 | 26 | 0 | 0 | 0 | 0 |
| `kde_edition` | `ps5-fedora-kde_edition` | 137 | 23 | 0 | 0 | 0 | 0 |
| `minimal_setup` | `ps5-fedora-minimal_setup` | 40 | 9 | 0 | 0 | 0 | 0 |
| `miraclewm_edition` | `ps5-fedora-miraclewm_edition` | 137 | 23 | 0 | 0 | 0 | 0 |
| `niri_edition` | `ps5-fedora-niri_edition` | 137 | 23 | 0 | 0 | 0 | 0 |
| `sway_edition` | `ps5-fedora-sway_edition` | 137 | 23 | 0 | 0 | 0 | 0 |
| `test_build` | `ps5-fedora-test_build` | 194 | 26 | 0 | 0 | 0 | 0 |

## Paquets

| Paquet | `base` | `budgie_edition` | `cinnamon_edition` | `cosmic_edition` | `desktop_edition` | `dev_edition` | `gaming_edition` | `kde_edition` | `minimal_setup` | `miraclewm_edition` | `niri_edition` | `sway_edition` | `test_build` |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| `gnome-shell` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-session` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-classic-session` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-terminal` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gdm` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `mutter` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `nautilus` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-control-center` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-settings-daemon` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-keyring` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `seahorse` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `pinentry-gnome3` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `xdg-utils` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `xdg-desktop-portal` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `xdg-desktop-portal-gnome` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `xdg-desktop-portal-gtk` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `xdg-user-dirs-gtk` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gvfs` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gvfs-smb` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gvfs-nfs` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gvfs-fuse` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gvfs-mtp` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gvfs-afc` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gvfs-goa` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gvfs-gphoto2` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gnome-backgrounds` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-text-editor` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-system-monitor` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-disk-utility` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-calculator` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-tweaks` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-extensions-app` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-software` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-initial-setup` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-boxes` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-calendar` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-characters` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-clocks` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-color-manager` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-connections` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-contacts` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-epub-thumbnailer` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-font-viewer` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-logs` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-maps` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-remote-desktop` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-user-docs` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-user-share` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-weather` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `file-roller` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `loupe` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `evince` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `papers` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `papers-nautilus` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `baobab` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `sushi` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `showtime` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `decibels` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `snapshot` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `rygel` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `localsearch` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `tinysparql` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `glycin-thumbnailer` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gst-thumbnailers` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `librsvg2` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `vte-profile` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `gnome-browser-connector` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `yelp` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `toolbox` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `systemd-oomd-defaults` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `fprintd-pam` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `glib-networking` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `PackageKit-command-not-found` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `PackageKit-gtk3-module` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `xorg-x11-server-Xwayland` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `polkit` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `bluez` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `bluez-tools` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gnome-bluetooth` | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| `pipewire` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `wireplumber` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `pipewire-pulseaudio` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gstreamer1-plugins-base` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gstreamer1-plugins-good` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gstreamer1-plugins-bad-free` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gstreamer1-plugins-ugly-free` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gstreamer1-libav` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `mesa-dri-drivers` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `mesa-libEGL` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `mesa-vulkan-drivers` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `mesa-va-drivers` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `vulkan-tools` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `mesa-demos` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `libinput` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `NetworkManager` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `NetworkManager-wifi` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `network-manager-applet` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `ModemManager` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `NetworkManager-adsl` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `NetworkManager-libreswan-gnome` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `NetworkManager-openconnect-gnome` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `NetworkManager-openvpn-gnome` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `NetworkManager-ppp` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `NetworkManager-ssh-gnome` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `NetworkManager-wwan` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `avahi` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `linux-firmware` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `iw` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `wpa_supplicant` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `wireless-regdb` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cifs-utils` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `samba-client` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `samba` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `nfs-utils` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `ethtool` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `nmap-ncat` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `bind-utils` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `curl` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `wget` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `util-linux` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `pciutils` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `usbutils` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `zlib-devel` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `python3-PyQt6` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gnome-shell-extension-gsconnect` | ✓ |  |  |  | ✓ |  |  |  |  |  |  |  | ✓ |
| `fuse-sshfs` | ✓ | ✓ | ✓ | ✓ | ✓ |  |  | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `nautilus-python` | ✓ |  |  |  | ✓ |  |  |  |  |  |  |  | ✓ |
| `android-tools` | ✓ | ✓ | ✓ | ✓ | ✓ |  |  | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `wl-clipboard` | ✓ | ✓ | ✓ | ✓ | ✓ |  |  | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `cups` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `cups-filters` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `system-config-printer` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `hplip` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gutenprint-cups` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `splix` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `sane-backends` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `sane-backends-drivers-scanners` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `libsane-hpaio` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `simple-scan` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `git` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `make` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `gcc` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `gcc-c++` | ✓ | ✓ | ✓ | ✓ |  | ✓ |  | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gdb` | ✓ | ✓ | ✓ | ✓ |  | ✓ |  | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `cmake` | ✓ | ✓ | ✓ | ✓ |  | ✓ |  | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `ninja-build` | ✓ | ✓ | ✓ | ✓ |  | ✓ |  | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `meson` | ✓ | ✓ | ✓ | ✓ |  | ✓ |  | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `autoconf` | ✓ | ✓ | ✓ | ✓ |  | ✓ |  | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `automake` | ✓ | ✓ | ✓ | ✓ |  | ✓ |  | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `libtool` | ✓ | ✓ | ✓ | ✓ |  | ✓ |  | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `patch` | ✓ | ✓ | ✓ | ✓ |  | ✓ |  | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `binutils` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `pkgconf` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `pkgconf-pkg-config` | ✓ | ✓ | ✓ | ✓ |  | ✓ |  | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `rpm-build` | ✓ | ✓ | ✓ | ✓ |  | ✓ |  | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `python3-pip` | ✓ | ✓ | ✓ | ✓ |  | ✓ |  | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `python3-pyyaml` | ✓ | ✓ | ✓ | ✓ |  | ✓ |  | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `python3-gobject` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gtk4` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `libadwaita` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `gobject-introspection` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `desktop-file-utils` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `xhost` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `glibc-all-langpacks` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `langpacks-fr` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `langpacks-en` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `firefox-langpacks` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `xkeyboard-config` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `ibus` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `ibus-gtk3` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `ibus-gtk4` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `bash-completion` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `zenity` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `newt` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `openssh-server` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `sudo` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `nano` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dracut` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `kmod` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `e2fsprogs` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `parted` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cloud-utils-growpart` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `kexec-tools` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `zram-generator-defaults` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `firefox` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `flatpak` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `fuse` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `fuse-libs` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `dejavu-sans-fonts` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `liberation-fonts` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `adobe-source-code-pro-fonts` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `fontconfig` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `google-noto-color-emoji-fonts` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `google-noto-sans-symbols-fonts` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| `xorg-x11-server-Xorg` |  | ✓ | ✓ |  |  |  |  |  |  |  |  |  |  |
| `xorg-x11-drv-amdgpu` |  | ✓ | ✓ |  |  |  |  |  |  |  |  |  |  |
| `xorg-x11-drv-libinput` |  | ✓ | ✓ |  |  |  |  |  |  |  |  |  |  |
| `xorg-x11-xinit` |  | ✓ | ✓ |  |  |  |  |  |  |  |  |  |  |
| `xorg-x11-utils` |  | ✓ | ✓ |  |  |  |  |  |  |  |  |  |  |
| `adwaita-icon-theme` |  | ✓ | ✓ |  |  |  |  |  |  |  |  |  |  |
| `hicolor-icon-theme` |  | ✓ | ✓ |  |  |  |  |  |  |  |  |  |  |
| `glib2` |  | ✓ | ✓ |  |  |  |  |  |  |  |  |  |  |
| `p7zip` |  | ✓ | ✓ | ✓ |  |  |  | ✓ |  | ✓ | ✓ | ✓ |  |
| `dnf-plugins-core` |  |  |  |  |  |  |  |  | ✓ |  |  |  |  |
| `tar` |  |  |  |  |  |  |  |  | ✓ |  |  |  |  |
| `xz` |  |  |  |  |  |  |  |  | ✓ |  |  |  |  |

## Blocs de script (actions)

| Bloc | `base` | `budgie_edition` | `cinnamon_edition` | `cosmic_edition` | `desktop_edition` | `dev_edition` | `gaming_edition` | `kde_edition` | `minimal_setup` | `miraclewm_edition` | `niri_edition` | `sway_edition` | `test_build` |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| Rafraîchissement des fontes | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| Activation globale de bash-completion pour les sessions Bash | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| RPM Fusion, Codecs & Flathub | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| Steam pilotes graphiques 32 bits | ✓ | ✓ | ✓ | ✓ |  |  | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| Flathub | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| Installation de Balena Etcher uniquement | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| Compilation et installation manuelle de ps5-linux-tools | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| SSH & Services de base | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| Session graphique (GDM, CUPS, Bluetooth) | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| grow-rootfs | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| SELinux désactivé | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| Utilisateur par défaut (ps5/ps5, sudo) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| Autologin GDM | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| Script Nautilus "Ouvrir dans le terminal" + lanceur dossier courant | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| Déverrouillage automatique du trousseau GNOME (fix cookies Opera/Chrome) | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  | ✓ |
| zram swap | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| Mise en veille désactivée (système + écran) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Écran : X11 / XWayland | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| GNOME, Cinnamon, Budgie, MATE : gsettings | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| KDE Plasma 6 : PowerDevil + verrouillage d'écran | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Installation Decky Loader | ✓ |  |  |  |  |  | ✓ |  |  |  |  |  | ✓ |
| Service systemd automatique pour Fan ON et Boost ON | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Installation PS5 Fedora Manager | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| Install custom kernel rpm | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| PS5 internal WiFi | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Budgie à la place de GNOME |  | ✓ |  |  |  |  |  |  |  |  |  |  |  |
| Session graphique (Budgie, CUPS, Bluetooth) |  | ✓ |  |  |  |  |  |  |  |  |  |  |  |
| Autologin SDDM (Budgie) |  | ✓ |  |  |  |  |  |  |  |  |  |  |  |
| Cinnamon (X11) à la place de GNOME |  |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| Session graphique (Cinnamon X11, CUPS, Bluetooth) |  |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| Autologin LightDM (Cinnamon X11) |  |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| COSMIC Desktop (remplace GNOME) |  |  |  | ✓ |  |  |  |  |  |  |  |  |  |
| Session graphique (COSMIC, CUPS, Bluetooth) |  |  |  | ✓ |  |  |  |  |  |  |  |  |  |
| Autologin COSMIC greeter (greetd) |  |  |  | ✓ |  |  |  |  |  |  |  |  |  |
| Gaming stack (Steam, Gamescope, MangoHud, GameMode) |  |  |  |  |  |  | ✓ |  |  |  |  |  | ✓ |
| KDE Plasma 6 (Wayland) à la place de GNOME |  |  |  |  |  |  |  | ✓ |  |  |  |  |  |
| Session graphique (KDE Plasma Wayland, CUPS, Bluetooth) |  |  |  |  |  |  |  | ✓ |  |  |  |  |  |
| Autologin SDDM (Plasma Wayland) |  |  |  |  |  |  |  | ✓ |  |  |  |  |  |
| Default user |  |  |  |  |  |  |  |  | ✓ |  |  |  |  |
| Miracle WM (Wayland, tiling) à la place de GNOME |  |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| Session graphique (Miracle WM Wayland, CUPS, Bluetooth) |  |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| Autologin SDDM (Miracle WM) |  |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| Niri (Wayland, scrollable tiling) à la place de GNOME |  |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| Session graphique (Niri Wayland, CUPS, Bluetooth) |  |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| Autologin SDDM (Niri) |  |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| Sway (Wayland, tiling) à la place de GNOME |  |  |  |  |  |  |  |  |  |  |  | ✓ |  |
| Session graphique (Sway Wayland, CUPS, Bluetooth) |  |  |  |  |  |  |  |  |  |  |  | ✓ |  |
| Autologin SDDM (Sway) |  |  |  |  |  |  |  |  |  |  |  | ✓ |  |

## Ajouts propres aux éditions

### `budgie_edition` — `ps5-fedora-budgie_edition`

- **Paquets en plus de la base** : `xorg-x11-server-Xorg`, `xorg-x11-drv-amdgpu`, `xorg-x11-drv-libinput`, `xorg-x11-xinit`, `xorg-x11-utils`, `adwaita-icon-theme`, `hicolor-icon-theme`, `glib2`, `p7zip`
- **Paquets retirés de la base** : 58 (voir le tableau)
- **Blocs propres à l'édition** : Budgie à la place de GNOME, Session graphique (Budgie, CUPS, Bluetooth), Autologin SDDM (Budgie)

### `cinnamon_edition` — `ps5-fedora-cinnamon_edition`

- **Paquets en plus de la base** : `xorg-x11-server-Xorg`, `xorg-x11-drv-amdgpu`, `xorg-x11-drv-libinput`, `xorg-x11-xinit`, `xorg-x11-utils`, `adwaita-icon-theme`, `hicolor-icon-theme`, `glib2`, `p7zip`
- **Paquets retirés de la base** : 58 (voir le tableau)
- **Blocs propres à l'édition** : Cinnamon (X11) à la place de GNOME, Session graphique (Cinnamon X11, CUPS, Bluetooth), Autologin LightDM (Cinnamon X11)

### `cosmic_edition` — `ps5-fedora-cosmic_edition`

- **Paquets en plus de la base** : `p7zip`
- **Paquets retirés de la base** : 58 (voir le tableau)
- **Blocs propres à l'édition** : COSMIC Desktop (remplace GNOME), Session graphique (COSMIC, CUPS, Bluetooth), Autologin COSMIC greeter (greetd)

### `desktop_edition` — `ps5-fedora-desktop_edition`

- **Paquets retirés de la base** : 13 (voir le tableau)

### `dev_edition` — `ps5-fedora-dev_edition`

- **Paquets retirés de la base** : 5 (voir le tableau)

### `gaming_edition` — `ps5-fedora-gaming_edition`

- **Paquets retirés de la base** : 18 (voir le tableau)
- **Blocs propres à l'édition** : Gaming stack (Steam, Gamescope, MangoHud, GameMode)

### `kde_edition` — `ps5-fedora-kde_edition`

- **Paquets en plus de la base** : `p7zip`
- **Paquets retirés de la base** : 58 (voir le tableau)
- **Blocs propres à l'édition** : KDE Plasma 6 (Wayland) à la place de GNOME, Session graphique (KDE Plasma Wayland, CUPS, Bluetooth), Autologin SDDM (Plasma Wayland)

### `minimal_setup` — `ps5-fedora-minimal_setup`

- **Paquets en plus de la base** : `dnf-plugins-core`, `tar`, `xz`
- **Paquets retirés de la base** : 157 (voir le tableau)
- **Blocs propres à l'édition** : Default user

### `miraclewm_edition` — `ps5-fedora-miraclewm_edition`

- **Paquets en plus de la base** : `p7zip`
- **Paquets retirés de la base** : 58 (voir le tableau)
- **Blocs propres à l'édition** : Miracle WM (Wayland, tiling) à la place de GNOME, Session graphique (Miracle WM Wayland, CUPS, Bluetooth), Autologin SDDM (Miracle WM)

### `niri_edition` — `ps5-fedora-niri_edition`

- **Paquets en plus de la base** : `p7zip`
- **Paquets retirés de la base** : 58 (voir le tableau)
- **Blocs propres à l'édition** : Niri (Wayland, scrollable tiling) à la place de GNOME, Session graphique (Niri Wayland, CUPS, Bluetooth), Autologin SDDM (Niri)

### `sway_edition` — `ps5-fedora-sway_edition`

- **Paquets en plus de la base** : `p7zip`
- **Paquets retirés de la base** : 58 (voir le tableau)
- **Blocs propres à l'édition** : Sway (Wayland, tiling) à la place de GNOME, Session graphique (Sway Wayland, CUPS, Bluetooth), Autologin SDDM (Sway)

### `test_build` — `ps5-fedora-test_build`

- **Blocs propres à l'édition** : Gaming stack (Steam, Gamescope, MangoHud, GameMode)

Légende : ✓ = présent dans la build.
