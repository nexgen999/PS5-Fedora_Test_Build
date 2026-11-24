# Documentation

Index des documents du dépôt. Chaque sujet existe en français et en anglais.

## Par besoin

| Je veux… | Document |
|---|---|
| Voir la liste des builds et choisir la bonne | [`editions_fr.md`](editions_fr.md) · [`editions_en.md`](editions_en.md) |
| Comprendre comment une image est fabriquée (noyau → rootfs → disque) | [`builder_fr.md`](builder_fr.md) · [`builder_en.md`](builder_en.md) |
| Cocher/décocher des paquets et des scripts dans un YAML | [`editor_fr.md`](editor_fr.md) · [`editor_en.md`](editor_en.md) |
| Savoir ce qui tourne dans GitHub Actions, les caches et les releases | [`ci_fr.md`](ci_fr.md) · [`ci_en.md`](ci_en.md) |
| Réparer un build rouge, une session qui ne démarre pas, un artefact | [`troubleshooting_fr.md`](troubleshooting_fr.md) · [`troubleshooting_en.md`](troubleshooting_en.md) |

## Ordre de lecture conseillé

1. **Catalogue des builds** — ce que chaque YAML produit, le socle commun PS5, les
   sessions Wayland et l'autologin.
2. **Builder** — les trois étapes, les options de `build_image.sh`, l'anatomie d'un YAML.
3. **CI** — déclencheurs, matrice parallèle, cache du noyau, tags datés et élagage.
4. **Éditeur** — modifier une édition sans casser les blocs communs.
5. **Dépannage** — à garder sous la main.

## Fichiers

| Fichier | Sujet |
|---|---|
| [`editions_fr.md`](editions_fr.md) / [`editions_en.md`](editions_en.md) | les 11 builds Fedora : contenu, bureau, connexion, quand la choisir, limites |
| [`builder_fr.md`](builder_fr.md) / [`builder_en.md`](builder_en.md) | `build_image.sh`, étapes noyau/rootfs/image, options, sorties |
| [`editor_fr.md`](editor_fr.md) / [`editor_en.md`](editor_en.md) | éditeur Tkinter : paquets, blocs, ajouts, comparatif |
| [`ci_fr.md`](ci_fr.md) / [`ci_en.md`](ci_en.md) | workflow GitHub Actions, parallélisme, cache, artefacts, releases |
| [`troubleshooting_fr.md`](troubleshooting_fr.md) / [`troubleshooting_en.md`](troubleshooting_en.md) | catalogue de symptômes et solutions |

## Fichiers générés

| Fichier | Producteur |
|---|---|
| [`../build.difference.md`](../build.difference.md) | `python3 tools/edition_editor.py --difference` (ou chaque enregistrement dans l'éditeur) |

## Rappels utiles

- Une édition = un YAML dans `distros/fedora/` ; le CI la découvre tout seul.
- Le nom d'image (`image.name`) détermine le `.img`, les archives et le préfixe du tag.
- Les commits qui ne touchent que `tools/**`, `**.md` ou `.gitignore` ne déclenchent pas
  de build.
- Les anciennes releases sont conservées à 5 par édition ; les artefacts CI expirent en
  7 jours.
