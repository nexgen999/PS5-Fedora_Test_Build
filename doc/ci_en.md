# CI — GitHub Actions pipeline

The repository builds and publishes the images from GitHub. This document describes what
happens on every push, how to rebuild a single edition, how the kernel cache works and how
to read a red run.

- Build catalogue: [`editions_en.md`](editions_en.md)
- Local builder: [`builder_en.md`](builder_en.md)
- Troubleshooting: [`troubleshooting_en.md`](troubleshooting_en.md)
- Version française : [`ci_fr.md`](ci_fr.md)

## Triggers

| Trigger | File | Effect |
|---|---|---|
| Push to `main` | `.github/workflows/trigger-builds.yml` (workflow `deploy`) | runs `build-image.yml`, unless the commit only touches `tools/**`, `**.md`, `.gitignore` |
| Manual run | Actions → **deploy** or **Build Image** → *Run workflow* | form with checkboxes (see below) |
| Pull request labelled `run-ci` | `trigger-builds.yml` | builds the PR without publishing a release |

### Manual run form

GitHub cannot render a list of tickable builds, so the form offers **checkboxes**
(`type: boolean`, one per edition) plus four fields.

| Field | Purpose |
|---|---|
| `all_editions` (ticked by default) | builds **every** `distros/<distro>/*.yaml` — a YAML added later is picked up automatically |
| `image`, `fedora-kde_edition`, … checkboxes | untick `all_editions`, then tick the editions to build |
| `variant` | extra edition stems, comma separated (for a YAML with no checkbox yet) |
| `skip_editions` | edition stems to exclude, comma separated (works with `all_editions` ticked) |

Final selection = (`all_editions` ? every edition : ∅) ∪ ticked boxes ∪ `variant` −
`skip_editions`. An unknown name in `variant` fails the `editions` job and lists the
available editions; a ticked box whose YAML was deleted is ignored with a warning.

## Job chain

```
editions ──► kernel ──► build (matrix) ──► publish ──► release (matrix) ──► release-prune
```

| Job | Role | Details |
|---|---|---|
| `editions` | discovers `distros/fedora/*.yaml` and applies the form selection | outputs the JSON matrix used by `build` and `release` |
| `kernel` | compiles the kernel **once** per run | writes the `.rpm` to `kernel-pkg/`, uploads the `kernel-rpm` artifact, feeds the cache |
| `build` | one matrix entry per edition | downloads the `.rpm`, runs `build_image.sh`, verifies the image, splits it into 7z volumes, uploads artifacts |
| `publish` | creates **one** dated release for the whole run | reads only the small `meta-*` artifacts: edition table, per-image notes, failed-edition list |
| `release` | one matrix entry per edition | downloads its edition's volumes and adds them to the shared release (`gh release upload`) |
| `release-prune` | prunes old dated releases | keeps the `KEEP_RELEASES` newest ones (release + tag) |

### Parallelism

`build` and `release` have **no** `max-parallel`: every edition starts at the same time,
each on its own Ubuntu runner (independent disk, Docker and `output/`). GitHub queues
whatever exceeds the account's concurrent-job limit (20 on a free plan for a public
repository) — that is not an error.

Two guard rails remain:

- `fail-fast: false` on both matrices: one failure never cancels the other editions.
- A per-edition `concurrency` group (`ps5-image-<edition>`): two successive runs never
  build the same edition twice.

### Failure isolation

In `build`, the "Build <edition> image" step uses `continue-on-error`. When it fails:

1. the following steps (report, 7z compression, metadata, uploads) are **skipped** for
   that edition only;
2. a final "Report failed edition" step writes to the *job summary* and turns the job red;
3. the other editions keep going, and `publish` (`if: !cancelled()`) creates the run's
   release with the editions that produced their archives; the others are listed there as
   not published and `release` only logs a `::warning::` for them instead of failing.

A run can therefore be red while still publishing the valid builds.

### Kernel cache

The kernel only depends on the patches tag picked in `build_image.sh` (`PATCHES_REF`) and
on the `docker/kernel-builder{,-rpm}` recipes. The cache key is:

```
kernel-rpm-<first 16 chars of the tag SHA>-<recipe fingerprint>
```

- `actions/cache/restore` restores `kernel-pkg/` (the `.rpm`, `VERSION` and a `BUILD_INFO`
  with ref/SHA/version). On a hit the ~45 min compile is skipped and the `.rpm` is copied
  into `image/linux-bin/`.
- `actions/cache/save` only runs after a real build, so a hit never wastes the 10 GB
  repository quota.
- The cache invalidates automatically when the patches tag moves or a kernel
  Dockerfile/script changes. To force a rebuild: Actions → **Caches**, delete the
  `kernel-rpm-…` entry, or change `PATCHES_REF`.
- GitHub evicts a cache unused for 7 days.

## Artifacts

| Artifact | Content | Retention |
|---|---|---|
| `kernel-rpm` | kernel `.rpm` + `VERSION` + `BUILD_INFO` | 7 days |
| `meta-<edition>` | image name, edition, kernel version, patches SHA, timestamp, volume checksums | 1 day |
| `ps5-<edition>-img` | `*.img.7z.001…` volumes (1.5 GiB each) | 7 days |

Volumes are 1.5 GiB to stay under GitHub's 2 GiB per-file limit.

## Releases

**One release per build**, not one per edition, so the Releases page stays readable.

- Tag: `ps5-<distro>-images-YYYY.MM.DD-HHMMSS` in UTC, e.g.
  `ps5-fedora-images-2026.11.24-020015`. Nothing is overwritten: each run creates its own.
- Assets: the 7z volumes of **every** edition built (`ps5-fedora.img.7z.001`,
  `ps5-fedora-kde_edition.img.7z.001`, …). Image names are unique per edition, so no
  volume overwrites another.
- The body holds a table (edition, image, volume count), then one section per image: YAML
  description, kernel version, patches commit link, build date, volume list and SHA256
  checksums. Editions that failed are listed with a link to the run.
- `publish` creates the release empty; the `release` jobs then add their volumes in
  parallel (`gh release upload --clobber`), so the release fills up during the run.
- **Latest** badge: always the newest run's release (`--latest`).
- `KEEP_RELEASES: '5'`: only the 5 newest dated releases are kept; older ones are deleted
  (release + tag).
- Releases from the old per-edition scheme (`<image.name>-YYYY.MM.DD-HHMM`) are not touched
  by pruning: delete them by hand once the new releases are verified.
- Extracting an archive needs **every** volume, then the `.001`:

```bash
7z x ps5-fedora-kde_edition.img.7z.001
```

## Permissions and secrets

- `build`: `contents: read`; `release`: `contents: write` (needed to create tags and delete
  old releases).
- No extra secret: only `GITHUB_TOKEN` is used. The patches repository is public.

## Common operations

| Goal | How |
|---|---|
| Rebuild one edition | Actions → **Build Image** → *Run workflow* → untick "build everything" → tick `fedora-kde_edition` |
| Rebuild an edition with no checkbox | *Run workflow* → `variant: fedora-my_new_yaml` |
| Rebuild everything | *Run workflow* with "build everything" ticked (default), or push a commit touching `distros/**` |
| Skip one edition in a full run | "build everything" ticked + `skip_editions: fedora-test_build` |
| Add an edition | create `distros/fedora/<name>.yaml` and push: discovery, build and publication in the run's release are automatic (add a checkbox to select it by hand) |
| Rename an image | change `image.name`: new archive names and assets (old releases stay) |
| Cancel a run | *Cancel*: running jobs are interrupted, the release only contains volumes already uploaded |
| Follow a run | *Summary* tab: selected editions, one summary per failed edition, artifact links |

## Quotas and cost

- Each job consumes runner minutes; parallelising does not change the total, it only
  compresses it into a shorter window.
- Artifact and cache limits: 10 GB of cache per repository, artifacts counted in the
  repository quota (1 to 7 days retention).
- A full image is ~3-4 GB compressed (3 volumes), so ~13 editions × 3 volumes per run
  inside **a single** release: that is why artifact retention is short and releases carry
  long-term storage.
