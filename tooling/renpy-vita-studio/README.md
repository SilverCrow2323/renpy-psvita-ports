# Ren'Py Vita Studio — core preview

<sub>SPDW Factory · Windows / Linux · Python 3.11+</sub>

A cautious inspection and preparation core for user-supplied Ren'Py projects targeting PlayStation Vita.

> **Alpha foundation, not a one-click port converter.** This tool inventories projects, reads standard RPA-2.0 / RPA-3.0 archives and prepares a non-destructive Vita app staging folder. It does not patch games, build or adapt a Ren'Py runtime, or promise compatibility. It can package an already-built Vita `eboot.bin` when VitaSDK's VPK tool is available.

## Current capabilities

- Read-only project inventory: \`game/\`, scripts, RPA archives, media, native libraries, Python runtime directories and Vita LiveArea assets.
- Reads \`game/options.rpy\` without executing it. Game version and Ren'Py engine version are kept separate.
- Fingerprints modern engine versions from \`renpy/vc_version.py\` and legacy versions from a literal \`version_tuple\`; confidence and evidence are reported.
- Lists and extracts standard RPA-2.0 and RPA-3.0 archives.
- Uses a restricted pickle unpickler, bounded decompression, path-traversal checks, extraction size limits and fresh-directory extraction.
- Read-only \`doctor\` report for host OS, Python, CMake/build tools, VitaSDK environment and Vita cross-compiler discovery. It never runs compilers or modifies the host.
- **Staging preview:** copies \`game/\` and \`sce_sys/\` into \`app/<TITLE_ID>/\`, parses bounded PSF metadata, checks that `TITLE_ID` matches the requested ID and checks PNG headers/dimensions, reports LiveArea assets, rejects symlinks and refuses to overwrite an existing target.
- Carries through an optional runtime-built `eboot.bin` and writes a SHA-256 manifest for the staged payload.
- **VPK packaging preview:** invokes VitaSDK `vita-pack-vpk` without a shell, refuses overwrite, and checks the VPK CRC and verifies the expected archive entries.

## Requirements

- Python 3.11 or newer
- Windows 10/11 or a maintained Linux distribution
- No third-party runtime dependencies for the current core

## Run from source

\`\`\`sh
cd tooling/renpy-vita-studio
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux:   source .venv/bin/activate
python -m pip install -e .
renpy-vita-studio --help
renpy-vita-studio doctor
\`\`\`

## Examples

\`\`\`sh
# Inventory a project
renpy-vita-studio inspect "/path/to/Game" --json

# Inspect/extract a standard archive
renpy-vita-studio rpa list "/path/to/Game/game/archive.rpa" --json
renpy-vita-studio rpa extract "/path/to/Game/game/archive.rpa" "./rpa-extract"

# Prepare a Vita app folder (copies eboot.bin too if the runtime build supplied it)
renpy-vita-studio stage "/path/to/Game" "./vita-output" --title-id PCSE00001

# Package only after a compatible runtime has produced eboot.bin
renpy-vita-studio vpk "./vita-output/app/PCSE00001" "./release/Game.vpk"
\`\`\`

The staging command expects a project root containing both \`game/\` and \`sce_sys/\`, including \`sce_sys/param.sfo\` and \`sce_sys/icon0.png\`. It creates \`vita-output/app/PCSE00001/\`. Supply the correct title ID and metadata yourself; the tool does not invent or rewrite them.

## Safety boundaries

- Only standard RPA-2.0 and RPA-3.0 are supported in this preview.
- Custom/encrypted archive variants and RPA-1.0 / standalone RPI are not supported.
- RPYC files are inventoried but never unpickled or decompiled.
- The inspector does not execute \`options.rpy\` or other game code.
- Staging refuses to overwrite an existing \`app/<TITLE_ID>\` and never edits the source project.
- \`param.sfo\` is checked for a PSF header only; fields are not parsed or rewritten.
- PNG checks validate the header and dimensions, not full image decoding or Vita-specific size requirements. LiveArea assets are reported, not checked against a device-specific artwork profile.
- The manifest hashes staged payload files; it is not a signature or compatibility certificate.
- No DRM bypass, decryption, game-data redistribution or proprietary payload bundling.
- The `vpk` command only wraps an already-built `eboot.bin` with VitaSDK's `vita-pack-vpk`; it does not compile or adapt the Ren'Py runtime, sign binaries, install the package or validate execution on a Vita.

## Development

\`\`\`sh
PYTHONPATH=src python -m unittest discover -s tests -v
\`\`\`

## Relationship to upstream

The native runtime baseline is [SonicMastr/renpy-vita](https://github.com/SonicMastr/renpy-vita). This core is a new SPDW Factory desktop-side tool, not a claim that the upstream Distribution Tool source was available or directly refactored. Runtime adapters for the legacy Python 2.7 port and the community Python 3.11 Ren'Py Vita 8 port must remain separate until their licensing, APIs and build requirements are audited.

## Roadmap

1. Broaden archive fixtures and engine/runtime fingerprint coverage.
2. Expand LiveArea asset dimension checks and validate title metadata against runtime profiles.
3. Add explicit profile adapters for supported Vita runtimes.
4. Extend the VPK wrapper with reproducible build manifests and runtime build integration.
5. Desktop GUI and optional USB/network device integration.
6. Evaluate a Vita-side companion only for tasks that fit Vita memory and native APIs.
