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
| Lancement manuel | Actions → **deploy** ou **Build Image** → *Run workflow* | formulaire avec cases à cocher (voir ci-dessous) |
| Pull request étiquetée `run-ci` | `trigger-builds.yml` | construit la PR sans publier de release |

### Formulaire de lancement manuel

GitHub ne sait pas afficher une liste de builds cochables : le formulaire propose donc des
**cases à cocher** (`type: boolean`, une par édition) et quatre champs.

| Champ | Rôle |
|---|---|
| `all_editions` (coché par défaut) | construit **tous** les `distros/<distro>/*.yaml` trouvés — un YAML ajouté plus tard est pris automatiquement |
| cases `image`, `fedora-kde_edition`, … | décocher `all_editions`, puis cocher les éditions voulues |
| `variant` | éditions à ajouter à la main, séparées par des virgules (utile pour un YAML qui n'a pas encore sa case) |
| `skip_editions` | éditions à exclure, séparées par des virgules (fonctionne aussi avec `all_editions` coché) |

Sélection finale = (`all_editions` ? toutes les éditions : ∅) ∪ cases cochées ∪ `variant`
− `skip_editions`. Un nom inconnu dans `variant` fait échouer le job `editions` en listant
les éditions disponibles ; une case cochée dont le YAML a été supprimé est ignorée avec un
avertissement.

## Chaîne des jobs

```
editions ──► kernel ──► build (matrice) ──► publish ──► release (matrice) ──► release-prune
```

| Job | Rôle | Détail |
|---|---|---|
| `editions` | découvre `distros/fedora/*.yaml` et applique la sélection du formulaire | produit la matrice JSON utilisée par `build` et `release` |
| `kernel` | compile le noyau **une fois** par run | met le `.rpm` dans `kernel-pkg/`, publie l'artefact `kernel-rpm`, alimente le cache |
| `build` | une entrée de matrice par édition | télécharge le `.rpm`, lance `build_image.sh`, vérifie l'image, la découpe en volumes 7z, publie les artefacts |
| `publish` | crée **une** release datée pour tout le run | ne lit que les petits artefacts `meta-*` : tableau des éditions, notes par image, liste des éditions en échec |
| `release` | une entrée de matrice par édition | télécharge les volumes de son édition et les ajoute à la release commune (`gh release upload`) |
| `release-prune` | élague les vieilles releases datées | conserve les `KEEP_RELEASES` plus récentes (release + tag) |

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
3. les autres éditions continuent, et `publish` (`if: !cancelled()`) crée la release du run
   avec celles qui ont produit leurs archives ; les autres y sont listées comme non
   publiées et `release` leur écrit un simple `::warning::` au lieu d'un échec.

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

**Une seule release par build**, pas une par édition : la page Releases reste lisible.

- Tag : `ps5-<distro>-images-AAAA.MM.JJ-HHMMSS` en UTC, par exemple
  `ps5-fedora-images-2026.11.24-020015`. Rien n'est écrasé : chaque run crée sa release.
- Assets : les volumes 7z de **toutes** les éditions construites (`ps5-fedora.img.7z.001`,
  `ps5-fedora-kde_edition.img.7z.001`, …). Les noms d'image étant uniques par édition,
  aucun volume n'écrase un autre.
- Le corps contient un tableau (édition, image, nombre de volumes), puis une section par
  image : description du YAML, version du noyau, lien vers le commit de patches, date de
  build, liste des volumes et checksums SHA256. Les éditions en échec y sont listées avec
  un lien vers le run.
- La release est créée vide par `publish`, puis les jobs `release` y ajoutent leurs volumes
  en parallèle (`gh release upload --clobber`) : la release se remplit pendant le run.
- Badge **Latest** : toujours la release la plus récente du run (`--latest`).
- `KEEP_RELEASES: '5'` : seules les 5 releases datées les plus récentes sont conservées ;
  les plus anciennes sont supprimées (release + tag).
- Les anciennes releases **par édition** (tags `<image.name>-AAAA.MM.JJ-HHMM`) ne sont pas
  touchées par l'élagage : elles peuvent être supprimées à la main une fois les nouvelles
  releases vérifiées.
- La récupération d'une archive demande **tous** les volumes, puis extraction du `.001` :

```bash
7z x ps5-fedora-kde_edition.img.7z.001
```

## Permissions et secrets

- `build` : `contents: read` ; `release` : `contents: write` (nécessaire pour créer les
  tags et supprimer les anciennes releases).
- Aucun secret supplémentaire : seul `GITHUB_TOKEN` est utilisé. Le dépôt de patches est
  public.

## Opérations courantes

| Objectif | Marche à suivre |
|---|---|
| Reconstruire une seule édition | Actions → **Build Image** → *Run workflow* → décocher « Tout construire » → cocher `fedora-kde_edition` |
| Reconstruire une édition sans case à cocher | *Run workflow* → `variant: fedora-mon_nouveau_yaml` |
| Tout reconstruire | *Run workflow* avec « Tout construire » coché (défaut), ou pousser un commit sur `distros/**` |
| Exclure une édition d'un run complet | « Tout construire » coché + `skip_editions: fedora-test_build` |
| Ajouter une édition | créer `distros/fedora/<nom>.yaml` et pousser : découverte, build et publication dans la release du run sont automatiques (ajouter une case au formulaire pour pouvoir la cocher) |
| Renommer une image | changer `image.name` dans le YAML : nouveaux noms d'archives et nouveaux assets (les anciennes releases restent) |
| Annuler un run | bouton *Cancel* : les jobs en cours sont interrompus, la release ne contient que les volumes déjà uploadés |
| Suivre un run | onglet *Summary* : éditions sélectionnées, résumé par édition en échec, liens vers les artefacts |

## Quotas et coûts

- Chaque job consomme des minutes du runner ; paralléliser ne change pas le total, cela
  concentre seulement la durée sur une plage plus courte.
- Limite d'espace des artefacts et du cache : 10 Go de cache par dépôt, artefacts comptés
  dans le quota du dépôt (rétention 1 à 7 jours).
- Une image complète pèse ~3 à 4 Go compressée (3 volumes), soit ~11 éditions × 3 volumes
  par run regroupés dans **une seule** release : c'est la raison de la rétention courte des
  artefacts, les releases prenant le relais pour la conservation longue.
