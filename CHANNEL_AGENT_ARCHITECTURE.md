# Jazz Soul Beat — Category Agent Architecture

## Decision
Jazz Soul Beat is organized as five editorial playlist profiles, not one generic music producer. Each profile owns its playlist identity, musical direction, composition brief, arrangement rules and category-specific quality review. They share a single production scheduler, engine router, quality system and private catalog. The original four-agent taxonomy remains only as a legacy compatibility map.

## Category agents
1. **Work & Study** — focused, low-fatigue jazz for concentration and reading.
2. **Coffee Time** — warm, sophisticated café jazz with an organic pulse.
3. **Sleep** — delicate, quiet jazz with controlled dynamics and gentle resolution.
4. **Chill** — elegant late-night jazz/soul with atmospheric but human-feeling phrasing.
5. **Christian Jazz & Worship** — original English lyrics or instrumental worship jazz with separate lyric and rights review.

The machine-readable profiles live in `config/channel_agents.json`. They are the source of truth for each agent's identity and constraints.

## Shared production pipeline
Each category agent sends a structured brief to the common pipeline:
1. Category director chooses the emotional and musical objective.
2. Composer/arranger prepares a distinct melody, harmony, instrumentation and song structure.
3. Engine router checks free availability, current quota, model version, runtime and commercial-use conditions.
4. Exactly one generation job runs at a time to avoid wasting free GPU quota.
5. Audio QA measures and checks the generated file.
6. Rights/provenance review records the exact model, weights, host, version, prompt, date and applicable terms.
7. Catalog manager stores approved audio and its evidence in the permanent private library.

## Failover rules
- ACE-Step is currently the first integration attempt, not the only approved engine.
- HeartMuLa, Magenta RealTime and DiffRhythm are candidates, not production-ready engines until their exact free execution path, model/weight terms and output workflow are tested.
- Do not use a candidate just because its source code is open. Check code license, weight license, host terms, account limits and output rights separately.
- Run a lightweight availability/API preflight before spending GPU time.
- Do not run several GPU generators in parallel on a shared free quota.
- A failed engine must not block the other category agents from preparing briefs, lyrics, arrangements, QA rules or catalog work.
- Never enable paid billing or paid fallback.

## Production target
The planning target is 12 approved songs per month, approximately one per day. This is a target, not a promise that free GPU quotas can guarantee it. Track attempts, successful generations, approved songs and remaining quota separately.

## Publication and storage safeguards
- No public upload or distribution without explicit user authorization.
- GitHub Actions artifacts are temporary diagnostics/output handoff, not permanent music storage.
- Do not mark a song approved until it has passed technical checks, rights/provenance checks and human listening review.
- Christian lyric content must be original, coherent and in English. Record Psalm/Proverb references; verify any quoted Bible translation before commercial release.

## Current implementation status
This file and the category profiles define the architecture and musical policies. The five editorial profiles are operationally represented and covered by readiness checks; generation, rights approval, permanent private storage and publication remain deliberately gated. The ACE-Step generation workflow remains an unverified first engine integration, while approved audio is still insufficient for the one-hour target.
