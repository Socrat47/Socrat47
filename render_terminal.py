"""Render the editable ASCII black-hole terminal used by the profile README.

Requires Pillow: python3 -m pip install Pillow
Run from anywhere: python3 render_terminal.py
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "terminal-session.gif"
SIZE = (1060, 484)
FONT_PATHS = (
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"),
    Path("C:/Windows/Fonts/consola.ttf"),
    Path("C:/Windows/Fonts/lucon.ttf"),
)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = FONT_PATHS[1:] + FONT_PATHS[:1] if bold else FONT_PATHS
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


MONO = font(19)
SMALL = font(17)
BOLD = font(21, bold=True)
ASCII = font(20, bold=True)
FRAME_DURATIONS = (150, 150, 150, 150, 800, 800, 800)
STEPS_PER_COMMAND = len(FRAME_DURATIONS)
COMMANDS = ("fastfetch --dev", "whoami", "cat philosophy.txt", "./run --mode=current")

BG = "#0b0f18"
PANEL = "#101622"
TOP = "#1c2533"
EDGE = "#37465c"
TEXT = "#e2e8f0"
MUTED = "#8fa0b5"
TEAL = "#5eead4"
AMBER = "#ffbf69"
PINK = "#e48dbe"


def black_hole(draw: ImageDraw.ImageDraw, frame: int) -> None:
    """Every visible mark in the illustration is a monospace character."""
    phase = frame * 2 * math.pi / 16
    x0, y0 = 34, 126
    cw, ch = 13.1, 16.1
    for gy in range(19):
        for gx in range(39):
            dx, dy = gx - 19, gy - 9
            radius = math.hypot(dx / 1.25, dy / 0.80)
            disk = math.hypot(dx / 18.5, (dy - 1.7) / 3.4)
            angle = math.atan2(dy, dx)
            ripple = math.sin(2.6 * angle - phase + radius * 0.46)

            glyph = ""
            color = MUTED
            if 5.0 <= radius < 7.9:
                glyph = "@" if radius < 5.9 else ("O" if radius < 6.8 else "o")
                color = AMBER if dy > 0 else PINK
                if ripple > 0.7:
                    glyph = "#" if radius < 6.4 else "*"
                    color = "#ffe4a8"
            elif 0.63 < disk < 1.17 and radius >= 5.0:
                glyph = "*" if disk < 0.93 else (":" if ripple > -0.2 else ".")
                color = AMBER if dy > 0 else PINK
            elif 7.9 <= radius < 9.6 and ripple > -0.65:
                glyph = "." if ripple < 0.3 else ":"
                color = "#a978ae"

            if glyph:
                draw.text((x0 + gx * cw, y0 + gy * ch), glyph, font=ASCII, fill=color)


def command_output(draw: ImageDraw.ImageDraw, command_index: int) -> None:
    x, y = 550, 141
    titles = ("socrat47@dev", "whoami", "philosophy.txt", "mode: current")
    draw.text((x, y), titles[command_index], font=BOLD, fill=TEAL)
    draw.line((x, y + 34, 1015, y + 34), fill=EDGE, width=1)

    if command_index == 0:
        rows = (
            ("Role", "Full stack developer"),
            ("OS", "Backend-first, frontend-fluent"),
            ("Focus", "System design & architecture"),
            ("AI/CV", "Practical integration"),
            ("Status", "Always learning"),
        )
        for n, (label, value) in enumerate(rows):
            row_y = y + 57 + n * 39
            draw.text((x, row_y), f"{label}:", font=SMALL, fill=AMBER)
            draw.text((x + 112, row_y), value, font=SMALL, fill=TEXT)
        return

    output = (
        (),
        (
            "> booting socrat47_profile.sh...",
            "> backend brain...          [OK]",
            "> system design...          [OK]",
            "> AI curiosity...           [OK]",
            "",
            "Full stack developer.",
            'Sistemleri "neden çalışıyor" diye',
            "tasarlarım.",
        ),
        (
            "Kod yazmak kolay kısmı. Zor olan;",
            "doğru veri modelini seçmek, sistemi",
            "büyümeye hazır tasarlamak ve beş yıl",
            "sonra okunabilir bırakmak.",
            "",
            "AI beni değiştirmedi, hızlandırdı.",
            "Sistemin neden böyle davrandığını",
            "ben anlıyorum — model değil.",
        ),
        (
            "[*] Backend sistemlerini",
            "    sağlamlaştırıyor",
            "[*] AI/CV entegrasyonlarını",
            "    mimariye oturtuyor",
            "[*] Çalışan kod ile doğru kodun",
            "    farkını kovalıyor",
        ),
    )[command_index]
    for n, line in enumerate(output):
        color = AMBER if line.startswith((">", "[*]")) else TEXT
        draw.text((x, y + 55 + n * 29), line, font=SMALL, fill=color)


def frame_image(index: int) -> Image.Image:
    command_index, step = divmod(index, STEPS_PER_COMMAND)
    command = COMMANDS[command_index]
    image = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((12, 12, 1048, 472), radius=13, fill=PANEL, outline=EDGE, width=2)
    draw.rounded_rectangle((13, 13, 1047, 54), radius=12, fill=TOP)
    draw.rectangle((13, 43, 1047, 54), fill=TOP)
    for x, color in ((35, "#ff6b6b"), (58, "#f5bd4f"), (81, "#4ade80")):
        draw.ellipse((x - 6, 28, x + 6, 40), fill=color)
    draw.text((337, 23), "socrat47@dev: ~ / session", font=SMALL, fill=MUTED)

    draw.text((35, 69), "~$", font=MONO, fill=TEAL)
    typed = command[: math.ceil(len(command) * min(step + 1, 4) / 4)]
    draw.text((73, 69), typed, font=MONO, fill=TEXT)
    if step < 4 or step % 2 == 0:
        cursor_x = 73 + draw.textlength(typed, font=MONO) + 3
        draw.rectangle((cursor_x, 73, cursor_x + 10, 93), fill=TEAL)
    draw.line((35, 111, 1024, 111), fill=EDGE, width=1)
    black_hole(draw, index)
    if step >= 4:
        command_output(draw, command_index)

    draw.line((35, 434, 1024, 434), fill=EDGE, width=1)
    draw.text((35, 445), "~$", font=SMALL, fill=TEAL)
    draw.text((899, 445), f"[ {command_index + 1:02d} / 04 ]", font=SMALL, fill=MUTED)
    return image


def main() -> None:
    frames = [frame_image(i).quantize(colors=96) for i in range(len(COMMANDS) * STEPS_PER_COMMAND)]
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=list(FRAME_DURATIONS) * len(COMMANDS),
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
