# Jazz Soul Beat — Development Directives

These directives govern every autonomous development, cleanup and optimization cycle.

## Current findings

- Public controller tests: 104 passed and 47 subtests passed with PYTHONPATH configured.
- Private agent source compiles, but the local environment is missing declared dependencies; the complete test suite cannot be considered green until requirements.txt is installed.
- Local visual inventory contains 33 JPG, 18 PNG and 18 MP4 assets under assets/visual-agents.
- No candidate_scenes directory or CANDIDATE_MANIFEST.json exists locally yet.
- Local tracks/library.csv contains 37 rows and 37 rights_verified values, but no approved column and no metadata_source column. This is a contract mismatch and must be migrated before production decisions.
- Rights-verified is not the same as approved. No agent may infer approval from rights_verified alone.

## Priority order

### P0 — Restore truthful state

1. Run the manifest/schema migration before every production or audit cycle.
2. Make tracks/library.csv conform to one versioned schema, including approved, metadata_source, duration_seconds and all required provenance fields.
3. Reconcile CSV, SQLite and Drive state without deleting audio or visual assets.
4. Produce a machine-readable mismatch report when CSV, SQLite and Drive disagree.
5. Install requirements.txt in every CI job before running private tests.
6. Fail closed when a migration, restore or provenance check fails.

### P0 — Make visual production observable

1. Run the continuous visual producer every 12 hours.
2. Restore assets/visual-agents from private Drive before generation.
3. Generate only into assets/visual-agents/<category>/candidate_scenes/.
4. Never overwrite an existing candidate, approved sample, base image or motion file.
5. Require a unique SHA-256, QHD JPEG validation, category, playlist mapping, motion opportunity and prompt hash.
6. Persist CANDIDATE_MANIFEST.json and the production report after every run.
7. Treat every generated image as GENERATED_PENDING_HUMAN_QA. Generation is not approval.
8. Do not render or publish a video from a candidate image.

### P1 — Improve the development loop

Every six-hour development cycle must:

- run public tests with PYTHONPATH configured;
- compile and test the private agent after installing requirements;
- audit cross-repository contracts;
- audit visual, audio, output and checkpoint inventories;
- run PDCA and record Plan, Do, Check and Act evidence;
- classify each issue as HEALTHY, WARNING, BLOCKED or ACTION_REQUIRED;
- create one bounded report, not duplicate issues;
- open a reviewed Pull Request for source corrections.

### P1 — Safe cleanup

Agents may clean only:

- stale caches and generated temporary reports;
- duplicate derived reports after a manifest confirms the canonical copy;
- expired CI artifacts according to retention policy.

Agents must never automatically delete:

- music;
- images;
- motion scenes;
- videos;
- approval ledgers;
- rights evidence;
- Drive backups;
- YouTube assets.

### P2 — Production quality

Before any image enters a video:

- style match must pass against the approved sample set;
- no real people or photographic output;
- scene must map to one playlist and season;
- localized motion must have valid occlusion/depth evidence;
- no zoom, pan, full-frame rain or effects crossing solid objects;
- final audio must pass adaptive transition analysis;
- description, track list, performer/source and rights status must be complete in English.

## Autonomy boundaries

Automatic:

- inventory, testing, schema checks, deduplication reports, candidate generation, Drive persistence, PDCA reports and failure alerts.

Pull Request required:

- source-code changes, schema migrations, workflow changes, dependency updates and contract changes.

Human approval required:

- creative approval of images;
- music approval for publication;
- rights exceptions;
- YouTube upload/publication;
- deletion of any production asset;
- secret or OAuth changes.

## Definition of done

A cycle is complete only when its report includes:

- exact commit or agent ref;
- test results;
- production counts;
- persisted manifest paths;
- blockers and root causes;
- corrective action;
- regression test;
- next scheduled action.

No agent may report success merely because a job started.


## Immediate treatment rule

This rule applies to the architect and to every production, development, audit and supervisory agent. Every autonomous cycle must treat each detected finding immediately.

- Safe, reversible and testable defects must be corrected in the same cycle.
- The agent must run the relevant regression test immediately after the correction.
- Blockers must be diagnosed, mitigated or escalated in the same cycle; they may not be left as passive observations.
- Missing reports, manifests, heartbeats or production evidence must be regenerated or marked explicitly as blocked with a concrete next action.
- The agent must continue through the defined backlog without waiting for another conversational approval.
- Approval is required only for destructive actions, publication, rights exceptions, secret/OAuth changes, or irreversible infrastructure changes.
- A cycle may not be reported as complete while known safe corrective work remains untreated.


### Immediate execution responsibility

The architect and every agent are operationally responsible for treating findings, not merely reporting them. When a safe correction is available, the same cycle must execute it and verify it. At minimum, safe cycles must apply manifest migrations, refresh inventories and regenerate missing machine-readable reports. A report that only says "fix later" is a failed cycle unless the finding crosses a defined safety boundary.
