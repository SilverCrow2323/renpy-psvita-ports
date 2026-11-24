# Repository structure

This repository is the central Ren'Py Vita catalogue and shared documentation hub.

```text
.
├── README.md
├── CHANGELOG.md
├── docs/
│   ├── README.md
│   ├── COMPATIBILITY.md
│   ├── PORT-STATUS.md
│   ├── SUGGESTING-A-GAME.md
│   ├── TESTING.md
│   ├── REPOSITORY-STRUCTURE.md
│   └── games/
│       └── sakura-succubus/
│           ├── README.md
│           ├── 1.md
│           ├── 2.md
│           ├── 3.md
│           └── 4.md
└── wiki-source/
    └── (existing GitHub Wiki source; maintained separately)
```

## Why the Sakura series has one guide

The four Sakura Succubus ports share the same basic installation workflow and upstream Ren'Py Vita distribution path, but each has a distinct title ID, original-game source and known-issue record. The shared guide explains the common workflow; per-title pages hold the differences.

## What stays outside this repository

- Original commercial game data and extracted game folders.
- VPK binaries and generated build outputs.
- Proprietary artwork and audio from the original games.
- Engine/runtime source owned by upstream projects.
- Separate port-specific repositories while consolidation is reviewed.

The four legacy Sakura repositories are linked for traceability. This documentation consolidation does not rewrite their Git history or silently delete/archive them.
