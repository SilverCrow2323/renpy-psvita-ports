# Compatibility guide

Ren'Py Vita makes a subset of Ren'Py games possible on PlayStation Vita. It does not make every Ren'Py release compatible automatically.

## Baseline facts

The upstream [Ren'Py Vita project](https://github.com/SonicMastr/renpy-vita) describes a native Vita port and a distribution tool. Its README documents long load times, possible image-loading hitches and unsupported video playback. These are baseline limitations; individual games can add further constraints.

| Area | What to expect |
|---|---|
| Game complexity | Historical porting notes recommend relatively basic games. |
| Video | Video playback is documented as unsupported by the baseline path. |
| Images | Large or numerous images can increase loading time and memory pressure. |
| Rendering | Custom shaders, effects or unusual display assumptions need individual testing. |
| Native extensions | Python modules or native libraries unavailable in the Vita runtime may block a port. |
| Saves and menus | A game may boot while save/load or settings screens remain faulty. |
| Performance | Must be measured on the target Vita; emulator behavior is not a substitute for device testing. |

## Status is evidence, not prophecy

A result applies to the exact game build, Ren'Py version, runtime revision, conversion method and patches used during the test. Record those details. Do not generalize a failure from one build to all versions.

## Minimum compatibility investigation

1. Identify the exact game release and its Ren'Py version, if available.
2. Check whether the game uses video, custom rendering, unusual transitions or native extensions.
3. Keep original game files separate from Vita distribution output.
4. Attempt a baseline conversion before applying custom patches.
5. Record boot, menu, new-game, scene-transition, save/load and long-session behavior.
6. If a patch is needed, document it separately from the baseline result.

## Known historical observations

The old catalogue recorded:
- Sakura Dungeon: Ren'Py error during the first fight.
- Milk Outside a Bag of Milk Outside a Bag of Milk: error around the opening sequence and starting the main game.
- Toketsu, Analogue — A Hate Story, Strike The Light, Hate Plus, Long Live the Queen, Over The Hills And Far Away and Katawa Shoujo: did not boot in the recorded basic conversion attempts.

These are historical observations, not recent regression-test results. The original test environment and exact game/runtime revisions were not fully captured.

## References

- [SonicMastr/renpy-vita](https://github.com/SonicMastr/renpy-vita)
- [Upstream README](https://github.com/SonicMastr/renpy-vita#readme)
- [Project port status](PORT-STATUS.md)
