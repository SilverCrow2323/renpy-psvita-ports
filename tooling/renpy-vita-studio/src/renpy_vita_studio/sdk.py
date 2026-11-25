"""VitaSDK discovery shared by the GUI, CLI, diagnostics and packager."""
from __future__ import annotations
import os, shutil
from pathlib import Path

def configure_vitasdk_path() -> str | None:
    """Find VitaSDK even when an XFCE launcher has not loaded shell profiles."""
    candidates=[]
    configured=os.environ.get("VITASDK","").strip()
    if configured: candidates.append(Path(configured).expanduser())
    candidates.extend((Path("/usr/local/vitasdk"),Path("/opt/vitasdk"),Path.home()/"vitasdk"))
    seen=set()
    for root in candidates:
        try: resolved=root.resolve()
        except OSError: continue
        if str(resolved) in seen: continue
        seen.add(str(resolved)); bindir=resolved/"bin"
        if bindir.is_dir():
            os.environ.setdefault("VITASDK",str(resolved))
            entries=os.environ.get("PATH","").split(os.pathsep)
            if str(bindir) not in entries: os.environ["PATH"]=str(bindir)+os.pathsep+os.environ.get("PATH","")
            return str(resolved)
    return None

def find_vitasdk_tool(name: str) -> str | None:
    configure_vitasdk_path()
    found=shutil.which(name)
    if found: return found
    root=os.environ.get("VITASDK","").strip()
    if root:
        candidate=Path(root).expanduser()/"bin"/name
        if candidate.is_file() and os.access(candidate,os.X_OK): return str(candidate)
    return None
