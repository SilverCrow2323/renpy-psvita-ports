"""Read-only inventory and conservative compatibility hints for Ren'Py projects."""

from __future__ import annotations

import re
from pathlib import Path

VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogv", ".ogg", ".mkv", ".avi", ".mov", ".mpeg", ".mpg"}
NATIVE_EXTENSIONS = {".so", ".dll", ".pyd", ".dylib"}
MAX_OPTIONS_BYTES = 2 * 1024 * 1024
MAX_FINGERPRINT_BYTES = 512 * 1024


def _read_text(path: Path, limit: int) -> str:
    try:
        if path.stat().st_size > limit:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _read_options(path: Path) -> str:
    return _read_text(path, MAX_OPTIONS_BYTES)


def _detect_engine_version(project: Path) -> dict:
    """Read version literals from engine-owned files; never execute project code."""
    roots = [project / "renpy"]
    if project.name.lower() == "game":
        roots.append(project.parent / "renpy")

    for engine_root in roots:
        if not engine_root.is_dir():
            continue

        # Modern Ren'Py writes the generated version literal here.
        vc_version = _read_text(engine_root / "vc_version.py", MAX_FINGERPRINT_BYTES)
        match = re.search(
            r"""^\s*version\s*=\s*["'](\d+\.\d+\.\d+(?:\.\d+)?(?:[-+][\w.-]+)?)["']""",
            vc_version,
            re.MULTILINE,
        )
        if match:
            return {
                "version": match.group(1),
                "confidence": "high",
                "source": (engine_root / "vc_version.py").as_posix(),
                "evidence": "literal version assignment in Ren'Py's generated vc_version.py",
            }

        # Older releases embedded a literal tuple in renpy/__init__.py.
        init_text = _read_text(engine_root / "__init__.py", MAX_FINGERPRINT_BYTES)
        tuple_match = re.search(
            r"^\s*version_tuple\s*=\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)",
            init_text,
            re.MULTILINE,
        )
        if tuple_match:
            return {
                "version": ".".join(tuple_match.groups()),
                "confidence": "medium",
                "source": (engine_root / "__init__.py").as_posix(),
                "evidence": "literal major/minor/patch tuple in Ren'Py's engine package",
            }

    return {
        "version": None,
        "confidence": "none",
        "source": None,
        "evidence": "no supported engine version literal found",
    }


def inspect_project(root: str | Path) -> dict:
    project = Path(root).expanduser().resolve()
    if not project.is_dir():
        raise ValueError(f"project directory does not exist: {project}")

    game_dir = project / "game"
    if not game_dir.is_dir():
        # Accept a direct game/ directory as input too.
        if project.name.lower() == "game":
            game_dir = project
        else:
            raise ValueError("no game/ directory found; select the game root or its game/ folder")

    files: list[Path] = []
    total_bytes = 0
    for path in project.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        files.append(path)
        try:
            total_bytes += path.stat().st_size
        except OSError:
            pass
        if len(files) > 250_000:
            raise ValueError("project contains more than 250,000 files; scan aborted")

    relative = [p.relative_to(project).as_posix() for p in files]
    options = _read_options(game_dir / "options.rpy")
    version_match = re.search(r"""(?:define\s+)?config\.version\s*=\s*["']([^"']+)["']""", options)
    name_match = re.search(r"""(?:define\s+)?config\.name\s*=\s*["']([^"']+)["']""", options)

    engine_version = _detect_engine_version(project)
    archives = [p for p in files if p.suffix.lower() == ".rpa"]
    scripts = [p for p in files if p.suffix.lower() in {".rpy", ".rpyc", ".rpym", ".rpymc"}]
    videos = [p for p in files if p.suffix.lower() in VIDEO_EXTENSIONS]
    native = [p for p in files if p.suffix.lower() in NATIVE_EXTENSIONS]
    image_count = sum(1 for p in files if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".avif"})
    audio_count = sum(1 for p in files if p.suffix.lower() in {".ogg", ".opus", ".mp3", ".wav", ".flac"})

    livearea = project / "sce_sys"
    if project.name.lower() == "game":
        livearea = project.parent / "sce_sys"
    livearea_checks = {
        "sce_sys_present": livearea.is_dir(),
        "icon0": (livearea / "icon0.png").is_file(),
        "pic0": (livearea / "pic0.png").is_file(),
        "param_sfo": (livearea / "param.sfo").is_file(),
        "livearea_template": (livearea / "livearea" / "contents" / "template.xml").is_file(),
        "livearea_background": (livearea / "livearea" / "contents" / "bg.png").is_file(),
        "livearea_startup": (livearea / "livearea" / "contents" / "startup.png").is_file(),
    }

    engine_dirs = [name for name in ("renpy", "lib", "common") if (project / name).is_dir()]
    if project.name.lower() == "game" and (project.parent / "renpy").is_dir() and "renpy" not in engine_dirs:
        engine_dirs.append("renpy")
    python_runtime_dirs = sorted({
        p.relative_to(project).parts[1]
        for p in files
        if len(p.relative_to(project).parts) > 2
        and p.relative_to(project).parts[0] == "lib"
        and p.relative_to(project).parts[1].lower().startswith("python")
    })

    hints = []
    if archives:
        hints.append("RPA archives detected; inspect each archive before selecting an extraction strategy.")
    if videos:
        hints.append("Video files detected; baseline Ren'Py Vita documentation lists video playback as unsupported.")
    if native:
        hints.append("Native extension libraries detected; desktop binaries are not Vita-compatible by default.")
    if any(p.suffix.lower() == ".rpyc" for p in scripts) and not any(p.suffix.lower() == ".rpy" for p in scripts):
        hints.append("Compiled scripts detected without visible source scripts; engine-version matching may be important.")
    if not livearea_checks["sce_sys_present"]:
        hints.append("No sce_sys/ directory found; Vita LiveArea metadata/assets still need to be prepared.")
    if not livearea_checks["param_sfo"]:
        hints.append("No param.sfo found; this scan does not generate Vita metadata.")
    if engine_version["version"] is None:
        hints.append("Ren'Py engine version is unknown: no supported literal fingerprint was found.")
    else:
        hints.append(
            f"Ren'Py engine fingerprint: {engine_version['version']} "
            f"({engine_version['confidence']} confidence; {engine_version['source']})."
        )
    if python_runtime_dirs:
        hints.append("Bundled Python runtime directories detected; these identify packaged runtimes, not by themselves the Ren'Py engine version.")

    return {
        "project_root": str(project),
        "game_directory": str(game_dir),
        "title": name_match.group(1) if name_match else project.name,
        "game_version": version_match.group(1) if version_match else None,
        "renpy_version": engine_version["version"],
        "renpy_version_detection": engine_version,
        "file_count": len(files),
        "total_bytes": total_bytes,
        "rpa_archives": [p.relative_to(project).as_posix() for p in archives],
        "script_files": len(scripts),
        "video_files": [p.relative_to(project).as_posix() for p in videos],
        "native_libraries": [p.relative_to(project).as_posix() for p in native],
        "image_count": image_count,
        "audio_count": audio_count,
        "engine_directories": engine_dirs,
        "python_runtime_directories": python_runtime_dirs,
        "vita_livearea": livearea_checks,
        "compatibility_hints": hints,
        "confidence": "inventory-plus-engine-fingerprint" if engine_version["version"] else "inventory-only",
        "limitations": [
            "A file inventory is not a compatibility test.",
            "This version does not parse RPYC scripts, decrypt custom archives, patch games or build VPK files.",
            "Engine fingerprints are read from literal metadata only; unknown versions remain unknown.",
        ],
    }
