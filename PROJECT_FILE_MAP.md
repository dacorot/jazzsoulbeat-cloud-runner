# Jazz Soul Beat — Project File Map

This is the human and agent entry point for locating project information.

## 1. Code and automation

- Public controller: `jazzsoulbeat-cloud-runner`
- Private production agent: `jazzsoulbeat-agent`
- Workflows: `.github/workflows/`
- Public policies and contracts: `*.md` and `config/`
- Private production logic: root Python modules and private tests

## 2. Audio

- Active evergreen manifest: `tracks/library.csv`
- Active seasonal manifests: `tracks/seasonal/<season>/library.csv`
- Approved/imported audio: `tracks/imported/`
- Unapproved candidates: `tracks/review/`
- Rights and provenance reports: `output/library-promotion/`, `output/library-growth/`
- Audio database: `data/agent.db` (derived; manifests remain authoritative)

Never search `tracks/review/` as production capacity.

## 3. Visuals

- Approved style references: `assets/visual-agents/approved-style-samples/`
- Category visual libraries: `assets/visual-agents/<category>/`
- New generated candidates: `assets/visual-agents/<category>/candidate_scenes/`
- Motion sources: `assets/visual-agents/<category>/motion/`
- Visual manifests: category `manifest.json`, `SCENE_MANIFEST.json`, and candidate `CANDIDATE_MANIFEST.json`
- Visual QA and rejected material: `output/visual-production/`, `music-production/visual-rejected/`

Candidates are not approved video inputs.

## 4. Video runs

- Cloud/private-agent renders: `output/<run-id>/`
- Legacy local review renders: `music-production/generated/`
- Visual review packages: `music-production/visual-review/`
- Hash-bound approval ledgers: `music-production/approval_ledger.json` and private output manifests

A valid render folder contains the video, mix, thumbnail, description, music source and visual provenance.

## 5. Recovery order after restart

1. Read `PROJECT_CONTEXT.md`.
2. Read `DEVELOPMENT_DIRECTIVES.md`.
3. Read `config/artifact_taxonomy.json`.
4. Run the canonical inventory agent.
5. Restore private Drive state.
6. Read the latest production, audio and visual reports.
7. Resume from the latest checkpoint; never recreate an already-existing asset.

## 6. Naming pattern

- Video run: `output/YYYYMMDD-HHMMSS-ffffff/`
- Render files: `video.mp4`, `mix.mp3`, `thumb.jpg`, `description.txt`
- Provenance: `MUSIC_SOURCE.txt`, `VISUAL_SCENE_PROVENANCE.json`
- Candidate images: `candidate_<sequence>.jpg`
- Reports: `output/<domain>/<report-name>.json`

Existing historical paths remain readable. They are indexed, not moved during active production.
