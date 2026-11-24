# Port status

Use these labels consistently. A title must never move to a stronger status without evidence.

| Status | Meaning | Evidence needed |
|---|---|---|
| **Suggested** | A community member proposed the title | Issue with game identity/source |
| **Queued** | Accepted for evaluation, but no test is underway | Maintainer triage note |
| **Testing** | A conversion or runtime test is actively evaluated | Exact build/runtime and test owner |
| **Boots** | The app launches to a usable initial screen | Platform and build details |
| **Session-tested** | Meaningful gameplay was exercised | Reproduction notes and tested scenes |
| **Playable** | A substantial playthrough works with limitations disclosed | Extended target-hardware evidence |
| **Available port** | A separate project repository or release exists | Project link; no implied retest |
| **Blocked** | A specific blocker prevents progress | Exact error, dependency or missing input |
| **Failed basic conversion** | The unpatched baseline conversion failed | Exact failure stage and environment |

## Current catalogue snapshot

The root README retains the historical in-testing and candidate lists. The issue tracker is the live source for community proposals and discussion.

- [Open porting issues](https://github.com/SilverCrow2323/Renpy-Vita-Portings/issues)
- [Available ports](../README.md#available-renpy-vita-ports)

## Reporting rules

- Do not label a title **Playable** because it merely boots.
- Do not label a port **tested on Vita** if only an emulator or CI runner was used.
- Do not label an old issue as current test evidence.
- Keep baseline conversion and patched conversion results separate.
- Add game version, runtime revision, Vita model/firmware and test date whenever known.
