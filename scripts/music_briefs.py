"""English-language creative briefs for original, non-repetitive jazz/soul auditions.

A brief expresses *musical direction*, not evidence that the generated audio
sounds good. No music enters a video without a separate human creative review.
"""
from __future__ import annotations

from dataclasses import dataclass

COMMON = (
    "Original composition; no cover, quoted melody, known artist imitation, or sampling. "
    "A convincing adult professional jazz/soul ensemble with a complete band sound, human-feeling microtiming, dynamic breath, "
    "intentional silence, melodic development and a natural ending. "
    "No synth test tones, cheap chiptune or arpeggiator loops. "
    "Professional coherent harmonic movement; melodic conversation and subtle variations. Quiet late-night listening only: no dance groove, funk, disco, boogie, bossa, upbeat shuffle, hip-hop beat, vocals or spoken words."
)

QUALITY_FLOOR = (
    "This must be materially better than the approved minimum baseline, not merely equal to it. "
    "Use a complete professional ensemble, convincing harmonic movement, clear melodic development, "
    "balanced dynamics and a resolved ending. Reject demo-like two-instrument sketches, generic loops, "
    "thin arrangements, abrupt rhythm changes and any passage that sounds unfinished. "
    "The genre identity must be audible in harmony, phrasing, rhythm, instrumentation and arrangement, "
    "not inferred from the title or atmosphere. Future candidates must improve on the listener-approved reference candidates."
)

GENRE_SIGNATURES = {
    "soft_jazz": (
        "Authentic soft jazz identity: extended major-7, minor-7, dominant-9/13 and ii-V-I movement; "
        "intentional comping, melodic improvisation and restrained brush swing or straight-eighth phrasing."
    ),
    "soft_soul": (
        "Authentic soft soul identity: warm Rhodes/Wurlitzer color, expressive gospel-informed 7th/9th harmony, "
        "human pocket, call-and-response phrasing and restrained ensemble dynamics without a pop or dance chorus."
    ),
    "soft_lofi": (
        "Authentic soft lo-fi identity: jazz harmony and a complete live-feeling ensemble remain primary; "
        "tape/room texture is subtle secondary character, never a repetitive beat loop or a substitute for composition."
    ),
}

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
        if type(duration_seconds) is not int or not 240 <= duration_seconds <= 480:
            raise ValueError("Only 240–480 second song auditions are permitted.")
        return (
            f"{duration_seconds}-second original instrumental jazz/soul song. "
            f"Title: {self.title}. Tempo approximately {self.bpm} BPM, key {self.key}. "
            f"{self.ensemble} {self.arrangement} {self.sound} {GENRE_SIGNATURES.get(self.slug, '')} {QUALITY_FLOOR} {COMMON} "
            "Structured original full song, not background music created by looping a short passage."
        )

BRIEFS = {
    "work_study": Brief(
        "work_study", "The Last Page of the Night", 72, "C major",
        "Acoustic piano, Rhodes, upright bass, brushed drums, clean hollowbody guitar, quiet tenor sax, muted trumpet, vibraphone and discreet Hammond organ.",
        "Short instrumental intro, memorable spacious theme, subtle development, contrasting middle section, "
        "improvised piano response, final restatement and proper ending.",
        "Focused background listening: musical but low-fatigue, no piercing lead or sudden dynamics.",
    ),
    "coffee_time": Brief(
        "coffee_time", "Rain on the Café Window", 78, "F major",
        "Expressive warm grand piano, natural upright bass, brushed kit, mellow muted trumpet.",
        "Eight-bar piano introduction; lyrical 16-bar A theme; answered A variation; contrasting bridge "
        "with jazz guitar comping; lyrical restrained trumpet improvisation; return to theme; resolved outro.",
        "Warm intimate coffeehouse studio sound, soft straight-eighth pocket, gentle pulse and low dynamics.",
    ),
    "sleep": Brief(
        "sleep", "When the City Sleeps", 66, "B flat major",
        "Soft acoustic grand piano, Rhodes, warm double bass, delicate brushed percussion, clean guitar, sparse mellow flugelhorn, vibraphone and quiet strings.",
        "Patient introductory motif, flowing long phrases, slow harmonic answers, lyrical bridge, "
        "subtle variation, increasingly quiet reprise and gentle full resolution.",
        "Sleep-friendly slow jazz ballad, understated textures, seamless musical flow without repetition.",
    ),
    "chill": Brief(
        "chill", "Blue Hour Conversations", 84, "D minor",
        "Electric piano, acoustic piano, expressive tenor saxophone, melodic upright bass, brushed jazz drums, warm guitar, muted trumpet and restrained vibraphone.",
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

GENRE_BRIEFS = {
    "jazz": Brief(
        "soft_jazz", "Blue Room After Midnight", 70, "C major",
        "Acoustic grand piano, Rhodes, upright bass, brushed jazz kit, hollowbody guitar, tenor saxophone, muted trumpet, vibraphone and subtle Hammond organ.",
        "Lyrical 16-bar theme, conversational piano and sax responses, a restrained improvised middle, harmonic bridge, return and carefully shaped coda.",
        "Late-night straight-eighth jazz with sophisticated voicings, human swing inflection without a driving groove, warm room ambience and low fatigue.",
    ),
    "soul": Brief(
        "soft_soul", "Velvet Window Light", 72, "F major",
        "Rhodes and acoustic piano, warm electric and upright bass, brushed drums, clean guitar, muted trumpet, tenor saxophone, vibraphone and restrained Hammond organ.",
        "Patient verse-like theme, soulful call and response, tasteful harmonic lift, instrumental keyboard and sax conversation, reprise and resolved outro.",
        "Quiet sophisticated soul-jazz with gospel-informed harmony, deep pocket at low energy, no pop chorus, no funk or dance emphasis, natural band interaction.",
    ),
    "lofi": Brief(
        "soft_lofi", "Dusty Lamp on the Desk", 68, "B flat major",
        "Felt piano, Rhodes, upright bass, brushed drums, muted jazz guitar, soft tenor saxophone, vibraphone and very subtle tape warmth.",
        "Sparse but complete opening, evolving jazz theme, gentle variations, a short contrasting bridge, understated solo exchange, reprise and quiet ending.",
        "Lo-fi texture used only as tasteful room character over real jazz harmony and a complete ensemble; never a beat loop, hip-hop groove, vinyl gimmick or two-instrument demo.",
    ),
}

def choose_brief(slug: str) -> Brief:
    if not isinstance(slug, str) or slug not in BRIEFS:
        raise ValueError("Unsupported music category. Must be one of: " + ", ".join(BRIEFS))
    return BRIEFS[slug]

def choose_genre_brief(genre: str) -> Brief:
    if not isinstance(genre, str) or genre not in GENRE_BRIEFS:
        raise ValueError("Unsupported production genre. Must be one of: " + ", ".join(GENRE_BRIEFS))
    return GENRE_BRIEFS[genre]
