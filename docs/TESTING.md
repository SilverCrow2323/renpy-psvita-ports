# Testing checklist

A useful report tells another person what was tested, with which files, on which runtime, and what actually happened. "Works for me" is a nice feeling, not a test report.

## Test identity

- [ ] Game title and exact release/build recorded.
- [ ] Original game source recorded.
- [ ] Ren'Py version recorded, if identifiable.
- [ ] Ren'Py Vita runtime/distribution revision recorded.
- [ ] Baseline conversion or custom-patched conversion clearly identified.
- [ ] Test platform identified: physical Vita, emulator, or CI.

## Functional pass

- [ ] Application launches.
- [ ] LiveArea metadata and icon render correctly.
- [ ] Main menu renders and accepts input.
- [ ] New game starts.
- [ ] Text, images and transitions render.
- [ ] Multiple scenes can be visited.
- [ ] Save and load are checked.
- [ ] Settings and other menus are checked.
- [ ] Suspend/resume and a longer session are checked when practical.
- [ ] No unsupported video dependency blocks progression.

## Report failures precisely

Record the exact action, scene, visible behavior, error text and whether it reproduces. Attach logs or screenshots only when they do not expose copyrighted game content or personal information. Do not upload commercial game files.

## Result categories

| Observation | Report as |
|---|---|
| Launches to LiveArea/main menu | Boot result |
| Main menu and new game work | Initial session result |
| A specific scene errors | Runtime/session failure |
| App fails before menu | Boot failure |
| Works only with a patch | Patched result; describe patch |
| Tested only in emulator | Emulator-only result |
| Tested on physical Vita | Device-tested result; include model/firmware |

## Physical hardware honesty

CI can validate scripts, metadata and package structure. It cannot prove real Vita performance, input feel, suspend/resume behavior, memory stability or full gameplay. State clearly when hardware was not available.
