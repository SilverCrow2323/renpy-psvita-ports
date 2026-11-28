# Roadmap — Ren'Py Vita Port Hub

## M0 — Preserve project evidence
- [x] Track the candidate, failed-conversion and available-port lists.
- [x] Maintain a testing checklist that records exact game/runtime builds and observed outcomes.
- [x] Keep individual port repositories separate from the hub.
- [ ] Reconcile the legacy README list with a versioned machine-readable catalogue.

## M1 — Intake and compatibility quality
- [x] Define evidence fields for boot, menu, session, video and patched results.
- [x] Add regression coverage that keeps the README and tracked port-status page aligned.
- [ ] Replace free-form suggestion intake with structured fields for official source and redistribution/license notes.
- [ ] Add a reviewed status vocabulary and require a date/evidence reference for compatibility changes.

## M2 — Reproducible porting
- [ ] Record the exact Ren'Py Vita tool/runtime revision for every maintained port.
- [ ] Define a repeatable host-side inspection workflow for RPA, OGG, image and archive metadata without bundling game data.
- [ ] Document supported and unsupported Ren'Py features with a versioned test matrix.

## M3 — Release coordination
- [ ] Link each port's release, title ID, source attribution and known limitations.
- [ ] Validate that generated catalogue entries match the individual repositories.
- [ ] Keep hardware qualification separate from automated metadata checks.

## Acceptance
Every status change has a source/build identifier and evidence category; the hub's port links remain aligned with individual repository names; suggestions do not imply compatibility; no original game assets are committed.

## Release target
Maintain the existing hub as a documentation/catalogue project. The next meaningful version follows completion of the structured catalogue and its validation workflow, not a cosmetic README update.
