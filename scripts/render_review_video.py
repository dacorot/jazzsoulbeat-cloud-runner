#!/usr/bin/env python3
"""Render a short QHD audiovisual audition without granting approval."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _integrated_rain_layers(image_path: Path, width: int, height: int):
    """Extract the rain already painted into the approved plate.

    This deliberately does not draw synthetic lines over the room.  It derives
    a transparent highlight texture from the source artwork and later moves
    only that texture inside the glass panes.  Window mullions, piano, table,
    cup and furniture therefore remain part of the locked background plate.
    """
    base = Image.open(image_path).convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
    panes = ((307, 0, 365, 222), (372, 0, 429, 222),
             (437, 0, 496, 222), (504, 0, 564, 222), (572, 0, 640, 222))
    layers = []
    for left, top, right, bottom in panes:
        # Keep only bright, narrow vertical structures.  A broad brightness
        # threshold would also capture lamps/cars/buildings and would produce
        # the rectangular ghosts seen in the rejected texture experiment.
        pane_alpha = Image.new("L", (width, height), 0)
        alpha_px = pane_alpha.load()
        rgb = base.load()
        for y in range(top + 1, bottom - 1):
            for x in range(left + 1, right - 1):
                r, g, b = rgb[x, y]
                lum = (r + g + b) // 3
                left_lum = sum(rgb[x - 1, y]) // 3
                right_lum = sum(rgb[x + 1, y]) // 3
                contrast = lum - max(left_lum, right_lum)
                alpha_px[x, y] = min(150, max(0, (contrast - 10) * 12)) if lum > 90 else 0
        # Slightly soften the extracted marks; sharp highlights remain in the
        # source and the moving component should read as wet glass, not sparks.
        pane_alpha = pane_alpha.filter(ImageFilter.GaussianBlur(0.35))
        cool = Image.new("RGBA", (width, height), (190, 225, 245, 0))
        cool.putalpha(pane_alpha)
        layers.append((cool, (left, top, right, bottom)))
    return layers


def _make_motion_frames(folder: Path, *, width: int = 640, height: int = 360,
                        fps: int = 12, cycle_seconds: int = 60,
                        rain_mode: str = "procedural_window",
                        image_path: Path | None = None) -> None:
    """Create a lightweight transparent 60-second ambient-motion layer.

    Coordinates are intentionally tied to the supplied cafe composition: the
    right side is the window, and the lower-left cup receives steam. The layer
    is transparent everywhere else so it does not redraw the artwork.
    """
    folder.mkdir(parents=True, exist_ok=True)
    frame_count = fps * cycle_seconds
    # Keep rain inside individual panes.  The integrated plate has a broad
    # window wall on the right; the legacy plate uses only its upper-right
    # panes.  Lower furniture remains outside the animated region.
    if rain_mode == "integrated_plate":
        panes = ((300, 0, 382, 205), (392, 0, 474, 205),
                 (484, 0, 566, 205), (576, 0, 640, 205))
    elif rain_mode == "masked_window":
        # Conservative clean-window-v2 mask: stop above furniture until a
        # depth matte exists, so rain can never cross interior objects.
        panes = ((314, 0, 365, 225), (368, 0, 421, 225),
                 (424, 0, 476, 225), (480, 0, 531, 225),
                 (536, 0, 588, 225), (594, 0, 640, 225))
    else:
        panes = ((452, 0, 492, 108), (500, 0, 640, 108))
    rain = []
    integrated_layers = (_integrated_rain_layers(image_path, width, height)
                         if rain_mode == "integrated_plate" and image_path else [])
    if rain_mode in {"procedural_window", "masked_window"}:
        for i in range(72):
            left, top, right, bottom = panes[i % len(panes)]
            rain.append((left + (i * 17) % max(1, right - left),
                         top + (i * 29) % max(1, bottom - top),
                         7 + (i * 11) % 15, 0.8 + (i % 4) * 0.18,
                         (i * 3) % len(panes)))
    for frame in range(frame_count):
        t = frame / fps
        layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer, "RGBA")

        if rain_mode == "integrated_plate" and integrated_layers:
            # Animate highlights extracted from the plate.  Each pane has its
            # own slow phase so the glass does not look like one looping card.
            for index, (rain_layer, box) in enumerate(integrated_layers):
                left, top, right, bottom = box
                shift = int((t * (4.5 + index * 0.8) + index * 17) % (bottom - top))
                shifted = ImageChops.offset(rain_layer, 0, shift)
                pane = shifted.crop((left, top, right, bottom))
                pane_full = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                pane_full.paste(pane, (left, top), pane)
                layer = Image.alpha_composite(layer, pane_full)

        if rain_mode in {"procedural_window", "masked_window"}:
            # Rain remains behind the window frame area rather than covering the room.
            for x, y0, length, slope, pane_index in rain:
                left, top, right, bottom = panes[pane_index]
                y = top + ((y0 - top + t * (24 + (x % 5) * 4)) % (bottom - top))
                x_now = x + int(2 * __import__("math").sin(t * 0.7 + x))
                rain_alpha = 115
                draw.line((x_now, y, x_now - 2, min(bottom - 1, y + length)),
                          fill=(190, 221, 244, rain_alpha), width=1)
                if y < top + 12:
                    drop_alpha = 70 if rain_mode == "masked_window" else 60
                    draw.ellipse((x_now - 2, y, x_now + 3, y + 5), fill=(220, 235, 248, drop_alpha))

        # Steam is built from soft, deforming translucent vapor pockets rather
        # than bright strokes.  This gives it a diffuse, rising shape and
        # avoids the artificial "drawn smoke" appearance.
        steam = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        steam_draw = ImageDraw.Draw(steam, "RGBA")
        import math
        # Motion geometry is scene-specific.  The integrated rain plate has
        # the cup in the lower centre; the legacy library plate has it lower
        # left.  Never reuse one scene's coordinates for another image.
        steam_bases = (288, 298, 308) if rain_mode in {"integrated_plate", "masked_window"} else (139, 149, 159)
        steam_rim = 270 if rain_mode in {"integrated_plate", "masked_window"} else 234
        for index, x_base in enumerate(steam_bases):
            phase = t * (0.62 + index * 0.08) + index * 1.9
            for puff in range(9):
                rise = (phase * 18 + puff * 10) % 70
                y = steam_rim - rise
                x = x_base + 8 * math.sin(phase + puff * 0.75)
                width_puff = 8 + int(5 * (0.5 + 0.5 * math.sin(phase + puff)))
                height_puff = 10 + int(6 * (0.5 + 0.5 * math.cos(phase * 1.2 + puff)))
                alpha = max(18, int(88 * (1 - rise / 88)))
                steam_draw.ellipse((x - width_puff, y - height_puff,
                                    x + width_puff, y + height_puff),
                                   fill=(255, 244, 225, alpha))
        layer = Image.alpha_composite(layer, steam.filter(ImageFilter.GaussianBlur(7.0)))

        # A small sharper core gives the vapor a readable origin and contour;
        # the broad blurred puffs above provide the softer diffusion.
        steam_core = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        core_draw = ImageDraw.Draw(steam_core, "RGBA")
        for index, x_base in enumerate(steam_bases):
            points = []
            for step in range(25):
                rise = (t * (5.0 + index * 0.6) + index * 9) % 48
                y = steam_rim - rise - step * 1.9
                x = x_base + 4.5 * math.sin(t * 0.75 + step * 0.33 + index)
                points.append((x, y))
            core_alpha = 140 if rain_mode in {"integrated_plate", "masked_window"} else 92
            core_draw.line(points, fill=(255, 246, 230, core_alpha), width=2)
        core_blur = 1.6 if rain_mode in {"integrated_plate", "masked_window"} else 2.5
        layer = Image.alpha_composite(layer, steam_core.filter(ImageFilter.GaussianBlur(core_blur)))

        # Slow, broad warm reflections from the lamps and candles.  They are
        # blurred and confined to the room/table, so the scene visibly breathes
        # without adding floating dots or lighting the rain itself.
        glow = int(10 + 13 * (0.5 + 0.5 * math.sin(t * 0.20)))
        reflections = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        reflection_draw = ImageDraw.Draw(reflections, "RGBA")
        if rain_mode in {"integrated_plate", "masked_window"}:
            reflection_draw.ellipse((35, 245, 210, 390), fill=(255, 151, 66, glow))
            reflection_draw.ellipse((250, 275, 430, 380), fill=(255, 188, 96, max(5, glow - 3)))
            reflection_draw.rectangle((80, 325, 500, 358), fill=(255, 166, 70, max(4, glow // 2)))
        else:
            reflection_draw.ellipse((36, 210, 205, 390), fill=(255, 151, 66, glow))
            reflection_draw.ellipse((430, 190, 610, 375), fill=(255, 188, 96, max(5, glow - 3)))
            reflection_draw.rectangle((100, 319, 430, 355), fill=(255, 166, 70, max(4, glow // 2)))
        layer = Image.alpha_composite(layer, reflections.filter(ImageFilter.GaussianBlur(24)))

        layer.save(folder / f"frame-{frame:05d}.png", compress_level=1)


def render(audio: Path, image: Path, output: Path, duration: int,
           rain_mode: str = "procedural_window") -> dict:
    if not audio.is_file() or not image.is_file():
        raise FileNotFoundError("Audio e imagen deben existir")
    if not 180 <= duration <= 360:
        raise ValueError("La audición debe durar entre 180 y 360 segundos")
    if rain_mode not in {"procedural_window", "integrated_plate", "masked_window"}:
        raise ValueError("rain_mode inválido")
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise RuntimeError("FFmpeg y FFprobe son obligatorios")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Render to a sibling temporary file.  A cancelled or failed FFmpeg run
    # must never leave a file at the final path that looks publishable.
    # Keep the real media suffix so FFmpeg can infer the muxer.  A name such
    # as ``video.mp4.part`` is rejected because its final suffix is unknown.
    partial = output.with_name(output.stem + ".part" + output.suffix)
    partial.unlink(missing_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="jsb-motion-") as temp:
            motion_dir = Path(temp) / "frames"
            _make_motion_frames(motion_dir, rain_mode=rain_mode, image_path=image)
            # Keep the base plate fixed while the effects are layered.  A moving
            # zoom on the plate with a fixed motion layer misregisters the window
            # mask and makes rain appear inside the room.
            vf = (
                "scale=2560:1440:force_original_aspect_ratio=increase,"
                "crop=2560:1440[bg];"
                "[1:v]scale=2560:1440:flags=bicubic[fx];"
                "[bg][fx]overlay=0:0:format=auto:shortest=1,format=yuv420p[vout]"
            )
            subprocess.run([
                ffmpeg, "-nostdin", "-y", "-loglevel", "error", "-loop", "1", "-i", str(image),
                "-framerate", "12", "-stream_loop", "-1", "-i", str(motion_dir / "frame-%05d.png"),
                "-i", str(audio), "-map", "[vout]", "-map", "2:a:0", "-filter_complex", vf,
                "-t", str(duration), "-r", "12", "-c:v", "libx264", "-preset", "veryfast",
                "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                "-ar", "48000", "-movflags", "+faststart", str(partial),
            ], check=True)
        probe = subprocess.run([
            ffprobe, "-v", "error", "-show_entries",
            "stream=codec_type,codec_name,width,height,channels:format=duration",
            "-of", "json", str(partial),
        ], check=True, capture_output=True, text=True)
        output_data = json.loads(probe.stdout)
        partial.replace(output)
    finally:
        partial.unlink(missing_ok=True)
    data = output_data
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    sound = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    actual = float(data.get("format", {}).get("duration", 0))
    if not video or (video.get("width"), video.get("height")) != (2560, 1440):
        raise RuntimeError(f"Resolución QHD no verificada: {video}")
    if not sound or sound.get("codec_name") != "aac" or sound.get("channels") != 2:
        raise RuntimeError(f"Audio estéreo AAC no verificado: {sound}")
    if abs(actual - duration) > 2:
        raise RuntimeError(f"Duración inesperada: {actual}")
    return {
        "status": "PRIVATE_REVIEW_ONLY_NOT_APPROVED",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "audio": str(audio), "audio_sha256": digest(audio),
        "image": str(image), "image_sha256": digest(image),
        "video": str(output), "video_sha256": digest(output),
        "duration_seconds": actual, "width": 2560, "height": 1440,
        "audio_codec": "aac", "video_codec": "h264", "fps": 12,
        "motion_profile": ("integrated_plate-extracted-rain-texture-steam-reflections"
                           if rain_mode == "integrated_plate" else
                           "masked-window-exterior-rain-steam-reflections"
                           if rain_mode == "masked_window" else
                           f"{rain_mode}-steam-reflections"),
        "motion_cycle_seconds": 60,
        "ambient_motion": (["exterior rain confined to upper window panes", "clean animated coffee steam", "subtle warm reflections"]
                            if rain_mode == "masked_window" else
                            ["integrated exterior rain", "clean animated coffee steam", "subtle warm reflections"]
                            if rain_mode == "integrated_plate" else
                            ["rain confined to window panes", "clean animated coffee steam", "subtle warm reflections"]),
        "creative_approval": False, "rights_verified": False,
        "eligible_for_video_assembly": False, "youtube_upload": "NOT_AUTHORIZED",
        "publication": "DISABLED",
        "note": "Short listening audition only; not a 2–3 hour master and not publication-approved.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--duration", type=int, default=240)
    parser.add_argument("--rain-mode", choices=("procedural_window", "integrated_plate", "masked_window"),
                        default="procedural_window")
    args = parser.parse_args()
    report = render(args.audio, args.image, args.output, args.duration, args.rain_mode)
    report_path = args.output.with_suffix(".review.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
