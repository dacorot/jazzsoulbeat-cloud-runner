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
