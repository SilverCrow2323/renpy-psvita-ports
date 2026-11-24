<p align="center">
  <img src="https://i.ibb.co/MB8wvG6/Tk-L6-PRey-H926q-Ph9utlp-Nv6-HUihn-I6-X0-RUh-Gnlg-sc.webp" alt="Ren'Py Vita Hub" width="760">
</p>

<h1 align="center">REN'PY VITA HUB</h1>
<p align="center"><strong>SPDW Factory · Visual novels, rebuilt for the handheld era.</strong><br>
A curated catalogue of Ren'Py projects, Vita ports, compatibility evidence and practical tooling.</p>

<p align="center">
  <img alt="Platform" src="https://img.shields.io/badge/platform-PlayStation%20Vita-6750a4">
  <img alt="Engine" src="https://img.shields.io/badge/engine-Ren'Py-f07857">
  <img alt="Catalogue" src="https://img.shields.io/badge/catalogue-community--curated-26734d">
  <img alt="Status" src="https://img.shields.io/badge/status-active%20documentation-2874a6">
  <img alt="License" src="https://img.shields.io/badge/content-documentation%20only-lightgrey">
</p>

> [!IMPORTANT]
> **Listed does not mean playable.** A title can be a community suggestion, an untested candidate, a partial port or a tested release. We label those states separately. No compatibility promises by vibes alone.

---

## 🎮 The hub

Ren'Py Vita Hub is the central home for the community catalogue of visual novels and Ren'Py projects being evaluated, adapted or already ported for PlayStation Vita.

The project consolidates the old porting list and the four Sakura Succubus project records into one place. It also provides practical documentation and a future-facing catalogue site with one page per title.

**This repository does not distribute commercial game data, original scripts, music, artwork or copyrighted game payloads.** Obtain each game from its creator or official storefront. The Vita porting tools only prepare files supplied by the user.

## Start here

| Looking for… | Open |
|---|---|
| The visual catalogue and title pages | [Ren'Py Vita Catalogue](docs/index.md) |
| All submitted titles | [Catalogue index](docs/catalogue.md) |
| Compatibility limits and known blockers | [Compatibility guide](docs/COMPATIBILITY.md) |
| What each status actually means | [Port status](docs/PORT-STATUS.md) |
| How to suggest a title | [Suggestion guide](docs/SUGGESTING-A-GAME.md) |
| How to report a test properly | [Testing checklist](docs/TESTING.md) |
| Sakura Succubus 1–4 | [Unified series guide](docs/games/sakura-succubus/README.md) |
| Community port installation guides | [Porting guides](docs/PORTING-GUIDES.md) |
| Repository layout | [Structure guide](docs/REPOSITORY-STRUCTURE.md) |

> **Website note:** the catalogue is being prepared under `docs/` for GitHub Pages. Until Pages is enabled in repository settings, the Markdown pages above are the canonical readable version.

## 🟢 Available ports and maintained projects

These are separate projects, not all builds of the same maturity. Follow each repository for its own releases, installation notes and issue tracker.

| Title / project | Project |
|---|---|
| (Don't) Open Your Eyes Vita | [Open repository](https://github.com/SilverCrow2323/Don-t-OpenYourVita) |
| Sakura Succubus series | [Series guide](docs/games/sakura-succubus/README.md) |
| ├ Sakura Succubus | [Project](https://github.com/SilverCrow2323/Sakura-Succubus-Vita) · [Title sheet](docs/games/sakura-succubus/1.md) |
| ├ Sakura Succubus 2 | [Project](https://github.com/SilverCrow2323/Sakura-Succubus-2-Vita) · [Title sheet](docs/games/sakura-succubus/2.md) |
| ├ Sakura Succubus 3 | [Project](https://github.com/SilverCrow2323/Sakura-Succubus-3-Vita) · [Title sheet](docs/games/sakura-succubus/3.md) |
| └ Sakura Succubus 4 | [Project](https://github.com/SilverCrow2323/Sakura-Succubus-4-Vita) · [Title sheet](docs/games/sakura-succubus/4.md) |
| Magical Literary Heroine Natsuki Saves the Literature Club! | [Project](https://github.com/SilverCrow2323/Magical-Literary-Heroine-Natsuki-Saves-The-Literature-Club-Vita) |
| HIKE BACK Vita | [Project](https://github.com/SilverCrow2323/HIKE-BACK-Vita) |
| Harvest December: Reharvested Portable | [Project](https://github.com/SilverCrow2323/Harvest-December-Reharvested-Portable) |

### Community projects

- [Doki Doki Literature Club Vita](https://github.com/SonicMastr/Doki-Doki-Literature-Club-Vita)
- [Contract Demon Vita](https://github.com/SonicMastr/Contract-Demon-Vita)
- [Adastra Vita](https://www.reddit.com/r/Adastra_/comments/tctmeg/port_of_adastra_for_the_ps_vita/)

## 🧪 The queue is not a compatibility list

The [catalogue](docs/catalogue.md) includes community suggestions and their source issues. A proposal remains **unverified** until someone tests the exact game build on a documented runtime and records evidence.

A few examples from the current queue:

- [Maid Mansion — issue #2](https://github.com/SilverCrow2323/renpy-psvita-ports/issues/2): historically marked as in progress; needs a fresh reproducible status.
- [Sakura Alien — issue #26](https://github.com/SilverCrow2323/renpy-psvita-ports/issues/26): Steam listing supplied; technical details still missing.
- [Slay the Princess: The Pristine Cut — issue #24](https://github.com/SilverCrow2323/renpy-psvita-ports/issues/24): video use in later scenes is an open compatibility question.
- [Nekopara collection — issue #23](https://github.com/SilverCrow2323/renpy-psvita-ports/issues/23): bundled proposal; individual volumes need separate test records.

Historical basic-conversion blockers are recorded in the [compatibility guide](docs/COMPATIBILITY.md). They are observations tied to a particular game build and baseline port, not eternal verdicts.

## 🧰 Ren'Py Vita Tooling — the next big piece

We are evaluating [SonicMastr's original Ren'Py Vita port](https://github.com/SonicMastr/renpy-vita) as the native Vita runtime and its legacy Distribution Tool as a starting point for workflow research.

The intended SPDW tool is a separate, adaptive project:

- **Windows + Linux desktop app** with a guided project scanner and build pipeline.
- **Game inspection:** detect Ren'Py project structure, engine/runtime hints, archives such as RPA, scripts and assets; produce a readable report before changing anything.
- **Asset preparation:** validate `game/`, `sce_sys/`, LiveArea images, title ID, metadata and Vita package structure.
- **Build:** create a VPK only when the selected runtime and inputs are compatible; preserve logs and a reproducible manifest.
- **Device workflow:** optional Vita discovery/connection, transfer and install with explicit confirmation.
- **Profiles, not magic:** detect what can be detected, ask only for missing data, and expose per-game overrides when heuristics are uncertain.
- **Possible Vita-side companion:** investigate what can realistically run on-device; packaging and installation are desktop responsibilities unless a safe native workflow proves otherwise.

RPA inspection is not the same as magically converting a game. Archive formats, encrypted/compiled scripts, Ren'Py versions, video, rendering, memory and native extensions can all block a port. The tool must report those limits instead of promising one-click universal compatibility.

See [the tooling design notes](docs/TOOLING-ROADMAP.md). No new cross-platform builder or universal VPK generator is claimed to exist yet.

## 🤝 Contribute without making a mess

Open **one issue per game**. Use the dedicated templates and include the exact game edition, official source, known engine version, evidence and any suspected video/native dependencies.

- [Suggest a game](https://github.com/SilverCrow2323/renpy-psvita-ports/issues/new?template=ren-py-game.md)
- [Report a tool or runtime bug](https://github.com/SilverCrow2323/renpy-psvita-ports/issues/new?template=bug-report.md)
- [Submit a compatibility test](https://github.com/SilverCrow2323/renpy-psvita-ports/issues/new?template=compatibility-test.md)
- [Browse open issues](https://github.com/SilverCrow2323/renpy-psvita-ports/issues)

Please do not upload game archives, decrypted game folders, copyrighted scripts, music, textures or executable payloads. Share logs and minimal reproducible metadata instead.

## 📦 Repository scope

This is the canonical catalogue and shared documentation home. Legacy per-title repositories are retained for their existing history and project-specific records while consolidation is reviewed. They are not silently deleted or archived.

The old tracked Wiki source and publisher are being replaced by the central catalogue under `docs/`. GitHub's separate Wiki feature must also be disabled in repository settings; that setting is not exposed by the current repository-edit integration, so it remains a manual settings step.

---

<p align="center"><strong>SPDW FACTORY</strong><br><sub>Ren'Py Vita Hub · Less guesswork. Better ports. Receipts for every claim.</sub></p>
