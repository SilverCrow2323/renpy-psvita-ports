"""VitaSDK discovery shared by the GUI, CLI, diagnostics and packager."""
from __future__ import annotations

import os
import shutil
from pathlib import Path


def _home_directory() -> Path | None:
    """Return the user's home directory when the host can resolve one."""
    try:
        return Path.home()
    except (OSError, RuntimeError):
        # Windows services and some stripped-down launch environments can
        # lack HOME/USERPROFILE. SDK discovery must still report "not found"
        # rather than crashing the diagnostics screen.
        return None


def configure_vitasdk_path() -> str | None:
    """Find VitaSDK even when an XFCE launcher has not loaded shell profiles."""
    candidates: list[Path] = []
    configured = os.environ.get("VITASDK", "").strip()
    if configured:
        try:
            candidates.append(Path(configured).expanduser())
        except (OSError, RuntimeError):
            candidates.append(Path(configured))

    candidates.extend((Path("/usr/local/vitasdk"), Path("/opt/vitasdk")))
    home = _home_directory()
    if home is not None:
        candidates.append(home / "vitasdk")

    seen: set[str] = set()
    for root in candidates:
        try:
            resolved = root.resolve()
        except (OSError, RuntimeError):
            continue
        identity = os.path.normcase(str(resolved))
        if identity in seen:
            continue
        seen.add(identity)

        bindir = resolved / "bin"
        if not bindir.is_dir():
            continue

        if not os.environ.get("VITASDK"):
            os.environ["VITASDK"] = str(resolved)

        path_entries = os.environ.get("PATH", "").split(os.pathsep)
        bindir_text = str(bindir)
        if os.path.normcase(bindir_text) not in {
            os.path.normcase(entry) for entry in path_entries if entry
        }:
            os.environ["PATH"] = os.pathsep.join(
                [bindir_text, *(entry for entry in path_entries if entry)]
            )
        return str(resolved)

    return None


def find_vitasdk_tool(name: str) -> str | None:
    configure_vitasdk_path()
    found = shutil.which(name)
    if found:
        return found

    root = os.environ.get("VITASDK", "").strip()
    if root:
        try:
            candidate = Path(root).expanduser() / "bin" / name
        except (OSError, RuntimeError):
            return None
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None
