"""First-run runtime downloads with digest checks and safe ZIP extraction."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import threading
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

from .runtime_catalog import RUNTIMES

MAX_RUNTIME_BYTES = 300 * 1024 * 1024
MAX_EXTRACTED_BYTES = 700 * 1024 * 1024
MAX_ARCHIVE_ENTRIES = 100_000

class RuntimeError(ValueError):
    pass

def runtime_cache_dir() -> Path:
    base = os.environ.get("XDG_DATA_HOME")
    root = Path(base).expanduser() if base else Path.home() / ".local" / "share"
    return root / "renpy-vita-studio" / "runtimes"

def _safe_member(name: str) -> PurePosixPath:
    path = PurePosixPath(name.replace("\\", "/"))
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise RuntimeError(f"Unsafe path in runtime archive: {name}")
    if path.parts and ":" in path.parts[0]:
        raise RuntimeError(f"Drive path in runtime archive: {name}")
    return path

def _download(url: str, destination: Path) -> str:
    digest = hashlib.sha256()
    total = 0
    request = urllib.request.Request(url, headers={"User-Agent": "RenPy-Vita-Studio/0.2"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response, destination.open("wb") as out:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_RUNTIME_BYTES:
                    raise RuntimeError("Runtime download exceeds the 300 MiB safety limit")
                digest.update(chunk)
                out.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    if total == 0:
        destination.unlink(missing_ok=True)
        raise RuntimeError("The runtime download is empty")
    return digest.hexdigest()

def _extract_safe(archive_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    total = 0
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        if len(infos) > MAX_ARCHIVE_ENTRIES:
            raise RuntimeError("Runtime archive contains too many entries")
        for info in infos:
            member = _safe_member(info.filename)
            mode = (info.external_attr >> 16) & 0xFFFF
            if mode and (mode & 0o170000) == 0o120000:
                raise RuntimeError(f"Symbolic link in runtime archive: {info.filename}")
            total += info.file_size
            if total > MAX_EXTRACTED_BYTES:
                raise RuntimeError("Expanded runtime exceeds the 700 MiB safety limit")
            target = destination.joinpath(*member.parts)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as source, target.open("xb") as out:
                shutil.copyfileobj(source, out, length=1024 * 1024)

def _find_runtime_root(extracted: Path) -> Path:
    candidates = [p.parent for p in extracted.rglob("eboot.bin") if p.is_file()]
    if not candidates:
        raise RuntimeError("The downloaded archive does not contain eboot.bin; it is not a usable Vita runtime package")
    # Prefer the shallowest eboot root to avoid selecting a nested example/template.
    return min(candidates, key=lambda p: len(p.parts))

def _ensure_runtime_unlocked(runtime_id: str, progress=None) -> dict:
    if runtime_id not in RUNTIMES:
        raise RuntimeError(f"Unknown runtime profile: {runtime_id}")
    profile = RUNTIMES[runtime_id]
    cache = runtime_cache_dir() / runtime_id
    marker = cache / "runtime-install.json"
    if marker.is_file() and (cache / "payload" / "eboot.bin").is_file():
        try:
            data = json.loads(marker.read_text(encoding="utf-8"))
            data["payload_path"] = str(cache / "payload")
            return data
        except (OSError, json.JSONDecodeError):
            pass

    cache.parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=f".{runtime_id}-", dir=cache.parent))
    try:
        archive_path = work / "runtime.zip"
        if progress:
            progress("Downloading runtime archive…")
        digest = _download(profile["url"], archive_path)
        expected = profile.get("sha256")
        if expected and digest.lower() != expected.lower():
            raise RuntimeError(f"Runtime SHA-256 mismatch: expected {expected}, received {digest}")
        extracted = work / "extracted"
        if progress:
            progress("Checking and extracting runtime…")
        _extract_safe(archive_path, extracted)
        runtime_root = _find_runtime_root(extracted)
        payload = work / "payload"
        shutil.copytree(runtime_root, payload, symlinks=False)
        if not (payload / "eboot.bin").is_file():
            raise RuntimeError("Runtime extraction did not produce eboot.bin")
        metadata = {
            "runtime_id": runtime_id,
            "name": profile["name"],
            "source": profile["source"],
            "download_url": profile["url"],
            "sha256": digest,
            "sha256_upstream_pinned": bool(expected),
            "payload_root": "payload",
        }
        if cache.exists():
            shutil.rmtree(cache)
        cache.mkdir(parents=True)
        shutil.copytree(payload, cache / "payload")
        (cache / "runtime-install.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        return {**metadata, "payload_path": str(cache / "payload")}
    finally:
        shutil.rmtree(work, ignore_errors=True)


_RUNTIME_LOCKS: dict[str, threading.Lock] = {}
_RUNTIME_LOCKS_GUARD = threading.Lock()

def ensure_runtime(runtime_id: str, progress=None) -> dict:
    # First-run prefetch and a simultaneous VPK build must not replace the same cache at once.
    with _RUNTIME_LOCKS_GUARD:
        lock = _RUNTIME_LOCKS.setdefault(runtime_id, threading.Lock())
    with lock:
        return _ensure_runtime_unlocked(runtime_id, progress)

def get_installed_runtime(runtime_id: str) -> dict | None:
    cache = runtime_cache_dir() / runtime_id
    marker = cache / "runtime-install.json"
    payload = cache / "payload"
    if not marker.is_file() or not (payload / "eboot.bin").is_file():
        return None
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
        data["payload_path"] = str(payload)
        return data
    except (OSError, json.JSONDecodeError):
        return None
