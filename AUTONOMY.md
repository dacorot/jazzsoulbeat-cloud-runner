# Jazz Soul Beat Agent — continuous cloud operation

## Operating model

The agent operates seven days a week through scheduled, bounded cloud executions. The Windows PC does not need to remain on. This is continuous orchestration, not one permanently running process: GitHub Actions starts jobs throughout the day and night, restores durable state from private Google Drive, performs bounded work, verifies it and persists evidence.

All human-facing times use Colombia (America/Bogota, UTC-5). GitHub Actions cron expressions use UTC and starts may be delayed by platform load.

## Scheduled jobs

| Cadence (Colombia) | Workflow | Purpose |
|---|---|---|
| Every 6 hours, 24/7 | private-agent-preflight.yml | Agent health pulse: compile, unit tests, self-test, artifact QA and safe QA-only Drive persistence. |
| Daily, 07:00 | build-first-review-video.yml | Attempt a private one-hour review video only when the complete approved and rights-verified music gate passes. |
| Daily, 07:30 | discover-music-candidates.yml | Refresh candidate catalogues and consolidated review queues. Candidate discovery never approves tracks. |
| Monday, 07:17 | audit-openlofi-rights.yml | Recheck Open Lo-Fi source statements, audio hashes and rights evidence; read-only. |
| First day monthly, 07:30 | refresh-ketsa-review-library.yml | Refresh official Ketsa candidate audio, audition sampler and rights/provenance reports; review-only. |
| First day monthly, 08:30 | refresh-incompetech-review-library.yml | Refresh official Incompetech candidates, sampler and rights/provenance reports; review-only. |
| On demand | private-cloud-agent.yml | Manually requested self-test or approved-library build. |

## Deming PDCA — mandatory for every task

Every scheduled or manually dispatched task follows the same control loop:
1. **Plan:** restore the latest Drive state; read prior defects, pending actions and checkpoints; choose a bounded priority; define acceptance checks and safety gates.
2. **Do:** execute the task with an exact agent revision and unique run record.
3. **Check:** validate outputs, provenance, media properties, tests and private persistence. A command exit code alone is not acceptance.
4. **Act:** apply only safe, authorized and reproducible corrections; add regression coverage; retry bounded/idempotent work; record root cause and evidence. Escalate decisions requiring human judgment or rights approval without stopping unrelated safe tasks.

The six-hour preflight is the recurring technical health check. Daily discovery and production attempts advance the work queue. Weekly and monthly audits deepen the rights/provenance checks. The PDCA log and acceptance checklist are defined in [PDCA.md](PDCA.md).

## Production and publication gates

- Only audio referenced by production manifests and passing source, rights, duration and metadata checks may enter production.
- Candidate discovery, download and rights audits never approve tracks automatically.
- The first video is 60 minutes; later videos alternate 2- and 3-hour targets as the approved library permits.
- No video is built from an incomplete library, shortened tracks or repeated tracks.
- Finished review packages remain in private Google Drive.
- **No YouTube upload is allowed, including private upload, until the user explicitly authorizes it.** Public publishing always requires separate explicit authorization.
- No paid services, paid fallbacks, subscriptions or billing activation.
- A blocked rights gate is a valid, clearly reported outcome; it is never silently bypassed.

## Execution limits and truthful status

GitHub Actions is a job scheduler, not a permanently running server. Each execution is bounded, may be delayed, and must persist checkpoints before it ends. “Continuous” means repeated, scheduled PDCA cycles across the full 24-hour day, not an uninterrupted process. The agent must never claim a cycle completed until its outputs and evidence have been verified.

## Current discovery baseline

The consolidated music review queues are stored in private Drive. Every candidate remains pending until the complete rights chain is reviewed. Duration and catalogue metadata are triage evidence only, not proof that a recording is safe for commercial synchronization.

## Reusing the runner for other agents

Use .github/workflows/reusable-private-agent.yml only for independent agents with separate private Drive namespaces, secrets and publication gates. Never share Jazz Soul Beat's production library, credentials or publication channel.


## Three autonomy levels

### Level A — full autonomy inside approved boundaries

The agent may independently research music and visual references, plan work, discover candidates, collect rights evidence, create original artwork and video, perform editorial/media/technical audits, correct reproducible defects, retry transient failures with bounded attempts, maintain operational memory, report KPIs and optimize internal workflows that do not change fundamental policy.

### Level B — conditional autonomy

The agent may reorder priorities, propose formats, test alternative compositions, adjust internal processes, run isolated experiments and recommend calendar or architecture improvements. It must record the reason, scope, evidence and rollback path. Changes affecting policy, identity, security or publication permissions require human approval.

### Level C — reserved human decisions

The following actions are denied by default and require explicit human approval:
- Approve music rights or change any rights status from PENDING to APPROVED.
- Upload to YouTube, including private upload, or publish publicly.
- Schedule a public/social publication.
- Change the approved visual identity or replace the approved character reference.
- Change fundamental security policy, permissions or approval rules.
- Activate paid services, subscriptions, billing or expenditure.
- Delete important data or perform irreversible external actions.
- Contact rights holders or providers on the user's behalf.

Internal GitHub Actions schedules are operational infrastructure and may run autonomously; this is distinct from scheduling a public post.

## Version-bound approval

Any human approval must identify the action and exact SHA-256 of the artifact reviewed. If the video, audio, thumbnail, metadata or other material element changes after approval, the approval no longer applies and a new review is required. Unknown actions are denied by default. Every allow/deny decision is stored in the autonomy audit ledger.

The `autonomy-approve` command records an explicit approval; `autonomy-check` evaluates it. An approval for one file version must never authorize a modified version.

## Stop, recover and continue

| Situation | Required behavior |
|---|---|
| Temporary network/API failure | Bounded retry with backoff; record outcome |
| Technical/rendering failure | Try a different safe strategy; run regression checks |
| Rights evidence incomplete or contradictory | Keep the track pending; continue unrelated work |
| Human approval required | Block only that action; continue other safe tasks |
| Missing approved visual reference | Do not invent or replace it; flag the dependency |
| Free resource unavailable/quota exhausted | Pause that task or use an already approved free alternative; never enable billing |
| Important state cannot be restored | Stop state-mutating work and preserve evidence |

## Three operational memory layers

- **Operational memory:** task queue, checkpoints, decisions, blockers, retries and artifacts.
- **Creative memory:** approved character/visual references, scene continuity, music direction and production preferences.
- **Learning memory:** measured results, root causes, corrective actions, regression outcomes and recurring defects.

These records are persisted in the private SQLite database in Google Drive. The agent may maintain operational and learning records but may not rewrite its own permission boundaries or fundamental brand rules.

## Governance implementation

The private agent contains:
- `autonomy.py`: allow/deny policy, audit trail and SHA-256-bound human approvals.
- `performance.py`: historical event ledger, KPI calculations and JSON/Markdown reports.
- `pdca.py`: persistent Plan/Do/Check/Act cycle records, evidence and corrective actions.

The cloud controller uses reusable PDCA actions around production, discovery, review audits and manual agent jobs. State is restored before a cycle and persisted to private Drive after ACT. The code is considered operational only after the corresponding cloud run and regression tests pass.
