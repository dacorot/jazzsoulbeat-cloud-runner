# Music source policy — Jazz Soul Beat

Last checked: 2026-11-12

## Openverse

- Official API: https://api.openverse.org/v1/
- Official documentation: https://developer.wordpress.org/openverse/ or https://api.openverse.org/v1/
- Audio search is available through the official API; anonymous access is available with rate and pagination limits.
- The discovery client filters for `license=by,cc0`, `license_type=commercial`, audio category, long audio and supported formats.
- The agent further limits candidates to canonical CC BY 3.0/4.0 or CC0 1.0 license URLs and duration greater than 180 seconds.
- Openverse is an aggregator. It explicitly does not warrant the accuracy of the licensing information. Every source page, uploader authority, composition, performance, master recording, samples, synchronization rights and attribution must still be checked.
- Use the API only. Do not scrape Openverse or bypass its rate limits. Do not parallelize requests to evade rate restrictions.
- The first cloud-runner request returned HTTP 401 without credentials. The agent supports optional OAuth using GitHub Actions secrets `OPENVERSE_CLIENT_ID` and `OPENVERSE_CLIENT_SECRET`. Registration is free but requires a developer application and email verification. These secrets are not currently configured; do not fabricate credentials or treat Openverse as an active source until authenticated access succeeds.
- Discovery is read-only. No downloads, approvals or imports occur in the discovery workflow.

## Jamendo

- Official API documentation: https://developer.jamendo.com/v3.0/docs
- API terms: https://devportal.jamendo.com/api_terms_of_use
- API access requires a developer account and client ID.
- The API terms state that API use is free for non-commercial purposes. Commercial uses, including uses directed toward commercial advantage or advertising revenue, require contacting Jamendo Licensing for a quote.
- Therefore Jamendo's free API is not an approved free source for this monetized YouTube project. Do not integrate it as a free commercial music source or enable paid licensing without the user's explicit approval.

## Non-negotiable intake boundary

A search result, Creative Commons label, API filter, or successful technical audit is not a rights approval. Every candidate remains `PENDING — NOT APPROVED` until the rights evidence and human decision are complete. Never change `rights_verified` or import candidates into production automatically.


## User-submitted leads reviewed on 2026-11-12

### Thematic — Jazz Cafe playlist
- Playlist: https://app.hellothematic.com/playlist/129811
- The playlist page lists 43 songs in jazz-hop, lo-fi jazz and chill styles.
- Thematic's published creator terms require the user's own per-song, per-channel license link in every video description.
- Thematic explicitly prohibits audio-only videos, including playlist videos, visualizers and lyric videos.
- Not approved for Jazz Soul Beat's music-first long-form playlist format. Do not scrape/download or ingest playlist tracks automatically.

### Envato Elements — Lo-fi catalogue and “That Is Lofi”
- Catalogue: https://elements.envato.com/royalty-free-music/lofi
- Item: https://elements.envato.com/that-is-lofi-MYXZMAH
- The item page lists a 2:06 instrumental track by Feetmusic, a subscription starting at USD 16.50/month, BMI affiliation and Content ID claims that require clearing with an Envato license.
- Envato's music terms prohibit use where the value of the video is predominantly derived from the music; its FAQ specifically identifies music-first YouTube videos with a single image or image compilation as not permitted.
- Also conflicts with the project's no-paid-services constraint. Not an approved source.

### Copyright Free Lofi
- Website: https://copyrightfreelofi.com/
- Usage policy: https://copyrightfreelofi.com/usage-policy/
- The published policy permits background music in specified audiovisual/podcast content but prohibits standalone music uploads, music visualizers, music players, lyric videos and similar listening-first content. It also prohibits remixing/editing tracks.
- Not approved for Jazz Soul Beat's music-first playlist format.

These sources may be revisited only if the channel format or the user's no-paid-services constraint changes. They are not part of the production intake queue.
