# The edition editor — `tools/edition_editor.py`

A Python/Tkinter tool that starts from the reference build `distros/fedora/image.yaml`
and writes a self-contained edition YAML into `distros/fedora/`. You tick the packages
and script blocks to keep, optionally add repositories, RPM packages, Flatpaks,
commands and free-form scripts, then save. The generated file keeps the exact format
of the base build, so `build_image.sh`, `entrypoint.sh` and the GitHub workflow need
no changes — the file simply has to exist for a new build, its archives and its
release to be produced.

- Builder documentation: [`builder_en.md`](builder_en.md)
- Version française : [`editor_fr.md`](editor_fr.md)

## Requirements and launch

```bash
sudo dnf install python3-tkinter     # Fedora (once)
sudo apt install python3-tk          # Debian/Ubuntu

python3 tools/edition_editor.py               # opens the window
python3 tools/edition_editor.py --check       # prints what it parsed, no GUI
python3 tools/edition_editor.py --difference  # regenerates build.difference.md
```

| Command | Effect |
|---|---|
| no argument | graphical interface |
| `--check` | lists package groups and script blocks (tagged `commun` or `optionnel`) |
| `--difference` | rewrites `build.difference.md` at the repository root |

Without tkinter the module is still importable: `--check` and `--difference` work, and
only opening the window is refused with an install hint. PyYAML is **optional**: when
present, every generated YAML is validated before writing; otherwise the file is
written as-is (the build would catch structural errors anyway).

## What it reads from `image.yaml`

The file is not reloaded through PyYAML: it is split line by line, which is what makes
a byte-for-byte identical rewrite possible (comments, ordering, indentation).

| YAML part | Handling |
|---|---|
| `image:` | copied as-is, except `name` and `description`, which are replaced on save |
| `source:` | copied as-is |
| `packages:` → `sets:` → `- packages:` | each comment line followed by `- package` lines forms a **group**; the rest (`manager`, `update`, `cleanup`, `sets:`, `action: install`) is preserved |
| `files:` | copied as-is (`hostname`, `hosts`, `dump`, `copy` generators pointing at `/tmp/build-staging`) |
| `actions:` | split by `- trigger:` and then by block markers |

### Block markers

Inside an `action: |-` block, every section introduced by a comment such as

```yaml
      # --- Global bash-completion activation for Bash sessions ---
```

becomes a checkbox. Whatever comes before the first marker of a trigger is the
**preamble** and is always kept. Purely system triggers (`post-unpack`, `post-update`)
are never split: all of their content is kept.

Blocks flagged as **common** stay in every build; their checkbox is ticked and greyed
out. The list lives in `REQUIRED_HINTS` in the script:

> RPM Fusion, Flathub, ps5-linux-tools, SSH & Services, Firmware AMD PS5,
> grow-rootfs, SELinux, Utilisateur par défaut, zram, kernel rpm, WiFi,
> Fan ON et Boost ON, PS5 Fedora Manager

Practical consequence: to make a new script selectable, add a `# --- Title ---`
comment right above it in `image.yaml`.

## The interface

### "Packages & blocks" tab

- **Packages**: one header per group showing `(checked/total)`. Ticking the header
  toggles the whole group. The **Search** field filters by package or group name, and
  **Check all / Uncheck all** act globally.
- **Script blocks**: one checkbox per block, with its first code line as a preview.
  Common `[commun]` blocks are locked.

### "Additions" tab

Five free-text fields, one entry per line, for things `image.yaml` does not contain.
They are stored **inside the edition YAML** as dedicated blocks, so the file stays
self-contained and the fields refill when the edition is reopened.

| Field | What is written to the YAML | Placement |
|---|---|---|
| Extra repositories | the lines verbatim | `post-packages`, right after RPM Fusion / Flathub |
| RPM packages | `dnf install -y --allowerasing --skip-unavailable p1 p2 \|\| true` | after the repositories |
| Flatpak apps | `flatpak install -y flathub id1 id2 \|\| true` | after the RPM packages |
| Install commands | the lines verbatim | after the Flatpaks |
| Extra scripts | the lines verbatim | end of `post-files` |

Generated block titles (also used when reading back):
`Dépôts supplémentaires (édition)`, `Paquets supplémentaires (édition)`,
`Applications Flatpak (édition)`, `Commandes d'installation (édition)`,
`Scripts supplémentaires (édition)`.

On reload the tool reads those blocks back into the fields; `dnf install` and
`flatpak install` lines are tokenised so only package names and Flatpak IDs are kept.

### Buttons

| Button | Action |
|---|---|
| Load an edition… | opens an existing YAML and fills checkboxes, name, description and additions (Ctrl+O) |
| Save | writes `distros/fedora/<YAML file>` and regenerates the comparison (Ctrl+S) |
| Save as… | choose another path |
| YAML preview | shows the file that would be written, without saving |
| Build comparison | regenerates `build.difference.md` |
| Reset to base | reloads `image.yaml` with everything checked and empty additions |

The status bar permanently shows `checked/total packages — checked/total blocks`.

## Saving

1. **Image name**: `[A-Za-z0-9][A-Za-z0-9._-]*`. This is `image.name` in the YAML, and
   therefore the `.img` name, the archive names and the release tag prefix.
2. **YAML file**: pre-filled from the name (`ps5-` stripped, remainder sanitised) and
   editable by hand. Files always go to `distros/fedora/` (unless *Save as…*).
3. **Description**: required; it ends up in `image.description` and in the GitHub
   release body. It is quoted automatically when it contains `:` or `#`.
4. **Checks**:
   - refused when the name is invalid, the description empty, or no package selected;
   - YAML validation (with PyYAML): `image.name` present, at least one package, a
     complete `actions` section;
   - warnings (can be bypassed): `git`/`make`/`gcc` unticked while ps5-linux-tools is
     compiled during the build; Flatpaks requested without the Flathub block;
     additions filled in locked mode;
   - confirmation before overwriting an existing file, and a second confirmation for
     `image.yaml` (the reference build).
5. Finally it reports the file name, reminds you the workflow will pick it up, and
   regenerates the comparison.

## Locked mode (hand-written edition)

If the loaded YAML contains code that does not exist in `image.yaml`, the tool does not
try to split it: it keeps the `actions` section **verbatim** and locks the block
checkboxes. A banner explains it and only the name, description and packages stay
editable. This is the case for `fedora-minimal_setup.yaml`.

Two consequences worth knowing:

- the **Additions** fields are not written in this mode (a warning says so on save);
- on save, packages are rewritten in `image.yaml` order: same content (same packages,
  same scripts) but comments and ordering may change.

Editions produced by the tool itself round-trip byte for byte.

## The `build.difference.md` comparison

Generated on every save, by the **Build comparison** button, or by `--difference`.
There is no timestamp: the file only changes when the builds change. It contains:

1. a **summary** per build (image, package count, block count, repositories, added
   packages, Flatpaks, scripts);
2. the **package × build** table (`✓` or blank);
3. the **script block × build** table;
4. one section per edition: packages added / removed relative to the base, blocks
   specific to the edition, and the list of its repositories, RPM packages, Flatpaks,
   commands and scripts.

## Known limitations

- The tool does not build anything: it writes a YAML. Building and releasing happen
  afterwards through `build_image.sh` or the GitHub workflow.
- It only changes `name`, `description`, the package list and action blocks; `source:`
  and `files:` are copied verbatim. Kernel, file generators or image size must be
  edited in `image.yaml` by hand.
- Blocks are recognised by their marker title: renaming a `# --- Title ---` in
  `image.yaml` turns that block into an edition-specific one on reload (still included,
  but no longer linked to the base).
- The window has no theme or responsive layout below 940×620.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `ModuleNotFoundError: No module named 'tkinter'` | install `python3-tkinter` (Fedora) or `python3-tk` (Debian/Ubuntu); `--check` works without it |
| `AttributeError: 'Checkbutton' object has no attribute 'get'` | old version of the tool: update `tools/edition_editor.py` |
| "YAML invalide" on save | PyYAML is installed and the generated text does not parse; report the message, the YAML preview shows the exact text |
| The YAML never appears in the comparison | the comparison only reads `distros/fedora/*.yaml`: check the file was written there (not through *Save as…* elsewhere) |
| Nothing builds after a push | the `deploy` workflow ignores changes to `tools/**`, `**.md` and `.gitignore`: only `distros/**` changes (or a manual run) start a build |

## Code map

| Item | Role |
|---|---|
| `load_model` / `parse_text` | split a YAML into `image`, `source`, package groups, `files`, triggers and blocks |
| `render_edition` | rewrite the whole YAML from the model and the checkbox state |
| `extras_blocks` / `apply_extras` / `extras_from_blocks` | round-trip between the "Additions" fields and the YAML blocks |
| `selection_from_loaded` | derive checkbox state from an existing YAML (+ locked mode) |
| `difference_markdown` / `write_difference_file` | generate `build.difference.md` |
| `validate_edition_text` | PyYAML checks before writing |
| `EditionEditor` | the Tkinter window (`_build_ui`, `_populate`, `_save`, `_load_file`) |

Quick headless checks:

```bash
python3 -m py_compile tools/edition_editor.py
python3 tools/edition_editor.py --check
python3 tools/edition_editor.py --difference
```
