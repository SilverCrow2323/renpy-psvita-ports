"""Vita VPK packaging for a staged app with a runtime-built eboot.bin."""

from __future__ import annotations

import re
import shutil
import subprocess
import zipfile
from pathlib import Path

from .stage import StageError, _read_sfo, _reject_symlinks

MAX_COMMAND_CHARS = 24_000


def build_vpk(staged_app: str | Path, output: str | Path) -> dict:
    """Call VitaSDK's vita-pack-vpk without a shell and verify the resulting archive."""
    app = Path(staged_app).expanduser().resolve()
    target = Path(output).expanduser().resolve()

    if not app.is_dir():
        raise StageError(f"staged app directory does not exist: {app}")
    title_id = app.name
    if not re.fullmatch(r"[A-Z]{4}[0-9]{5}", title_id):
        raise StageError("staged app folder must be named with its Vita-format title ID (4 letters + 5 digits)")
    if target.suffix.lower() != ".vpk":
        raise StageError("output filename must use the .vpk extension")
    if target.exists() or target.is_symlink():
        raise StageError(f"output already exists; refusing to overwrite: {target}")
    if target in app.parents or app in target.parents:
        raise StageError("VPK output and staged app must be separate paths")

    eboot = app / "eboot.bin"
    sfo = app / "sce_sys" / "param.sfo"
    if not eboot.is_file():
        raise StageError("staged app is missing eboot.bin; build it with a compatible Vita runtime first")
    if not sfo.is_file():
        raise StageError("staged app is missing sce_sys/param.sfo")
    _reject_symlinks(app)
    _sfo_size, fields = _read_sfo(sfo)
    if fields.get("TITLE_ID") != title_id:
        raise StageError("staged app folder title ID does not match sce_sys/param.sfo")

    packer = shutil.which("vita-pack-vpk")
    if not packer:
        raise StageError("vita-pack-vpk was not found; install/configure VitaSDK and add its bin directory to PATH")

    payload = []
    for path in sorted(p for p in app.rglob("*") if p.is_file()):
        relative = path.relative_to(app).as_posix()
        if relative in {"eboot.bin", "sce_sys/param.sfo", "spdw-stage-manifest.json"}:
            continue
        if "=" in str(path) or "=" in relative or "\n" in str(path) or "\n" in relative:
            raise StageError(f"file path cannot be represented safely in vita-pack-vpk arguments: {path}")
        payload.append((path, relative))

    command = [packer, "--sfo", str(sfo), "--eboot", str(eboot)]
    for source, destination in payload:
        command.extend(["--add", f"{source}={destination}"])
    command.append(str(target))
    command_size = sum(len(arg) + 1 for arg in command)
    if command_size > MAX_COMMAND_CHARS:
        raise StageError(
            f"package has too many/long file paths for a safe command line ({command_size} chars); "
            "reduce path lengths or package a smaller staged set"
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            command,
            cwd=app,
            check=False,
            capture_output=True,
            text=True,
            timeout=300,
            shell=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "no diagnostic output").strip()
            raise StageError(f"vita-pack-vpk failed with exit code {result.returncode}: {detail[-2000:]}")
        if not target.is_file() or target.stat().st_size == 0:
            raise StageError("vita-pack-vpk returned success but did not create a non-empty output")
        try:
            with zipfile.ZipFile(target) as archive:
                corrupt_entry = archive.testzip()
                if corrupt_entry is not None:
                    raise StageError(f"VPK archive CRC check failed at {corrupt_entry}")
                names = set(archive.namelist())
        except (OSError, zipfile.BadZipFile) as exc:
            raise StageError(f"vita-pack-vpk output is not a readable VPK/ZIP archive: {exc}") from exc

        required = {"eboot.bin", "sce_sys/param.sfo"}
        expected = required | {relative for _source, relative in payload}
        missing = sorted(expected - names)
        if missing:
            raise StageError("VPK is missing expected entries: " + ", ".join(missing[:20]))
        return {
            "output": str(target),
            "title_id": title_id,
            "size_bytes": target.stat().st_size,
            "entry_count": len(names),
            "payload_files_added": len(payload),
            "verified_entries": len(expected),
            "tool": packer,
            "limitations": [
                "The VPK was created by the external VitaSDK tool; this command does not build eboot.bin.",
                "Archive structure was checked, but installation and runtime execution on a physical Vita were not tested.",
            ],
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        if target.exists():
            target.unlink()
        raise StageError(f"VPK packaging could not complete: {exc}") from exc
    except Exception:
        if target.exists():
            target.unlink()
        raise
