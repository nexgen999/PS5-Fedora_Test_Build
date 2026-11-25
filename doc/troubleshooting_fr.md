# Dépannage

Guide par symptôme. Commencez toujours par la **première erreur** du log : les suivantes
en découlent presque toujours.

- Catalogue des builds : [`editions_fr.md`](editions_fr.md)
- Pipeline CI : [`ci_fr.md`](ci_fr.md)
- Builder local : [`builder_fr.md`](builder_fr.md)
- English version: [`troubleshooting_en.md`](troubleshooting_en.md)

## Où lire quoi

| Contexte | Endroit |
|---|---|
| Build local | sortie terminal + `build.log` (tout le détail verbeux) |
| CI | log de l'étape rouge, puis *Summary* du run |
| Système installé | `journalctl -b`, `systemctl --failed` depuis la PS5 |

## Build local

| Symptôme | Cause | Solution |
|---|---|---|
| `permission denied` sur `docker` | utilisateur hors du groupe docker | `sudo usermod -aG docker $USER` puis `newgrp docker` |
| `Unknown edition 'x' for fedora` | le YAML n'existe pas | le message liste les éditions ; `--variant` prend le nom **sans** `.yaml` |
| `dnf` échoue sur Steam/GameScope | paquets installés avant RPM Fusion | garder l'ordre des blocs : RPM Fusion d'abord, gaming ensuite |
| Échec de compilation de `ps5-linux-tools` | `git`/`make`/`gcc` absents | ajouter ces paquets à l'édition (le YAML `minimal_setup` les a) |
| Rootfs incohérent après une modification | cache `work/chroot-…` obsolète | relancer avec `--clean` (vide `work/`, `linux-bin/`, `cache/`, `output/`) |
| `no space left on device` | chroot + image de 12 Go par édition | libérer de l'espace ou baisser `--img-size` |
| Le noyau est recompilé à chaque fois | `linux-bin/*.rpm` absent ou supprimé | normal après `--clean` ; sinon le script réutilise le `.rpm` existant |

## CI / GitHub Actions

| Symptôme | Cause | Solution |
|---|---|---|
| Rien ne se lance après un push | `paths-ignore` (`tools/**`, `**.md`, `.gitignore`) | toucher `distros/**` ou lancer le workflow manuellement |
| Une seule édition est rouge, les autres publiées | isolation voulue | corriger le YAML puis relancer avec `variant` |
| `::error::Edition X failed to build` | étape `build` en échec | ouvrir le log de « Build X image » : la première erreur est la cause |
| `Failed to enable unit: Unit x.service does not exist` | le script active un service dont le paquet n'est pas installé dans l'édition | déjà géré par `enable_unit` (l'unité est ignorée) ; pour l'activer vraiment, ajouter le paquet |
| `ERREUR: cosmic-session absent` / `sway absent` / `niri absent` / `miracle-wm absent` | groupe comps ou paquet indisponible pour cette release Fedora | vérifier `dnf environment list` / `dnf list` sur Fedora 45, corriger le nom, relancer |
| `no .rpm produced in image/linux-bin` | échec de packaging du noyau | lire le log du job `kernel` ; relancer après correction |
| Artefact noyau en `EACCES` | upload de l'arbre `linux-bin/staging/` (fichiers root) | ne pas uploader `linux-bin/` : le workflow copie le `.rpm` dans `kernel-pkg/` |
| `An error has occurred during zip creation for the artifact` | même cause : `upload-artifact` zippe des fichiers illisibles | conserver le motif `kernel-pkg/` |
| Le job `kernel` ne recompile pas | cache valide (tag de patches et recettes inchangés) | comportement voulu ; pour forcer, supprimer le cache `kernel-rpm-…` dans Actions → Caches |
| `No build output for edition X; skipping its release` | build en échec ou artefact absent | corriger le build ; la release du run contient les autres éditions |
| `fatal error: zlib.h: No such file or directory` (étape `make` de ps5-linux-tools) | l'édition installe `ps5-linux-tools` sans les en-têtes zlib | ajouter `zlib-devel` au bloc toolchain (`m2_init.c` inclut `<zlib.h>`, le Makefile passe `-lz`) — corrigé pour `minimal_setup` |
| L'écran s'éteint ou la PS5 se met en veille | réglages du bureau ou `systemd-logind` | lancer `sudo ps5-no-sleep` (masque `sleep`/`suspend`/`hibernate`, coupe l'extinction d'écran GNOME/Cinnamon/Budgie/KDE) ; il tourne aussi à chaque login |
| `fatal: not a git repository` dans `publish` | job sans `checkout`, `gh` ne peut pas deviner le dépôt | les commandes `gh release create/upload` passent `--repo "$GITHUB_REPOSITORY"` |
| Release refusée / tag déjà existant | deux runs dans la même seconde | le tag contient les secondes (`HHMMSS`) ; relancer |
| Le run dure longtemps | 13 éditions à construire | le noyau est mis en cache ; les builds tournent en parallèle |

## YAML et éditeur graphique

| Symptôme | Cause | Solution |
|---|---|---|
| « mode verrouillé » | le YAML contient des scripts absents de `image.yaml` (ex. `minimal_setup`) | comportement voulu : les scripts sont conservés tels quels, seuls les paquets et blocs reconnus changent |
| Les ajouts ne sont pas écrits en mode verrouillé | limitation du mode verrouillé | avertissement affiché ; éditer le YAML à la main pour ce cas |
| Un bloc n'apparaît pas dans l'éditeur | marqueur `# --- Titre ---` manquant | ajouter le marqueur au-dessus du bloc |
| `--check` ne liste pas un bloc comme `[commun]` | contenu différent de `image.yaml` | normal pour un bloc spécifique à l'édition (il sera `[optionnel]`) |
| `build.difference.md` semble obsolète | fichier généré | relancer `python3 tools/edition_editor.py --difference` |

## Sur la PS5, une fois démarrée

| Symptôme | Diagnostic | Piste |
|---|---|---|
| Pas de session graphique | `systemctl --failed`, `journalctl -b -u sddm` | vérifier que le greeter est activé et que la session existe |
| SDDM écran noir | `journalctl -b -u sddm`, `ls /usr/share/wayland-sessions` | nom de session dans `autologin.conf` erroné, ou greeter X11 sans serveur X : `sddm-wayland-sway` / `sddm-wayland-plasma` |
| COSMIC ne démarre pas | `systemctl status cosmic-greeter`, `cat /etc/greetd/cosmic-greeter.toml` | le greeter utilise `greetd` ; l'autologin est un bloc `[initial_session]` |
| GNOME redemande l'assistant de configuration | marqueur manquant | `/home/ps5/.config/gnome-initial-setup-done` doit exister |
| Applications X11 muettes | `echo $XDG_SESSION_TYPE`, `ls /usr/bin/Xwayland` | XWayland est installé ; vérifier le paquet `xorg-x11-server-Xwayland` |
| Pas de WiFi interne | `systemctl status ps5-iw620`, `dmesg | grep -i moal` | firmware attendu dans l'ESP (`nxp/pcieuartiw620_combo_v1.bin`) ; `nmcli radio wifi on` |
| Ventilateur/boost inactifs | `systemctl status ps5-performance`, `ps5_control --fan on` | le binaire est dans `/usr/local/sbin/ps5_control`, service oneshot |
| PS5 Fedora Manager absente | `ls /usr/share/applications | grep -i ps5` | le bloc d'installation est dans `post-files` ; `update-desktop-database` |
| Mauvaise résolution / pas de Vulkan | `vulkaninfo --summary` | Mesa AMD doit être présent ; évolution du firmware PS5 hors périmètre |

Commandes de diagnostic utiles :

```bash
systemctl --failed
journalctl -b -p err
ls /usr/share/wayland-sessions/     # noms utilisables dans Session=
nmcli device status
ip -br addr
df -h /
free -h
```

## Archives et releases

| Symptôme | Cause | Solution |
|---|---|---|
| Extraction impossible | volume manquant | télécharger **tous** les `*.7z.00N` dans le même dossier puis `7z x …001` |
| Checksum différent | téléchargement interrompu | comparer avec `meta/<image>.sha256` publié dans le corps de la release |
| Ancienne release disparue | élagage automatique | `KEEP_RELEASES` = 5 releases (une par run) ; récupérer une version plus récente |
| Release sans une édition | build en échec dans ce run | voir la section « Éditions non publiées » du corps de la release, puis le run lié |
| Une release par édition dans l'ancien format | releases créées avant le passage à une release par run | elles ne sont pas élaguées ; les supprimer à la main une fois les nouvelles vérifiées |
