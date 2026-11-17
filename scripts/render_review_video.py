#!/usr/bin/env python3
"""Render a short QHD audiovisual audition without granting approval."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
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
                        fps: int = 30, cycle_seconds: int = 20,
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
    mullions = ()
    if rain_mode == "integrated_plate":
        panes = ((300, 0, 382, 205), (392, 0, 474, 205),
                 (484, 0, 566, 205), (576, 0, 640, 205))
    elif rain_mode == "masked_window":
        # Clean-window-v2 has five exterior panes. Use the full upper glass
        # plus explicit road bands; these are the areas where the exterior is
        # visible without painting over the café's furniture.
        panes = ((307, 0, 365, 155), (372, 0, 429, 155),
                 (437, 0, 496, 155), (504, 0, 564, 155),
                 (572, 0, 640, 155),
                 (307, 150, 365, 180), (372, 150, 429, 180),
                 (437, 150, 496, 185), (504, 150, 564, 195),
                 (572, 150, 640, 205))
        # The dark vertical mullions are solid foreground structure. A streak
        # may stop at them but must never pass over them.
        mullions = ((365, 372), (429, 437), (496, 504), (564, 572))
    else:
        panes = ((452, 0, 492, 108), (500, 0, 640, 108))
    rain = []
    droplets = []
    base_rgb = (Image.open(image_path).convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
                if rain_mode == "masked_window" and image_path else None)
    exterior_px = None
    if base_rgb is not None:
        # Precompute the exterior/room matte once. Re-evaluating PIL pixels for
        # every streak on every frame makes long reviews needlessly slow.
        exterior = Image.new("1", (width, height), 0)
        source_px = base_rgb.load()
        matte_px = exterior.load()
        for py in range(height):
            for px in range(width):
                r, g, b = source_px[px, py]
                cool_sky = b >= r * 0.75 and b >= g * 0.75
                cool_road = (py >= 145 and b >= r * 0.55 and b >= g * 0.65)
                matte_px[px, py] = 1 if (cool_sky or cool_road) else 0
        exterior_px = exterior.load()
        # Detect every dark, continuous window mullion in the locked plate;
        # the composition contains more intermediate posts than a fixed list
        # can safely describe. Expand each detected column by one pixel.
        dark_columns = []
        for px in range(270, min(width, 640)):
            dark_fraction = sum(
                1 for py in range(0, min(height, 210))
                if max(source_px[px, py]) < 25
            ) / min(height, 210)
            if dark_fraction > 0.72:
                dark_columns.append(px)
        groups = []
        for px in dark_columns:
            if not groups or px > groups[-1][-1] + 1:
                groups.append([px])
            else:
                groups[-1].append(px)
        mullions = tuple((max(0, group[0] - 1), min(width, group[-1] + 2))
                         for group in groups)
    integrated_layers = (_integrated_rain_layers(image_path, width, height)
                         if rain_mode == "integrated_plate" and image_path else [])
    if rain_mode in {"procedural_window", "masked_window"}:
        # Dense multi-scale rainfall: long soft streaks plus small beads that
        # slide on the glass. Both are deterministic so the 20-second loop is
        # exactly repeatable.
        for i in range(500):
            left, top, right, bottom = panes[i % len(panes)]
            rain.append((left + (i * 17) % max(1, right - left),
                         top + (i * 29) % max(1, bottom - top),
                         4 + (i * 11) % 18, 0.7 + (i % 5) * 0.16,
                         (i * 3) % len(panes)))
            droplets.append((left + (i * 23 + 7) % max(1, right - left),
                             top + (i * 31 + 11) % max(1, bottom - top),
                             0.18 + (i % 3) * 0.12,
                             0.55 + (i % 5) * 0.12,
                             (i * 5 + 2) % len(panes)))
    for frame in range(frame_count):
        t = frame / fps
        phase = frame / frame_count
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
                y = top + int((y0 - top + phase * (bottom - top)) % (bottom - top))
                x_now = x + int(4 * math.sin(2 * math.pi * phase + x * 0.13))
                if rain_mode == "masked_window":
                    rain_alpha = 72 + (x % 3) * 12 if pane_index % 2 else 112 + (x % 3) * 12
                else:
                    rain_alpha = 115
                # A small consistent wind angle makes the streaks read as
                # falling rain rather than vertical UI marks.
                dx = max(2, int(slope * 3.6))
                points = []
                for step in range(length + 1):
                    px = x_now - int(dx * step / max(1, length))
                    py = min(bottom - 1, y + step)
                    visible = True
                    if exterior_px is not None:
                        visible = bool(exterior_px[max(0, min(width - 1, px)), py])
                    if any(left <= px < right for left, right in mullions):
                        visible = False
                    if visible:
                        points.append((px, py))
                    elif len(points) > 1:
                        draw.line(points, fill=(190, 221, 244, rain_alpha), width=1)
                        points = []
                if len(points) > 1:
                    draw.line(points, fill=(190, 221, 244, rain_alpha), width=1)

            for x, y0, radius, speed, pane_index in droplets:
                left, top, right, bottom = panes[pane_index]
                y = top + int((y0 - top + phase * (bottom - top) * speed) % (bottom - top))
                x_now = x + int(2 * math.sin(2 * math.pi * phase + x * 0.09))
                if exterior_px is not None:
                    if not exterior_px[max(0, min(width - 1, x_now)), y]:
                        continue
                if any(left <= x_now < right for left, right in mullions):
                    continue
                if y <= top + 12:
                    continue
                alpha = 25 + int(25 * (0.5 + 0.5 * math.sin(2 * math.pi * phase + x)))
                drop_len = max(1, int(radius * 2.5))
                draw.line((x_now, y, x_now - 1, y + drop_len),
                          fill=(205, 230, 245, alpha), width=1)

        # Steam is built from soft, deforming translucent vapor pockets rather
        # than bright strokes.  This gives it a diffuse, rising shape and
        # avoids the artificial "drawn smoke" appearance.
        steam = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        steam_draw = ImageDraw.Draw(steam, "RGBA")
        # Motion geometry is scene-specific.  The integrated rain plate has
        # the cup in the lower centre; the legacy library plate has it lower
        # left.  Never reuse one scene's coordinates for another image.
        steam_bases = (288, 298, 308) if rain_mode in {"integrated_plate", "masked_window"} else (139, 149, 159)
        steam_rim = 270 if rain_mode in {"integrated_plate", "masked_window"} else 234
        for index, x_base in enumerate(steam_bases):
            phase_offset = index * 1.9
            for puff in range(9):
                rise = ((frame / frame_count) * 70 + puff * 10) % 70
                y = steam_rim - rise
                x = x_base + 8 * math.sin(2 * math.pi * phase + phase_offset + puff * 0.75)
                width_puff = 8 + int(5 * (0.5 + 0.5 * math.sin(2 * math.pi * phase + phase_offset + puff)))
                height_puff = 10 + int(6 * (0.5 + 0.5 * math.cos(2 * math.pi * phase * 1.2 + phase_offset + puff)))
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
                rise = (phase * 48 + index * 9 + step * 1.9) % 48
                y = steam_rim - rise - step * 1.9
                x = x_base + 4.5 * math.sin(2 * math.pi * phase + step * 0.33 + index)
                points.append((x, y))
            core_alpha = 140 if rain_mode in {"integrated_plate", "masked_window"} else 92
            core_draw.line(points, fill=(255, 246, 230, core_alpha), width=2)
        core_blur = 1.6 if rain_mode in {"integrated_plate", "masked_window"} else 2.5
        layer = Image.alpha_composite(layer, steam_core.filter(ImageFilter.GaussianBlur(core_blur)))

        # Slow, broad warm reflections from the lamps and candles.  They are
        # blurred and confined to the room/table, so the scene visibly breathes
        # without adding floating dots or lighting the rain itself.
        glow = int(10 + 13 * (0.5 + 0.5 * math.sin(2 * math.pi * phase)))
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
           rain_mode: str = "procedural_window", *, fps: int = 30,
           output_width: int = 1920, output_height: int = 1080,
           cycle_seconds: int = 20) -> dict:
    if not audio.is_file() or not image.is_file():
        raise FileNotFoundError("Audio e imagen deben existir")
    if not 20 <= duration <= 360:
        raise ValueError("La audición debe durar entre 20 y 360 segundos")
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
            _make_motion_frames(motion_dir, fps=fps, cycle_seconds=cycle_seconds,
                                rain_mode=rain_mode, image_path=image)
            # Keep the base plate fixed while the effects are layered.  A moving
            # zoom on the plate with a fixed motion layer misregisters the window
            # mask and makes rain appear inside the room.
            vf = (
                f"scale={output_width}:{output_height}:force_original_aspect_ratio=increase,"
                f"crop={output_width}:{output_height}[bg];"
                f"[1:v]scale={output_width}:{output_height}:flags=bicubic[fx];"
                "[bg][fx]overlay=0:0:format=auto:shortest=1,format=yuv420p[vout]"
            )
            subprocess.run([
                ffmpeg, "-nostdin", "-y", "-loglevel", "error", "-loop", "1", "-i", str(image),
                "-framerate", "12", "-stream_loop", "-1", "-i", str(motion_dir / "frame-%05d.png"),
                "-i", str(audio), "-map", "[vout]", "-map", "2:a:0", "-filter_complex", vf,
                "-t", str(duration), "-r", str(fps), "-c:v", "libx264", "-preset", "veryfast",
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
    if not video or (video.get("width"), video.get("height")) != (output_width, output_height):
        raise RuntimeError(f"Resolución de salida no verificada: {video}")
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
        "duration_seconds": actual, "width": output_width, "height": output_height,
        "audio_codec": "aac", "video_codec": "h264", "fps": fps,
        "motion_profile": ("integrated_plate-extracted-rain-texture-steam-reflections"
                           if rain_mode == "integrated_plate" else
                           "masked-window-exterior-rain-steam-reflections"
                           if rain_mode == "masked_window" else
                           f"{rain_mode}-steam-reflections"),
        "motion_cycle_seconds": cycle_seconds,
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
    parser.add_argument("--duration", type=int, default=20)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--cycle-seconds", type=int, default=20)
    parser.add_argument("--rain-mode", choices=("procedural_window", "integrated_plate", "masked_window"),
                        default="procedural_window")
    args = parser.parse_args()
    report = render(args.audio, args.image, args.output, args.duration, args.rain_mode,
                    fps=args.fps, output_width=args.width, output_height=args.height,
                    cycle_seconds=args.cycle_seconds)
    report_path = args.output.with_suffix(".review.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

