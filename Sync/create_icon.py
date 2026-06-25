"""
Generate bookkeeper.ico for the Sync Now desktop shortcut.
Requires: pip install pillow

Output: bookkeeper.ico (next to this script)
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os

PURPLE = (26, 10, 46, 255)     # BMBooks #1A0A2E
WHITE  = (255, 255, 255, 255)
GREEN  = (150, 191, 72, 255)   # Shopify #96BF48


def make_icon(size):
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded rectangle background
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=size // 6, fill=PURPLE)

    cx, cy   = size / 2, size / 2
    arrow_r  = size * 0.38
    lw       = max(2, size // 16)
    al       = lw * 2.5   # arrowhead leg length

    # Two arcs (top-right and bottom-left) with arrowheads — classic sync icon
    arcs = [
        (210, 120,  1),   # bottom-left arc, arrowhead points right
        ( 30, 120, -1),   # top-right arc, arrowhead points left
    ]
    for start, sweep, flip in arcs:
        bbox = [cx - arrow_r, cy - arrow_r, cx + arrow_r, cy + arrow_r]
        draw.arc(bbox, start=start, end=start + sweep, fill=GREEN, width=lw)

        end_rad = math.radians(start + sweep)
        tx = cx + arrow_r * math.cos(end_rad)
        ty = cy + arrow_r * math.sin(end_rad)
        tang = end_rad + math.pi / 2 * flip
        pts = [
            (tx, ty),
            (tx + al * math.cos(tang - 0.5), ty + al * math.sin(tang - 0.5)),
            (tx + al * math.cos(tang + 0.5), ty + al * math.sin(tang + 0.5)),
        ]
        draw.polygon(pts, fill=GREEN)

    # "BK" centred in white
    fs = max(int(size * 0.32), 8)
    for name in ("arialbd.ttf", "arial.ttf", "Arial Bold.ttf", "Arial.ttf"):
        try:
            font = ImageFont.truetype(name, fs)
            break
        except OSError:
            continue
    else:
        font = ImageFont.load_default()

    bb = draw.textbbox((0, 0), "BK", font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw.text(((size - tw) / 2 - bb[0], (size - th) / 2 - bb[1]), "BK",
              fill=WHITE, font=font)

    return img


if __name__ == "__main__":
    sizes  = [256, 48, 32, 16]
    images = [make_icon(s) for s in sizes]
    out    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bookkeeper.ico")
    images[0].save(out, format="ICO", sizes=[(s, s) for s in sizes],
                   append_images=images[1:])
    print(f"Saved: {out}")
