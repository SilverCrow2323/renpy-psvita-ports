"""Read-only host and VitaSDK toolchain diagnostics."""

from __future__ import annotations

import os
import platform
import shutil
import sys

TOOL_CANDIDATES = {
    "cmake": ("cmake",),
    "make": ("make", "gmake"),
    "ninja": ("ninja",),
    "vita_cc": ("arm-vita-eabi-gcc",),
    "vita_cxx": ("arm-vita-eabi-g++",),
    "vita_pack_vpk": ("vita-pack-vpk",),
    "zip": ("7z", "7zz", "zip"),
}


def inspect_environment() -> dict:
    """Report available tools without invoking compilers or changing the host."""
    tools = {}
    for key, candidates in TOOL_CANDIDATES.items():
        found = next((shutil.which(candidate) for candidate in candidates if shutil.which(candidate)), None)
        tools[key] = {"available": found is not None, "path": found}

    vita_sdk = os.environ.get("VITASDK")
    compiler_ready = tools["vita_cc"]["available"] and tools["vita_cxx"]["available"]
    sdk_path_valid = bool(vita_sdk and os.path.isdir(os.path.expanduser(vita_sdk)))

    if sdk_path_valid and compiler_ready:
        vita_status = "toolchain-detected"
    elif vita_sdk or compiler_ready:
        vita_status = "partial"
    else:
        vita_status = "not-detected"

    return {
        "host": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "python_executable": sys.executable,
        },
        "vita_sdk": {
            "environment_variable_set": bool(vita_sdk),
            "path": vita_sdk,
            "path_exists": sdk_path_valid,
            "status": vita_status,
        },
        "tools": tools,
        "notes": [
            "This check only locates tools; it does not run compilers, configure projects or build packages.",
            "A detected compiler and VITASDK path do not prove that a complete or compatible VitaSDK is installed.",
            "VPK packaging is not implemented by this preview.",
        ],
    }
