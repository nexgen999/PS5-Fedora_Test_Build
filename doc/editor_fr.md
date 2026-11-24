# L'éditeur d'éditions — `tools/edition_editor.py`

Outil en Python/Tkinter qui part de la build de référence `distros/fedora/image.yaml`
et écrit un YAML d'édition autonome dans `distros/fedora/`. On y coche les paquets et
les blocs de script à garder, on ajoute éventuellement dépôts, paquets RPM, flatpaks,
commandes et scripts, puis on enregistre : le fichier produit garde exactement le
format de la base, donc `build_image.sh`, `entrypoint.sh` et le workflow GitHub n'ont
rien de spécifique à faire — il suffit que le fichier existe pour qu'une nouvelle
build, ses archives et sa release soient créées.

- Documentation du builder : [`builder_fr.md`](builder_fr.md)
- English version: [`editor_en.md`](editor_en.md)

## Prérequis et lancement

```bash
sudo dnf install python3-tkinter     # Fedora (une seule fois)
sudo apt install python3-tk          # Debian/Ubuntu

python3 tools/edition_editor.py               # ouvre la fenêtre
python3 tools/edition_editor.py --check       # affiche ce qui est lu, sans GUI
python3 tools/edition_editor.py --difference  # régénère build.difference.md
```

| Commande | Effet |
|---|---|
| sans argument | interface graphique |
| `--check` | liste les groupes de paquets et les blocs de script (marqués `commun` ou `optionnel`) |
| `--difference` | réécrit `build.difference.md` à la racine du dépôt |

Sans tkinter, le module reste importable : `--check` et `--difference` fonctionnent,
seul le lancement de la fenêtre est refusé avec un message d'installation.
PyYAML est **optionnel** : s'il est présent, chaque YAML généré est validé avant
écriture ; sinon l'outil écrit sans validation (le build la fera de toute façon).

## Ce que l'outil lit dans `image.yaml`

Le fichier n'est pas rechargé via PyYAML : il est découpé ligne par ligne, ce qui
permet de réécrire un YAML identique à l'octet près (commentaires, ordre, indentation).

| Partie du YAML | Traitement |
|---|---|
| `image:` | recopié tel quel, sauf `name` et `description` qui sont remplacés à l'enregistrement |
| `source:` | recopié tel quel |
| `packages:` → `sets:` → `- packages:` | chaque ligne de commentaire suivie de `- paquet` forme un **groupe** ; le reste (`manager`, `update`, `cleanup`, `sets:`, `action: install`) est conservé |
| `files:` | recopié tel quel (générateurs `hostname`, `hosts`, `dump`, `copy` vers `/tmp/build-staging`) |
| `actions:` | découpé par `- trigger:` puis par marqueurs de blocs |

### Les marqueurs de blocs

Dans un `action: |-`, chaque section délimitée par un commentaire

```yaml
      # --- Activation globale de bash-completion pour les sessions Bash ---
```

devient une case à cocher. Ce qui précède le premier marqueur d'un trigger est le
**préambule** : il est toujours conservé. Les triggers purement système
(`post-unpack`, `post-update`) ne sont jamais découpés : tout leur contenu est gardé.

Les blocs dits **communs** restent dans toutes les builds ; leur case est cochée et
grisée. La liste est définie par `REQUIRED_HINTS` dans le script :

> RPM Fusion, Flathub, ps5-linux-tools, SSH & Services, Firmware AMD PS5,
> grow-rootfs, SELinux, Utilisateur par défaut, zram, kernel rpm, WiFi,
> Fan ON et Boost ON, PS5 Fedora Manager

Conséquence pratique : pour rendre un nouveau script sélectionnable, il suffit
d'ajouter un commentaire `# --- Titre ---` juste avant dans `image.yaml`.

## L'interface

### Onglet « Paquets & blocs »

- **Paquets** : un en-tête par groupe avec le compteur `(cochés/total)`. Cocher ou
  décocher l'en-tête agit sur tout le groupe. Le champ **Rechercher** filtre par nom
  de paquet ou de groupe, et **Tout cocher / Tout décocher** agit globalement.
- **Blocs de script** : une case par bloc, avec sa première ligne de code en aperçu.
  Les blocs `[commun]` sont verrouillés.

### Onglet « Ajouts »

Cinq champs libres, une entrée par ligne, pour ajouter ce que `image.yaml` ne contient
pas. Ils sont stockés **dans le YAML de l'édition** sous forme de blocs dédiés : le
fichier reste autonome et les champs se rechargent si on rouvre l'édition.

| Champ | Ce qui est écrit dans le YAML | Emplacement |
|---|---|---|
| Dépôts supplémentaires | les lignes telles quelles | `post-packages`, juste après RPM Fusion / Flathub |
| Paquets RPM | `dnf install -y --allowerasing --skip-unavailable p1 p2 || true` | après les dépôts |
| Applications Flatpak | `flatpak install -y flathub id1 id2 || true` | après les paquets RPM |
| Commandes d'installation | les lignes telles quelles | après les flatpaks |
| Scripts supplémentaires | les lignes telles quelles | fin de `post-files` |

Titres des blocs générés (ils servent aussi à la relecture) :
`Dépôts supplémentaires (édition)`, `Paquets supplémentaires (édition)`,
`Applications Flatpak (édition)`, `Commandes d'installation (édition)`,
`Scripts supplémentaires (édition)`.

Au rechargement, l'outil relit ces blocs et remplit les champs à nouveau : les
commandes `dnf install` / `flatpak install` sont décomposées pour ne récupérer que les
noms de paquets et les identifiants flatpak.

### Boutons

| Bouton | Action |
|---|---|
| Charger une édition… | ouvre un YAML existant et remplit cases, nom, description, ajouts (Ctrl+O) |
| Enregistrer | écrit `distros/fedora/<Fichier YAML>` et régénère le comparatif (Ctrl+S) |
| Enregistrer sous… | choisit un autre chemin |
| Aperçu YAML | montre le fichier qui serait écrit, sans rien enregistrer |
| Comparatif des builds | régénère `build.difference.md` |
| Repartir de la base | recharge `image.yaml` avec tout coché et les ajouts vidés |

Le compteur en bas indique en permanence `paquets cochés/total — blocs cochés/total`.

## Enregistrement

1. **Nom de l'image** : `[A-Za-z0-9][A-Za-z0-9._-]*`. C'est `image.name` dans le YAML,
   et donc le nom du `.img`, des archives et le préfixe du tag de release.
2. **Fichier YAML** : pré-rempli automatiquement à partir du nom (`ps5-` retiré, le
   reste assaini), modifiable à la main. Le fichier est toujours écrit dans
   `distros/fedora/` (sauf via *Enregistrer sous…*).
3. **Description** : obligatoire ; elle part dans `image.description` et dans le corps
   de la release GitHub. Elle est mise entre guillemets automatiquement si elle
   contient `:` ou `#`.
4. **Contrôles** :
   - refus si le nom est invalide, la description vide, ou aucun paquet coché ;
   - validation YAML (si PyYAML est installé) : `image.name` présent, au moins un
     paquet, section `actions` complète ;
   - avertissements (on peut passer outre) : `git`/`make`/`gcc` décochés alors que
     ps5-linux-tools est compilé pendant le build ; flatpaks demandés sans le bloc
     Flathub ; champs « Ajouts » remplis en mode verrouillé ;
   - confirmation avant d'écraser un fichier existant, et double confirmation pour
     `image.yaml` (la build de référence).
5. À la fin : le nom du fichier, un rappel que le workflow le prendra automatiquement,
   et le comparatif est régénéré.

## Mode verrouillé (édition écrite à la main)

Si le YAML chargé contient du code qui n'existe pas dans `image.yaml`, l'outil ne
cherche pas à le découper : il conserve la section `actions` **telle quelle** et
verrouille les cases de blocs. Un bandeau l'indique et seuls le nom, la description et
les paquets restent modifiables. C'est le cas de `fedora-minimal_setup.yaml`.

Deux conséquences à connaître :

- les champs de l'onglet **Ajouts** ne sont pas écrits dans ce mode (un avertissement
  le signale à l'enregistrement) ;
- à l'enregistrement, les paquets sont réécrits dans l'ordre de `image.yaml` : le
  contenu est identique (mêmes paquets, mêmes scripts) mais les commentaires et
  l'ordre peuvent changer.

Les éditions générées par l'outil, elles, se réenregistrent à l'octet près.

## Le comparatif `build.difference.md`

Généré à chaque enregistrement, par le bouton **Comparatif des builds** ou par
`--difference`. Aucun horodatage : le fichier ne change que si les builds changent.
Il contient :

1. un **résumé** par build (image, nombre de paquets, de blocs, dépôts, paquets
   ajoutés, flatpaks, scripts) ;
2. le tableau **paquet × build** (`✓` ou vide) ;
3. le tableau **bloc de script × build** ;
4. une section par édition : paquets en plus / retirés par rapport à la base, blocs
   propres à l'édition, et la liste de ses dépôts, paquets RPM, flatpaks, commandes et
   scripts.

## Limites connues

- L'outil ne crée pas de build : il écrit un YAML. La build et la release se font
  ensuite par `build_image.sh` ou par le workflow GitHub.
- Il ne modifie que `name`, `description`, la liste des paquets et les blocs
  d'actions ; `source:` et `files:` sont recopiés à l'identique. Pour changer le
  noyau, les générateurs de fichiers ou la taille d'image, éditer `image.yaml` à la
  main.
- Les blocs ne sont reconnus que par leur titre de marqueur : renommer un
  `# --- Titre ---` dans `image.yaml` transforme le bloc en bloc « propre à
  l'édition » à la relecture (il reste inclus, mais n'est plus relié à la base).
- La fenêtre n'a pas de thème ni de taille adaptative en dessous de 940×620.

## Dépannage

| Symptôme | Cause / solution |
|---|---|
| `ModuleNotFoundError: No module named 'tkinter'` | installer `python3-tkinter` (Fedora) ou `python3-tk` (Debian/Ubuntu) ; `--check` fonctionne sans |
| `AttributeError: 'Checkbutton' object has no attribute 'get'` | ancienne version de l'outil : mettre à jour `tools/edition_editor.py` |
| « YAML invalide » à l'enregistrement | PyYAML est installé et le fichier produit ne se relit pas ; envoyer le message d'erreur, l'aperçu YAML montre le texte exact |
| Le YAML n'apparaît pas dans le comparatif | le comparatif ne lit que `distros/fedora/*.yaml` : vérifier que le fichier a bien été écrit là (et non via un `Enregistrer sous…` ailleurs) |
| Rien ne se construit après un push | le workflow `deploy` ignore les modifications de `tools/**`, `**.md` et `.gitignore` : seuls les changements de `distros/**` (ou un lancement manuel) déclenchent une build |

## Repères dans le code

| Élément | Rôle |
|---|---|
| `load_model` / `parse_text` | découpe un YAML en `image`, `source`, groupes de paquets, `files`, triggers et blocs |
| `render_edition` | réécrit le YAML complet à partir du modèle et des cases cochées |
| `extras_blocks` / `apply_extras` / `extras_from_blocks` | conversion aller-retour entre les champs « Ajouts » et les blocs du YAML |
| `selection_from_loaded` | déduit l'état des cases depuis un YAML existant (+ mode verrouillé) |
| `difference_markdown` / `write_difference_file` | génère `build.difference.md` |
| `validate_edition_text` | contrôles PyYAML avant écriture |
| `EditionEditor` | la fenêtre Tkinter (`_build_ui`, `_populate`, `_save`, `_load_file`) |

Tests rapides sans écran :

```bash
python3 -m py_compile tools/edition_editor.py
python3 tools/edition_editor.py --check
python3 tools/edition_editor.py --difference
```
