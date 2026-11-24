# Ren'Py Vita Tooling — design brief

> **Status: research and architecture phase.** No universal converter, desktop GUI or one-click Vita installer is being advertised as available.

## 1. Upstream baseline

The original [SonicMastr/renpy-vita](https://github.com/SonicMastr/renpy-vita) repository is the native PlayStation Vita runtime. Its public source tree uses a VitaSDK/CMake build, Python 2.7 headers/libraries, SDL2 and native Vita libraries. Its only published release currently visible to this review is the 2021 v1.0 Distribution Tool archive.

The old README describes Linux/WSL build steps and a Windows distribution workflow. The distribution tool's source code is not present in the inspected public repository tree, so it cannot be safely refactored in place from the available source. The runtime itself is a separate engineering problem from the packaging GUI.

A second project, [Grimiku/RenPy-Vita-8](https://github.com/Grimiku/RenPy-Vita-8), updates the Vita runtime around Python 3.11 and a newer Ren'Py branch. This is a valuable compatibility reference, not proof that every Ren'Py 8 game works.

## 2. Product direction

A desktop-first application for Windows and Linux, with a possible Vita-side companion only where device APIs and memory constraints make it practical.

### Main workflow

1. **Import** a user-supplied game folder or archive.
2. **Inventory** the project without modifying the original.
3. **Detect** likely Ren'Py version, project structure, RPA archives, compiled scripts, media and platform-specific payloads.
4. **Assess** known Vita constraints and produce a confidence-rated report.
5. **Prepare** a separate staging directory, preserving originals and recording every transformation.
6. **Validate** LiveArea assets, title ID, SFO metadata, file layout, paths and package size.
7. **Build** a VPK only when a selected runtime profile and input set pass validation.
8. **Transfer/install** through USB or network only after explicit user confirmation, with rollback-safe staging and logs.

## 3. Architecture

- **Core:** Python package with a stable CLI; GUI calls the same core operations.
- **Desktop GUI:** Qt/PySide or another maintained cross-platform toolkit, selected after a small dependency/prototype comparison.
- **Adapters:** separate adapters for baseline Ren'Py 7 / Python 2.7 Vita runtime, Ren'Py 8 / Python 3.11 Vita runtime, and future community runtime variants.
- **Inspection:** read-only scanner for directory trees, `.rpa` archives, `.rpyc`/compiled scripts, `.rpy`, images, audio, video and native extensions.
- **Build backend:** isolated staging, deterministic manifest, VitaSDK integration and explicit build logs.
- **Device backend:** optional Vita connection and package transfer; no silent install or destructive replacement.
- **Profiles:** per-game overrides for engine version, archive handling, asset substitutions and known limitations.

## 4. RPA handling

RPA support must be version-aware. The inspector should identify archive header/version and index layout, list entries, validate offsets and optionally extract user-owned files into a chosen staging directory. It must not assume every archive is a standard unencrypted RPA or claim to recover protected/encrypted content.

A first milestone should be read-only inspection and safe extraction for documented RPA variants, backed by fixtures and corruption tests. Extraction must defend against path traversal, oversized entries, duplicate paths and malformed indexes.

## 5. Adaptive detection — no false universal promise

The tool can infer likely engine versions and common project layouts from metadata and files, but it cannot guarantee compatibility from a folder scan. Native Python modules, video codecs, rendering paths, memory use, dynamic imports, encrypted archives and game-specific code may require manual patches or may be impossible on a chosen runtime.

Every report should distinguish:
- **Detected** — directly observed in files.
- **Inferred** — likely based on signatures or metadata.
- **Unknown** — not enough evidence.
- **Blocked** — known incompatibility with the selected runtime.

## 6. Vita-side companion

A native Vita app may eventually handle device-side diagnostics, transfer reception, package installation or launch shortcuts. It should not be a requirement for desktop packaging. Building a full Ren'Py game-conversion tool on Vita is not a sensible first target because of memory, filesystem and toolchain constraints.

## 7. Milestones

| Milestone | Deliverable | Exit criteria |
|---|---|---|
| M0 | Source and compatibility audit | Runtime variants, licenses, submodules and toolchain documented |
| M1 | Read-only inspector CLI | Directory and RPA inventory, JSON/HTML report, safe path handling |
| M2 | Cross-platform desktop shell | Windows/Linux packaging and import/report workflow |
| M3 | Staging + metadata editor | Validated LiveArea/SFO structure, reproducible manifest |
| M4 | VPK backend | Builds against a known runtime profile with automated package checks |
| M5 | Device integration | Explicit transfer/install, logs and recovery path |
| M6 | Vita companion feasibility | Prototype only if native APIs and user value justify it |

## 8. Non-negotiable safety and licensing rules

- Never bundle commercial game data, original scripts, music, artwork or proprietary runtime files.
- Do not bypass DRM, encryption, ownership checks or platform restrictions.
- Keep the original source untouched; all extraction/build work happens in a separate staging directory.
- Record source hashes, tool versions, selected runtime profile and generated output hashes.
- Never claim a title is compatible solely because a VPK was created or it reached the LiveArea.
- Keep the upstream runtime's license and attribution intact; review all third-party licenses before redistribution.
