# Visual Motion Agent

The visual_motion_agent is the dedicated visual pipeline for Jazz Soul Beat.

It accepts an approved base image and permits exactly one profile: static_rain_steam_only.

That profile locks the camera and base plate, keeps the exterior rain texture static behind window mullions, and animates only coffee steam. It rejects other frame rates, resolutions, and unsafe motion contracts. It never grants creative approval or publishes media.

Run a contract plan with:

```bash
python scripts/visual_motion_agent.py \\
  --image path/to/approved-base.png \\
  --output-json visual-motion-plan.json
```

Technical rendering remains gated by the exact base-image hash, human animation approval, rights checks, and publication authorization.
