"""Non-destructive staging for a Vita app folder; this does not create a VPK."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import struct
from pathlib import Path

TITLE_ID_RE = re.compile(r"^[A-Z0-9]{9}$")
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SFO_MAGIC = b"\x00PSF"


class StageError(ValueError):
    """Raised when a project is not safe or complete enough to stage."""


def _png_dimensions(path: Path) -> tuple[int, int]:
    try:
        with path.open("rb") as stream:
            header = stream.read(24)
    except OSError as exc:
        raise StageError(f"cannot read image {path}: {exc}") from exc
    if len(header) < 24 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        raise StageError(f"{path} is not a valid PNG header")
    width, height = struct.unpack(">II", header[16:24])
    if width == 0 or height == 0:
        raise StageError(f"{path} has invalid PNG dimensions")
    return width, height


def _read_sfo(path: Path) -> tuple[int, dict]:
    """Parse bounded PSF metadata without interpreting executable content."""
    max_sfo_bytes = 4 * 1024 * 1024
    try:
        size = path.stat().st_size
        if size < 20 or size > max_sfo_bytes:
            raise StageError(f"{path} has an invalid PSF file size")
        data = path.read_bytes()
    except OSError as exc:
        raise StageError(f"cannot read {path}: {exc}") from exc

    if data[:4] != SFO_MAGIC:
        raise StageError(f"{path} is missing a valid PSF magic/header")
    _version, key_start, data_start, entry_count = struct.unpack_from("<IIII", data, 4)
    entries_start = 20
    entries_end = entries_start + entry_count * 16
    if entry_count > 4096 or entries_end > len(data):
        raise StageError(f"{path} has an invalid PSF entry table")
    if key_start < entries_end or key_start > data_start or data_start > len(data):
        raise StageError(f"{path} has invalid PSF key/data table offsets")

    key_table_end = data_start
    fields = {}
    for index in range(entry_count):
        offset = entries_start + index * 16
        key_offset, value_format, value_length, value_max_length, value_offset = struct.unpack_from(
            "<HHIII", data, offset
        )
        key_position = key_start + key_offset
        if key_position < key_start or key_position >= key_table_end:
            raise StageError(f"{path} contains an out-of-range PSF key offset")
        key_end = data.find(b"\\x00", key_position, key_table_end)
        if key_end < 0:
            raise StageError(f"{path} contains an unterminated PSF key")
        try:
            key = data[key_position:key_end].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise StageError(f"{path} contains a non-UTF-8 PSF key") from exc
        if not key or key in fields:
            raise StageError(f"{path} contains an empty or duplicate PSF key")

        value_start = data_start + value_offset
        value_end = value_start + value_length
        if value_length > value_max_length or value_start < data_start or value_end > len(data):
            raise StageError(f"{path} contains an out-of-range PSF value")
        raw = data[value_start:value_end]
        if value_format == 0x0204:
            raw = raw.split(b"\\x00", 1)[0]
            try:
                value = raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise StageError(f"{path} contains invalid UTF-8 in {key}") from exc
        elif value_format == 0x0404:
            if value_length != 4:
                raise StageError(f"{path} contains an invalid integer field: {key}")
            value = struct.unpack("<I", raw)[0]
        else:
            value = {"format": value_format, "length": value_length}
        fields[key] = value
    return size, fields

def _reject_symlinks(root: Path) -> None:
    for path in root.rglob("*"):
        if path.is_symlink():
            raise StageError(f"symbolic links are not allowed in staging input: {path}")


def _hash_files(root: Path) -> list[dict]:
    records = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        records.append({
            "path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "sha256": digest.hexdigest(),
        })
    return records


def stage_project(
    project_root: str | Path,
    destination: str | Path,
    title_id: str,
) -> dict:
    """Copy game/ and sce_sys/ into app/<TITLE_ID>, refusing overwrite."""
    source = Path(project_root).expanduser().resolve()
    target = Path(destination).expanduser().resolve()

    if not TITLE_ID_RE.fullmatch(title_id):
        raise StageError("title ID must be exactly 9 uppercase alphanumeric characters")
    if not source.is_dir():
        raise StageError(f"project directory does not exist: {source}")

    app_root = target / "app" / title_id
    if app_root.exists() or app_root.is_symlink():
        raise StageError(f"destination already exists; refusing to overwrite: {app_root}")
    if app_root in source.parents or source in app_root.parents:
        raise StageError("source and destination overlap; choose a separate staging directory")

    game = source / "game"
    sce_sys = source / "sce_sys"
    if not game.is_dir():
        raise StageError("project root must contain a game/ directory")
    if not sce_sys.is_dir():
        raise StageError("project root must contain sce_sys/")
    if not (sce_sys / "param.sfo").is_file():
        raise StageError("sce_sys/param.sfo is required for Vita staging")
    if not (sce_sys / "icon0.png").is_file():
        raise StageError("sce_sys/icon0.png is required for Vita staging")

    _reject_symlinks(source)
    sfo_size, sfo_fields = _read_sfo(sce_sys / "param.sfo")
    sfo_title_id = sfo_fields.get("TITLE_ID")
    if not isinstance(sfo_title_id, str):
        raise StageError("sce_sys/param.sfo does not contain a readable TITLE_ID string")
    if sfo_title_id != title_id:
        raise StageError(
            f"title ID mismatch: --title-id is {title_id}, but param.sfo contains {sfo_title_id}"
        )
    icon_dimensions = _png_dimensions(sce_sys / "icon0.png")

    optional_images = {}
    for name in ("pic0.png", "pic1.png"):
        candidate = sce_sys / name
        if candidate.is_file():
            optional_images[name] = _png_dimensions(candidate)

    app_root.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copytree(game, app_root / "game", symlinks=False)
        shutil.copytree(sce_sys, app_root / "sce_sys", symlinks=False)
        files = _hash_files(app_root)
        manifest = {
            "format": "spdw-renpy-vita-stage-v1",
            "title_id": title_id,
            "source_project": str(source),
            "app_directory": str(app_root),
            "file_count": len(files),
            "total_bytes": sum(item["size"] for item in files),
            "vita_metadata": {
                "param_sfo_bytes": sfo_size,\n                "param_sfo_fields": {key: sfo_fields[key] for key in ("TITLE", "TITLE_ID", "APP_VER", "CATEGORY") if key in sfo_fields},
                "icon0_png_dimensions": list(icon_dimensions),
                "optional_png_dimensions": optional_images,
            },
            "files": files,
            "limitations": [
                "Staging copies files; it does not build or sign a VPK.",
                "param.sfo is checked for a PSF header only; its fields are not parsed or rewritten.",
                "PNG checks validate the header and dimensions, not full image decoding or Vita-specific size requirements.",
                "A successful staging operation is not a runtime compatibility test.",
            ],
        }
        manifest_path = app_root / "spdw-stage-manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return {
            "title_id": title_id,
            "app_directory": str(app_root),
            "manifest": str(manifest_path),
            "file_count": len(files),
            "total_bytes": manifest["total_bytes"],
            "vita_metadata": manifest["vita_metadata"],
        }
    except Exception:
        # Only remove the newly-created target; never touch the supplied source.
        if app_root.exists():
            shutil.rmtree(app_root)
        raise
