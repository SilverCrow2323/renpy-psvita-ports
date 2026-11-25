"""Pinned, human-readable Ren'Py Vita runtime catalogue."""
from __future__ import annotations

RUNTIMES = {
    "renpy7-legacy": {
        "name": "Ren'Py Vita 7 — Legacy (SonicMastr)",
        "engine": "Ren'Py 7 generation · Python 2.7",
        "url": "https://github.com/SonicMastr/renpy-vita/releases/download/v1.0/Ren.Py.PSVita.Distribution.Tool.zip",
        "sha256": None,
        "archive": "zip",
        "description": "Il runtime storico. È la scelta da provare per progetti Ren'Py più vecchi e port già testati su questa base. Usa Python 2.7 ed è una piattaforma legacy: non aspettarti supporto per funzioni moderne o video.",
        "warning": "Archivio upstream del 2021: il tool ne registra l'hash al primo download, ma il rilascio non pubblica un digest SHA-256 verificabile.",
        "source": "https://github.com/SonicMastr/renpy-vita/releases/tag/v1.0",
    },
    "renpy8-pvr": {
        "name": "Ren'Py Vita 8 — PVR (Grimiku v0.2.1)",
        "engine": "Ren'Py 8 · Python 3.11 · PVR_PSP2",
        "url": "https://github.com/Grimiku/RenPy-Vita-8/releases/download/v0.2.1/RenPy_Vita_8_v0.2.1_PVR.zip",
        "sha256": "139a48dbcf7c8766a0ba7ada4e7db12a52d45b7600ce211f1b7c7ff15b16826d",
        "archive": "zip",
        "description": "Runtime Ren'Py 8 con backend PVR_PSP2. È la scelta consigliata come prima prova per i giochi Ren'Py 8: versione PVR autonoma, senza il requisito SHACCCG di VitaGL.",
        "warning": "La compatibilità del gioco va comunque verificata: un runtime 8 non rende automaticamente compatibili script, moduli nativi o funzioni non supportate.",
        "source": "https://github.com/Grimiku/RenPy-Vita-8/releases/tag/v0.2.1",
    },
    "renpy8-vgl": {
        "name": "Ren'Py Vita 8 — VitaGL (Grimiku v0.2.1)",
        "engine": "Ren'Py 8 · Python 3.11 · VitaGL",
        "url": "https://github.com/Grimiku/RenPy-Vita-8/releases/download/v0.2.1/RenPy_Vita_8_v0.2.1_VGL.zip",
        "sha256": "742e9708c6132f76c93a0a96b9f894319709e5fa1bc01d2db1fd319ba41c6b76",
        "archive": "zip",
        "description": "Variante Ren'Py 8 con backend VitaGL, pensata come percorso grafico alternativo e più aggiornabile. Può essere utile per sperimentare con giochi moderni.",
        "warning": "Upstream la descrive come ancora acerba, potenzialmente più lenta e più soggetta a glitch. Richiede libshacccg.suprx in ur0:/data/ sulla PS Vita.",
        "source": "https://github.com/Grimiku/RenPy-Vita-8/releases/tag/v0.2.1",
    },
}

def list_runtimes() -> list[dict]:
    return [{"runtime_id": key, **value} for key, value in RUNTIMES.items()]
