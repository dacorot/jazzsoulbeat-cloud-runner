# Jazz Soul Beat Music Agents

A free GitHub Actions workflow that runs Hunter -> Guardian -> Downloader -> Curator.
It follows the machine-readable policy in `config/music_search_policy.json` and
searches Internet Archive metadata for jazz, soul, bossa nova, blues and lo-fi
candidate recordings.
Only records whose item metadata explicitly identifies CC0, CC BY or CC BY-SA are downloaded.
The workflow keeps a CSV catalog, per-item JSON evidence and a rejection report as a 30-day Actions artifact.

## Important safeguards
- This is a candidate-acquisition pipeline, not automatic publication clearance.
- Curator performs a technical duration check (>=120 seconds); human listening and exact license/attribution review remain required.
- Do not use a track commercially until the item page, rights holder, license version and attribution requirements are checked.
- CC BY-SA has share-alike obligations; verify compatibility with the intended video/audio distribution.
- Internet Archive metadata can be inaccurate. A metadata license field alone is not conclusive proof.
- The search agent rejects short candidates, spoken-word terms and genres outside
  the approved editorial policy before they enter the review queue.
- The search agent is operational for discovery, but it never claims that a
  candidate is approved; primary rights review and human listening remain gates.
- Audio files are stored only in the workflow artifact for 30 days; this workflow does not yet sync to Google Drive.
- Runs on GitHub-hosted runners within the account's free Actions quota. GitHub may impose usage limits; no paid services are configured.

## Run
GitHub -> Actions -> Jazz Soul Beat - Music Agents -> Run workflow.
