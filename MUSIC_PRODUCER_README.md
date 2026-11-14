# Jazz Soul Beat — Free-Only Original Music Producer

The real music producer is `.github/workflows/music-producer.yml`. It requests a standalone 240-second original jazz/soul audition from the free `Blursed/Ace-Step-v1.5` ZeroGPU Space, using `acestep-v15-turbo`. It automatically rotates through five English-language briefs (coffee, study, sleep, chill, Christian instrumental) on Tuesday, Thursday, and Saturday, 08:30 America/Bogota. GH schedule delays and Hugging Face quotas may prevent production; **three videos per week are not yet available**.

## Verified operational history — 2026-11-14

- Run [43642680136](https://github.com/dacorot/jazzsoulbeat-cloud-runner/actions/runs/43642680136): one **real model-generated 180-second jazz/soul audio**, SHA-256 `84169a019eb2e48f171d0c9a99ec1fd4906a8206ac9647712ffb7cce243f2200`, 48 kHz stereo, stored in private Drive.
- [Private waveform QA](https://github.com/dacorot/jazzsoulbeat-cloud-runner/actions/runs/43643173313): passed duration, SHA-256, presence of audio, mean level −14.3 dB, peak 0.0 dB and no extended silence. **This is technical QC only; musical merit is unverified.**
- Run [43643343102](https://github.com/dacorot/jazzsoulbeat-cloud-runner/actions/runs/43643343102): second 240-second attempt failed due **free ZeroGPU quota** (provider said 180 seconds requested, 145 seconds remaining; retry after about 9 hours). No paid fallback. The free service cannot guarantee schedule or throughput.
- Earlier Space/XL runs failed due missing initialized model and provider CPU–GPU tensor mismatch. These are upstream provider errors.
- The procedural 512-bar synthesizer was explicitly **rejected** by the channel owner. It is a test fixture, not a release-quality music generator.

## Technical constraints

- No paid infrastructure, credits, subscriptions, local computer, third-party samples, public GitHub music artifacts, or automatic rights approval.
- On a successful external run: require exact media SHA-256, valid MP3 stream and duration, waveform QA, private Google Drive persistence; failed uploads must cause workflow failure.
- Audio always stays `PENDING_HUMAN_LISTENING`, with `eligible_for_video_assembly: false` and `rights_verified: false`. Technical tests never promote it.
- Exact-video human SHA-256 approval is required before **private YouTube upload**. All public/social publication and public scheduling are explicitly disabled.
- Each individual original song must be independently accepted before it can enter the longform library; looping a short song to simulate two hours is prohibited.

## Commands

```bash
python -m unittest discover -s tests -p 'test_music*.py' -v
python -m scripts.music_producer_agent
python -m scripts.music_audio_qc --report music-production/production_report.json
```

The generator command requires a currently functional free ZeroGPU Space, while the QA suite uses mocked external services and never incurs external calls.
