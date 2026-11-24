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
| Manual run | Actions → **deploy** or **Build Image** → *Run workflow* | empty `variant` = every edition |
| Pull request labelled `run-ci` | `trigger-builds.yml` | builds the PR without publishing a release |

The `variant` input takes a YAML name without `.yaml` (e.g. `fedora-cosmic_edition`). An
unknown value fails the `editions` job and lists the available editions.

## Job chain

```
editions ──► kernel ──► build (matrix, every edition in parallel) ──► release (matrix)
```

| Job | Role | Details |
|---|---|---|
| `editions` | discovers `distros/fedora/*.yaml` (or just `variant`) | outputs the JSON matrix used by `build` and `release` |
| `kernel` | compiles the kernel **once** per run | writes the `.rpm` to `kernel-pkg/`, uploads the `kernel-rpm` artifact, feeds the cache |
| `build` | one matrix entry per edition | downloads the `.rpm`, runs `build_image.sh`, verifies the image, splits it into 7z volumes, uploads artifacts |
| `release` | one matrix entry per edition | publishes the volumes under a dated tag, then prunes old releases |

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
3. the other editions keep going, and `release` (`if: !cancelled()`) publishes the ones
   that produced their archives — an edition without artifacts only gets a `::warning::`.

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

- One tag per edition and per build: `<image.name>-YYYY.MM.DD-HHMM` in UTC, e.g.
  `ps5-fedora-sway_edition-2026.11.24-1830`. Nothing is overwritten.
- The release body contains the YAML description, the kernel version, a link to the
  patches commit, the date and the SHA256 checksums of the volumes.
- **Latest** badge: only the `image` edition (`make_latest`), so parallel releases never
  fight over it.
- `KEEP_RELEASES: '5'`: after publishing, only the 5 newest dated releases of that edition
  are kept; older ones are deleted (release + tag).
- Extracting an archive needs **every** volume, then the `.001`:

```bash
7z x ps5-fedora-sway_edition-2026.11.24-1830.img.7z.001
```

## Permissions and secrets

- `build`: `contents: read`; `release`: `contents: write` (needed to create tags and delete
  old releases).
- No extra secret: only `GITHUB_TOKEN` is used. The patches repository is public.

## Common operations

| Goal | How |
|---|---|
| Rebuild one edition | Actions → **Build Image** → *Run workflow* → `variant: fedora-kde_edition` |
| Rebuild everything | *Run workflow* with an empty `variant`, or push a commit touching `distros/**` |
| Add an edition | create `distros/fedora/<name>.yaml` and push: discovery, build, release and pruning are automatic |
| Rename an image | change `image.name`: new archive names and a new tag series (old releases stay; pruning only applies to the new series) |
| Cancel a run | *Cancel*: running jobs are interrupted, `release` only publishes artifacts already present |
| Follow a run | *Summary* tab: one summary per failed edition, links to artifacts |

## Quotas and cost

- Each job consumes runner minutes; parallelising does not change the total, it only
  compresses it into a shorter window.
- Artifact and cache limits: 10 GB of cache per repository, artifacts counted in the
  repository quota (1 to 7 days retention).
- A full image is ~3-4 GB compressed (3 volumes), so ~11 editions × 3 volumes per run:
  that is why artifact retention is short and releases carry long-term storage.
