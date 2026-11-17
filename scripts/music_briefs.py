"""English-language creative briefs for original, non-repetitive jazz/soul auditions.

A brief expresses *musical direction*, not evidence that the generated audio
sounds good. No music enters a video without a separate human creative review.
"""
from __future__ import annotations

from dataclasses import dataclass

COMMON = (
    "Original composition; no cover, quoted melody, known artist imitation, or sampling. "
    "A convincing adult jazz ensemble with human-feeling microtiming, dynamic breath, "
    "intentional silence, melodic development and a natural ending. "
    "No synth test tones, cheap chiptune or arpeggiator loops. "
    "Professional coherent harmonic movement; melodic conversation and subtle variations."
)

@dataclass(frozen=True)
class Brief:
    slug: str
    title: str
    bpm: int
    key: str
    ensemble: str
    arrangement: str
    sound: str

    def prompt(self, duration_seconds: int) -> str:
        if type(duration_seconds) is not int or not 180 <= duration_seconds <= 360:
            raise ValueError("Only 180–360 second song auditions are permitted.")
        return (
            f"{duration_seconds}-second original instrumental jazz/soul song. "
            f"Title: {self.title}. Tempo approximately {self.bpm} BPM, key {self.key}. "
            f"{self.ensemble} {self.arrangement} {self.sound} {COMMON} "
            "Structured original full song, not background music created by looping a short passage."
        )

BRIEFS = {
    "work_study": Brief(
        "work_study", "The Last Page of the Night", 72, "C major",
        "Rhodes with acoustic piano touches, upright bass, restrained brushed drums and subtle hollowbody guitar.",
        "Short instrumental intro, memorable spacious theme, subtle development, contrasting middle section, "
        "improvised piano response, final restatement and proper ending.",
        "Focused background listening: musical but low-fatigue, no piercing lead or sudden dynamics.",
    ),
    "coffee_time": Brief(
        "coffee_time", "Rain on the Café Window", 78, "F major",
        "Expressive warm grand piano, natural upright bass, brushed kit, mellow muted trumpet.",
        "Eight-bar piano introduction; lyrical 16-bar A theme; answered A variation; contrasting bridge "
        "with jazz guitar comping; lyrical restrained trumpet improvisation; return to theme; resolved outro.",
        "Warm intimate coffeehouse studio sound, natural swing, soft touch, gentle groove.",
    ),
    "sleep": Brief(
        "sleep", "When the City Sleeps", 66, "B flat major",
        "Soft acoustic grand piano, warm double bass, delicate brushed percussion, sparse mellow flugelhorn.",
        "Patient introductory motif, flowing long phrases, slow harmonic answers, lyrical bridge, "
        "subtle variation, increasingly quiet reprise and gentle full resolution.",
        "Sleep-friendly slow jazz ballad, understated textures, seamless musical flow without repetition.",
    ),
    "chill": Brief(
        "chill", "Blue Hour Conversations", 84, "D minor",
        "Electric piano, expressive tenor saxophone, melodic upright bass, brushed jazz drums and warm guitar.",
        "Distinctive main melody, answer phrase, evolving verse, short minor-major contrasting bridge, "
        "tasteful sax improvisation, resolved chorus return and shaped instrumental outro.",
        "Sophisticated late-night soul jazz, understated pocket and human rhythmic tension.",
    ),
    "christian_jazz_worship": Brief(
        "christian_jazz_worship", "Grace Before Morning", 70, "G major",
        "Acoustic grand piano, warm upright bass, subtle gospel-influenced organ pads and brushed drums.",
        "Reverent opening theme, hopeful response, uplifting gospel-jazz harmonic bridge, "
        "gentle piano solo, resolved theme and peaceful coda. Instrumental audition only; lyric production "
        "requires a separate English-language biblical review path.",
        "Quiet worshipful jazz rooted in consolation, gratitude and hope; elegant, not theatrical. "
        "Do not quote or imitate copyrighted worship songs.",
    ),
}

def choose_brief(slug: str) -> Brief:
    if not isinstance(slug, str) or slug not in BRIEFS:
        raise ValueError("Unsupported music category. Must be one of: " + ", ".join(BRIEFS))
    return BRIEFS[slug]
