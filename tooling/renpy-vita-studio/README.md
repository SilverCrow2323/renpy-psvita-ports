# Ren'Py Vita Studio

SPDW Factory · Linux / Windows · Python 3.11+

A guided desktop workflow that starts from the original Ren'Py project folder and produces a PlayStation Vita VPK. Studio packages the selected game's game/ directory with a chosen prebuilt Vita runtime; it is not a universal compatibility converter.

## Guided workflow

1. GAME — select the original game folder (the folder containing game/) or select game/ itself. Studio inventories the project and runs a conservative compatibility preflight.
2. RUNTIME — choose one of the managed runtime profiles. Studio downloads and caches the profiles locally, with transfer progress and retry support.
3. LIVEAREA — enter the game title, Vita Title ID and app version. Choose separate artwork for bubble icon, boot screen, LiveArea background and startup artwork, or use generated title cards.
4. BUILD VPK — Studio combines runtime + game + generated Vita metadata, calls VitaSDK's vita-pack-vpk, checks archive CRCs and required entries, and writes a JSON build report and SHA-256 sidecar.

## Runtime choices

| Profile | Engine / backend | What it means |
|---|---|---|
| Ren'Py Vita 7 Legacy | SonicMastr · Python 2.7 | Historical runtime for older Ren'Py projects. |
| Ren'Py Vita 8 PVR 0.2.1 | Grimiku · Python 3.11 · PVR_PSP2 | Recommended first attempt for Ren'Py 8. |
| Ren'Py Vita 8 VitaGL 0.2.1 | Grimiku · Python 3.11 · VitaGL | Alternative experimental graphics backend; requires libshacccg.suprx on the console. |

## Debian installation and dependencies

The .deb declares its system requirements in Debian's Depends metadata (Python 3.11+, Tkinter and Pillow). Install it through APT so missing packages are resolved and installed automatically:

    sudo apt install ./renpy-vita-studio_VERSION_all.deb

Do not use dpkg -i when you want automatic dependency resolution: dpkg alone reports missing dependencies but does not download them. If you already used dpkg -i, run sudo apt --fix-broken install.

VitaSDK is deliberately not bundled or silently installed by the Debian package. It is a separate toolchain. Studio automatically checks VITASDK/bin, /usr/local/vitasdk/bin, /opt/vitasdk/bin and ~/vitasdk/bin, then adds the detected bin directory to its own PATH. This also works when Studio is launched from the XFCE application menu without inheriting the terminal's shell PATH.

Build the Debian package:

    cd tooling/renpy-vita-studio
    bash packaging/linux/build-deb.sh

## CLI

    renpy-vita-studio --help
    renpy-vita-studio inspect "/path/to/original-game" --json
    renpy-vita-studio doctor
    renpy-vita-studio profiles
    renpy-vita-studio build-plan

## Compatibility and validation

The preflight reports Ren'Py engine fingerprints, video files, native libraries, archives and other compatibility hints. It does not execute game code or guarantee that the selected runtime can run the game. Video playback, native desktop libraries, custom/encrypted archive variants and RPYC decompilation may require manual work.

Studio never edits the original game directory, rejects symlinks inside game/, and refuses to overwrite an existing VPK. A successful build verifies the archive structure and CRCs; it does not prove installation or execution on a physical PS Vita. Device testing remains a separate required step.

## Development

    python -m pip install -e .
    PYTHONPATH=src python -m unittest discover -s tests -v
