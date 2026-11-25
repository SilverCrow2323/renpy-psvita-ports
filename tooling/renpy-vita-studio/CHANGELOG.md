# Changelog

## 0.2.0 — Guided desktop builder

- Added a four-step desktop workflow: original game folder, runtime, generated LiveArea and VPK build.
- The input is the user's original game root or its game/ directory; no prebuilt Vita app folder or user-created sce_sys/ is required.
- Added managed Ren'Py Vita 7 Legacy, Ren'Py Vita 8 PVR 0.2.1 and Ren'Py Vita 8 VitaGL 0.2.1 runtime profiles.
- Added first-launch background downloads for all runtime profiles, upstream SHA-256 verification where published, safe ZIP extraction and persistent runtime cache.
- Added game-artwork discovery with separate image selectors for icon, boot screen, LiveArea background and startup image; added automatic crop/resize, indexed PNG output, transparent startup-art support and Vita-compatible CRLF LiveArea XML.
- Added automatic Vita param.sfo generation, editable app version and a safe default Title ID.
- Added an end-to-end VPK build pipeline, recursive directory packaging, archive verification, JSON build report and SHA-256 sidecar.
- Added Linux Debian package generation and a desktop-menu launcher.
- Added compatibility preflight warnings to the desktop project screen.
- Added tests for original-folder input, symlink rejection, SFO generation, LiveArea output, runtime profile definitions, archive path traversal and build orchestration.

## 0.1.0 — Inspection and packaging core

- Initial read-only project inventory, RPA inspection/extraction, runtime profile hints, staging and VPK wrapper.
