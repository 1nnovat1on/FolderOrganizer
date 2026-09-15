"""Testable local file organization operations."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil

MANIFEST_NAME = ".folderorganizer-last-run.json"


@dataclass(frozen=True)
class Preview:
    groups: dict[str, list[str]]
    file_count: int
    excluded_count: int


@dataclass(frozen=True)
class MoveRecord:
    original_path: str
    destination_path: str


@dataclass(frozen=True)
class OrganizationResult:
    moves: list[MoveRecord]
    manifest_path: Path


@dataclass(frozen=True)
class UndoResult:
    restored_count: int
    skipped_count: int
    message: str


def _is_hidden(path: Path) -> bool:
    if path.name.startswith("."):
        return True
    attributes = getattr(path.stat(), "st_file_attributes", 0)
    hidden_attribute = getattr(__import__("stat"), "FILE_ATTRIBUTE_HIDDEN", 2)
    return bool(attributes & hidden_attribute)


def _visible_top_level_files(folder: Path) -> tuple[list[Path], int]:
    files: list[Path] = []
    excluded_count = 0
    for candidate in folder.iterdir():
        if _is_hidden(candidate) or not candidate.is_file():
            excluded_count += 1
        else:
            files.append(candidate)
    return files, excluded_count


def _extension_folder_name(path: Path) -> str:
    return path.suffix.lower().lstrip(".") or "no_extension"


def build_preview(folder: Path) -> Preview:
    """Return visible top-level regular files grouped by normalized extension."""
    groups: dict[str, list[str]] = defaultdict(list)
    files, excluded_count = _visible_top_level_files(Path(folder))
    for candidate in files:
        groups[_extension_folder_name(candidate)].append(candidate.name)
    ordered_groups = {key: sorted(value, key=str.casefold) for key, value in sorted(groups.items())}
    return Preview(ordered_groups, sum(map(len, ordered_groups.values())), excluded_count)


def _available_destination(destination_folder: Path, source_name: str) -> Path:
    candidate = destination_folder / source_name
    if not candidate.exists():
        return candidate
    source_path = Path(source_name)
    stem, suffix = source_path.stem, source_path.suffix
    number = 1
    while True:
        candidate = destination_folder / f"{stem} ({number}){suffix}"
        if not candidate.exists():
            return candidate
        number += 1


def organize_preview(folder: Path, *, confirmed: bool) -> OrganizationResult:
    """Move previewed files only after explicit confirmation and record an undo manifest."""
    root = Path(folder)
    manifest_path = root / MANIFEST_NAME
    if not confirmed:
        return OrganizationResult([], manifest_path)

    files, _ = _visible_top_level_files(root)
    moves: list[MoveRecord] = []
    for source in files:
        destination_folder = root / _extension_folder_name(source)
        destination_folder.mkdir(exist_ok=True)
        destination = _available_destination(destination_folder, source.name)
        shutil.move(str(source), str(destination))
        moves.append(MoveRecord(str(source), str(destination)))

    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "moves": [asdict(move) for move in moves],
    }
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return OrganizationResult(moves, manifest_path)


def undo_last_run(folder: Path) -> UndoResult:
    """Restore files from the most recent manifest without overwriting anything."""
    manifest_path = Path(folder) / MANIFEST_NAME
    if not manifest_path.is_file():
        return UndoResult(0, 0, "No previous run manifest was found.")

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    restored = 0
    skipped = 0
    for move in reversed(payload.get("moves", [])):
        original = Path(move["original_path"])
        destination = Path(move["destination_path"])
        if not destination.is_file() or original.exists():
            skipped += 1
            continue
        original.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(destination), str(original))
        restored += 1

    if skipped == 0:
        manifest_path.unlink()
        message = f"Restored {restored} file(s)."
    else:
        message = f"Restored {restored} file(s); skipped {skipped} to avoid overwriting."
    return UndoResult(restored, skipped, message)
