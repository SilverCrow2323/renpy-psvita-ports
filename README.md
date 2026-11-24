# Ren'Py Vita Hub

<p align="center">
  <img src="https://i.ibb.co/MB8wvG6/Tk-L6-PRey-H926q-Ph9utlp-Nv6-HUihn-I6-X0-RUh-Gnlg-sc.webp" alt="Ren'Py Vita" width="720">
</p>

<p align="center"><strong>SPDW Factory · PlayStation Vita · Ren'Py porting catalogue</strong><br><em>One hub for ports, compatibility notes, test evidence and practical documentation.</em></p>

<p align="center">
  <img alt="Platform" src="https://img.shields.io/badge/platform-PS%20Vita-5b4b9a">
  <img alt="Engine" src="https://img.shields.io/badge/engine-Ren'Py-ff7a59">
  <img alt="Catalogue" src="https://img.shields.io/badge/catalogue-unified-2f855a">
  <img alt="Docs" src="https://img.shields.io/badge/docs-maintained-2874a6">
</p>

> [!IMPORTANT]
> **A catalogue entry is not a compatibility guarantee.** A listed title may be a suggestion, a basic conversion test, a separately maintained port, or a project with known limitations. Check its status before downloading or attempting a build.

## What is this?

Ren'Py Vita Hub is the central catalogue and documentation home for Ren'Py visual-novel ports targeting PlayStation Vita through [SonicMastr's native Ren'Py Vita project](https://github.com/SonicMastr/renpy-vita).

This repository brings the former Ren'Py porting list and the four Sakura Succubus Vita project records into one navigable place. The Sakura Succubus entries now share one series guide and consistent per-title documentation.

**This is a catalogue and documentation hub — not a game installer, a VPK mirror, or a bundle of commercial game data.** Original game files must be obtained from the respective rights holders.

## Start here

| I want to… | Go to |
|---|---|
| Find a Vita port | [Available ports](#available-renpy-vita-ports) |
| Install a Sakura Succubus port | [Sakura Succubus series guide](docs/games/sakura-succubus/README.md) |
| Understand compatibility | [Compatibility guide](docs/COMPATIBILITY.md) |
| See status categories | [Port status](docs/PORT-STATUS.md) |
| Suggest a game | [Suggestion guide](docs/SUGGESTING-A-GAME.md) |
| Submit test evidence | [Testing checklist](docs/TESTING.md) |
| Understand the layout | [Repository structure](docs/REPOSITORY-STRUCTURE.md) |

## Available Ren'Py Vita ports

These are separate port projects. Their inclusion means a project exists; it does not imply every release has been recently retested.

| Port | Project |
|---|---|
| (Don't) Open Your Eyes Vita | [Don-t-OpenYourVita](https://github.com/SilverCrow2323/Don-t-OpenYourVita) |
| **Sakura Succubus series** | [Unified series documentation](docs/games/sakura-succubus/README.md) |
| ├ Sakura Succubus | [Legacy project](https://github.com/SilverCrow2323/Sakura-Succubus-Vita) · [Guide](docs/games/sakura-succubus/1.md) |
| ├ Sakura Succubus 2 | [Legacy project](https://github.com/SilverCrow2323/Sakura-Succubus-2-Vita) · [Guide](docs/games/sakura-succubus/2.md) |
| ├ Sakura Succubus 3 | [Legacy project](https://github.com/SilverCrow2323/Sakura-Succubus-3-Vita) · [Guide](docs/games/sakura-succubus/3.md) |
| └ Sakura Succubus 4 | [Legacy project](https://github.com/SilverCrow2323/Sakura-Succubus-4-Vita) · [Guide](docs/games/sakura-succubus/4.md) |
| DDLC Mod — Magical Literary Heroine Natsuki Saves the Literature Club! | [Project](https://github.com/SilverCrow2323/Magical-Literary-Heroine-Natsuki-Saves-The-Literature-Club-Vita) |
| HIKE BACK Vita | [Project](https://github.com/SilverCrow2323/HIKE-BACK-Vita) |
| Harvest December: Reharvested Portable | [Project](https://github.com/SilverCrow2323/Harvest-December-Reharvested-Portable) |

### Other community ports

- [Doki Doki Literature Club Vita](https://github.com/SonicMastr/Doki-Doki-Literature-Club-Vita)
- [Contract Demon Vita](https://github.com/SonicMastr/Contract-Demon-Vita)
- [Adastra Vita](https://www.reddit.com/r/Adastra_/comments/tctmeg/port_of_adastra_for_the_ps_vita/)

## Porting queue

The queue records community proposals and test work. It is separate from the available-port list.

### In testing / evaluation

- Maid Mansion — [issue #2](https://github.com/SilverCrow2323/Renpy-Vita-Portings/issues/2)
- Harvest December: Reharvested — dedicated port project linked above.

### Suggested candidates

Examples from the issue tracker include [Sakura Alien (#26)](https://github.com/SilverCrow2323/Renpy-Vita-Portings/issues/26), [Slay the Princess — The Pristine Cut (#24)](https://github.com/SilverCrow2323/Renpy-Vita-Portings/issues/24), [Nekopara series (#23)](https://github.com/SilverCrow2323/Renpy-Vita-Portings/issues/23), [ATRI — My Dear Moments (#21)](https://github.com/SilverCrow2323/Renpy-Vita-Portings/issues/21), and [One Thousand Lies (#20)](https://github.com/SilverCrow2323/Renpy-Vita-Portings/issues/20).

See the [full issue tracker](https://github.com/SilverCrow2323/Renpy-Vita-Portings/issues). An open issue is a proposal, not an approved or active port.

### Historical basic-conversion failures

The old list recorded two different failure classes for unpatched/basic conversions:

- **Runtime/session errors:** Sakura Dungeon (first fight); Milk Outside a Bag of Milk Outside a Bag of Milk (opening sequence / starting the main game).
- **Does not boot:** Toketsu, Analogue — A Hate Story, Strike The Light, Hate Plus, Long Live the Queen, Over The Hills And Far Away, and Katawa Shoujo.

These are historical observations, not universal verdicts. A different game build, runtime revision or targeted patch may change the result. See [Compatibility](docs/COMPATIBILITY.md).

## Important technical limits

- The original project documentation recommends relatively basic games.
- Video playback is documented as unsupported by the baseline porting path.
- Performance, memory use, loading time, rendering and input depend on the game and its assets.
- A successful boot does not prove that the full story, menus, saves or every scene work.
- A basic conversion failure does not prove that a game can never be ported with patches.

Read the [compatibility guide](docs/COMPATIBILITY.md) before opening a request or interpreting a test result.

## Contributing

Open one issue per title. Include the exact game release, official source, known Ren'Py version, suspected video/rendering dependencies, and reproducible evidence. Never attach commercial game data, scripts, music, images or other copyrighted payloads.

- [Suggest a game](docs/SUGGESTING-A-GAME.md)
- [Testing checklist](docs/TESTING.md)
- [Issue tracker](https://github.com/SilverCrow2323/Renpy-Vita-Portings/issues)

## Repository status and scope

This repository is the canonical home for the catalogue, compatibility notes and shared documentation. The four former Sakura Succubus repositories are retained as legacy per-title project records for traceability while this consolidation is reviewed. They have **not** been archived, deleted, or technically merged at the Git-object level.

No commercial game assets or executable payloads are redistributed by this documentation change.

<p align="center"><sub>SPDW Factory · Ren'Py Vita Hub · Documentation edition 2.0.0</sub></p>
