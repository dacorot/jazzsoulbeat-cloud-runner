# Jazz Soul Beat — Information Architecture

## Source of truth

| Domain | Canonical source | Runtime copy | Owner |
|---|---|---|---|
| Agent code and workflows | GitHub repositories | Runner checkout | Orchestrator |
| Approved production audio | Private Drive + active manifests | Ephemeral runner | Music reconciliation agent |
| Review candidates | Private Drive review roots | Temporary review checkout | Discovery and rights agents |
| Rights evidence | Private Drive reports, exact hashes and URLs | Runner reports | Copyright agent |
| YouTube channel state | YouTube API/Studio | Audit snapshots in Drive | Channel audit agent |
| Telegram approvals | Private Drive ledger and offset | Runner checkout | Approval agent |
| Conversation continuity | Local handoff plus project context | Session checkout | Continuity protocol |

## Music lifecycle

DISCOVERED -> DOWNLOADED_FOR_REVIEW -> RIGHTS_PENDING -> CREATIVE_PENDING -> APPROVED_PENDING_IMPORT -> ACTIVE_APPROVED -> USED_IN_PRODUCTION -> QUARANTINED -> RETIRED

Only ACTIVE_APPROVED may enter production. Candidates are never counted as library capacity.

## Required identity

Every audio item must have:

- stable title and artist;
- collection and season;
- source URL and license evidence URL;
- exact artifact SHA-256;
- duration and readable-audio result;
- composition, performance and recording attestations;
- rights decision and review date.

## Managed roots

- tracks/: active production manifests and imported approved audio.
- tracks/review/: downloaded candidates; never production-ready by location alone.
- tracks/seasonal/<season>/: approved seasonal manifests only.
- output/: reports, plans, audit evidence and hash-bound artifacts.
- data/agent.db: derived runtime index, rebuildable from manifests.
- assets/visual-agents/: visual source library and provenance.

Secrets, tokens, OAuth files and private media never enter GitHub.

## Agent ownership

- orchestrator_agent: sequences work and resumes checkpoints.
- music_reconciliation_agent: reconciles all catalogs, seasonal packages and active manifests.
- rights_decision_agent: accepts complete evidence or rejects ambiguity.
- library_promotion_import_agent: copies only hash-verified approved audio.
- legacy_channel_audit_agent: inventories old YouTube videos read-only.
- legacy_channel_remediation_agent: prepares/applies evidence-backed metadata corrections; never deletes.
- live_stream_agent: checks live readiness and builds daily plans; never starts public streams without gates.
- copyright_watch_agent: rechecks rights changes and quarantines affected material.
- release_coordinator: connects Telegram approval to private upload and scheduling gates.

## Non-negotiable gates

- No candidate is counted as approved capacity.
- No ambiguous rights evidence is auto-accepted.
- No public YouTube change occurs without the corresponding approval manifest.
- No deletion is automatic.
- Every workflow persists its report privately and is idempotent.
- Every cycle records Plan, Do, Check and Act evidence.

## Capacity reporting

Every report must show separately:

- active approved tracks and seconds;
- approved-but-not-imported tracks and seconds;
- seasonal approved tracks by season;
- rights-pending candidates and seconds;
- quarantined or retired items;
- rejected items and reasons.

This prevents a small active manifest from being confused with the total project inventory.
