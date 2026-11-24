# Fonctionnement du builder — `build_image.sh`

Le dépôt construit des images Linux amorçables pour PlayStation 5 (image disque GPT à
flasher sur clé USB) en enchaînant des conteneurs Docker : compilation du noyau PS5,
construction du rootfs de la distribution, puis assemblage de l'image disque.

- Éditeur graphique des YAML : [`editor_fr.md`](editor_fr.md)
- English version: [`builder_en.md`](builder_en.md)

## Vue d'ensemble

```
build_image.sh --distro fedora --variant fedora-gaming_edition
        │
        ├─ 1. Noyau      : clone ps5-linux-patches + linux stable, applique les patches,
        │                  compile, installe les modules dans linux-bin/staging,
        │                  puis empaquette en .rpm (fedora) / .deb / .pkg.tar.zst
        │
        ├─ 2. Rootfs     : distrobuilder build-dir distros/fedora/<edition>.yaml
        │                  -> work/chroot-fedora-<edition>/  (dnf, fichiers, scripts)
        │
        └─ 3. Image      : truncate + parted + mkfs + copie du rootfs
                           -> output/<image.name>.img
```

Tout ce qui est verbeux part dans `build.log` ; le terminal affiche un spinner par
étape. Le script est en `set -e` : la première étape en échec arrête tout, et le
message final propose `--clean` quand le cache est suspect.

## Prérequis

- Docker, avec le droit de lancer des conteneurs `--privileged`
  (`sudo usermod -aG docker $USER` puis `newgrp docker`).
- ~30 Go d'espace libre (rootfs + noyau + image de 12 Go).
- Le build tourne en `linux/amd64` (`DOCKER_DEFAULT_PLATFORM` est exporté).

## Utilisation

```bash
./build_image.sh                                        # Ubuntu 26.04 (défaut)
./build_image.sh --distro fedora                         # édition de base (image.yaml)
./build_image.sh --distro fedora --variant fedora-dev_edition
./build_image.sh --distro all                            # image multi-distro 32 Go
./build_image.sh --kernel-only                           # noyau seul, pas d'image
```

| Option | Rôle | Défaut |
|---|---|---|
| `--distro` | `ubuntu2604`, `arch`, `cachyos`, `fedora`, `proxmox`, `debian`, `bazzite`, `bazzite-deck`, `batocera`, `all` | `ubuntu2604` |
| `--variant` | nom du YAML dans `distros/<distro>/` (sans `.yaml`) | `image` |
| `--kernel` | répertoire source du noyau déjà cloné | auto (`work/linux`) |
| `--img-size` | taille de l'image en Mo | `12000` (`32000` pour `all`) |
| `--clean` | supprime tous les caches puis reconstruit | off |
| `--clean-only` | supprime les caches et sort | off |
| `--kernel-only` | compile et empaquette le noyau, puis sort | off |
| `--patches-ref` | branche/tag/SHA des patches PS5 | tag défini dans le script |
| `--print-name` | affiche le nom d'image résolu depuis le YAML, puis sort | off |

Une variante inconnue affiche la liste des éditions disponibles et sort en erreur.

## Les trois étapes

### 1. Noyau

1. `work/ps5-linux-patches` est cloné (shallow) sur `--patches-ref`.
2. La version cible est lue dans l'en-tête `# Linux/x.y.z …` du `.config` du patch set,
   puis le noyau stable correspondant est cloné dans `work/linux` (depth 1).
3. Tous les `*.patch` sont appliqués (`git apply --exclude=Makefile`), et le `.config`
   du patch set est copié.
4. L'image `ps5-kernel-builder` compile le noyau ; tous les artefacts sont écrits dans
   `linux-bin/staging/` (bzImage, System.map, modules, headers, `/etc` et `/usr/local`
   pour les helpers PS5 : firmware, BT, etc.).
5. Le format de paquet dépend de la distribution : `.rpm` (fedora/bazzite), `.deb`
   (ubuntu/debian/proxmox), `.pkg.tar.zst` (arch/cachyos), les trois pour `all`.
6. `linux-bin/VERSION` contient la version du noyau (nom du répertoire de modules).

### 2. Rootfs

`docker/image-builder/entrypoint.sh` prépare `/tmp/build-staging` (hooks
`zz-update-boot`, `fstab` avec les labels, `grow-rootfs`, paquets du noyau), puis
lance :

```bash
distrobuilder build-dir "$IMAGE_YAML" "$CHROOT" \
    --with-post-files --cache-dir /build/cache --cleanup=false
```

C'est **le YAML de l'édition qui pilote cette étape** : paquets, fichiers et actions.
Les distributions qui fournissent leur propre `distros/<distro>/build-rootfs.sh`
(bazzite, batocera…) remplacent distrobuilder.

Le chroot est réutilisé d'un run à l'autre s'il est déjà peuplé ; `--clean` le vide.

### 3. Image disque

- fichier temporaire `output/.<nom>.img.tmp` (`truncate` à `--img-size`) ;
- table GPT : p1 ext4 (root, de 500 Mo à la fin), p2 FAT32 (ESP, 1 Mo → 500 Mo) ;
- `losetup` + `kpartx`, `mkfs.ext4 -L <distro>` et `mkfs.vfat -n boot` ;
- copie du chroot, déplacement de `/boot/efi` vers la partition ESP ;
- `cmdline.txt` (gabarit `distros/<distro>/cmdline.txt` ou `boot/cmdline.txt`, avec
  `__DISTRO__` remplacé par le label), `vram.txt`, `kexec.sh` ;
- renommage final en `output/<image.name>.img`.

## Éditions (YAML) et nom d'image

Chaque build Fedora est décrite par un fichier `distros/fedora/<stem>.yaml`. Le nom de
l'image vient de `image.name` dans ce fichier :

| Édition | YAML | `image.name` |
|---|---|---|
| Base | `image.yaml` | `ps5-fedora` |
| Desktop | `fedora-desktop_edition.yaml` | `ps5-fedora-desktop_edition` |
| Gaming | `fedora-gaming_edition.yaml` | `ps5-fedora-gaming_edition` |
| Dev | `fedora-dev_edition.yaml` | `ps5-fedora-dev_edition` |
| Minimal | `fedora-minimal_setup.yaml` | `ps5-fedora-minimal_setup` |
| Test | `fedora-test_build.yaml` | `ps5-fedora-test_build` |

- `image.name` devient le `.img`, les noms d'archives et le préfixe du tag de release.
- Sans `image.name`, le script retombe sur `ps5-<distro>[-<variant>]`.
- Chaque édition a **son propre chroot** : `work/chroot` pour `image.yaml`,
  `work/chroot-<distro>-<variant>` sinon. Aucune réutilisation croisée.
- `--print-name` imprime le nom résolu (utilisé par le workflow).

## Anatomie d'un YAML d'édition

```yaml
image:
  name: ps5-fedora-gaming_edition     # -> output/ps5-fedora-gaming_edition.img
  distribution: fedora
  release: "45"
  description: Fedora GNOME + Gaming  # reprise dans la release GitHub
  architecture: x86_64

source:                               # d'où vient le rootfs
  downloader: fedora-http
  url: https://kojipkgs.fedoraproject.org
  skip_verification: true

packages:
  manager: dnf
  update: true
  cleanup: true
  sets:
    - packages:
        # commentaire = titre du groupe dans l'éditeur
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
  - trigger: post-unpack            # toujours exécuté en entier
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

Points importants :

- **Triggers** utilisés : `post-unpack`, `post-update`, `post-packages`, `post-files`.
- Les commentaires `# --- Titre ---` découpent un trigger en blocs que l'éditeur peut
  cocher/décocher ; sans marqueur, tout le script est conservé.
- Les paquets du noyau sont copiés dans `/opt/rpms` (générateur `copy` sur
  `/tmp/build-staging/rpms`) et installés par un bloc de `post-packages`.
- `steam`, `gamescope`, `mangohud`, `gamemode` doivent être installés **après** RPM
  Fusion (dans `post-packages`), sinon `dnf` échoue : ces paquets n'existent pas dans
  les dépôts Fedora de base.
- `ps5-linux-tools` est compilé pendant le build : la toolchain `git`, `make`, `gcc`
  (et `binutils`, `pkgconf`) doit rester dans les éditions concernées.
- Blocs présents dans toutes les builds : noyau, WiFi interne, fan ON/boost ON,
  PS5 Fedora Manager, RPM Fusion, Flathub, grow-rootfs, SELinux, utilisateur par
  défaut, zram.

## Ajouter une édition

**Avec l'éditeur** (recommandé) : voir [`editor_fr.md`](editor_fr.md), puis
`Enregistrer` — le fichier arrive dans `distros/fedora/` et le comparatif est mis à jour.

**À la main** :

1. `cp distros/fedora/fedora-dev_edition.yaml distros/fedora/fedora-ma_edition.yaml`
2. changer `image.name` et `image.description`, ajuster les paquets/scripts ;
3. rien d'autre : le workflow liste `distros/fedora/*.yaml` et construit, compresse et
   publie chaque fichier trouvé.

`image.yaml` sert aussi de base au job noyau du CI : elle doit rester la build de
référence complète.

## Intégration continue (GitHub Actions)

`.github/workflows/trigger-builds.yml` (`deploy`) déclenche `build-image.yml` sur
push vers `main` (sauf `tools/**`, `**.md`, `.gitignore`), sur lancement manuel, ou
sur une PR étiquetée `run-ci`.

```
editions ──► kernel ──► build (matrice, 1 édition à la fois) ──► release (matrice)
```

| Job | Rôle |
|---|---|
| `editions` | liste `distros/fedora/*.yaml` (ou seulement `variant` si fourni) et produit la matrice |
| `kernel` | compile le noyau **une fois**, copie le `.rpm` dans `kernel-pkg/` et publie l'artefact `kernel-rpm` |
| `build` | pour chaque édition : télécharge le `.rpm`, lance `build_image.sh --variant <edition>`, vérifie l'image, compresse en volumes 7z de 1,5 Gio (`7z -mx=4 -v1500m`) |
| `release` | publie une release par édition, avec checksums, et élague les anciennes |

- Tag : `<image.name>-AAAA.MM.JJ-HHMM` en UTC, par exemple
  `ps5-fedora-gaming_edition-2026.11.24-1830`.
- Rien n'est écrasé : chaque build crée un nouveau tag.
- `KEEP_RELEASES: '5'` (dans `build-image.yml`) : seules les 5 releases datées les plus
  récentes de chaque édition sont gardées, les suivantes sont supprimées (release +
  tag). Le badge *Latest* n'est posé que par l'édition `image`.
- Les volumes 7z font 1,5 Gio pour rester sous la limite de 2 Gio par fichier GitHub.
- Le job `kernel` copie le `.rpm` dans un dossier appartenant au runner avant l'upload :
  `linux-bin/` contient aussi l'arbre `staging/` écrit en root par le conteneur, que
  `upload-artifact` ne peut pas lire.
- **Un échec est isolé par édition.** `build` tourne avec `fail-fast: false` ; l'étape
  « Build <édition> image » est en `continue-on-error`, les étapes suivantes (report,
  compression, artefacts) sont sautées pour cette édition seulement, puis une dernière
  étape remet le job en échec avec un résumé dans le *job summary*. Les autres éditions
  de la matrice continuent, et `release` (`!cancelled()`) publie uniquement celles qui
  ont produit leurs archives : une édition sans artefact reçoit un simple avertissement.
  Un run peut donc être rouge tout en publiant les builds valides.

## Sorties

| Chemin | Contenu |
|---|---|
| `output/<image.name>.img` | image disque GPT à flasher |
| `output/*.img.7z.00*` | archives (CI) |
| `linux-bin/*.rpm` / `*.deb` / `*.pkg.tar.zst` | paquets du noyau |
| `linux-bin/VERSION` | version du noyau compilé |
| `linux-bin/staging/` | artefacts intermédiaires du noyau (non publiés) |
| `work/chroot[-…]/` | rootfs mis en cache |
| `build.log` | journal complet du build |

Flasher sur clé USB :

```bash
sudo dd if=output/ps5-fedora.img of=/dev/sdX bs=4M status=progress
```

Pour les releases, télécharger **tous** les volumes puis extraire le `.001`.

## Noyau seul et multi-distro

```bash
./build_image.sh --kernel-only                     # .deb (défaut ubuntu)
./build_image.sh --kernel-only --distro fedora     # .rpm
./build_image.sh --kernel-only --distro all        # .deb + .pkg.tar.zst
```

`--distro all` construit une image de 32 Go, quatre partitions (ESP + Ubuntu + Arch +
CachyOS) avec des scripts `kexec` pour changer de distribution au démarrage.

## Dépannage

| Symptôme | Cause / solution |
|---|---|
| `permission denied` sur `docker` | `sudo usermod -aG docker $USER` puis `newgrp docker` |
| `Unknown edition 'x' for fedora` | le YAML n'existe pas dans `distros/fedora/` ; le message liste les éditions |
| `dnf` échoue sur steam/gamescope | paquets installés avant RPM Fusion : les déplacer après dans `post-packages` |
| Échec de compilation de ps5-linux-tools | `git`/`make`/`gcc` absents de l'édition |
| rootfs incohérent après une modification | relancer avec `--clean` (vide `work/`, `linux-bin/`, `cache/`, `output/`) |
| « no space left on device » | libérer de l'espace : chaque édition garde son chroot + image de 12 Go |
| Artefact noyau en `EACCES` dans le CI | ne pas uploader `linux-bin/` en entier : le workflow copie d'abord le `.rpm` |
| Rien ne se lance après un push | le workflow ignore `tools/**`, `**.md`, `.gitignore` : toucher `distros/**` ou lancer `deploy` manuellement |
| `Failed to enable unit: Unit x.service does not exist` | le script active un service dont le paquet n'est pas installé dans l'édition ; `enable_unit` (dans `post-packages`) ignore désormais les unités absentes |
| Une seule édition est rouge, les autres sont publiées | comportement voulu : les échecs sont isolés ; corriger le YAML puis relancer avec `variant` |

## Carte des fichiers

```
build_image.sh                     # orchestration (noyau, rootfs, image)
docker/kernel-builder/             # compilation du noyau + packaging .deb
docker/kernel-builder-rpm/         # packaging .rpm (spec linux-ps5)
docker/kernel-builder-arch/        # packaging .pkg.tar.zst
docker/image-builder/
  Dockerfile                       # distrobuilder, skopeo, umoci, parted…
  entrypoint.sh                    # build d'une distribution
  entrypoint-multi.sh              # build multi-distro
distros/fedora/*.yaml              # une édition = un fichier
distros/fedora/build-rootfs.sh     # (si présent) rootfs maison
distros/shared/                    # hooks communs (zz-update-boot…)
boot/                              # cmdline.txt, vram.txt, kexec.sh
tools/edition_editor.py            # éditeur graphique des YAML
doc/                               # cette documentation
```
