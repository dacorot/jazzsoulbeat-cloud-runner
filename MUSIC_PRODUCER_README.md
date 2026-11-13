# Jazz Soul Beat — Original Music Producer

This cloud workflow attempts to generate an original instrumental using the public ACE-Step 1.5 Hugging Face Space through Gradio's API.

## Cost and safety
- Free-only: no paid API, hosted GPU rental, subscription, or local computer required.
- The public Space may have ZeroGPU quotas, queue limits, downtime, or API changes. A failed/blocked run is reported; there is no paid fallback.
- Optional `HF_TOKEN` repository secret can identify a free Hugging Face account and may improve access/quota. Do not use a paid token or enable billing.
- The workflow does not publish or distribute anything.
- Audio is delivered as a GitHub Actions artifact for 30 days; download it before expiry.
- A model license does not guarantee that every generated output is unique or automatically cleared. Listen, check similarity, retain the prompt/model/version evidence, and review commercial-use terms before release.

## First composition
**Midnight Has a Soul** — 84 BPM, D minor, sophisticated contemporary jazz soul, piano lead, tenor saxophone responses, upright bass, brushed drums, original melody, no vocals, no artist imitation. Target duration: 180 seconds.

## Run
GitHub → Actions → **Jazz Soul Beat - Original Music Producer** → Run workflow.
The workflow is also triggered by a commit that changes `MUSIC_PRODUCER_START.md`.

## Output
Artifact: `jazz-soul-beat-original-music`
- `generated/`: generated audio, if successful
- `production_report.json`: result, prompt, engine, endpoint and status
- `space_api_snapshot.json`: API diagnostics if generation is blocked
