# Jazz Soul Beat — Asset Management Policy

All agents must follow this policy.

## Canonical locations

- `tracks/`: approved production audio and manifests.
- `tracks/review/`: unapproved audio under review; never select for production.
- `tracks/seasonal/<season>/`: approved seasonal audio only.
- `assets/visual-agents/`: reusable visual assets, scenes and motion sources.
- `output/<run-id>/`: one production run and its derived video, audio, thumbnail and manifests.
- `output/asset-inventory/`: searchable hash-bound inventory.
- `output/<domain>/`: reports and evidence for that domain.
- `data/agent.db`: derived index only; manifests remain authoritative.
- Private Drive: runtime state, review media, evidence and reports.
- GitHub: source code, workflows, policies and lightweight manifests only.

## Required behavior

1. Search `output/asset-inventory/asset-inventory.json` before creating or downloading an asset.
2. Reuse an existing SHA-256 match instead of creating a duplicate.
3. Give every generated asset a stable run ID, semantic name, type, status and provenance.
4. Write media and its manifest atomically in the same managed root.
5. Keep review, approved, rejected, quarantine and retired states separate.
6. Never put secrets, tokens, private media or runtime databases in GitHub.
7. Never move, rename or delete an asset without a hash-bound migration report.
8. Update the inventory after every approved mutation.
9. Do not select an asset for production unless its status is explicitly approved.
10. Persist reports and checkpoints to private Drive.

## Status vocabulary

DISCOVERED, REVIEW_ONLY, RIGHTS_PENDING, CREATIVE_PENDING,
APPROVED_PENDING_IMPORT, ACTIVE_APPROVED, SEASONAL_MANAGED,
EVIDENCE_OR_MANIFEST, QUARANTINED, REJECTED, RETIRED.

## Ownership

The orchestrator enforces this policy. The reconciliation agent maintains the
music inventory. The asset inventory agent maintains the global asset map.
Copyright, visual, production, YouTube and Telegram agents may only write inside
their assigned domain roots and must leave a report.
