#!/usr/bin/env python3
"""Éditeur graphique d'éditions PS5 Fedora.

Lit la build de base `distros/fedora/image.yaml`, affiche ses paquets (groupés)
et ses blocs de script (repérés par les commentaires `# --- Titre ---`), puis
génère un YAML d'édition autonome dans `distros/fedora/`.

Le YAML produit garde exactement le format de la base : `build_image.sh`,
`entrypoint.sh` et le workflow n'ont rien de spécifique à faire, il suffit que
le fichier existe pour qu'une nouvelle build soit prise en compte.

Dépendances : tkinter (paquet `python3-tkinter`). PyYAML est optionnel : s'il
est présent, le YAML généré est validé avant écriture.

Lancement :
    python3 tools/edition_editor.py
    python3 tools/edition_editor.py --check   # affiche la structure lue, sans GUI
"""

from __future__ import annotations

import copy
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:  # tkinter est optionnel : le module doit rester importable sans GUI
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    from tkinter import font as tkfont

    TK_AVAILABLE = True
except Exception:  # pragma: no cover - dépend de l'installation système
    TK_AVAILABLE = False

REPO_ROOT = Path(__file__).resolve().parent.parent
DISTRO_DIR = REPO_ROOT / "distros" / "fedora"
BASE_YAML = DISTRO_DIR / "image.yaml"

SECTION_RE = re.compile(r"^([a-z_]+):\s*$")
MARKER_RE = re.compile(r"^\s*# ---\s*(?P<title>.+?)\s*---\s*$")
TRIGGER_RE = re.compile(r"^\s*-\s+trigger:\s*(?P<name>\S+)\s*$")
ACTION_RE = re.compile(r"^\s+action:\s*\|-?\s*$")
IMAGE_NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")

# Blocs qui doivent rester dans toutes les builds (cochés et verrouillés).
REQUIRED_HINTS = (
    "RPM Fusion",
    "Flathub",
    "ps5-linux-tools",
    "SSH & Services",
    "Firmware AMD PS5",
    "grow-rootfs",
    "SELinux",
    "Utilisateur par défaut",
    "zram",
    "kernel rpm",
    "WiFi",
    "Fan ON et Boost ON",
    "PS5 Fedora Manager",
)
# Triggers purement système : tout y est toujours conservé.
ALWAYS_TRIGGERS = ("post-unpack", "post-update")

# Paquets nécessaires à la compilation de ps5-linux-tools pendant le build.
TOOLCHAIN = ("git", "make", "gcc")


# ---------------------------------------------------------------------------
# Modèle du YAML
# ---------------------------------------------------------------------------


def trim_trailing_blank(lines: list[str]) -> list[str]:
    out = list(lines)
    while out and not out[-1].strip():
        out.pop()
    return out


def yaml_scalar(value: str) -> str:
    """Rend une valeur sûre pour un champ `clé: valeur` (guillemets si besoin)."""
    if value == "" or re.search(r"[:#]", value) or value != value.strip():
        return json.dumps(value, ensure_ascii=False)
    return value


@dataclass
class PackageGroup:
    comment: str
    packages: list[str] = field(default_factory=list)

    @property
    def title(self) -> str:
        return self.comment.strip().lstrip("#").strip()

    def names(self) -> list[str]:
        return [p.strip()[2:].strip() for p in self.packages if p.strip().startswith("- ")]


@dataclass
class ScriptBlock:
    title: str
    marker: str | None
    lines: list[str] = field(default_factory=list)
    required: bool = False

    @property
    def signature(self) -> str:
        """Première ligne de code du bloc : sert à reconnaître un bloc dans un YAML."""
        for line in self.lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                return stripped
        return ""


@dataclass
class Trigger:
    name: str
    header: list[str] = field(default_factory=list)
    body: list[str] = field(default_factory=list)
    preamble: list[str] = field(default_factory=list)
    blocks: list[ScriptBlock] = field(default_factory=list)

    def split_blocks(self) -> None:
        markers = [i for i, line in enumerate(self.body) if MARKER_RE.match(line)]
        if not markers:
            self.preamble = trim_trailing_blank(self.body)
            self.blocks = []
            return
        self.preamble = trim_trailing_blank(self.body[: markers[0]])
        blocks: list[ScriptBlock] = []
        for n, start in enumerate(markers):
            end = markers[n + 1] if n + 1 < len(markers) else len(self.body)
            chunk = self.body[start:end]
            match = MARKER_RE.match(chunk[0])
            blocks.append(
                ScriptBlock(
                    title=match.group("title") if match else "Bloc",
                    marker=chunk[0],
                    lines=trim_trailing_blank(chunk[1:]),
                )
            )
        self.blocks = blocks

    def full_text(self) -> str:
        parts = [*self.preamble]
        for block in self.blocks:
            if block.marker:
                parts.append(block.marker)
            parts.extend(block.lines)
        return "\n".join(parts)


@dataclass
class Model:
    image: list[str]
    source: list[str]
    packages_head: list[str]
    groups: list[PackageGroup]
    packages_tail: list[str]
    files: list[str]
    triggers: list[Trigger]

    def all_package_names(self) -> list[str]:
        names: list[str] = []
        for group in self.groups:
            names.extend(group.names())
        return names

    def trigger(self, name: str) -> Trigger | None:
        for trigger in self.triggers:
            if trigger.name == name:
                return trigger
        return None


def split_sections(text: str, source: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    order: list[str] = []
    current: str | None = None
    for number, line in enumerate(text.splitlines(), start=1):
        match = SECTION_RE.match(line)
        if match:
            current = match.group(1)
            if current in sections:
                raise ValueError(f"{source}:{number} : section « {current}: » en double")
            sections[current] = [line]
            order.append(current)
        elif current is None:
            if line.strip():
                raise ValueError(f"{source}:{number} : contenu avant la première section")
        else:
            sections[current].append(line)
    return sections


def parse_packages(lines: list[str], source: str) -> tuple[list[str], list[PackageGroup], list[str]]:
    try:
        sets_index = next(i for i, line in enumerate(lines) if line.strip() == "sets:")
    except StopIteration:
        raise ValueError(f"{source} : « sets: » introuvable dans packages") from None
    try:
        packages_index = next(i for i in range(sets_index, len(lines)) if lines[i].strip() == "- packages:")
    except StopIteration:
        raise ValueError(f"{source} : « - packages: » introuvable dans packages") from None
    try:
        action_index = next(
            i for i in range(packages_index + 1, len(lines)) if lines[i].strip() == "action: install"
        )
    except StopIteration:
        raise ValueError(f"{source} : « action: install » introuvable dans packages") from None

    head = lines[: packages_index + 1]
    tail = lines[action_index:]
    groups: list[PackageGroup] = []
    current: PackageGroup | None = None
    for line in lines[packages_index + 1:action_index]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            current = PackageGroup(line)
            groups.append(current)
        elif stripped.startswith("- "):
            if current is None:
                current = PackageGroup("        # Paquets")
                groups.append(current)
            current.packages.append(line)
        else:
            raise ValueError(f"{source} : ligne inattendue dans la liste de paquets : {line!r}")
    return head, groups, tail


def parse_actions(lines: list[str], source: str) -> list[Trigger]:
    triggers: list[Trigger] = []
    current: Trigger | None = None
    for line in lines[1:]:
        match = TRIGGER_RE.match(line)
        if match:
            current = Trigger(match.group("name"), header=[line])
            triggers.append(current)
            continue
        if current is None:
            if line.strip():
                raise ValueError(f"{source} : ligne inattendue sous actions : {line!r}")
            continue
        if len(current.header) == 1 and ACTION_RE.match(line):
            current.header.append(line)
            continue
        current.body.append(line)

    seen: set[str] = set()
    for trigger in triggers:
        if trigger.name in seen:
            raise ValueError(f"{source} : trigger « {trigger.name} » en double")
        seen.add(trigger.name)
        trigger.split_blocks()
        for block in trigger.blocks:
            block.required = trigger.name in ALWAYS_TRIGGERS or any(
                hint.lower() in block.title.lower() for hint in REQUIRED_HINTS
            )
    return triggers


def parse_text(text: str, source: str) -> Model:
    sections = split_sections(text, source)
    for key in ("image", "source", "packages", "files", "actions"):
        if key not in sections:
            raise ValueError(f"{source} : section « {key}: » manquante")
    head, groups, tail = parse_packages(sections["packages"], source)
    triggers = parse_actions(sections["actions"], source)
    return Model(
        image=trim_trailing_blank(sections["image"]),
        source=trim_trailing_blank(sections["source"]),
        packages_head=trim_trailing_blank(head),
        groups=groups,
        packages_tail=trim_trailing_blank(tail),
        files=trim_trailing_blank(sections["files"]),
        triggers=triggers,
    )


def load_model(path: Path) -> Model:
    return parse_text(path.read_text(encoding="utf-8"), str(path))


# ---------------------------------------------------------------------------
# Lecture / écriture d'un champ, génération du YAML d'édition
# ---------------------------------------------------------------------------


def get_image_field(model: Model, key: str) -> str:
    prefix = f"  {key}:"
    for line in model.image:
        if line.startswith(prefix):
            value = line[len(prefix):].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            return value
    return ""


def set_image_field(lines: list[str], key: str, value: str) -> list[str]:
    out = list(lines)
    prefix = f"  {key}:"
    for index, line in enumerate(out):
        if line.startswith(prefix):
            out[index] = f"{prefix} {yaml_scalar(value)}"
            return out
    raise ValueError(f"champ image.{key} introuvable dans le YAML de base")


def render_edition(
    model: Model,
    name: str,
    description: str,
    is_pkg_selected,
    is_block_selected,
    actions_override: list[str] | None = None,
) -> str:
    image = set_image_field(model.image, "name", name)
    image = set_image_field(image, "description", description)

    package_lines = list(model.packages_head)
    for group in model.groups:
        kept = [line for line in group.packages if is_pkg_selected(package_name(line))]
        if not kept:
            continue
        if len(package_lines) > len(model.packages_head):
            package_lines.append("")
        package_lines.append(group.comment)
        package_lines.extend(kept)
    package_lines.extend(model.packages_tail)

    if actions_override is not None:
        action_lines = list(actions_override)
    else:
        action_lines = ["actions:"]
        for index, trigger in enumerate(model.triggers):
            if index:
                action_lines.append("")
            action_lines.extend(trigger.header)
            body = list(trigger.preamble)
            for block in trigger.blocks:
                if not (block.required or is_block_selected(trigger, block)):
                    continue
                if body:
                    body.append("")
                if block.marker:
                    body.append(block.marker)
                body.extend(block.lines)
            action_lines.extend(body)

    chunks = [
        image,
        model.source,
        package_lines,
        model.files,
        action_lines,
    ]
    out: list[str] = []
    for index, chunk in enumerate(chunks):
        if index:
            out.append("")
        out.extend(trim_trailing_blank(chunk))
    return "\n".join(out) + "\n"


def package_name(line: str) -> str:
    return line.strip()[2:].strip()


def default_stem(name: str) -> str:
    stem = name[4:] if name.startswith("ps5-") else name
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-._")
    return stem or "edition"


# ---------------------------------------------------------------------------
# Ajouts propres à une édition : dépôts, paquets, flatpaks, commandes, scripts.
# Ils sont stockés dans le YAML de l'édition sous forme de blocs dédiés, donc
# rien à maintenir à côté : le fichier reste autonome et rechargeable.
# ---------------------------------------------------------------------------

EXTRA_DEPOTS = "Dépôts supplémentaires (édition)"
EXTRA_PACKAGES = "Paquets supplémentaires (édition)"
EXTRA_FLATPAKS = "Applications Flatpak (édition)"
EXTRA_COMMANDS = "Commandes d'installation (édition)"
EXTRA_SCRIPTS = "Scripts supplémentaires (édition)"
EXTRA_FIELDS = {
    "depots": EXTRA_DEPOTS,
    "packages": EXTRA_PACKAGES,
    "flatpaks": EXTRA_FLATPAKS,
    "commands": EXTRA_COMMANDS,
    "scripts": EXTRA_SCRIPTS,
}
EXTRA_TITLES = tuple(EXTRA_FIELDS.values())

DNF_DROP = {"dnf", "install", "-y", "--allowerasing", "--skip-unavailable", "||", "true"}
FLATPAK_DROP = {"flatpak", "install", "-y", "flathub", "||", "true"}


def _clean_extras(texts: dict[str, list[str]]) -> dict[str, list[str]]:
    return {
        key: [line for line in lines if line.strip()]
        for key, lines in texts.items()
    }


def _shell_block(title: str, lines: list[str]) -> ScriptBlock | None:
    body = [f"      {line.rstrip()}" for line in lines if line.strip()]
    if not body:
        return None
    return ScriptBlock(title=title, marker=f"      # --- {title} ---", lines=body)


def extras_blocks(
    depots: list[str],
    packages: list[str],
    flatpaks: list[str],
    commands: list[str],
    scripts: list[str],
) -> list[ScriptBlock]:
    """Transforme les champs de l'onglet « Ajouts » en blocs de script."""
    texts = _clean_extras(
        {"depots": depots, "packages": packages, "flatpaks": flatpaks,
         "commands": commands, "scripts": scripts}
    )
    blocks: list[ScriptBlock] = []

    block = _shell_block(EXTRA_DEPOTS, texts["depots"])
    if block:
        blocks.append(block)

    names = [line.strip() for line in texts["packages"]]
    if names:
        blocks.append(
            ScriptBlock(
                title=EXTRA_PACKAGES,
                marker=f"      # --- {EXTRA_PACKAGES} ---",
                lines=[
                    "      dnf install -y --allowerasing --skip-unavailable "
                    + " ".join(names)
                    + " || true"
                ],
            )
        )

    ids = [line.strip() for line in texts["flatpaks"]]
    if ids:
        blocks.append(
            ScriptBlock(
                title=EXTRA_FLATPAKS,
                marker=f"      # --- {EXTRA_FLATPAKS} ---",
                lines=["      flatpak install -y flathub " + " ".join(ids) + " || true"],
            )
        )

    block = _shell_block(EXTRA_COMMANDS, texts["commands"])
    if block:
        blocks.append(block)

    block = _shell_block(EXTRA_SCRIPTS, texts["scripts"])
    if block:
        blocks.append(block)
    return blocks


def apply_extras(model: Model, blocks: list[ScriptBlock]) -> None:
    """Place les blocs d'ajouts au bon endroit dans les actions.

    Dépôts, paquets, flatpaks et commandes vont dans post-packages juste après
    RPM Fusion / Flathub (donc après l'ajout des dépôts) ; les scripts libres
    vont à la fin de post-files.
    """
    for trigger in model.triggers:
        trigger.blocks = [block for block in trigger.blocks if block.title not in EXTRA_TITLES]

    post = model.trigger("post-packages")
    if post is not None:
        index = 0
        for position, block in enumerate(post.blocks):
            if block.title.startswith("RPM Fusion") or block.title == "Flathub":
                index = position + 1
        post.blocks[index:index] = [block for block in blocks if block.title != EXTRA_SCRIPTS]

    files_trigger = model.trigger("post-files")
    scripts = [block for block in blocks if block.title == EXTRA_SCRIPTS]
    if files_trigger is not None and scripts:
        files_trigger.blocks.extend(scripts)


def _tokens(line: str, drop: set[str]) -> list[str]:
    return [token for token in line.replace("\\", " ").split() if token not in drop]


def extras_from_blocks(blocks: list[ScriptBlock]) -> dict[str, list[str]]:
    """Relit les champs de l'onglet « Ajouts » depuis un YAML d'édition."""
    texts: dict[str, list[str]] = {key: [] for key in EXTRA_FIELDS}
    reverse = {title: key for key, title in EXTRA_FIELDS.items()}
    for block in blocks:
        key = reverse.get(block.title)
        if key is None:
            continue
        raw = [line.strip() for line in block.lines if line.strip()]
        if key == "packages":
            names: list[str] = []
            for line in raw:
                names.extend(_tokens(line, DNF_DROP))
            texts[key] = names or raw
        elif key == "flatpaks":
            ids: list[str] = []
            for line in raw:
                ids.extend(_tokens(line, FLATPAK_DROP))
            texts[key] = ids or raw
        else:
            texts[key].extend(raw)
    return texts


def actions_section(model: Model) -> list[str]:
    """Section `actions:` brute (recopie fidèle, marqueurs compris)."""
    lines = ["actions:"]
    for index, trigger in enumerate(model.triggers):
        if index:
            lines.append("")
        lines.extend(trigger.header)
        lines.extend(trim_trailing_blank(trigger.body))
    return lines


def unknown_action_lines(base: Model, loaded: Model, ignore: set[str] | None = None) -> list[str]:
    """Lignes de code de l'édition absentes de la base (scripts sur mesure)."""
    base_text = "\n".join(trigger.full_text() for trigger in base.triggers)
    known = {line.strip() for line in base_text.splitlines() if line.strip()}
    ignored = ignore or set()
    unknown: list[str] = []
    for trigger in loaded.triggers:
        for line in trigger.body:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped in known or stripped in ignored:
                continue
            unknown.append(stripped)
    return unknown


def selection_from_loaded(base: Model, loaded: Model) -> tuple[
    dict[str, bool],
    dict[tuple[str, str], bool],
    list[str],
    list[tuple[str, int, ScriptBlock]],
    dict[str, list[str]],
    list[str] | None,
]:
    """Déduit l'état des cases à partir d'un YAML d'édition existant.

    Retourne (paquets cochés, blocs cochés, paquets hors base, blocs propres à
    l'édition, champs « Ajouts », actions brutes). Les actions brutes ne sont
    renvoyées que si l'édition contient du script qui n'existe pas dans la base :
    dans ce cas elles sont recopiées telles quelles à l'enregistrement.
    """
    base_names = set(base.all_package_names())
    loaded_names = {name for group in loaded.groups for name in group.names()}
    extras = sorted(loaded_names - base_names)

    package_state = {name: (name in loaded_names) for name in base.all_package_names()}
    for name in extras:
        package_state[name] = True

    base_titles = {(trigger.name, block.title) for trigger in base.triggers for block in trigger.blocks}
    base_lines = {
        trigger.name: {line.strip() for line in trigger.full_text().splitlines() if line.strip()}
        for trigger in base.triggers
    }
    extra_blocks: list[tuple[str, int, ScriptBlock]] = []
    recognized: list[ScriptBlock] = []
    for trigger in loaded.triggers:
        known = base_lines.get(trigger.name, set())
        for index, block in enumerate(trigger.blocks):
            if block.title in EXTRA_TITLES:
                recognized.append(block)
                continue
            if (trigger.name, block.title) in base_titles:
                continue
            # Bloc renommé ou fusionné : ses lignes viennent toutes de la base.
            if all(line.strip() in known for line in block.lines if line.strip()):
                continue
            block.required = False
            extra_blocks.append((trigger.name, index, block))

    block_state: dict[tuple[str, str], bool] = {}
    for trigger in base.triggers:
        loaded_trigger = loaded.trigger(trigger.name)
        text = loaded_trigger.full_text() if loaded_trigger else ""
        for block in trigger.blocks:
            block_state[(trigger.name, block.title)] = bool(block.signature and block.signature in text)
    for trigger_name, _index, block in extra_blocks:
        block_state[(trigger_name, block.title)] = True

    extra_lines = {
        line.strip() for _t, _i, block in extra_blocks for line in block.lines if line.strip()
    }
    extra_lines |= {line.strip() for block in recognized for line in block.lines if line.strip()}
    raw = actions_section(loaded) if unknown_action_lines(base, loaded, extra_lines) else None
    return package_state, block_state, extras, extra_blocks, extras_from_blocks(recognized), raw


def validate_edition_text(text: str) -> tuple[list[str], list[str]]:
    """Retourne (erreurs, avertissements). La validation YAML est optionnelle."""
    errors: list[str] = []
    warnings: list[str] = []
    try:
        import yaml  # type: ignore
    except Exception:
        return errors, warnings
    try:
        document = yaml.safe_load(text)
    except Exception as exc:  # YAML invalide
        return [f"YAML invalide : {exc}"], warnings
    if not isinstance(document, dict):
        return ["Le YAML généré n'est pas un dictionnaire."], warnings
    image = document.get("image") or {}
    packages = document.get("packages") or {}
    sets = packages.get("sets") or []
    count = len((sets[0] or {}).get("packages") or []) if sets else 0
    if not image.get("name"):
        errors.append("image.name est vide.")
    if count == 0:
        errors.append("Aucun paquet sélectionné.")
    if len(document.get("actions") or []) < 3:
        errors.append("Bloc actions incomplet.")
    return errors, warnings


# ---------------------------------------------------------------------------
# Comparatif des builds : build.difference.md
# ---------------------------------------------------------------------------

DIFFERENCE_FILE = REPO_ROOT / "build.difference.md"


def _md_cell(value: str) -> str:
    return value.replace("|", "\\|")


def collect_builds(dist_dir: Path = DISTRO_DIR) -> list[tuple[str, str, Model]]:
    builds: list[tuple[str, str, Model]] = []
    for path in sorted(dist_dir.glob("*.yaml")):
        try:
            model = load_model(path)
        except Exception:
            continue
        label = "base" if path.name == "image.yaml" else path.stem.replace("fedora-", "", 1)
        builds.append((label, path.name, model))
    builds.sort(key=lambda item: (item[1] != "image.yaml", item[0]))
    return builds


def _edition_extras(model: Model) -> dict[str, list[str]]:
    blocks = [
        block
        for trigger in model.triggers
        for block in trigger.blocks
        if block.title in EXTRA_TITLES
    ]
    return extras_from_blocks(blocks)


def difference_markdown(dist_dir: Path = DISTRO_DIR) -> str:
    builds = collect_builds(dist_dir)
    if not builds:
        return "# Comparaison des builds\n\nAucun YAML trouvé.\n"
    labels = [label for label, _name, _model in builds]

    package_sets: dict[str, set[str]] = {}
    block_sets: dict[str, set[str]] = {}
    extras_by_label: dict[str, dict[str, list[str]]] = {}
    package_order: list[str] = []
    block_order: list[str] = []

    for label, _name, model in builds:
        names: list[str] = []
        for group in model.groups:
            names.extend(group.names())
        package_sets[label] = set(names)
        for name in names:
            if name not in package_order:
                package_order.append(name)

        titles: list[str] = []
        for trigger in model.triggers:
            for block in trigger.blocks:
                if block.title not in titles:
                    titles.append(block.title)
        block_sets[label] = set(titles)
        for title in titles:
            if title not in block_order:
                block_order.append(title)

        extras_by_label[label] = _edition_extras(model)

    lines = ["# Comparaison des builds PS5 Fedora", ""]
    lines.append(
        "Fichier généré par `tools/edition_editor.py` (bouton « Comparatif des builds » "
        "ou à chaque enregistrement d'une édition). Ne pas éditer à la main."
    )
    lines.append("")
    lines.append("## Résumé")
    lines.append("")
    lines.append(
        "| Build | Image | Paquets | Blocs | Dépôts | Paquets ajoutés | Flatpaks | Scripts |"
    )
    lines.append("|---|---|--:|--:|--:|--:|--:|--:|")
    for label, _name, model in builds:
        extras = extras_by_label[label]
        lines.append(
            f"| `{label}` | `{get_image_field(model, 'name')}` "
            f"| {len(package_sets[label])} | {len(block_sets[label])} "
            f"| {len(extras['depots'])} | {len(extras['packages'])} "
            f"| {len(extras['flatpaks'])} | {len(extras['scripts'])} |"
        )
    lines.append("")

    lines.append("## Paquets")
    lines.append("")
    lines.append("| Paquet | " + " | ".join(f"`{label}`" for label in labels) + " |")
    lines.append("|---|" + "|".join(":--:" for _ in labels) + "|")
    for package in package_order:
        cells = ["✓" if package in package_sets[label] else "" for label in labels]
        lines.append(f"| `{_md_cell(package)}` | " + " | ".join(cells) + " |")
    lines.append("")

    lines.append("## Blocs de script (actions)")
    lines.append("")
    lines.append("| Bloc | " + " | ".join(f"`{label}`" for label in labels) + " |")
    lines.append("|---|" + "|".join(":--:" for _ in labels) + "|")
    for title in block_order:
        cells = ["✓" if title in block_sets[label] else "" for label in labels]
        lines.append(f"| {_md_cell(title)} | " + " | ".join(cells) + " |")
    lines.append("")

    lines.append("## Ajouts propres aux éditions")
    lines.append("")
    base_packages = package_sets.get("base", set())
    base_blocks = block_sets.get("base", set())
    headings = (
        ("depots", "Dépôts ajoutés"),
        ("packages", "Paquets installés en post-packages"),
        ("flatpaks", "Flatpaks"),
        ("commands", "Commandes d'installation"),
        ("scripts", "Scripts (fin de post-files)"),
    )
    for label, name, model in builds:
        if name == "image.yaml":
            continue
        extras = extras_by_label[label]
        added = [
            package
            for package in package_order
            if package in package_sets[label] and package not in base_packages
        ]
        removed = [
            package
            for package in package_order
            if package in base_packages and package not in package_sets[label]
        ]
        own = [
            title
            for title in block_order
            if title in block_sets[label] and title not in base_blocks
        ]
        if not (added or removed or own or any(extras.values())):
            continue
        lines.append(f"### `{label}` — `{get_image_field(model, 'name')}`")
        lines.append("")
        if added:
            lines.append("- **Paquets en plus de la base** : " + ", ".join(f"`{p}`" for p in added))
        if removed:
            lines.append(f"- **Paquets retirés de la base** : {len(removed)} (voir le tableau)")
        if own:
            lines.append("- **Blocs propres à l'édition** : " + ", ".join(_md_cell(t) for t in own))
        for key, heading in headings:
            values = extras.get(key) or []
            if not values:
                continue
            lines.append(f"- **{heading}** :")
            for value in values:
                lines.append(f"  - `{value}`")
        lines.append("")

    lines.append("Légende : ✓ = présent dans la build.")
    return "\n".join(lines) + "\n"


def write_difference_file(path: Path | None = None, dist_dir: Path = DISTRO_DIR) -> Path:
    target = path or DIFFERENCE_FILE
    target.write_text(difference_markdown(dist_dir), encoding="utf-8")
    return target


# ---------------------------------------------------------------------------
# Interface graphique
# ---------------------------------------------------------------------------

if TK_AVAILABLE:

    class EditionEditor(tk.Tk):
        """Fenêtre principale : paquets à gauche, blocs de script à droite."""

        def __init__(self) -> None:
            super().__init__()
            self.title("PS5 Fedora — Éditeur d'éditions")
            self.geometry("1200x820")
            self.minsize(940, 620)

            self.model = load_model(BASE_YAML)
            self.pkg_state: dict[str, bool] = {}
            self.block_state: dict[tuple[str, str], bool] = {}
            self.pkg_vars: dict[str, tk.BooleanVar] = {}
            self.block_vars: dict[tuple[str, str], tk.BooleanVar] = {}
            self.pkg_rows: list[
                tuple[PackageGroup, ttk.Checkbutton, tk.BooleanVar, list[tuple[str, tk.BooleanVar, ttk.Checkbutton]]]
            ] = []
            self.raw_actions: list[str] | None = None
            self._scroll_target: tk.Canvas | None = None

            self.name_var = tk.StringVar()
            self.file_var = tk.StringVar()
            self.desc_var = tk.StringVar()
            self.search_var = tk.StringVar()
            self.status_var = tk.StringVar(value="Prêt.")

            self._build_ui()
            self._reset_to_base()

            self.bind("<Control-s>", lambda _event: self._save())
            self.bind("<Control-o>", lambda _event: self._load_file())

        # -- Construction de l'interface ---------------------------------

        def _build_ui(self) -> None:
            style = ttk.Style(self)
            bold = tkfont.nametofont("TkDefaultFont").copy()
            bold.configure(weight="bold")
            self.mono_font = tkfont.nametofont("TkFixedFont").copy()
            self.mono_font.configure(size=8)
            style.configure("Group.TCheckbutton", font=bold)
            style.configure("Trigger.TLabel", font=bold, foreground="#1f4e79")

            self.columnconfigure(0, weight=1)
            self.rowconfigure(2, weight=1)

            # Champs d'édition
            top = ttk.LabelFrame(self, text="Édition")
            top.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))
            top.columnconfigure(1, weight=2)
            top.columnconfigure(3, weight=3)

            ttk.Label(top, text="Nom de l'image :").grid(row=0, column=0, sticky="w", padx=(8, 4), pady=4)
            name_entry = ttk.Entry(top, textvariable=self.name_var)
            name_entry.grid(row=0, column=1, sticky="ew", pady=4)
            self.name_var.trace_add("write", self._on_name_changed)

            ttk.Label(top, text="Fichier YAML :").grid(row=0, column=2, sticky="w", padx=(12, 4))
            ttk.Entry(top, textvariable=self.file_var).grid(row=0, column=3, sticky="ew", pady=4, padx=(0, 8))

            ttk.Label(top, text="Description :").grid(row=1, column=0, sticky="w", padx=(8, 4), pady=(0, 8))
            ttk.Entry(top, textvariable=self.desc_var).grid(
                row=1, column=1, columnspan=3, sticky="ew", pady=(0, 8), padx=(0, 8)
            )

            # Barre d'outils
            bar = ttk.Frame(self)
            bar.grid(row=1, column=0, sticky="ew", padx=10)
            for text, command in (
                ("Charger une édition…", self._load_file),
                ("Enregistrer", self._save),
                ("Enregistrer sous…", lambda: self._save(ask_path=True)),
                ("Aperçu YAML", self._preview),
                ("Comparatif des builds", self._write_difference_click),
                ("Repartir de la base", self._reset_to_base),
            ):
                ttk.Button(bar, text=text, command=command).pack(side="left", padx=(0, 6), pady=4)

            # Onglets : paquets/blocs + ajouts propres à l'édition
            notebook = ttk.Notebook(self)
            notebook.grid(row=2, column=0, sticky="nsew", padx=10, pady=6)

            panes_holder = ttk.Frame(notebook)
            notebook.add(panes_holder, text="Paquets & blocs")
            panes = ttk.PanedWindow(panes_holder, orient="horizontal")
            panes.pack(fill="both", expand=True)

            left = ttk.LabelFrame(panes, text="Paquets")
            right = ttk.LabelFrame(panes, text="Blocs de script")
            panes.add(left, weight=3)
            panes.add(right, weight=2)

            extras_tab = ttk.Frame(notebook)
            notebook.add(extras_tab, text="Ajouts (dépôts / rpm / flatpak / scripts)")
            self._build_extras_tab(extras_tab)

            left.columnconfigure(0, weight=1)
            left.rowconfigure(2, weight=1)
            search_row = ttk.Frame(left)
            search_row.grid(row=0, column=0, columnspan=2, sticky="ew", padx=6, pady=4)
            ttk.Label(search_row, text="Rechercher :").pack(side="left")
            search = ttk.Entry(search_row, textvariable=self.search_var)
            search.pack(side="left", fill="x", expand=True, padx=(6, 6))
            self.search_var.trace_add("write", lambda *_: self._apply_filter())

            buttons_row = ttk.Frame(left)
            buttons_row.grid(row=1, column=0, columnspan=2, sticky="ew", padx=6)
            ttk.Button(buttons_row, text="Tout cocher", command=lambda: self._set_all_packages(True)).pack(
                side="left", padx=(0, 6), pady=(0, 4)
            )
            ttk.Button(buttons_row, text="Tout décocher", command=lambda: self._set_all_packages(False)).pack(
                side="left", pady=(0, 4)
            )

            self.pkg_canvas, self.pkg_frame = self._make_scroll(left)
            self.pkg_canvas.grid(row=2, column=0, sticky="nsew")
            self.pkg_scroll = ttk.Scrollbar(left, orient="vertical", command=self.pkg_canvas.yview)
            self.pkg_scroll.grid(row=2, column=1, sticky="ns")
            self.pkg_canvas.configure(yscrollcommand=self.pkg_scroll.set)

            right.columnconfigure(0, weight=1)
            right.rowconfigure(2, weight=1)
            self.banner = ttk.Label(
                right,
                text="",
                foreground="#8a4b00",
                wraplength=420,
                justify="left",
            )
            self.banner.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(6, 0))
            ttk.Label(
                right,
                text="Les blocs marqués [commun] sont toujours inclus (kernel, WiFi, "
                "fan/boost, ps5_control, manager…). Pour qu'un script ajouté ici soit "
                "sélectionnable, encadre-le dans image.yaml d'un commentaire "
                "« # --- Titre --- ». Les lignes de post-unpack / post-update sont "
                "toujours conservées.",
                foreground="#555",
                wraplength=420,
                justify="left",
            ).grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=(4, 6))

            self.block_canvas, self.block_frame = self._make_scroll(right)
            self.block_canvas.grid(row=2, column=0, sticky="nsew")
            block_scroll = ttk.Scrollbar(right, orient="vertical", command=self.block_canvas.yview)
            block_scroll.grid(row=2, column=1, sticky="ns")
            self.block_canvas.configure(yscrollcommand=block_scroll.set)

            ttk.Label(self, textvariable=self.status_var, anchor="w", relief="sunken").grid(
                row=3, column=0, sticky="ew", padx=10, pady=(0, 8)
            )

        def _make_scroll(self, parent) -> tuple[tk.Canvas, ttk.Frame]:
            canvas = tk.Canvas(parent, highlightthickness=0, borderwidth=0)
            inner = ttk.Frame(canvas)
            window = canvas.create_window((0, 0), window=inner, anchor="nw")
            inner.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window, width=e.width))
            for sequence in ("<Button-4>", "<Button-5>", "<MouseWheel>"):
                canvas.bind_all(sequence, self._on_wheel)
            canvas.bind("<Enter>", lambda _e, c=canvas: self._set_scroll_target(c))
            return canvas, inner

        def _set_scroll_target(self, canvas: tk.Canvas) -> None:
            self._scroll_target = canvas

        # -- Onglet « Ajouts » -------------------------------------------

        def _build_extras_tab(self, frame) -> None:
            frame.columnconfigure(0, weight=1, uniform="extras")
            frame.columnconfigure(1, weight=1, uniform="extras")
            for row in (1, 2, 3):
                frame.rowconfigure(row, weight=1)

            ttk.Label(
                frame,
                text="Ajoute ici ce qui n'existe pas dans image.yaml. Ordre d'exécution : "
                "dépôts → paquets RPM → flatpaks → commandes (post-packages), puis scripts "
                "(fin de post-files).",
                foreground="#555",
                wraplength=980,
                justify="left",
            ).grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 2))

            self.extra_texts: dict[str, tk.Text] = {}
            self._add_text_field(
                frame, "depots", "Dépôts supplémentaires (une commande par ligne)", 1, 0,
                "ex. dnf config-manager --add-repo https://exemple/depot.repo",
            )
            self._add_text_field(
                frame, "packages", "Paquets RPM (un nom par ligne)", 1, 1,
                "installés par dnf install --skip-unavailable, après les dépôts",
            )
            self._add_text_field(
                frame, "flatpaks", "Applications Flatpak (un ID par ligne)", 2, 0,
                "ex. com.spotify.Client (installé depuis Flathub)",
            )
            self._add_text_field(
                frame, "commands", "Commandes d'installation (une par ligne)", 2, 1,
                "ex. dnf install -y https://…/paquet.rpm",
            )
            self._add_text_field(
                frame, "scripts", "Scripts supplémentaires (exécutés en fin de post-files)", 3,
                0, "commandes shell, une par ligne", columnspan=2,
            )

        def _add_text_field(self, parent, key, label, row, column, hint, columnspan=1) -> None:
            box = ttk.LabelFrame(parent, text=label)
            box.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", padx=8, pady=6)
            box.columnconfigure(0, weight=1)
            box.rowconfigure(0, weight=1)
            text = tk.Text(box, height=5, wrap="none", font=self.mono_font, undo=True)
            scroll = ttk.Scrollbar(box, orient="vertical", command=text.yview)
            text.configure(yscrollcommand=scroll.set)
            text.grid(row=0, column=0, sticky="nsew")
            scroll.grid(row=0, column=1, sticky="ns")
            ttk.Label(box, text=hint, foreground="#777", font=self.mono_font).grid(
                row=1, column=0, columnspan=2, sticky="w", padx=6, pady=(2, 4)
            )
            self.extra_texts[key] = text

        def _collect_extras(self) -> dict[str, list[str]]:
            # tk.Text renvoie toujours un saut de ligne final : on retire les
            # lignes vides pour ne pas générer de blocs fantômes.
            return {
                key: [line for line in widget.get("1.0", "end").splitlines() if line.strip()]
                for key, widget in self.extra_texts.items()
            }

        def _set_extras(self, texts: dict[str, list[str]]) -> None:
            for key, widget in self.extra_texts.items():
                widget.delete("1.0", "end")
                values = texts.get(key) or []
                if values:
                    widget.insert("1.0", "\n".join(values))

        def _write_difference_click(self) -> None:
            target = write_difference_file()
            try:
                shown = target.relative_to(REPO_ROOT)
            except ValueError:
                shown = target
            self.status_var.set(f"Comparatif écrit : {shown}")
            messagebox.showinfo(
                "Comparatif généré",
                f"{shown} a été régénéré à partir des YAML de distros/fedora/.",
                parent=self,
            )

        def _on_wheel(self, event) -> None:
            # Le pointeur est souvent sur une case à cocher (enfant du canvas) :
            # on remonte jusqu'au canvas pour savoir quel panneau faire défiler.
            widget = self.winfo_containing(event.x_root, event.y_root)
            while widget is not None and not isinstance(widget, tk.Canvas):
                widget = getattr(widget, "master", None)
            if widget is None:
                return
            canvas = widget
            if not canvas.winfo_exists():
                return
            if getattr(event, "num", None) == 4:
                canvas.yview_scroll(-3, "units")
            elif getattr(event, "num", None) == 5:
                canvas.yview_scroll(3, "units")
            else:
                delta = getattr(event, "delta", 0)
                if delta:
                    canvas.yview_scroll(-3 if delta > 0 else 3, "units")

        # -- État ---------------------------------------------------------

        def _reset_to_base(self) -> None:
            self.model = load_model(BASE_YAML)
            self.raw_actions = None
            self.pkg_state = {name: True for name in self.model.all_package_names()}
            self.block_state = {
                (trigger.name, block.title): True
                for trigger in self.model.triggers
                for block in trigger.blocks
            }
            self.name_var.set("ps5-fedora")
            self.desc_var.set(get_image_field(self.model, "description"))
            self.file_var.set("image.yaml")
            self._last_auto_file = "image.yaml"
            self._populate()
            self._set_extras({})
            self.status_var.set(f"Base chargée : {BASE_YAML.name}")

        def _populate(self) -> None:
            for child in self.pkg_frame.winfo_children():
                child.destroy()
            for child in self.block_frame.winfo_children():
                child.destroy()
            self.pkg_vars.clear()
            self.block_vars.clear()
            self.pkg_rows = []
            self._populate_packages()
            self._populate_blocks()
            self._refresh_status()
            self.banner.configure(text="")

        def _populate_packages(self) -> None:
            row = 0
            for group in self.model.groups:
                names = group.names()
                if not names:
                    continue
                header_var = tk.BooleanVar(value=all(self.pkg_state.get(n, True) for n in names))
                header = ttk.Checkbutton(
                    self.pkg_frame,
                    text=group.title,
                    style="Group.TCheckbutton",
                    variable=header_var,
                    command=lambda g=group, v=header_var: self._toggle_group(g, v),
                )
                header.grid(row=row, column=0, sticky="w", padx=(6, 0), pady=(10, 0))
                row += 1
                rows = []
                for name in names:
                    var = tk.BooleanVar(value=self.pkg_state.get(name, True))
                    check = ttk.Checkbutton(
                        self.pkg_frame,
                        text=name,
                        variable=var,
                        command=lambda n=name, v=var: self._on_package_toggle(n, v),
                    )
                    check.grid(row=row, column=0, sticky="w", padx=(28, 0))
                    row += 1
                    rows.append((name, var, check))
                    self.pkg_vars[name] = var
                self.pkg_rows.append((group, header, header_var, rows))
            self._refresh_group_labels()

        def _populate_blocks(self) -> None:
            row = 0
            for trigger in self.model.triggers:
                ttk.Label(self.block_frame, text=trigger.name, style="Trigger.TLabel").grid(
                    row=row, column=0, sticky="w", padx=(6, 0), pady=(10, 2)
                )
                row += 1
                if not trigger.blocks:
                    ttk.Label(
                        self.block_frame,
                        text="    (scripts système, toujours inclus)",
                        foreground="#666",
                    ).grid(row=row, column=0, sticky="w", padx=(28, 0))
                    row += 1
                    continue
                for block in trigger.blocks:
                    key = (trigger.name, block.title)
                    var = tk.BooleanVar(value=block.required or self.block_state.get(key, True))
                    label = ("[commun] " if block.required else "") + block.title
                    check = ttk.Checkbutton(
                        self.block_frame,
                        text=label,
                        variable=var,
                        state="disabled" if (block.required or self.raw_actions) else "normal",
                        command=lambda k=key, v=var: self._on_block_toggle(k, v),
                    )
                    check.grid(row=row, column=0, sticky="w", padx=(24, 0))
                    row += 1
                    if block.signature:
                        ttk.Label(
                            self.block_frame,
                            text="        " + block.signature[:110],
                            foreground="#888",
                            font=self.mono_font,
                        ).grid(row=row, column=0, sticky="w", padx=(24, 0))
                        row += 1
                    self.block_vars[key] = var

        # -- Interactions -------------------------------------------------

        def _toggle_group(self, group: PackageGroup, header_var: tk.BooleanVar) -> None:
            value = header_var.get()
            for name in group.names():
                self.pkg_state[name] = value
                if name in self.pkg_vars:
                    self.pkg_vars[name].set(value)
            self._refresh_group_labels()
            self._refresh_status()

        def _on_package_toggle(self, name: str, var: tk.BooleanVar) -> None:
            self.pkg_state[name] = var.get()
            self._refresh_group_labels()
            self._refresh_status()

        def _on_block_toggle(self, key: tuple[str, str], var: tk.BooleanVar) -> None:
            self.block_state[key] = var.get()
            self._refresh_status()

        def _set_all_packages(self, value: bool) -> None:
            for name, var in self.pkg_vars.items():
                var.set(value)
                self.pkg_state[name] = value
            self._refresh_group_labels()
            self._refresh_status()

        def _refresh_group_labels(self) -> None:
            for group, header, header_var, rows in self.pkg_rows:
                checked = sum(1 for _name, var, _check in rows if var.get())
                header.configure(text=f"{group.title}  ({checked}/{len(rows)})")
                header_var.set(checked == len(rows) and len(rows) > 0)

        def _refresh_status(self) -> None:
            total = len(self.pkg_vars)
            checked = sum(1 for var in self.pkg_vars.values() if var.get())
            blocks = len(self.block_vars)
            selected = sum(1 for var in self.block_vars.values() if var.get())
            self.status_var.set(f"{checked}/{total} paquets — {selected}/{blocks} blocs de script")

        def _apply_filter(self) -> None:
            query = self.search_var.get().strip().lower()
            for group, header, _header_var, rows in self.pkg_rows:
                group_match = query in group.title.lower()
                visible = False
                for name, _var, widget in rows:
                    show = (not query) or group_match or (query in name.lower())
                    if show:
                        widget.grid()
                    else:
                        widget.grid_remove()
                    visible = visible or show
                if visible or group_match:
                    header.grid()
                else:
                    header.grid_remove()

        def _on_name_changed(self, *_args) -> None:
            name = self.name_var.get().strip()
            if not name:
                return
            current = self.file_var.get().strip()
            if not current or current == "image.yaml" or current == self._last_auto_file:
                self.file_var.set(default_stem(name) + ".yaml")
            self._last_auto_file = self.file_var.get().strip()

        _last_auto_file = ""

        # -- Génération / sauvegarde --------------------------------------

        def _build_text(self) -> str:
            model = copy.deepcopy(self.model)
            apply_extras(model, extras_blocks(**self._collect_extras()))
            return render_edition(
                model,
                self.name_var.get().strip(),
                self.desc_var.get().strip(),
                is_pkg_selected=lambda name: self.pkg_state.get(name, True),
                is_block_selected=lambda trigger, block: self.block_state.get(
                    (trigger.name, block.title), True
                ),
                actions_override=self.raw_actions,
            )

        def _target_path(self, ask_path: bool) -> Path | None:
            filename = self.file_var.get().strip() or default_stem(self.name_var.get().strip()) + ".yaml"
            if not filename.endswith(".yaml"):
                filename += ".yaml"
            if ask_path:
                chosen = filedialog.asksaveasfilename(
                    parent=self,
                    initialdir=str(DISTRO_DIR),
                    initialfile=filename,
                    defaultextension=".yaml",
                    filetypes=[("YAML", "*.yaml")],
                )
                return Path(chosen) if chosen else None
            return DISTRO_DIR / Path(filename).name

        def _save(self, ask_path: bool = False) -> None:
            name = self.name_var.get().strip()
            description = self.desc_var.get().strip()
            if not name or not IMAGE_NAME_RE.fullmatch(name):
                messagebox.showerror(
                    "Nom invalide",
                    "Le nom de l'image doit commencer par une lettre ou un chiffre et ne "
                    "contenir que des lettres, chiffres, points, tirets et underscores.",
                    parent=self,
                )
                return
            if not description:
                messagebox.showerror("Description vide", "Ajoute une description.", parent=self)
                return
            if not any(self.pkg_state.values()):
                messagebox.showerror("Aucun paquet", "Sélectionne au moins un paquet.", parent=self)
                return

            target = self._target_path(ask_path)
            if target is None:
                return

            text = self._build_text()
            errors, _warnings = validate_edition_text(text)
            if errors:
                messagebox.showerror("YAML invalide", "\n".join(errors), parent=self)
                return

            soft = self._soft_checks()
            if soft and not messagebox.askyesno(
                "Vérifications", "\n".join(soft) + "\n\nEnregistrer quand même ?", parent=self
            ):
                return

            if target.exists() and not ask_path:
                if not messagebox.askyesno(
                    "Écraser le fichier ?", f"{target.name} existe déjà. L'écraser ?", parent=self
                ):
                    return
            if target.name == "image.yaml" and not messagebox.askyesno(
                "Attention",
                "Tu vas écraser la build de base image.yaml. Continuer ?",
                parent=self,
            ):
                return

            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            try:
                shown = target.relative_to(REPO_ROOT)
            except ValueError:
                shown = target
            self.file_var.set(target.name)
            self.status_var.set(f"Enregistré : {shown}")
            try:
                difference = write_difference_file().relative_to(REPO_ROOT)
                difference_text = f"\n\nComparatif mis à jour : {difference}"
            except Exception:
                difference_text = ""
            messagebox.showinfo(
                "Édition enregistrée",
                f"{shown}\n\nLe workflow détecte automatiquement les YAML de "
                "distros/fedora/ : cette édition sera buildée et releasée au prochain run."
                + difference_text,
                parent=self,
            )

        def _soft_checks(self) -> list[str]:
            problems: list[str] = []
            toolchain_block = False
            for (trigger_name, title), var in self.block_vars.items():
                if var.get() and "ps5-linux-tools" in title.lower():
                    toolchain_block = True
            missing = [pkg for pkg in TOOLCHAIN if not self.pkg_state.get(pkg, False)]
            if toolchain_block and missing:
                problems.append(
                    "ps5-linux-tools est compilé pendant le build mais "
                    + ", ".join(missing)
                    + " ne sont pas cochés : l'étape échouera."
                )
            extras_filled = any(self._collect_extras().values())
            if self.raw_actions and extras_filled:
                problems.append(
                    "Cette édition garde ses scripts tels quels (mode verrouillé) : les "
                    "champs « Ajouts » ne seront pas écrits dans le YAML."
                )
            flatpaks = [line for line in self._collect_extras()["flatpaks"] if line.strip()]
            if flatpaks and not self.block_state.get(("post-packages", "Flathub"), True):
                problems.append(
                    "Des applications Flatpak sont demandées mais le bloc « Flathub » "
                    "est décoché : flatpak install échouera."
                )
            return problems

        def _preview(self) -> None:
            text = self._build_text()
            window = tk.Toplevel(self)
            window.title("Aperçu du YAML généré")
            window.geometry("940x720")
            widget = tk.Text(window, wrap="none", font=self.mono_font)
            widget.insert("1.0", text)
            widget.configure(state="disabled")
            scroll = ttk.Scrollbar(window, orient="vertical", command=widget.yview)
            widget.configure(yscrollcommand=scroll.set)
            widget.pack(side="left", fill="both", expand=True)
            scroll.pack(side="right", fill="y")

        # -- Chargement d'une édition existante ---------------------------

        def _load_file(self) -> None:
            chosen = filedialog.askopenfilename(
                parent=self,
                initialdir=str(DISTRO_DIR),
                filetypes=[("YAML", "*.yaml"), ("Tous les fichiers", "*")],
            )
            if not chosen:
                return
            path = Path(chosen)
            try:
                loaded = load_model(path)
            except Exception as exc:
                messagebox.showerror("Lecture impossible", str(exc), parent=self)
                return

            self.model = load_model(BASE_YAML)

            (
                package_state,
                block_state,
                extra_names,
                extra_blocks,
                extras_text,
                raw_actions,
            ) = selection_from_loaded(self.model, loaded)
            if raw_actions is None:
                for trigger_name, index, block in extra_blocks:
                    target = self.model.trigger(trigger_name)
                    if target is None or any(
                        existing.title == block.title for existing in target.blocks
                    ):
                        continue
                    target.blocks.insert(min(index, len(target.blocks)), block)
            if extra_names:
                self.model.groups.append(
                    PackageGroup(
                        "        # Paquets supplémentaires (hors image.yaml)",
                        [f"        - {name}" for name in extra_names],
                    )
                )
            self.pkg_state = package_state
            self.block_state = block_state
            self.raw_actions = raw_actions

            self.name_var.set(get_image_field(loaded, "name") or path.stem)
            self.desc_var.set(get_image_field(loaded, "description"))
            self.file_var.set(path.name)
            self._last_auto_file = path.name
            self._populate()
            self._set_extras(extras_text)
            if self.raw_actions:
                self.banner.configure(
                    text="Scripts personnalisés détectés : les blocs ne sont pas modifiables, "
                    "mais ils seront recopiés tels quels à l'enregistrement. Seuls les "
                    "paquets, le nom et la description sont éditables."
                )
                self.status_var.set(
                    self.status_var.get() + " — scripts de l'édition conservés tels quels"
                )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def print_structure() -> int:
    try:
        model = load_model(BASE_YAML)
    except Exception as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 1
    print(f"Base        : {BASE_YAML.relative_to(REPO_ROOT)}")
    print(f"Image       : {get_image_field(model, 'name')}")
    print(f"Paquets     : {len(model.all_package_names())} en {len(model.groups)} groupes")
    for group in model.groups:
        print(f"  - {group.title} : {len(group.names())}")
    print("Blocs       :")
    for trigger in model.triggers:
        required = sum(1 for block in trigger.blocks if block.required)
        print(f"  {trigger.name} : {len(trigger.blocks)} bloc(s), {required} commun(s)")
        for block in trigger.blocks:
            flag = "commun" if block.required else "optionnel"
            print(f"    [{flag}] {block.title}")
        if not trigger.blocks:
            print("    (scripts système, toujours inclus)")
    return 0


def main(argv: list[str]) -> int:
    if "--check" in argv:
        return print_structure()
    if "--difference" in argv:
        target = write_difference_file()
        try:
            shown = target.relative_to(REPO_ROOT)
        except ValueError:
            shown = target
        print(f"Écrit : {shown}")
        return 0
    if not TK_AVAILABLE:
        print(
            "Tkinter est indisponible.\n"
            "Installe-le puis relance :\n"
            "  Fedora : sudo dnf install python3-tkinter\n"
            "  Debian/Ubuntu : sudo apt install python3-tk",
            file=sys.stderr,
        )
        return 1
    app = EditionEditor()
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
