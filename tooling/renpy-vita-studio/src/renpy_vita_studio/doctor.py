"""Read-only host and VitaSDK toolchain diagnostics."""
from __future__ import annotations
import os, platform, shutil, sys
from .sdk import configure_vitasdk_path, find_vitasdk_tool
TOOL_CANDIDATES={"cmake":("cmake",),"make":("make","gmake"),"ninja":("ninja",),"vita_cc":("arm-vita-eabi-gcc",),"vita_cxx":("arm-vita-eabi-g++",),"vita_pack_vpk":("vita-pack-vpk",),"vita_mksfoex":("vita-mksfoex",),"vita_make_fself":("vita-make-fself",),"vita_elf_create":("vita-elf-create",),"python27":("python2.7","python2"),"python311":("python3.11",),"cython":("cython",),"rsync":("rsync",),"seven_zip":("7z","7zz"),"zip":("zip",)}
VITA_TOOLS={"vita_cc","vita_cxx","vita_pack_vpk","vita_mksfoex","vita_make_fself","vita_elf_create"}
def inspect_environment() -> dict:
    sdk_root=configure_vitasdk_path(); tools={}
    for key,candidates in TOOL_CANDIDATES.items():
        finder=find_vitasdk_tool if key in VITA_TOOLS else shutil.which
        found=next((finder(name) for name in candidates if finder(name)),None)
        tools[key]={"available":found is not None,"path":found}
    vita_sdk=os.environ.get("VITASDK"); valid=bool(sdk_root and os.path.isdir(sdk_root))
    compilers=tools["vita_cc"]["available"] and tools["vita_cxx"]["available"]
    packaging=tools["vita_pack_vpk"]["available"] and tools["vita_mksfoex"]["available"]
    build=tools["cmake"]["available"] and tools["make"]["available"]
    status="core-tools-detected" if valid and compilers and packaging and build else ("partial" if vita_sdk or compilers or packaging else "not-detected")
    return {"host":{"system":platform.system(),"release":platform.release(),"machine":platform.machine(),"python":platform.python_version(),"python_executable":sys.executable},"vita_sdk":{"environment_variable_set":bool(vita_sdk),"path":sdk_root or vita_sdk,"path_exists":valid,"status":status},"tools":tools,"notes":["VitaSDK discovery checks VITASDK, /usr/local/vitasdk, /opt/vitasdk and ~/vitasdk, and adds the detected bin directory to this process PATH.","This check only locates tools; it does not run compilers, configure projects or build packages.","Detected executables and a VITASDK path do not prove that a complete SDK, all libraries or a compatible runtime build environment are installed."]}
