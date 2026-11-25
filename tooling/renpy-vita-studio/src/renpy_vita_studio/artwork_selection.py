"""Explicit artwork choices for each generated LiveArea slot."""
from __future__ import annotations

from pathlib import Path

GENERATED_ARTWORK_LABEL = "Generate title card"


def artwork_choices(paths, game_dir: str | Path) -> list[str]:
    """Return one explicit generated-art option followed by game-relative images."""
    root = Path(game_dir).resolve()
    values = [GENERATED_ARTWORK_LABEL]
    for candidate in paths:
        path = Path(candidate)
        try:
            values.append(path.resolve().relative_to(root).as_posix())
        except ValueError:
            continue
    return values


def resolve_artwork_selection(value: str, game_dir: str | Path) -> Path | None:
    """Resolve a combobox choice; generated cards are represented by None."""
    choice = value.strip()
    if not choice or choice == GENERATED_ARTWORK_LABEL:
        return None
    path = Path(choice).expanduser()
    if not path.is_absolute():
        path = Path(game_dir) / path
    if not path.is_file():
        raise ValueError(f"Selected artwork file does not exist: {path}")
    return path.resolve()
