"""Vita VPK packaging for a staged app with a runtime-built eboot.bin."""
from __future__ import annotations
import re,subprocess,zipfile
from pathlib import Path
from .stage import StageError,_read_sfo,_reject_symlinks
from .sdk import find_vitasdk_tool
MAX_COMMAND_CHARS=24_000
def _safe_add_arg(source: Path,destination: str) -> list[str]:
    if "=" in str(source) or "=" in destination or "\n" in str(source) or "\n" in destination: raise StageError(f"file path cannot be represented safely in vita-pack-vpk arguments: {source}")
    return ["--add",f"{source}={destination}"]
def build_vpk(staged_app: str | Path,output: str | Path) -> dict:
    app=Path(staged_app).expanduser().resolve(); target_input=Path(output).expanduser()
    if target_input.is_symlink(): raise StageError(f"output path is a symbolic link: {target_input}")
    target=target_input.resolve()
    if not app.is_dir(): raise StageError(f"staged app directory does not exist: {app}")
    title_id=app.name
    if not re.fullmatch(r"[A-Z0-9]{9}",title_id): raise StageError("staged app folder must use a 9-character uppercase alphanumeric title ID")
    if target.suffix.lower()!=".vpk": raise StageError("output filename must use the .vpk extension")
    if target.exists() or target.is_symlink(): raise StageError(f"output already exists; refusing to overwrite: {target}")
    if target in app.parents or app in target.parents: raise StageError("VPK output and staged app must be separate paths")
    eboot=app/"eboot.bin"; sfo=app/"sce_sys"/"param.sfo"
    if not eboot.is_file(): raise StageError("staged app is missing eboot.bin; build it with a compatible Vita runtime first")
    if not sfo.is_file(): raise StageError("staged app is missing sce_sys/param.sfo")
    _reject_symlinks(app); _size,fields=_read_sfo(sfo)
    if fields.get("TITLE_ID")!=title_id: raise StageError("staged app folder title ID does not match sce_sys/param.sfo")
    packer=find_vitasdk_tool("vita-pack-vpk")
    if not packer: raise StageError("vita-pack-vpk was not found. Studio checked VITASDK/bin, /usr/local/vitasdk/bin, /opt/vitasdk/bin and ~/vitasdk/bin; install VitaSDK or configure VITASDK.")
    payload=sorted(p for p in app.rglob("*") if p.is_file() and p not in {eboot,sfo} and p.name!="spdw-stage-manifest.json"); args=[]
    for item in sorted(app.iterdir()):
        if item.name not in {"eboot.bin","sce_sys","spdw-stage-manifest.json"}: args.extend(_safe_add_arg(item,item.name))
    for item in sorted((app/"sce_sys").iterdir()):
        if item.name!="param.sfo": args.extend(_safe_add_arg(item,f"sce_sys/{item.name}"))
    command=[packer,"--sfo",str(sfo),"--eboot",str(eboot),*args,str(target)]; size=sum(len(x)+1 for x in command)
    if size>MAX_COMMAND_CHARS: raise StageError(f"package has too many/long top-level paths for a safe command line ({size} chars)")
    target.parent.mkdir(parents=True,exist_ok=True)
    try:
        result=subprocess.run(command,cwd=app,check=False,capture_output=True,text=True,timeout=900,shell=False)
        if result.returncode: raise StageError(f"vita-pack-vpk failed with exit code {result.returncode}: {(result.stderr or result.stdout or 'no diagnostic output').strip()[-2000:]}")
        if not target.is_file() or not target.stat().st_size: raise StageError("vita-pack-vpk returned success but did not create a non-empty output")
        try:
            with zipfile.ZipFile(target) as archive:
                corrupt=archive.testzip()
                if corrupt is not None: raise StageError(f"VPK archive CRC check failed at {corrupt}")
                names=set(archive.namelist())
        except (OSError,zipfile.BadZipFile) as exc: raise StageError(f"vita-pack-vpk output is not a readable VPK/ZIP archive: {exc}") from exc
        expected={"eboot.bin","sce_sys/param.sfo"}|{p.relative_to(app).as_posix() for p in payload}; missing=sorted(expected-names)
        if missing: raise StageError("VPK is missing expected entries: "+", ".join(missing[:20]))
        return {"output":str(target),"title_id":title_id,"size_bytes":target.stat().st_size,"entry_count":len(names),"payload_files_added":len(payload),"verified_entries":len(expected),"tool":packer,"limitations":["VPK archive structure and CRCs were checked; installation and execution on a physical Vita were not tested."]}
    except (OSError,subprocess.TimeoutExpired) as exc:
        target.unlink(missing_ok=True); raise StageError(f"VPK packaging could not complete: {exc}") from exc
    except Exception:
        target.unlink(missing_ok=True); raise
