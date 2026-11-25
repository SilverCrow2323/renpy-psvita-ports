"""Pinned, human-readable Ren'Py Vita runtime catalogue."""
from __future__ import annotations

RUNTIMES = {
    "renpy7-legacy": {
        "name": "Ren'Py Vita 7 — Legacy (SonicMastr)",
        "engine": "Ren'Py 7 generation · Python 2.7",
        "url": "https://github.com/SonicMastr/renpy-vita/releases/download/v1.0/Ren.Py.PSVita.Distribution.Tool.zip",
        "sha256": None,
        "archive": "zip",
        "description": "The historical runtime. It is the first profile to try for older Ren'Py projects and ports already tested on this base. It uses Python 2.7 and is a legacy platform; modern features and video playback should not be expected.",
        "warning": "2021 upstream archive. Studio records its SHA-256 on download, but the release does not publish a digest that can be independently verified.",
        "source": "https://github.com/SonicMastr/renpy-vita/releases/tag/v1.0",
    },
    "renpy8-pvr": {
        "name": "Ren'Py Vita 8 — PVR (Grimiku v0.2.1)",
        "engine": "Ren'Py 8 · Python 3.11 · PVR_PSP2",
        "url": "https://github.com/Grimiku/RenPy-Vita-8/releases/download/v0.2.1/RenPy_Vita_8_v0.2.1_PVR.zip",
        "sha256": "139a48dbcf7c8766a0ba7ada4e7db12a52d45b7600ce211f1b7c7ff15b16826d",
        "archive": "zip",
        "description": "Ren'Py 8 runtime using the PVR_PSP2 backend. Recommended as the first profile to try with Ren'Py 8 games: this is the standalone PVR build and does not have VitaGL's SHACCCG requirement.",
        "warning": "Game compatibility still needs to be checked. A Ren'Py 8 runtime does not automatically make unsupported scripts, native modules or engine features compatible.",
        "source": "https://github.com/Grimiku/RenPy-Vita-8/releases/tag/v0.2.1",
    },
    "renpy8-vgl": {
        "name": "Ren'Py Vita 8 — VitaGL (Grimiku v0.2.1)",
        "engine": "Ren'Py 8 · Python 3.11 · VitaGL",
        "url": "https://github.com/Grimiku/RenPy-Vita-8/releases/download/v0.2.1/RenPy_Vita_8_v0.2.1_VGL.zip",
        "sha256": "742e9708c6132f76c93a0a96b9f894319709e5fa1bc01d2db1fd319ba41c6b76",
        "archive": "zip",
        "description": "Ren'Py 8 variant using the VitaGL graphics backend, intended as an alternative graphics path. It may be useful when experimenting with newer games.",
        "warning": "Upstream describes this build as experimental, potentially slower and more prone to glitches. It requires libshacccg.suprx in ur0:/data/ on the PS Vita.",
        "source": "https://github.com/Grimiku/RenPy-Vita-8/releases/tag/v0.2.1",
    },
}

def list_runtimes() -> list[dict]:
    return [{"runtime_id": key, **value} for key, value in RUNTIMES.items()]
