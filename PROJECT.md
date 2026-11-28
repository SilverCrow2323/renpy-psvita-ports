# Project: Ren'Py PlayStation Vita Port Hub

## Purpose
Maintain the project-wide compatibility and intake record for Ren'Py games evaluated for PlayStation Vita. This repository coordinates separate game-port repositories; it does not contain or redistribute the original games and is not itself the Ren'Py runtime or a VPK builder.

## Users and use cases
- Vita owners looking for available ports and honest compatibility notes.
- Maintainers evaluating candidate games and recording reproducible results.
- Port contributors checking upstream sources, runtime limitations and package requirements.

## Scope and boundaries
In scope: candidate intake, compatibility triage, test-report format, status taxonomy, links to separate port repositories, and source/runtime provenance.

Out of scope: redistributing game data, claiming compatibility from a suggestion alone, maintaining individual VPK payloads, and changing the Ren'Py Vita runtime. The runtime/tool dependency is upstream at https://github.com/SonicMastr/renpy-vita. Individual ports retain their own package metadata and release history.

## Product modules
- Candidate intake: game title, official source, exact game build, Ren'Py version, and license/redistribution notes.
- Compatibility register: boot, menu, session, video, save/load and patched-vs-unpatched results.
- Port directory: links to independent Vita port repositories.
- Evidence guidance: logs/screenshots and reproducible scene/action descriptions without uploading copyrighted game files.
- Documentation source: tracked Markdown in wiki-source/ and the publishing helper in tools/.

## Target and dependencies
- PlayStation Vita / PlayStation TV.
- Ren'Py Vita runtime and VitaSDK toolchain as documented by the upstream project.
- Physical Vita testing for runtime claims; host-side parsing or packaging tests are not gameplay certification.

## Safety, accessibility and localization
Never accept original game payloads, private keys or account credentials. Record the publisher/source and license constraints before recommending a port. Keep status language explicit, Markdown tables and headings accessible, and documentation in English.

## Verified baseline
The README lists seven dedicated SilverCrow2323 Vita port repositories and a separately maintained Harvest December collaboration with takoyaki99. The project tracks candidate/failure notes and a test checklist; it does not claim that every candidate is compatible.
