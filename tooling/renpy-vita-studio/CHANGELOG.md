# Changelog

## Unreleased

- Added conservative Ren'Py engine fingerprinting from generated `renpy/vc_version.py` metadata (high confidence) and legacy literal `version_tuple` metadata (medium confidence).
- Kept the game version (`config.version`) separate from the engine version; unknown fingerprints remain unknown.
- Added tests for modern, legacy and ambiguous-version cases.

## 0.1.0 — Core preview

- Added read-only Ren'Py project inventory.
- Added standard RPA-2.0 and RPA-3.0 index inspection.
- Added restricted pickle loading and bounded decompression.
- Added safe extraction into a new destination directory.
- Added CLI and Windows/Linux Python 3.11/3.12 CI matrix.
- VPK building, GUI, Ren'Py runtime adaptation and Vita installation remain future work.
