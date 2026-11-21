Targeted preflight trigger marker. Updating this file runs the private-agent QA workflow.

Regression trigger 2026-11-14: verify exact-folder private production persistence and isolated original-music storage.

Regression trigger 2026-11-14: validate complete-render folder preconditions and exact-folder production Drive persistence.

Regression trigger 2026-11-14: ensure derived camera crops cannot satisfy the eight-independent-original-scenes production gate.

Regression trigger 2026-11-14: reject Windows-style traversal, alternate data streams, NUL bytes and noncanonical filenames in the visual scene manifest; run the full private-agent preflight against the current branch head.

Regression trigger 2026-11-14: re-run full QA after hardening production music-manifest path resolution against symlink substitution and Windows/noncanonical path forms.

Regression round 1 (2026-11-14): strict production license allowlist (CC BY 4.0/CC0 only); reject symlinked playlist roots, folders and sources; enforce exact SHA-256 human approval inside the YouTube upload function; retry resumable YouTube API chunks with bounded Google client retries. Run full private-agent QA, no YouTube upload.

Regression round 1 retry 2026-11-14: corrected license regex escaping after first QA exposed parser regressions; fixed upload test artifact lifetime; rerun all tests against current agent head.

Regression round 1 final rerun 2026-11-14: all source and regression-test fixes committed; validate exact current agent HEAD, including corrected strict-license regex and YouTube upload approval boundary.

Regression round 1 extended data-validation tests 2026-11-14: current private-agent head includes truncated CSV row normalization and rejects non-finite audio duration values; execute complete suite again.

Regression round 1: corrected truncated-manifest test to query the agent's canonical absolute SQLite file key; rerun full QA against latest commit.

Security preflight 2026-11-14: verify production-branch public/social/scheduled publication are absolutely denied even with legacy approval IDs.

Security preflight: reject any future use of the exact owner-rejected 512-bar audio at final FFmpeg mix boundary even when track metadata claims approved. 2026-11-14.

Regression trigger 2026-11-17: execute end-to-end private-agent preflight after public controller readiness expansion; verify compile, tests, self-test FFmpeg, Drive state boundaries and no publication.

Validation trigger: publication idempotency ledger and hash-bound scheduling integration.

Validation trigger: metadata gates, release coordinator and idempotent YouTube boundary.

2026-11-18 safe QA request: validate agent commit 0d3f850477d0c745c7cc073eab63990557486531, especially category-scoped seed recovery with malformed unrelated manifest rows; no music generation, render, rights approval, or upload.

2026-11-19 safe QA: validate private agent publication idempotency ledger commits 5aa90e3 and 464fae2 (strict SHA-256, immutable completed entries, no uploads). Run existing preflight only.

2026-11-21 safe QA: validate Incompetech rights audit fail-closed ISRC evidence commits d2fadaee and 96f56908; full existing tests only, no music generation, rendering, approvals or uploads.
