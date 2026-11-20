# Changelog

## v0.6 — 2026-11-20

- Replace the animation with backward → forward → drop. Keep the reversal
  continuous and use four matched overlay frames for the drop transition.
- Slow the drop to 85% speed, fade to black over 1.5 seconds, then hold black
  for 0.25 seconds: 520 frames, 21.67 seconds at 24 fps.
- Fill a 9:16 crop and center it on the native 720×1600 display. Match the
  supplied initial still to the first animation frame and blend into motion.
- Use the Lords of Acid excerpt from 37.50–56.54 seconds so the vocal cue lands
  at the 13.25-second drop transition. Reduce the level by 6 dB, fade in over
  0.5 seconds and fade out over 2 seconds.
- Complete the animation before leaving the boot screen, holding black if
  Android takes longer. Let music finish before animation teardown.
- Add media/package builders, a release preview and download checksums.
- Host validation passed. Phone boot playback and speaker loudness remain
  unverified for this version. Earlier v0.4/v0.5 builds were local previews.

## v0.3

Boot logo, animation and sound on the Foxxd A67L Gen 2.
