# Jazz Soul Beat — operational agent inventory

The project has 13 technical readiness controls. Four additional dedicated agents were added in this change to close the production chain:

| Agent | Responsibility | Safety boundary |
|---|---|---|
| rights_provenance_agent | Triage source URLs, licenses and provenance evidence | Read-only; never grants rights approval |
| scene_library_agent | Validate the private scene-image library and minimum coverage | Never replaces the approved base image |
| video_assembly_agent | Plan long-form assembly from approved audio and visual inputs | Planning only; publication disabled |
| release_qa_agent | Hash and independently inspect final media | Human review required; no publication |

Existing controls cover category briefs, scheduling, music discovery, audio production, visual motion, long-form library gating, approval handling, delivery coordination and PDCA/preflight.

The suite does not claim that the project is production-ready while approved audio, approved scene assets or human review are missing. A technical READY result means the agents can run and enforce those gates.

The music_dedup_agent is mandatory for every search lane. It compares SHA-256, source URL and normalized title/creator/duration against existing catalogs before any download; it never approves rights.
