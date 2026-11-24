# Community port guides

This page consolidates installation and reporting notes from the former per-repository GitHub Wikis. Where a legacy README did not provide a reliable title ID or install sequence, this guide says so rather than inventing one.

## (Don't) Open Your Eyes Vita

**Project:** [Don-t-OpenYourVita](https://github.com/SilverCrow2323/Don-t-OpenYourVita)  
**Original game:** [Creator's itch.io page](https://via01.itch.io/dont-open-your-eyes)  
**Application title ID:** `RNPYDNOPE`

The Vita VPK and the original PC game's `game/` directory are separate pieces. The port repository documents the following path:

```text
ux0:/app/RNPYDNOPE/game/
```

1. Install the port VPK using VitaShell.
2. Obtain the original game from the creator's page.
3. Copy the original `game/` folder into `ux0:/app/RNPYDNOPE/`.
4. Confirm the final path is `ux0:/app/RNPYDNOPE/game/`.
5. Launch from LiveArea.

If the app opens but content is missing, check the exact folder name and path first. Report the port/VPK version, Vita model/firmware, steps and complete error text. Do not upload the original game data.

## HIKE BACK Vita

**Project:** [HIKE-BACK-Vita](https://github.com/SilverCrow2323/HIKE-BACK-Vita)  
**Original game:** [ClownDream on itch.io](https://clowndream.itch.io/hikeback)  
**Application title ID:** `RENPYHIKE`

The legacy repository documents a VitaShell folder-install route because direct VPK installation may be slow:

1. Download the port VPK.
2. Extract it as an archive into a new folder.
3. Transfer the extracted folder to the Vita.
4. In VitaShell, highlight the folder, press **TRIANGLE → More → Install folder**, then confirm.
5. Copy the original game's `game/` folder to:

```text
ux0:/app/RENPYHIKE/game/
```

6. Keep the folder named `game` and launch from LiveArea.

The legacy README reports text lag in some sections and suggests overclocking may improve the experience. That is not a guarantee or a substitute for measuring performance. Include the exact scene and device state when reporting slowdowns.

## Magical Literary Heroine Natsuki Saves the Literature Club! Vita

**Project:** [Vita port repository](https://github.com/SilverCrow2323/Magical-Literary-Heroine-Natsuki-Saves-The-Literature-Club-Vita)  
**Original game:** [Doki Doki Literature Club on Steam](https://store.steampowered.com/app/698780/Doki_Doki_Literature_Club/)  
**Mod:** [Official mod homepage](https://www.mlhnstlc.com/)  
**Technical base:** [SonicMastr's Ren'Py Vita](https://github.com/SonicMastr/renpy-vita) and [DDLC Vita](https://github.com/SonicMastr/Doki-Doki-Literature-Club-Vita)

The legacy README identifies the project and its sources but does **not** specify a verified title ID, final `game/` destination or complete VPK installation sequence. Do not copy the title ID from another Ren'Py Vita port.

Before installing, check the exact [release notes](https://github.com/SilverCrow2323/Magical-Literary-Heroine-Natsuki-Saves-The-Literature-Club-Vita/releases). If the release does not provide a title ID and content layout, ask in the [project issues](https://github.com/SilverCrow2323/Magical-Literary-Heroine-Natsuki-Saves-The-Literature-Club-Vita/issues) before copying files.

## Harvest December: Reharvested Portable

**Project record:** [SilverCrow2323 repository](https://github.com/SilverCrow2323/Harvest-December-Reharvested-Portable)  
**Upstream collaboration:** [takoyaki99 repository](https://github.com/takoyaki99/Harvest-December-Reharvested-Portable)  
**PC Reharvested source:** [Autumn Rivers on itch.io](https://natirivers.itch.io/harvest-december-remake)

The legacy README describes the Vita port as in progress and the Switch as a hoped-for later target. It does not establish a finished public Vita release, validated title ID or complete installation path.

The tracked `PSVITA Port/` directory contains port-related files including `eboot.bin`, `renpy.py` and `sce_sys/`; their presence alone does not prove that a release is complete or installable.

Before attempting installation:
1. Check the upstream repository for current coordination and release status.
2. Confirm that a release is explicitly marked for PlayStation Vita.
3. Follow instructions for that exact build.
4. Do not infer a title-ID path from another port.

For a useful test report, record the Vita model, firmware, port commit/build, source game version, boot/menu/new-game behavior and exact error. Do not attach original game files or proprietary assets.

## Shared safety rules

- The Vita package and original PC game data are separate.
- Obtain original games and mods from their creators or official storefronts.
- Never commit game archives, proprietary scripts, music, images, saves or decrypted game folders.
- CI and repository contents cannot prove real-device compatibility.
- Report exact versions and reproducible steps; distinguish physical Vita tests from emulator-only tests.
