# Jazz Soul Beat Agent — autonomous cloud operation

The controller runs on GitHub Actions. It does not depend on the Windows PC remaining on.

## Scheduled jobs

All times below are Colombia time (UTC-5). GitHub Actions schedules are approximate and may start later during platform load.

| Schedule | Job | Purpose |
|---|---|---|
| Monday, 7:17 a. m. | audit-openlofi-rights.yml | Recheck the Open Lo-Fi release, source statements, audio hashes and rights evidence. Review-only; never approves tracks. |
| Tuesday, 7:41 a. m. | private-agent-preflight.yml | Calls the reusable QA runner: compile, unit tests, synthetic video, artifact verification and private Drive persistence. |
| Wednesday, 7:55 a. m. | build-first-review-video.yml | Restores only production-manifest audio. Builds only when one complete hour of approved, rights-verified music exists. |
| Thursday, 7:30 a. m. | discover-music-candidates.yml | Refreshes candidate catalogues from Wikimedia Commons, Incompetech, ccMixter and Ketsa; saves a consolidated review CSV. |
| First day of each month, 7:30 a. m. | refresh-ketsa-review-library.yml | Refreshes official Ketsa candidate audio and its rights/provenance reports. |
| First day of each month, 8:30 a. m. | refresh-incompetech-review-library.yml | Refreshes official Incompetech candidate audio and its rights/provenance reports. |

## Production and publishing gates

- The active music library accepts only audio referenced by production manifests and passing the rights, source, duration and music-metadata checks.
- Candidate discovery, download and rights audits never approve tracks automatically.
- A production video is not built from an incomplete hour, shortened tracks or repeated tracks.
- The scheduled build reports PENDING while the approved music library is insufficient; it does not misreport a skipped build as a completed video.
- If a valid YouTube OAuth secret is configured, the upload code is hard-coded to PRIVATE and checks the expected channel. Without OAuth, the MP4 stays in private Drive.
- Public publishing is not part of these workflows.
- Cloudflare FLUX Schnell is the only configured image-generation route. Missing credentials or free quota fail closed; no paid fallback or billing is enabled.

## Current discovery baseline

The first complete four-source pass produced 398 candidate rows:

- Wikimedia Commons: 171
- Incompetech: 43
- ccMixter: 84
- Ketsa: 100

The consolidated review queue is saved in Drive as output/MUSIC_CANDIDATE_REVIEW.csv. These are candidates, not approvals. Open Lo-Fi's separate 40-track review set and its rights audit remain under tracks/review/openlofi/ and output/openlofi-review/.

## Reusing the runner for three more agents

Use .github/workflows/reusable-private-agent.yml from each new controller. The private agent must expose the standard QA contract:

- requirements.txt
- main.py self-test
- main.py drive-push
- main.py drive-status
- tests/

Each agent must have its own private Drive folder/namespace and its own secrets. Do not share Jazz Soul Beat's production library, credentials, or publication channel with another agent. The reusable workflow performs QA and private persistence only; each agent keeps its own task-specific automation and approval gates.
