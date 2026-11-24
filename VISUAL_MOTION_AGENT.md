# Visual Motion Agent

The visual_motion_agent is the dedicated visual pipeline for Jazz Soul Beat.

It accepts an approved base image and permits exactly one visual language: a locked
16:9 plate with localized, scene-masked atmosphere. The professional quality gate
allows only the registered effect profiles; it rejects decorative full-frame overlays,
camera motion and effects that cross subject or window-mask boundaries.

The profile locks the camera and base plate, keeps exterior rain behind verified
window masks, and animates only restrained atmosphere such as coffee steam and
approved plate reflections. It rejects other frame rates, resolutions, missing
provenance and unsafe motion contracts. It never publishes media.

Run a contract plan with:

```bash
python scripts/visual_motion_agent.py \\
  --image path/to/approved-base.png \\
  --output-json visual-motion-plan.json
```

Technical rendering remains gated by the exact base-image hash, the automated
professional visual quality gate, rights checks and publication authorization.
