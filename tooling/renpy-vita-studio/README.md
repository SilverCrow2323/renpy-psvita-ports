# Ren'Py Vita Studio — core preview

<sub>SPDW Factory · Windows / Linux · Python 3.11+</sub>

A cautious inspection and preparation core for user-supplied Ren'Py projects targeting PlayStation Vita.

<blockquote>
<strong>Alpha foundation, not a one-click port converter.</strong> This first slice inventories projects and reads standard RPA-2.0 / RPA-3.0 archives. It does not patch games, run Ren'Py, build VPKs or promise compatibility.
</blockquote>

## Current capabilities

- Read-only project inventory: `game/`, scripts, RPA archives, media, native libraries, Python runtime directories and Vita LiveArea assets.
- Extracts conservative metadata from `game/options.rpy` without executing the script. The game version is kept separate from the Ren'Py engine version.\n- Fingerprints the engine from literal metadata in `renpy/vc_version.py` (high confidence) or a legacy literal `version_tuple` in `renpy/__init__.py` (medium confidence). Unknown versions stay unknown; bundled Python folders are supporting evidence, not a version verdict.
- Detects video and native library files as compatibility hints.
- Lists and extracts standard RPA-2.0 and RPA-3.0 archives.
- Uses a restricted pickle unpickler, bounded index decompression, path-traversal checks, extraction size limits and fresh-directory extraction.
- JSON output for future GUI integration.

## Requirements

- Python 3.11 or newer
- Windows 10/11 or a maintained Linux distribution
- No third-party runtime dependencies for the current core

## Run from source

```sh
cd tooling/renpy-vita-studio
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux:   source .venv/bin/activate
python -m pip install -e .
renpy-vita-studio --help
```

## Examples

```sh
renpy-vita-studio inspect "/path/to/Game"
renpy-vita-studio inspect "/path/to/Game" --json
renpy-vita-studio rpa list "/path/to/Game/game/archive.rpa" --json
renpy-vita-studio rpa extract "/path/to/Game/game/archive.rpa" "./staging/archive"
```

The extractor refuses to overwrite an existing destination. Choose a new empty path for each extraction.

## Safety boundaries

- Only standard RPA-2.0 and RPA-3.0 are supported in this preview.
- Custom/encrypted archive variants and RPA-1.0 / standalone RPI are not supported.
- RPYC files are inventoried but never unpickled or decompiled.
- The inspector does not execute `options.rpy` or other game code.
- Engine version detection is deliberately limited to supported literal fingerprints; a missing or ambiguous fingerprint remains unknown.
- No DRM bypass, decryption, game-data redistribution or proprietary payload bundling.
- No VPK generation or Vita installation is implemented yet.

## Development

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Relationship to upstream

The native runtime baseline is [SonicMastr/renpy-vita](https://github.com/SonicMastr/renpy-vita). This core is a new SPDW Factory desktop-side tool, not a claim that the upstream Distribution Tool source was available or directly refactored. Runtime adapters for the legacy Python 2.7 port and the community Python 3.11 Ren'Py Vita 8 port must remain separate until their licensing, APIs and build requirements are audited.

## Roadmap

1. RPA fixture coverage and cross-platform CI.
2. Better engine/runtime fingerprinting with explicit confidence levels.
3. LiveArea/SFO validation and a non-destructive staging builder.
4. VitaSDK-backed VPK packaging with reproducible manifests.
5. Desktop GUI and optional USB/network device integration.
6. Evaluate a Vita-side companion only for tasks that fit Vita memory and native APIs.
