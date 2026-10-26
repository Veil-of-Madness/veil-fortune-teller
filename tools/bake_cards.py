"""
Writes each card's tarot omen and meaning onto its art:
the omen goes in the empty title banner at the top, the meaning in the
empty text box under the picture, and a symbol for the card's type (Attack,
Effect or Block) in the small square in the top-left corner.

For every card in cards.json it makes, in ./tarot_cards/:
    card_<id>_upright.png   omen + upright meaning
    card_<id>_reversed.png  art turned upside down, text kept readable,
                            omen + reversed meaning
Set REVERSALS = False to make upright cards only.

Usage (from the VoM Tarot folder):
    pip install pillow requests
    python bake_cards.py
"""
import json, os, requests
from PIL import Image, ImageDraw, ImageFont

REVERSALS = True
SCALE = 4                     # 128x222 art becomes 512x888, pixel edges kept crisp

# Empty areas of the card frame, in original 128x222 pixels (left, top, right, bottom)
TEXT_BOX = (9, 165, 118, 210)
BANNER = (28, 8, 114, 22)
CORNER = (3, 3, 24, 24)       # small square, top left (22x22 inside)
CORNER_SHOWS = "type"         # "type" for an Attack/Effect/Block symbol, "tier" for I/II/III

# Pixel-art symbols for the corner, drawn at the art's own resolution so they
# match its pixels. "#" gold, "+" pale gold, "o" dark, "." left as is.
SYMBOLS = {                   # even widths and heights so they centre exactly in the square
    "Attack": [            # a blade, point up
        ".....##.....",
        "....#++#....",
        "....#++#....",
        "....#++#....",
        "....#++#....",
        "....#++#....",
        "....#++#....",
        "....#++#....",
        "....#++#....",
        "....#++#....",
        ".##########.",
        "..########..",
        "....#oo#....",
        "....#oo#....",
        "...######...",
        "....####....",
    ],
    "Effect": [            # an open eye with a slit pupil
        "......####......",
        "...###++++###...",
        "..#+++####+++#..",
        ".#+++#+oo+#+++#.",
        "#++++#+oo+#++++#",
        "#++++#+oo+#++++#",
        ".#+++#+oo+#+++#.",
        "..#+++####+++#..",
        "...###++++###...",
        "......####......",
    ],
    "Block": [             # a shield
        "##############",
        "#+++++##+++++#",
        "#+++++##+++++#",
        "#+++++##+++++#",
        "##############",
        "#+++++##+++++#",
        "#+++++##+++++#",
        ".#++++##++++#.",
        ".#++++##++++#.",
        "..#+++##+++#..",
        "...#++##++#...",
        "....#+##+#....",
        ".....####.....",
        "......##......",
    ],
}
PIXEL = {"#": (229, 190, 37, 255), "+": (240, 224, 182, 255), "o": (45, 5, 5, 255)}
PAD = 2                       # breathing room inside each area, original pixels

TEXT = (240, 224, 182)        # pale gold, readable on the dark red fill

NUMERALS = {1: "I", 2: "II", 3: "III", 4: "IV"}

FONT_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/imfellenglish/"
FONTS = {"roman": "IMFeENrm28P.ttf", "italic": "IMFeENit28P.ttf"}


def get_fonts():
    os.makedirs("fonts", exist_ok=True)
    for f in FONTS.values():
        path = os.path.join("fonts", f)
        if not os.path.exists(path):
            r = requests.get(FONT_URL + f, timeout=30)
            r.raise_for_status()
            open(path, "wb").write(r.content)
    return {k: os.path.join("fonts", v) for k, v in FONTS.items()}


def area(box, reversed_, w, h):
    """Scale an area to the enlarged card, moving it if the card is upside down."""
    l, t, r, b = box
    if reversed_:
        l, t, r, b = w - 1 - r, h - 1 - b, w - 1 - l, h - 1 - t
    p = PAD
    return ((l + p) * SCALE, (t + p) * SCALE, (r + 1 - p) * SCALE, (b + 1 - p) * SCALE)


def draw_symbol(img, name, box):
    """Draw a pixel symbol centred in box (original pixels, already rotated)."""
    rows = SYMBOLS[name]
    l, t, r, b = box
    x0 = l + (r - l + 1 - len(rows[0])) // 2
    y0 = t + (b - t + 1 - len(rows)) // 2
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in PIXEL:
                img.putpixel((x0 + x, y0 + y), PIXEL[ch])


def rotated(box, reversed_, w, h):
    l, t, r, b = box
    return (w - 1 - r, h - 1 - b, w - 1 - l, h - 1 - t) if reversed_ else box


def wrap(draw, text, font, width):
    lines, line = [], ""
    for word in text.split():
        test = f"{line} {word}".strip()
        if draw.textlength(test, font=font) <= width:
            line = test
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def write_block(draw, text, font_path, sizes, box, leading=1.22):
    """Centre wrapped text in box, using the largest size that fits."""
    l, t, r, b = box
    for size in sizes:
        font = ImageFont.truetype(font_path, size)
        lines = wrap(draw, text, font, r - l)
        line_h = round(size * leading)
        block_h = line_h * len(lines)
        if block_h <= b - t and all(draw.textlength(x, font=font) <= r - l for x in lines):
            break
    else:
        print(f"  warning: text may overflow its box: {text[:40]}...")
    y = t + (b - t - block_h) / 2
    for line in lines:
        w = draw.textlength(line, font=font)
        draw.text((l + (r - l - w) / 2, y), line, font=font, fill=TEXT)
        y += line_h


def bake(card, art, fonts, reversed_):
    w, h = art.size
    img = art.convert("RGBA")
    if reversed_:
        img = img.rotate(180)
    if CORNER_SHOWS == "type" and card["source"] in SYMBOLS:
        draw_symbol(img, card["source"], rotated(CORNER, reversed_, w, h))
    img = img.resize((w * SCALE, h * SCALE), Image.NEAREST)
    d = ImageDraw.Draw(img)
    write_block(d, card["omen"], fonts["roman"], range(42, 17, -1), area(BANNER, reversed_, w, h), 1.0)
    if CORNER_SHOWS == "tier":
        numeral = NUMERALS.get(card["tier"], str(card["tier"]))
        write_block(d, numeral, fonts["roman"], range(46, 17, -1), area(CORNER, reversed_, w, h), 1.0)
    meaning = card["reversed"] if reversed_ else card["upright"]
    write_block(d, meaning, fonts["italic"], range(36, 15, -1), area(TEXT_BOX, reversed_, w, h), 1.12)
    return img


def main():
    cards = json.load(open("cards.json", encoding="utf-8"))
    fonts = get_fonts()
    os.makedirs("tarot_cards", exist_ok=True)
    missing = []
    for c in cards:
        if not os.path.exists(c["image"]):
            missing.append(c["image"])
            continue
        art = Image.open(c["image"])
        for rev in ((False, True) if REVERSALS else (False,)):
            name = f"card_{c['id']}_{'reversed' if rev else 'upright'}.png"
            bake(c, art, fonts, rev).save(os.path.join("tarot_cards", name))
        print("baked", c["name"])
    print(f"\nDone: {len(cards) - len(missing)}/{len(cards)} cards baked into tarot_cards/")
    for m in missing:
        print("MISSING IMAGE:", m)


if __name__ == "__main__":
    main()
