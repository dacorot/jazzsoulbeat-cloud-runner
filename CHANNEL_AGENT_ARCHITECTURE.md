# Jazz Soul Beat — Category Agent Architecture

## Decision
Jazz Soul Beat is organized as four specialized creative agents, not one generic music producer. Each agent owns its playlist identity, musical direction, composition brief, arrangement rules and category-specific quality review. They share a single production scheduler, engine router, quality system and private catalog.

## Category agents
1. **Midnight Jazz & Soul** — mature, intimate, cinematic late-night jazz-soul; piano, warm tenor sax, upright bass and brushed drums.
2. **Coffee & Smooth Jazz** — relaxed, bright smooth jazz and bossa nova; nylon guitar, piano/Rhodes, light percussion and mellow winds.
3. **Soulful Blues** — expressive blues and soul; electric guitar, Rhodes/piano, Hammond organ and live-feel rhythm section.
4. **Christian Jazz & Gospel** — original English lyrics and spiritually coherent jazz/gospel, rooted in Psalms and Proverbs, with Scripture references and translation-rights checks.

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
This file and the category profiles define the architecture and musical policies. The four agents are not yet independently deployed or proven to generate audio. The ACE-Step generation workflow remains an unverified first engine integration. Permanent private storage and the shared quota-aware scheduler still need implementation and end-to-end tests.
