"""Evidence-based runtime profile hints; these are candidates, not compatibility claims."""

from __future__ import annotations

PROFILES = {
    "sonicmastr-python27": {
        "name": "SonicMastr Ren'Py Vita (legacy)",
        "python": "2.7",
        "engine_generation": "Ren'Py 7-era / legacy",
        "source": "https://github.com/SonicMastr/renpy-vita",
        "build_host": ["Linux", "WSL"],
        "requirements": [
            "VitaSDK",
            "Python 2.7.18",
            "Cython and the upstream static-module build steps",
            "SDL2 built with VIDEO_VITA_PVR=ON",
            "the legacy Python 2.7 Vita libraries and stubs described upstream",
        ],
        "notes": [
            "The upstream CMake target links python2.7 and builds eboot.bin.",
            "The public README documents video playback as unsupported.",
            "The upstream project and dependencies are legacy; this is a reference adapter target, not a recommended universal runtime.",
        ],
    },
    "grimiku-python311": {
        "name": "Grimiku RenPy-Vita-8",
        "python": "3.11",
        "engine_generation": "Ren'Py 8",
        "source": "https://github.com/Grimiku/RenPy-Vita-8",
        "build_host": ["Linux", "WSL"],
        "requirements": [
            "VitaSDK",
            "Python 3.11",
            "Cython 0.29.37 (upstream reports incompatibility with Cython 3.x)",
            "SDL2 built with VIDEO_VITA_PVR=ON",
            "the upstream CPython 3.11 Vita modifications and additional libraries",
            "rsync and 7-Zip for the upstream all-in-one build script",
        ],
        "notes": [
            "The upstream CMake target links python3.11 and builds eboot.bin.",
            "The upstream README says its feature baseline was updated through the end of 2024.",
            "VitaGL is an optional upstream branch/release with additional device-side requirements.",
        ],
    },
}


def assess_runtime_profile(
    engine_version: str | None,
    python_runtime_directories: list[str],
) -> dict:
    """Return conservative candidates using bundled Python folders as evidence."""
    python_versions = sorted({
        item.removeprefix("python")
        for item in python_runtime_directories
        if item.lower().startswith("python")
    })
    engine_major = None
    if engine_version:
        try:
            engine_major = int(engine_version.split(".", 1)[0])
        except (TypeError, ValueError):
            engine_major = None

    candidates = []
    if "2.7" in python_versions:
        if engine_major == 8:
            candidates.append({
                "profile_id": "sonicmastr-python27",
                "match": "conflicting-evidence",
                "confidence": "low",
                "evidence": [
                    "bundled lib/python2.7 runtime directory",
                    f"Ren'Py engine fingerprint {engine_version} is in the Ren'Py 8 generation",
                ],
            })
        else:
            candidates.append({
                "profile_id": "sonicmastr-python27",
                "match": "candidate",
                "confidence": "medium",
                "evidence": ["bundled lib/python2.7 runtime directory"],
            })

    if "3.11" in python_versions:
        if engine_major is not None and engine_major < 8:
            candidates.append({
                "profile_id": "grimiku-python311",
                "match": "conflicting-evidence",
                "confidence": "low",
                "evidence": [
                    "bundled lib/python3.11 runtime directory",
                    f"Ren'Py engine fingerprint {engine_version} is older than the Ren'Py 8 generation",
                ],
            })
        else:
            evidence = ["bundled lib/python3.11 runtime directory"]
            confidence = "medium"
            if engine_major == 8:
                confidence = "strong-indicator"
                evidence.append(f"Ren'Py engine fingerprint {engine_version} is in the Ren'Py 8 generation")
            candidates.append({
                "profile_id": "grimiku-python311",
                "match": "candidate",
                "confidence": confidence,
                "evidence": evidence,
            })

    if len(candidates) > 1:
        assessment = "ambiguous"
    elif candidates and candidates[0]["match"] == "conflicting-evidence":
        assessment = "conflict"
    elif candidates:
        assessment = "candidate"
    elif engine_major == 8:
        assessment = "unmatched"
    else:
        assessment = "unknown"

    return {
        "assessment": assessment,
        "engine_major": engine_major,
        "bundled_python_versions": python_versions,
        "candidates": candidates,
        "warning": "A profile match is a research/build-target hint, not proof that a game is compatible or that the runtime can be built from the supplied project.",
    }


def list_runtime_profiles() -> list[dict]:
    """Return serializable profile summaries for the CLI."""
    return [
        {"profile_id": profile_id, **profile}
        for profile_id, profile in PROFILES.items()
    ]
