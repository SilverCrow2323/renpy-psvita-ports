"""Audited, non-executing build plans for the reference Vita runtimes."""

from __future__ import annotations

from .runtime_profiles import PROFILES

_BUILD_PLANS = {
    "sonicmastr-python27": {
        "execution_status": "documentation-only",
        "host_policy": "Linux or WSL; upstream instructions are shell-based.",
        "preflight": [
            {"item": "VitaSDK", "requirement": "Installed and VITASDK points to the SDK root", "verification": "manual"},
            {"item": "Python", "requirement": "CPython 2.7.18 available as python2", "verification": "command-presence-only"},
            {"item": "Cython", "requirement": "Upstream-required Cython; exact pin is not stated in the public README", "verification": "manual-version-review"},
            {"item": "Git", "requirement": "Available for submodules and source checkout", "verification": "manual"},
            {"item": "PVR_PSP2 assets", "requirement": "PSVita_Release.zip and vitasdk_stubs.zip from upstream PVR_PSP2 releases", "verification": "manual"},
            {"item": "SDL2", "requirement": "Source tree capable of building with VIDEO_VITA_PVR=ON", "verification": "manual"},
            {"item": "Python Future", "requirement": "Upstream-compatible files installed into the VitaSDK Python 2.7 library", "verification": "manual"},
        ],
        "phases": [
            {"name": "Prepare toolchain", "detail": "Install VitaSDK and review upstream PVR_PSP2 release assets, provenance and licensing."},
            {"name": "Prepare Python support", "detail": "Use CPython 2.7.18 and the Python Future compatibility files required by this legacy port."},
            {"name": "Build SDL2", "detail": "Configure SDL2 for the Vita toolchain with VIDEO_VITA_PVR=ON, then build and install it."},
            {"name": "Prepare RenPy sources", "detail": "Initialize submodules; build static RenPy modules and pygame_sdl2 against VitaSDK."},
            {"name": "Link Python libraries", "detail": "Review link_compile_pylibs.bash and link_sources.bash; run only in a disposable isolated workspace."},
            {"name": "Build Vita executable", "detail": "Configure the upstream CMake project with the Vita toolchain and inspect the resulting eboot.bin."},
        ],
        "manual_blockers": [
            "The upstream README does not pin every dependency to immutable commits or archive hashes.",
            "Cython version and exact SDL/PVR_PSP2 dependency revisions require manual verification.",
            "Legacy Python 2.7 and custom Vita libraries are not provisioned or patched by Studio.",
            "No scripts are executed, sources fetched, SDK files modified, binaries signed or games installed.",
        ],
        "source": PROFILES["sonicmastr-python27"]["source"],
    },
    "grimiku-python311": {
        "execution_status": "documentation-only",
        "host_policy": "Linux or WSL; upstream describes a shell-based build environment.",
        "preflight": [
            {"item": "VitaSDK", "requirement": "Installed and VITASDK points to the SDK root", "verification": "manual"},
            {"item": "Python", "requirement": "CPython 3.11", "verification": "command-presence-only"},
            {"item": "Cython", "requirement": "0.29.37; upstream reports incompatibility with Cython 3.x", "verification": "manual-version-review"},
            {"item": "rsync", "requirement": "Required by upstream build scripts", "verification": "command-presence-only"},
            {"item": "7-Zip", "requirement": "Required by upstream all-in-one build flow", "verification": "command-presence-only"},
            {"item": "SDL2", "requirement": "Built with VIDEO_VITA_PVR=ON", "verification": "manual"},
            {"item": "OpenSSL", "requirement": "OpenSSL 1.1.1 recognized by VitaSDK CMake configuration", "verification": "manual"},
            {"item": "CPython Vita fork", "requirement": "Vita-specific CPython 3.11 modifications and additional libraries", "verification": "manual"},
            {"item": "FreeType", "requirement": "VitaSDK FreeType package modified to build with HarfBuzz", "verification": "manual"},
        ],
        "phases": [
            {"name": "Prepare host", "detail": "Use Linux or WSL with Python 3.11, Cython 0.29.37, rsync and 7-Zip; do not substitute Cython 3.x."},
            {"name": "Prepare VitaSDK libraries", "detail": "Verify OpenSSL 1.1.1, Vita-specific CPython 3.11 changes, additional libraries and HarfBuzz-enabled FreeType."},
            {"name": "Build SDL2", "detail": "Build SDL2 with VIDEO_VITA_PVR=ON against the intended VitaSDK toolchain."},
            {"name": "Review upstream build scripts", "detail": "Audit all_in_one.bash and source revisions before running in isolation; upstream warns the script may fail."},
            {"name": "Build and inspect runtime", "detail": "Complete the upstream static Python/RenPy and native build sequence, then verify eboot.bin and runtime assets."},
        ],
        "manual_blockers": [
            "The README describes major requirements rather than a fully reproducible, pinned build recipe.",
            "CPython modifications, SDK package patches and external library revisions require a separate audit.",
            "The all-in-one script is not treated as a trusted unattended installer and is never executed by Studio.",
            "VitaGL is an optional separate path with additional device-side requirements; this plan targets PVR_PSP2.",
            "No scripts are executed, sources fetched, SDK files modified, binaries signed or games installed.",
        ],
        "source": PROFILES["grimiku-python311"]["source"],
    },
}

def _with_id(profile_id: str, plan: dict) -> dict:
    return {"profile_id": profile_id, **plan}


def get_build_plan(profile_id: str | None = None) -> dict:
    """Return a serializable build plan; never executes or downloads anything."""
    warning = "Plans are research checklists, not verified reproducible builds. No commands are executed and no dependencies are downloaded."
    if profile_id is None:
        return {
            "execution_status": "documentation-only",
            "warning": warning,
            "profiles": [_with_id(key, value) for key, value in _BUILD_PLANS.items()],
        }
    if profile_id not in _BUILD_PLANS:
        raise ValueError(f"unknown profile {profile_id!r}; choose one of: {', '.join(_BUILD_PLANS)}")
    return {
        "execution_status": "documentation-only",
        "warning": "This plan is not a compatibility verdict or reproducible build lockfile. Review upstream sources and dependency revisions before execution.",
        **_with_id(profile_id, _BUILD_PLANS[profile_id]),
    }
