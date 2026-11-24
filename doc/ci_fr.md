# CI — pipeline GitHub Actions

Le dépôt construit et publie les images depuis GitHub. Ce document décrit ce qui se
passe à chaque push, comment relancer une seule édition, comment fonctionne le cache du
noyau et comment lire un run rouge.

- Catalogue des builds : [`editions_fr.md`](editions_fr.md)
- Builder local : [`builder_fr.md`](builder_fr.md)
- Dépannage : [`troubleshooting_fr.md`](troubleshooting_fr.md)
- English version: [`ci_en.md`](ci_en.md)

## Déclencheurs

| Déclencheur | Fichier | Effet |
|---|---|---|
| Push sur `main` | `.github/workflows/trigger-builds.yml` (workflow `deploy`) | lance `build-image.yml`, sauf si le commit ne touche que `tools/**`, `**.md`, `.gitignore` |
| Lancement manuel | Actions → **deploy** ou **Build Image** → *Run workflow* | champ `variant` vide = toutes les éditions |
| Pull request étiquetée `run-ci` | `trigger-builds.yml` | construit la PR sans publier de release |

Le champ `variant` accepte le nom d'un YAML sans `.yaml` (par exemple
`fedora-cosmic_edition`). Une valeur inconnue fait échouer le job `editions` en listant
les éditions disponibles.

## Chaîne des jobs

```
editions ──► kernel ──► build (matrice, toutes les éditions en parallèle) ──► release (matrice)
```

| Job | Rôle | Détail |
|---|---|---|
| `editions` | découvre `distros/fedora/*.yaml` (ou seulement `variant`) | produit la matrice JSON utilisée par `build` et `release` |
| `kernel` | compile le noyau **une fois** par run | met le `.rpm` dans `kernel-pkg/`, publie l'artefact `kernel-rpm`, alimente le cache |
| `build` | une entrée de matrice par édition | télécharge le `.rpm`, lance `build_image.sh`, vérifie l'image, la découpe en volumes 7z, publie les artefacts |
| `release` | une entrée de matrice par édition | publie les volumes sous un tag daté, puis élague les anciennes releases |

### Parallélisme

`build` et `release` n'ont **pas** de `max-parallel` : toutes les éditions démarrent en
même temps, chacune sur son propre runner Ubuntu (disque, Docker et `output/`
indépendants). GitHub met en file ce qui dépasse la limite de jobs concurrents du compte
(20 sur un compte gratuit pour un dépôt public) — ce n'est pas une erreur.

Deux garde-fous restent en place :

- `fail-fast: false` sur les deux matrices : un échec n'annule pas les autres éditions.
- Un `concurrency` par édition (`ps5-image-<edition>`) : deux runs successifs ne
  construisent pas la même édition en double.

### Isolation d'un échec

Dans `build`, l'étape « Build <édition> image » est en `continue-on-error`. Si elle
échoue :

1. les étapes suivantes (report, compression 7z, métadonnées, uploads) sont **sautées**
   pour cette édition seulement ;
2. une dernière étape « Report failed edition » écrit un message dans le *job summary* et
   remet le job en rouge ;
3. les autres éditions continuent, et `release` (`if: !cancelled()`) publie celles qui ont
   produit leurs archives — une édition sans artefact reçoit un simple `::warning::`.

Un run peut donc être rouge tout en publiant les builds valides.

### Cache du noyau

Le noyau ne dépend que du tag de patches choisi dans `build_image.sh` (`PATCHES_REF`) et
des recettes `docker/kernel-builder{,-rpm}`. La clé de cache est :

```
kernel-rpm-<16 premiers caractères du SHA du tag>-<empreinte des recettes>
```

- `actions/cache/restore` restaure `kernel-pkg/` (le `.rpm`, `VERSION` et un
  `BUILD_INFO` avec ref/SHA/version). En cas de succès, la compilation (~45 min) est
  sautée et le `.rpm` est recopié dans `image/linux-bin/`.
- `actions/cache/save` n'est exécuté que sur un vrai build, pour ne pas consommer le quota
  (10 Go par dépôt) en réenregistrant un cache déjà présent.
- Le cache s'invalide automatiquement si le tag de patches bouge ou si un Dockerfile/script
  du noyau est modifié. Pour forcer une recompilation : Actions → **Caches**, supprimer
  l'entrée `kernel-rpm-…`, ou changer `PATCHES_REF`.
- GitHub évince un cache inutilisé depuis 7 jours.

## Artefacts produits

| Artefact | Contenu | Rétention |
|---|---|---|
| `kernel-rpm` | `.rpm` du noyau + `VERSION` + `BUILD_INFO` | 7 jours |
| `meta-<édition>` | nom d'image, édition, version du noyau, SHA des patches, horodatage, checksums des volumes | 1 jour |
| `ps5-<édition>-img` | volumes `*.img.7z.001…` (1,5 Gio chacun) | 7 jours |

Les volumes font 1,5 Gio pour rester sous la limite GitHub de 2 Gio par fichier.

## Releases

- Un tag par édition et par build : `<image.name>-AAAA.MM.JJ-HHMM` en UTC, par exemple
  `ps5-fedora-sway_edition-2026.11.24-1830`. Rien n'est écrasé.
- Le corps de release contient la description du YAML, la version du noyau, le lien vers
  le commit de patches, la date et les checksums SHA256 des volumes.
- Badge **Latest** : uniquement l'édition `image` (`make_latest`), pour éviter que des
  releases parallèles se disputent le badge.
- `KEEP_RELEASES: '5'` : après publication, seules les 5 releases datées les plus récentes
  de l'édition sont conservées ; les plus anciennes sont supprimées (release + tag).
- La récupération d'une archive demande **tous** les volumes, puis extraction du `.001` :

```bash
7z x ps5-fedora-sway_edition-2026.11.24-1830.img.7z.001
```

## Permissions et secrets

- `build` : `contents: read` ; `release` : `contents: write` (nécessaire pour créer les
  tags et supprimer les anciennes releases).
- Aucun secret supplémentaire : seul `GITHUB_TOKEN` est utilisé. Le dépôt de patches est
  public.

## Opérations courantes

| Objectif | Marche à suivre |
|---|---|
| Reconstruire une seule édition | Actions → **Build Image** → *Run workflow* → `variant: fedora-kde_edition` |
| Tout reconstruire | *Run workflow* avec `variant` vide, ou pousser un commit sur `distros/**` |
| Ajouter une édition | créer `distros/fedora/<nom>.yaml` et pousser : découverte, build, release et élagage sont automatiques |
| Renommer une image | changer `image.name` dans le YAML : nouveaux noms d'archives et nouvelle série de tags (les anciennes releases restent, l'élagage ne concerne que la nouvelle série) |
| Annuler un run | bouton *Cancel* : les jobs en cours sont interrompus, `release` ne publie que les artefacts déjà présents |
| Suivre un run | onglet *Summary* : un résumé par édition en échec, liens vers les artefacts |

## Quotas et coûts

- Chaque job consomme des minutes du runner ; paralléliser ne change pas le total, cela
  concentre seulement la durée sur une plage plus courte.
- Limite d'espace des artefacts et du cache : 10 Go de cache par dépôt, artefacts comptés
  dans le quota du dépôt (rétention 1 à 7 jours).
- Une image complète pèse ~3 à 4 Go compressée (3 volumes), soit ~11 éditions × 3 volumes
  par run : c'est la raison de la rétention courte des artefacts, les releases prenant le
  relais pour la conservation longue.
