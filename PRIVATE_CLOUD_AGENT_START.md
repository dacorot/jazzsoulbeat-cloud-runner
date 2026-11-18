# Jazz Soul Beat — private cloud build request

task: build-evergreen
hours: 2
collection: evergreen
season: none
agent_ref: fix/real-music-and-cinematic-motion

Safety:
- Build only from tracks with approved=1 and rights_verified=1.
- Require at least 120 minutes of distinct approved evergreen audio after crossfades.
- If the library gate fails, stop without using pending candidates or synthetic filler.
- Save any eligible review package only to private Google Drive.
- Never upload to YouTube or change visibility.


Latest audit trigger: exercise scheduled-production eligibility gate. This run must skip video generation while the approved evergreen library is insufficient and must keep all output in private Drive.

Safe regression 2026-11-14: validate the scheduled production eligibility gate and scoped persistence; zero approved tracks must skip rendering without broad Drive sync.

Safe regression 2026-11-14: re-parse the final production workflow after QHD video, MP3 duration and 1280x720 thumbnail checks were added.

Final safe regression 2026-11-14: validate explicit production-gate summary, per-track source manifest, video SHA-256 provenance, audio and thumbnail quality checks.

Regression trigger 2026-11-14: validate cloud production workflow after adding private persistence for newly generated visual scenes; no upload or publication is enabled.

Regression trigger 2026-11-14: parse and validate the latest production workflow including the explicit visual-library persistence PDCA acceptance check; expected result remains a safe no-render gate while approved audio is absent.

Promotion trigger: import rights-verified original-music package into private library.

2026-11-18: Triggered after repairing the private-agent preflight and copyright quarantine bridge.
2026-11-18: Third closure audit trigger after stale-run cancellation policy.

Audit closure marker: final three-pass remediation run 2026-11-18T14:07:09Z
Closure retry marker: 2026-11-18T14:10:14.426Z
Retry FFmpeg install marker: 2026-11-18T14:11:29.255Z
Scene validator formatting fix marker: 2026-11-18T14:13:03.727Z
Final CI remediation marker: 2026-11-18T14:15:36.622Z
