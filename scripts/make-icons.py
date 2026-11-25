"""Draw the Home Screen icons into icons/: a letter card with a lowercase "a" on the app's accent colour.

Shapes only, no font, so the output doesn't depend on what's installed. Needs Pillow:
    .venv/bin/python scripts/make-icons.py
"""
from pathlib import Path
from PIL import Image, ImageDraw

ACCENT, PAPER = '#315e50', '#ffffff'
SIZES = {'icon-192.png': 192, 'icon-512.png': 512, 'apple-touch-icon.png': 180}
UNIT = 1024  # drawn at this size, then downscaled for smooth edges


def draw():
    img = Image.new('RGB', (UNIT, UNIT), ACCENT)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((192, 192, 832, 832), radius=96, fill=PAPER)
    d.ellipse((332, 392, 632, 692), outline=ACCENT, width=64)
    d.rectangle((600, 392, 664, 692), fill=ACCENT)
    return img


if __name__ == '__main__':
    out = Path(__file__).resolve().parents[1] / 'icons'
    out.mkdir(exist_ok=True)
    big = draw()
    for name, size in SIZES.items():
        big.resize((size, size), Image.LANCZOS).save(out / name, optimize=True)
