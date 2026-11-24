# Les builds Fedora — catalogue

Chaque build est **un fichier YAML** dans `distros/fedora/`. Le workflow les découvre
tout seul : ajouter un fichier suffit à obtenir une nouvelle image, ses archives et sa
propre release. Le nom de l'image, des archives et du tag vient de `image.name` dans le
YAML.

- Éditeur graphique pour cocher/décocher : [`editor_fr.md`](editor_fr.md)
- Fonctionnement du builder : [`builder_fr.md`](builder_fr.md)
- Pipeline GitHub Actions : [`ci_fr.md`](ci_fr.md)
- Dépannage : [`troubleshooting_fr.md`](troubleshooting_fr.md)
- English version: [`editions_en.md`](editions_en.md)

## Tableau récapitulatif

| Édition | Fichier | `image.name` | Paquets | Bureau / session | Connexion |
|---|---|---|--:|---|---|
| Base | `image.yaml` | `ps5-fedora` | 194 | GNOME (Wayland) | GDM + autologin |
| Desktop | `fedora-desktop_edition.yaml` | `ps5-fedora-desktop_edition` | 181 | GNOME (Wayland) | GDM + autologin |
| Dev | `fedora-dev_edition.yaml` | `ps5-fedora-dev_edition` | 189 | GNOME (Wayland) | GDM + autologin |
| Gaming | `fedora-gaming_edition.yaml` | `ps5-fedora-gaming_edition` | 176 | GNOME (Wayland) | GDM + autologin |
| Test | `fedora-test_build.yaml` | `ps5-fedora-test_build` | 194 | GNOME (Wayland) | GDM + autologin |
| Minimal | `fedora-minimal_setup.yaml` | `ps5-fedora-minimal_setup` | 39 | aucune (CLI) | console / SSH |
| COSMIC | `fedora-cosmic_edition.yaml` | `ps5-fedora-cosmic_edition` | 137 | COSMIC (Wayland) | cosmic-greeter (greetd) |
| KDE | `fedora-kde_edition.yaml` | `ps5-fedora-kde_edition` | 137 | Plasma 6 (Wayland) | SDDM |
| Sway | `fedora-sway_edition.yaml` | `ps5-fedora-sway_edition` | 137 | Sway (Wayland) | SDDM |
| Niri | `fedora-niri_edition.yaml` | `ps5-fedora-niri_edition` | 137 | Niri (Wayland) | SDDM |
| Miracle WM | `fedora-miraclewm_edition.yaml` | `ps5-fedora-miraclewm_edition` | 137 | Miracle WM (Wayland) | SDDM |

Le nombre de paquets est celui **listé dans le YAML** (ce que voit
[`build.difference.md`](../build.difference.md)). Les environnements de bureau alternatifs
(COSMIC, Plasma, Sway, Niri, Miracle WM) sont installés par leur groupe comps dans
`post-packages`, donc l'image finale contient bien plus que ces 137 paquets.

## Socle commun à toutes les builds Fedora

Tout ce qui suit est présent dans **chaque** image Fedora, quelle que soit l'édition :

- Fedora 45 x86_64 (`image.release: "45"`, source `kojipkgs.fedoraproject.org`), rootfs
  construit par distrobuilder.
- **Noyau PS5** compilé depuis `ps5-linux-patches` (tag `kernel-7.3.3-c8fe83a`, voir
  `PATCHES_REF` dans `build_image.sh`), empaqueté en `.rpm` et installé dans l'image
  depuis `/opt/rpms` par `post-files`.
- Utilisateur `ps5` / mot de passe `ps5`, groupe `wheel` avec `sudo` sans mot de passe,
  compte `root` verrouillé (`passwd -l root`), SSH activé (`PermitRootLogin no`,
  `PasswordAuthentication yes`).
- Réseau : `NetworkManager`, `avahi`, `iw`/`wpa_supplicant`/`wireless-regdb`,
  `linux-firmware`, SSH.
- **WiFi interne IW620** : service `ps5-iw620.service` qui récupère le firmware depuis
  l'ESP, décharge `moal` si nécessaire et réactive le radio.
- **Fan ON + Boost ON** : `ps5-performance.service` (oneshot) appelle `ps5_control --fan on`
  puis `--boost on`, binaire compilé depuis `ps5-linux-tools`.
- Rootfs extensible (`grow-rootfs.service`), zram = moitié de la RAM en zstd, SELinux
  désactivé.
- XWayland (`xorg-x11-server-Xwayland`) pour les applications X11, polkit, portals,
  polices, `bash-completion`.
- Toutes les sessions sont **Wayland** ; il n'y a pas de session X11 complète.

Commun à toutes **sauf `minimal_setup`** :

- RPM Fusion free + nonfree et les codecs (`ffmpeg`, `gstreamer1-plugins-bad-freeworld`,
  `gstreamer1-plugins-ugly`), Flathub, Balena Etcher, pilotes Mesa 32 bits (Steam/i686).
- **PS5 Fedora Manager** (application GTK4) installée dans `/usr/share/applications`.

## Famille GNOME

Ces cinq builds partagent le même bloc de bureau (GNOME Shell + GDM) et le même mécanisme
d'autologin : `/etc/gdm/custom.conf` avec `AutomaticLogin=ps5` et le marqueur
`gnome-initial-setup-done` pour ne pas afficher l'assistant au premier boot.

### Base — `image.yaml` → `ps5-fedora` (194 paquets)

La référence : GNOME complet, applications GNOME, connectivité mobile (GSConnect, MTP,
SSHFS, ADB/Fastboot), impression/scan, codecs, outillage de développement complet et
pile gaming (Steam, Decky Loader). C'est la seule édition qui porte le badge **Latest**
sur GitHub.

### Desktop — `fedora-desktop_edition.yaml` → 181 paquets

GNOME + applications + codecs + mobile + impression, **sans** l'outillage de
développement (pas de `gcc`/`cmake`/`gdb`/`rpm-build`/`python3-pip`) ni la pile gaming.
À choisir pour un poste de travail classique.

### Dev — `fedora-dev_edition.yaml` → 189 paquets

GNOME + toolchain complète (`gcc`, `gcc-c++`, `gdb`, `cmake`, `meson`, `ninja`,
`autoconf`, `automake`, `libtool`, `rpm-build`, `python3-pip`, `python3-pyyaml`) et
l'impression, **sans** gaming. À choisir pour compiler sur la console.

### Gaming — `fedora-gaming_edition.yaml` → 176 paquets

GNOME + Steam, Gamescope, MangoHud, GameMode, Mesa 32 bits, Decky Loader, sans la
toolchain de développement. À choisir si la PS5 sert de console de jeu.

### Test — `fedora-test_build.yaml` → 194 paquets

Copie complète de la base sous un autre nom, utilisée pour tester une modification sans
toucher aux releases de `ps5-fedora` (qui garde le badge Latest).

## Famille Wayland alternative (137 paquets listés)

Ces cinq builds partagent un socle identique : infrastructure de bureau (portals, GVfs,
polkit, PipeWire/WirePlumber, Mesa, NetworkManager et plugins), impression/scan,
connectivité mobile, toolchain de dev, localisation FR/EN + ibus, polices, Firefox,
Flatpak, et tout le post-files PS5 (fan/boost, manager, rpm noyau, WiFi interne, zram).
**GNOME est totalement absent** (pas de `gnome-shell`, `gdm`, `nautilus`,
`gnome-keyring`, ni applications GNOME).

Le bureau est installé dans `post-packages` par un groupe comps, puis une session
Wayland est activée avec autologin `ps5` :

| Édition | Installation | Session / autologin |
|---|---|---|
| COSMIC | `@cosmic-desktop-environment` + `cosmic-greeter cosmic-session cosmic-settings` | `cosmic-greeter.service` (greetd), `[initial_session] command = "cosmic-session"` dans `/etc/greetd/cosmic-greeter.toml` |
| KDE | `@kde-desktop-environment` + `sddm-wayland-plasma` | `sddm`, `/etc/sddm.conf.d/autologin.conf` → `Session=plasma` |
| Sway | `@sway-desktop-environment` + Waybar/foot/fuzzel/mako/grim/slurp, `xdg-desktop-portal-wlr`, `xwayland-satellite` | `sddm` (+ `sddm-wayland-sway`), `Session=sway` |
| Niri | `niri` + même outillage | `sddm`, `Session=niri` |
| Miracle WM | `@miraclewm-desktop-environment` + même outillage | `sddm`, `Session=miracle-wm` |

Détails utiles :

- Chaque édition vérifie que le binaire de session existe
  (`startplasma-wayland`, `sway`, `niri`, `miracle-wm`) et **échoue explicitement** sinon :
  pas d'image sans bureau.
- `xorg-x11-server-Xorg` est installé en secours pour le greeter SDDM s'il retombe sur son
  mode X11 ; les applications X11 tournent de toute façon via XWayland.
- Le nom dans `Session=` doit correspondre à un fichier de
  `/usr/share/wayland-sessions/` (sans `.desktop`). Pour changer de session par défaut,
  c'est cette ligne qu'il faut éditer.
- Contrairement à la famille GNOME, ces builds n'installent pas l'Extension Manager
  Flatpak (application GNOME).

À choisir selon la préférence : **KDE** pour l'écosystème Qt et les réglages graphiques,
**COSMIC** pour un bureau moderne proche de GNOME, **Sway/Miracle WM** pour du pavage
i3-like, **Niri** pour du pavage défilant.

## Minimal — `fedora-minimal_setup.yaml` → 39 paquets

Aucune session graphique : SSH, NetworkManager (+ WiFi), noyau PS5, fan/boost, WiFi
interne, zram, grow-rootfs, `git`/`make`/`gcc` (nécessaires pour compiler `ps5_control`),
polices console, localisation FR/EN. Pas de Flatpak, pas de codecs, pas de manager.
Idéale comme base serveur ou pour partir d'un système nu et ajouter ce qu'on veut.

## Choisir en une ligne

| Besoin | Édition |
|---|---|
| Le maximum d'applications GNOME | Base (`ps5-fedora`) |
| Poste de travail GNOME sans outils de dev | Desktop |
| Compiler / développer | Dev |
| Jouer (Steam, MangoHud…) | Gaming |
| Tester sans polluer la base | Test |
| Bureau Wayland non-GNOME | KDE, COSMIC, Sway, Niri ou Miracle WM |
| Serveur / console | Minimal |

## Construire une édition

```bash
./build_image.sh --distro fedora --variant fedora-sway_edition
# -> output/ps5-fedora-sway_edition.img  (12 Go par défaut)
```

- `--variant` prend le **nom du fichier sans `.yaml`**. Une variante inconnue liste les
  éditions disponibles et sort en erreur.
- `--print-name` affiche seulement le nom d'image résolu (utilisé par le CI).
- `--img-size` change la taille de l'image, `--clean` repart de zéro.
- Comptez ~30 Go libres : chaque édition garde son chroot dans
  `work/chroot-fedora-<édition>/`, plus l'image de 12 Go.
- Via GitHub Actions, tout est construit automatiquement (voir [`ci_fr.md`](ci_fr.md)) ;
  une édition peut être relancée seule avec l'entrée `variant`.

## Modifier une édition

Deux méthodes, décrites en détail dans [`editor_fr.md`](editor_fr.md) :

1. **Éditeur graphique** (`python3 tools/edition_editor.py`) : cocher/décocher des
   paquets et des blocs `# --- … ---`, ajouter dépôts, paquets RPM, flatpaks, commandes
   et scripts, puis enregistrer le YAML et régénérer `build.difference.md`.
2. **À la main** : éditer le YAML. Les blocs de script sont repérés par leurs marqueurs
   `# --- Titre ---` ; garder ces marqueurs permet à l'éditeur de continuer à les
   reconnaître.

Après modification, `git push` sur `main` déclenche la reconstruction (sauf si le commit
ne touche que `tools/**`, `**.md` ou `.gitignore`).

## Limites connues

- Les images ne sont **pas signées** et la vérification de la source Fedora est
  désactivée (`skip_verification: true`) : la chaîne repose sur HTTPS et sur les
  checksums publiés dans chaque release.
- Le mot de passe `ps5` est public : à changer après le premier boot si la machine est
  exposée au réseau.
- Toutes les sessions sont Wayland ; une application qui exige un serveur X11 complet ne
  fonctionnera pas (XWayland couvre la majorité des cas).
- Les anciennes releases sont élaguées à 5 par édition (`KEEP_RELEASES`), et les
  artefacts CI expirent après 7 jours.
