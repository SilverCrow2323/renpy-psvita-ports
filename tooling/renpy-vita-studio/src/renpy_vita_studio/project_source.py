"""Resolve a user's original Ren'Py game directory without requiring a Vita template."""
from __future__ import annotations

import hashlib
from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
EXCLUDED_DIRS = {".git", "__pycache__", ".renpy"}

class ProjectSourceError(ValueError):
    pass

def resolve_game_directory(selected: str | Path) -> tuple[Path, Path]:
    chosen = Path(selected).expanduser().resolve()
    if not chosen.is_dir():
        raise ProjectSourceError(f"Selected folder does not exist: {chosen}")
    if chosen.name.lower() == "game":
        game = chosen
        project_root = chosen.parent
    else:
        game = chosen / "game"
        project_root = chosen
    if not game.is_dir():
        raise ProjectSourceError("Select the original Ren'Py game folder (the folder that contains game/), or select game/ itself.")
    if not any(game.iterdir()):
        raise ProjectSourceError("The selected game/ folder is empty.")
    if game.is_symlink():
        raise ProjectSourceError("The game/ directory cannot be a symbolic link.")
    return project_root, game

def discover_artwork(game_dir: str | Path, limit: int = 300) -> list[Path]:
    root = Path(game_dir)
    found = []
    for path in root.rglob("*"):
        if any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_symlink() or not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        try:
            if path.stat().st_size <= 40 * 1024 * 1024:
                found.append(path)
        except OSError:
            continue
        if len(found) >= limit:
            break
    # Prefer larger, likely cover/background images while retaining deterministic order.
    return sorted(found, key=lambda p: (p.stat().st_size if p.exists() else 0), reverse=True)

def default_title_id(title: str, project_path: str | Path) -> str:
    digest = hashlib.sha256((title + str(Path(project_path).resolve())).encode("utf-8")).hexdigest()
    return "RNV" + digest[:6].upper()
