# Sakura Succubus Vita — unified series guide

<p align="center"><strong>Four games · One installation handbook · Four title-specific records</strong></p>

The Sakura Succubus Vita ports are now documented together in the Ren'Py Vita Hub. This replaces four slightly different README instructions with one consistent series guide and a dedicated page for each title.

## Choose your game

| Game | Title ID / destination | Original PC release |
|---|---|---|
| [Sakura Succubus](1.md) | RNPYSS001 | [Steam app 1202310](https://store.steampowered.com/app/1202310/Sakura_Succubus/) |
| [Sakura Succubus 2](2.md) | RNPYSS002 | [Steam app 1326000](https://store.steampowered.com/app/1326000/Sakura_Succubus_2/) |
| [Sakura Succubus 3](3.md) | RNPYSSIII | [Steam app 1406020](https://store.steampowered.com/app/1406020/Sakura_Succubus_3/) |
| [Sakura Succubus 4](4.md) | RNPYSS004 | [Steam app 1466690](https://store.steampowered.com/app/1466690/Sakura_Succubus_4/) |

The destination identifiers above come from the corresponding legacy project instructions. Confirm the installed application directory on your own device before copying files.

## Shared installation workflow

Each port requires two separate pieces:

1. The Vita port package (VPK / extracted application folder).
2. The original PC game's game directory, obtained from a legitimate copy of that specific game.

The original game's files are **not included** in the port package or this repository.

### Install the port package

The legacy project READMEs describe this VitaShell route because direct VPK installation may be slow:

1. Download the VPK supplied by the relevant port project/release.
2. On a PC or device, extract the VPK as an archive into a new folder.
3. Transfer the extracted folder to the Vita.
4. Open **VitaShell** and highlight that folder without opening it.
5. Press **TRIANGLE**, choose **More**, then **Install folder**.
6. Confirm the prompts and wait for installation to finish.

### Add the original game data

Copy the original game's game directory into the title-specific application directory:

```text
ux0:/app/<TITLE_ID>/game/
```

Use the exact title ID from the table and the matching per-game page. Do not copy the game directory beside the application folder, rename it, or mix data from different Sakura Succubus releases.

### Verify before launching

- [ ] The intended Vita application is installed in LiveArea.
- [ ] The directory name matches the title ID for the selected game.
- [ ] The final path ends in /<TITLE_ID>/game/.
- [ ] The copied data comes from the matching original game.
- [ ] The original game directory name is preserved.
- [ ] There is adequate free storage on the memory card.

Launch the game from LiveArea. If it fails, use the relevant per-title troubleshooting notes and report the exact game build, Vita model/firmware, port revision and failure point.

## Known limitations

- The shared upstream Ren'Py Vita baseline documents long loading times, possible image-loading hitches and no video playback.
- Sakura Succubus 3 and 4 legacy READMEs report occasional Settings and Load/Save menu glitches; Quick Load/Save is reported to work.
- These legacy notes are not a fresh hardware regression test. Do not assume an issue is fixed or still present without retesting.

## Legacy project records

- [Sakura Succubus Vita](https://github.com/SilverCrow2323/Sakura-Succubus-Vita)
- [Sakura Succubus 2 Vita](https://github.com/SilverCrow2323/Sakura-Succubus-2-Vita)
- [Sakura Succubus 3 Vita](https://github.com/SilverCrow2323/Sakura-Succubus-3-Vita)
- [Sakura Succubus 4 Vita](https://github.com/SilverCrow2323/Sakura-Succubus-4-Vita)

These remain linked while the consolidation is reviewed. No original game files, VPKs or proprietary payloads are redistributed here.
