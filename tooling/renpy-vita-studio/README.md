# Ren'Py Vita Studio

SPDW Factory · Linux / Windows · Python 3.11+

A guided desktop workflow that starts from the original Ren'Py project folder and produces a PlayStation Vita VPK. The user does not need to create an app/TITLE_ID folder, prepare sce_sys, supply a prebuilt LiveArea, or browse for a local runtime directory.

This is a practical porting and packaging assistant, not a universal compatibility converter. It packages the selected game's game/ directory with a chosen prebuilt Vita runtime. It does not patch game scripts, port native desktop libraries, or make unsupported Ren'Py features work on Vita.

## Guided workflow

1. GAME — select the original game folder (the folder containing game/) or select game/ itself. Studio inventories the project and runs a conservative compatibility preflight. It copies only game/; unrelated files, old Vita scaffolding, eboot.bin and sce_sys in the source folder are ignored.
2. RUNTIME — choose one of the managed runtime profiles. Studio downloads the selected runtime on first use, verifies its published digest where available, safely extracts it and caches it under the user's data directory.
3. LIVEAREA — enter the game title and Vita Title ID. Studio scans the game's own image assets and offers them in a drop-down. It can also use an external image or generate a simple title card. Artwork is cropped, resized, palette-optimized and written into a fresh sce_sys tree. A Vita-format param.sfo is generated automatically.
4. BUILD VPK — Studio combines runtime + game + generated Vita metadata, calls VitaSDK's vita-pack-vpk, checks archive CRCs and required entries, and writes a JSON build report and SHA-256 sidecar.

## Runtime choices

| Profile | Engine / backend | What it means |
|---|---|---|
| Ren'Py Vita 7 Legacy | SonicMastr · Python 2.7 | Historical runtime for older Ren'Py projects. Legacy dependencies and limited modern feature support. |
| Ren'Py Vita 8 PVR 0.2.1 | Grimiku · Python 3.11 · PVR_PSP2 | The recommended first attempt for Ren'Py 8. The PVR release is standalone. |
| Ren'Py Vita 8 VitaGL 0.2.1 | Grimiku · Python 3.11 · VitaGL | Alternative graphics backend, still experimental upstream; may be slower or glitchier and requires libshacccg.suprx under ur0:/data/ on the console. |

The two Ren'Py Vita 8 archives have upstream SHA-256 digests pinned in the runtime catalogue. The 2021 Ren'Py Vita 7 Distribution Tool archive does not publish a digest; Studio computes and records its SHA-256 after downloading it and clearly marks that it was not upstream-pinned. Runtime archives are cached in ~/.local/share/renpy-vita-studio/runtimes/ (or $XDG_DATA_HOME/renpy-vita-studio/runtimes/).

Downloads have size limits, ZIP path-traversal checks, symlink rejection and bounded extraction. Studio requires a usable eboot.bin in the downloaded runtime payload; an archive that does not contain one is rejected.

## Generated Vita files

- sce_sys/param.sfo — generated from the title, Title ID, app version and game category.
- sce_sys/icon0.png — 128×128 bubble icon.
- sce_sys/pic0.png — 960×544 launch image.
- sce_sys/livearea/contents/bg0.png — 840×500 LiveArea background.
- sce_sys/livearea/contents/startup.png — 280×158 startup image.
- sce_sys/livearea/contents/template.xml — basic a1 LiveArea layout referencing bg0.png and startup.png.

The images are encoded as compact indexed PNGs with per-asset size limits. The default Title ID generator creates a 4-letter + 5-digit Vita-format ID; the user can edit it. Avoid collisions with another installed app.

## Requirements

- Python 3.11 or newer.
- Tkinter (python3-tk on Debian/Ubuntu/MX Linux).
- Pillow (installed as a project dependency).
- VitaSDK installed and vita-pack-vpk available in PATH to create the VPK.

On MX Linux / Debian-based systems, install the GUI and packaging prerequisites:

    sudo apt install python3-tk
    cd tooling/renpy-vita-studio
    python3 -m venv .venv
    . .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -e .
    renpy-vita-studio-gui

CLI inspection and lower-level commands remain available:

    renpy-vita-studio --help
    renpy-vita-studio inspect "/path/to/original-game" --json
    renpy-vita-studio doctor
    renpy-vita-studio profiles
    renpy-vita-studio build-plan

## Compatibility preflight

The preflight reports evidence such as Ren'Py engine fingerprints, video files, native libraries, archives and other compatibility hints. It does not execute game code or guarantee that the selected runtime can run the game. In particular:
- Video playback is not generally supported by the referenced Vita runtimes.
- Native libraries compiled for Windows, Linux or desktop macOS are not Vita binaries.
- Custom/encrypted archive variants and RPYC decompilation are not handled.
- Game-specific script changes, screen/input adjustments, memory constraints and save compatibility may still require manual porting work.

Studio never edits the original game directory. It rejects symlinks inside game/ and refuses to overwrite an existing VPK.

## Validation boundaries

A successful build means the VPK tool created an archive and Studio verified its CRCs and expected entries. It does not mean the package has been installed or launched successfully on a physical PS Vita. VitaGL additionally requires the console-side SHACCCG module. Device testing remains a separate required step.

## Development

    python -m pip install -e .
    PYTHONPATH=src python -m unittest discover -s tests -v

The desktop GUI entry point is renpy-vita-studio-gui. The CLI entry point remains renpy-vita-studio.
