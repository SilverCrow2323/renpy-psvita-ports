"""End-to-end build pipeline: original game + managed runtime + generated LiveArea -> VPK."""
from __future__ import annotations
import hashlib,json,shutil,tempfile
from pathlib import Path
from .livearea import generate_livearea,write_param_sfo,validate_app_metadata,LiveAreaError
from .package import build_vpk
from .project_source import resolve_game_directory
from .runtime_manager import ensure_runtime

class BuildError(ValueError): pass

def _copy_runtime_payload(runtime_root: Path,app_root: Path) -> None:
    if not (runtime_root/"eboot.bin").is_file(): raise BuildError("Selected runtime is incomplete: eboot.bin is missing")
    for item in runtime_root.iterdir():
        if item.name in {"game","sce_sys","eboot.bin"}: continue
        target=app_root/item.name
        if item.is_dir(): shutil.copytree(item,target,symlinks=False,dirs_exist_ok=True)
        elif item.is_file(): shutil.copy2(item,target)
    shutil.copy2(runtime_root/"eboot.bin",app_root/"eboot.bin")
    runtime_sce=runtime_root/"sce_sys"
    if runtime_sce.is_dir(): shutil.copytree(runtime_sce,app_root/"sce_sys",symlinks=False,dirs_exist_ok=True)

def _sha256_file(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""): digest.update(chunk)
    return digest.hexdigest()

def build_game_vpk(selected_game_folder,runtime_id,title,title_id,output_vpk,artwork=None,progress=None,app_version="01.00") -> dict:
    _project_root,game_dir=resolve_game_directory(selected_game_folder)
    try:
        validate_app_metadata(title,title_id,app_version)
    except LiveAreaError as exc:
        raise BuildError(str(exc)) from exc
    output_input=Path(output_vpk).expanduser()
    if output_input.is_symlink():
        raise BuildError(f"Output path is a symbolic link; choose a regular file path: {output_input}")
    output=output_input.resolve()
    if output.suffix.lower()!=".vpk": raise BuildError("Output filename must end in .vpk")
    manifest_path=output.with_suffix(output.suffix+".json")
    checksum_path=output.with_suffix(output.suffix+".sha256")
    for candidate in (output,manifest_path,checksum_path):
        if candidate.exists() or candidate.is_symlink():
            raise BuildError(f"Output already exists; refusing to overwrite: {candidate}")
    if game_dir in output.parents: raise BuildError("Save the VPK outside the original game folder")
    runtime=ensure_runtime(runtime_id,progress=progress); runtime_root=Path(runtime["payload_path"])
    if progress: progress("Preparing Vita application…")
    with tempfile.TemporaryDirectory(prefix="renpy-vita-build-") as temp:
        app_root=Path(temp)/title_id; app_root.mkdir()
        _copy_runtime_payload(runtime_root,app_root)
        shutil.copytree(game_dir,app_root/"game",symlinks=False)
        sce_sys=app_root/"sce_sys"; sce_sys.mkdir(parents=True,exist_ok=True)
        write_param_sfo(sce_sys/"param.sfo",title,title_id,app_version)
        artwork_result=generate_livearea(sce_sys,title,artwork)
        if progress: progress("Creating and verifying VPK…")
        result=build_vpk(app_root,output); digest=_sha256_file(output)
        manifest={"format":"renpy-vita-studio-build-v1","title":title,"title_id":title_id,"app_version":app_version,
                  "runtime":runtime,"source_game_directory":str(game_dir),"copied_only_game_directory":True,
                  "artwork":artwork_result,"vpk":result,"sha256":digest}
        created_sidecars=[]
        try:
            with manifest_path.open("x",encoding="utf-8") as stream:
                stream.write(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
            created_sidecars.append(manifest_path)
            with checksum_path.open("x",encoding="ascii") as stream:
                stream.write(f"{digest}  {output.name}\n")
            created_sidecars.append(checksum_path)
        except Exception:
            for sidecar in created_sidecars:
                sidecar.unlink(missing_ok=True)
            output.unlink(missing_ok=True)
            raise
        return {"vpk":result,"manifest":str(manifest_path),"sha256":digest,"checksum_file":str(checksum_path),"artwork":artwork_result}
