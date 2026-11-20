#!/usr/bin/env python3
"""The World Today - 20 November 2026.

Pure-stdlib Python program that draws a newspaper front page summing up
the world news of Friday, 20 November 2026 as one 1024x1024 PNG.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
No network, no third-party packages, deterministic: two runs produce
identical bytes.

Lead + six verified stories of 20 November 2026:
  Lead: Trump, Xi and Putin hold the first-ever trilateral summit in
    Shenzhen, China, and release a joint peace declaration on nuclear
    arms, energy security and the world's conflicts.
  1. The Hague: the ICJ rules Myanmar's military likely intended to
    destroy a substantial part of the Rohingya in the 2017 crackdown.
  2. Seoul: South Korea's Supreme Court overturns ex-PM Han Duck-soo's
    conviction in the case tied to the 2024 martial law declaration.
  3. Suva: Fiji declares a national state of disaster as El Nino
    drought brings severe water shortages.
  4. Kyiv: a Ukrainian attack on the Crimean Bridge halts railway
    traffic; Russian strikes damage the Austrian and Dutch embassies.
  5. Vienna: the IAEA reports North Korea is expanding its uranium
    enrichment facility at Yongbyon.
  6. Caracas: the US and Venezuela sign a deal to restore military
    cooperation, under a year after Maduro's ouster.
Footer: Van Gogh sells for a record $190.4m; Cyclone Akvan bears down
on Odisha; Nicholls' century lifts New Zealand in Wellington.
"""

import os
import struct
import zlib
from pathlib import Path

W, H = 1024, 1024

PAPER = (248, 244, 236)
INK = (18, 18, 18)
RED = (176, 32, 32)
BLUE = (28, 62, 118)
SKY = (168, 198, 224)
SEA = (52, 104, 158)
LAND = (86, 148, 84)
GOLD = (198, 160, 40)
GREY = (96, 96, 96)
LIGHT = (233, 227, 213)
ORANGE = (226, 116, 54)
TEAL = (24, 120, 112)
NAVY = (24, 38, 68)

# ------------------------------------------------------------------ font
# 5x7 bitmap glyphs, written as seven 5-character rows ('#' = ink).
# Only the characters the page needs are defined.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def wrap(s, width_chars):
    """Greedy word wrap; returns a list of lines, each <= width_chars."""
    lines, cur = [], ""
    for word in s.split(" "):
        if cur and len(cur) + 1 + len(word) > width_chars:
            lines.append(cur)
            cur = word
        else:
            cur = (cur + " " + word).strip()
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, c)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def frame(self, x, y, w, h, c, t=1):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.put(xx, yy, c)

    def ring(self, cx, cy, r, c, t=2):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d2 <= (r + t) ** 2:
                    self.put(xx, yy, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            for xx in range(cx - rx, cx + rx + 1):
                if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0:
                    self.put(xx, yy, c)

    def glyph(self, ch, x, y, scale, c):
        rows = FONT.get(ch.upper(), FONT['?'])
        for r, row in enumerate(rows):
            for col, bit in enumerate(row):
                if bit == '1':
                    self.rect(x + col * scale, y + r * scale, scale, scale, c)

    def text(self, s, x, y, scale, c):
        cx = x
        for ch in s:
            self.glyph(ch, cx, y, scale, c)
            cx += 6 * scale
        return cx

    def text_centred(self, s, cx, y, scale, c):
        self.text(s, cx - text_width(s, scale) // 2, y, scale, c)

    def paragraph(self, s, x, y, width, scale, c, leading=None):
        if leading is None:
            leading = 9 * scale
        chars = max(1, width // (6 * scale))
        lines = wrap(s, chars)
        for i, line in enumerate(lines):
            self.text(line, x, y + i * leading, scale, c)
        return len(lines)


def star(cv, cx, cy, r, c):
    """Five-point star approximated with a filled disc plus spikes."""
    cv.disc(cx, cy, r, c)
    for dx, dy in ((0, -2), (-2, 1), (2, 1), (-1, -1), (1, -1)):
        cv.disc(cx + dx * r // 2, cy + dy * r // 2, max(1, r // 2), c)


def flag_usa(cv, x, y, w, h):
    stripe = max(1, h // 13)
    for i in range(13):
        cv.rect(x, y + i * stripe, w, stripe, RED if i % 2 == 0 else PAPER)
    cw, ch = w * 2 // 5, stripe * 7
    cv.rect(x, y, cw, ch, BLUE)
    for r in range(4):
        for col in range(5):
            cv.disc(x + 8 + col * (cw - 14) // 4,
                    y + 6 + r * (ch - 10) // 3, 2, PAPER)


def flag_china(cv, x, y, w, h):
    cv.rect(x, y, w, h, RED)
    star(cv, x + w // 5, y + h // 4, 9, GOLD)
    for dx, dy in ((28, -14), (34, 0), (28, 14), (14, 18)):
        star(cv, x + w // 5 + dx, y + h // 4 + dy, 4, GOLD)


def flag_russia(cv, x, y, w, h):
    third = h // 3
    cv.rect(x, y, w, third, PAPER)
    cv.rect(x, y + third, w, third, BLUE)
    cv.rect(x, y + 2 * third, w, h - 2 * third, RED)


# ------------------------------------------------------------------ page
def draw():
    cv = Canvas(W, H, PAPER)
    cv.frame(10, 10, W - 20, H - 20, INK, 3)
    cv.frame(18, 18, W - 36, H - 36, INK, 1)

    # Masthead
    cv.text_centred("THE WORLD TODAY", W // 2, 34, 6, INK)
    cv.hline(48, 92, W - 96, INK)
    cv.hline(48, 96, W - 96, INK)
    cv.text_centred("FRIDAY 20 NOVEMBER 2026 - THE DAY IN WORLD NEWS",
                    W // 2, 108, 2, RED)

    # ---- lead art panel: globe + three flags -------------------------
    px0, py0, pw, ph = 40, 138, 944, 236
    cv.frame(px0, py0, pw, ph, INK, 2)
    # sky bands
    for i in range(6):
        cv.rect(px0 + 2, py0 + 2 + i * (ph - 4) // 6, pw - 4,
                (ph - 4) // 6 + 1,
                (SKY[0] - i * 8, SKY[1] - i * 6, SKY[2] - i * 4))
    # sun
    cv.disc(px0 + 890, py0 + 40, 26, GOLD)
    cv.ring(px0 + 890, py0 + 40, 32, GOLD, 2)
    # globe
    gx, gy, gr = px0 + 150, py0 + 122, 96
    cv.disc(gx, gy, gr, SEA)
    cv.ellipse(gx - 34, gy - 30, 42, 26, LAND)
    cv.ellipse(gx + 38, gy + 8, 34, 20, LAND)
    cv.ellipse(gx - 8, gy + 52, 46, 16, LAND)
    cv.ellipse(gx + 52, gy - 48, 18, 12, LAND)
    cv.ring(gx, gy, gr, NAVY, 3)
    # meridian hints, clipped to the globe
    for k in range(-2, 3):
        for yy in range(gy - gr + 4, gy + gr - 3):
            xx = gx + int(k * gr * 0.42)
            if (xx - gx) ** 2 + (yy - gy) ** 2 <= (gr - 4) ** 2:
                cv.put(xx, yy, (120, 160, 190))
    # flags on poles
    poles = [(430, flag_usa, "USA"), (600, flag_china, "CHINA"),
             (770, flag_russia, "RUSSIA")]
    for fx, fn, label in poles:
        cv.vline(fx, py0 + 34, 178, INK)
        cv.disc(fx, py0 + 32, 5, GOLD)
        fn(cv, fx + 4, py0 + 40, 128, 84)
        cv.frame(fx + 4, py0 + 40, 128, 84, INK, 1)
        cv.text_centred(label, fx + 68, py0 + 134, 2, INK)
    cv.text_centred("THE FIRST TRILATERAL SUMMIT", px0 + 150, py0 + 222, 1, NAVY)

    # ---- lead headline + deck ---------------------------------------
    cv.text_centred("TRUMP, XI AND PUTIN MEET IN CHINA", W // 2, 396, 4, INK)
    cv.text_centred("AND SIGN A JOINT PEACE DECLARATION", W // 2, 432, 4, RED)
    deck = ("The three leaders hold the first trilateral summit in Shenzhen "
            "and release a joint declaration on nuclear arms, energy security "
            "and the world's conflicts.")
    cv.paragraph(deck, 112, 478, 800, 2, INK)
    cv.hline(48, 552, W - 96, INK)
    cv.hline(48, 556, W - 96, INK)

    # ---- story grid --------------------------------------------------
    stories = [
        ("THE HAGUE", "COURT: MYANMAR LIKELY SOUGHT TO DESTROY ROHINGYA",
         "The ICJ rules the 2017 crackdown likely aimed to destroy a "
         "substantial part of the Rohingya minority.", RED),
        ("SEOUL", "TOP COURT CLEARS EX-PM HAN DUCK-SOO",
         "South Korea's top court overturns the ex-PM's conviction tied to "
         "the 2024 martial law declaration.", BLUE),
        ("SUVA", "FIJI DECLARES DISASTER AS DROUGHT BITES",
         "A national state of disaster over severe drought and water "
         "shortages as El Nino parches the islands.", TEAL),
        ("KYIV", "UKRAINE HITS CRIMEAN BRIDGE; EMBASSIES DAMAGED",
         "A Ukrainian attack halts rail traffic on the Crimean Bridge; "
         "Russian strikes damage two embassies in Kyiv.", ORANGE),
        ("VIENNA", "NORTH KOREA EXPANDING URANIUM SITE, IAEA SAYS",
         "The UN nuclear watchdog reports Pyongyang is enlarging its uranium "
         "enrichment facility at Yongbyon.", NAVY),
        ("CARACAS", "US AND VENEZUELA RESTORE MILITARY TIES",
         "Washington and Caracas sign a deal to restore military cooperation, "
         "under a year after Maduro's ouster.", GOLD),
    ]
    gx0, gy0 = 40, 576
    tw, th = 464, 118
    for i, (kicker, head, body, accent) in enumerate(stories):
        x = gx0 + (i % 2) * (tw + 16)
        y = gy0 + (i // 2) * (th + 12)
        cv.rect(x, y, 6, th, accent)
        cv.text(kicker, x + 16, y + 2, 2, accent)
        cv.paragraph(head, x + 16, y + 22, tw - 16, 2, INK)
        cv.paragraph(body, x + 16, y + 62, tw - 16, 2, GREY)
        cv.hline(x, y + th - 1, tw, LIGHT)

    # ---- footer ------------------------------------------------------
    cv.hline(48, 956, W - 96, INK)
    foot1 = "ALSO: VAN GOGH SELLS FOR A RECORD $190.4M - CYCLONE AKVAN BEARS DOWN ON ODISHA"
    foot2 = "NICHOLLS' CENTURY LIFTS NEW ZEALAND IN WELLINGTON - ANTHROPIC VALUED AT $1.5 TRILLION"
    cv.text_centred(foot1, W // 2, 968, 1, INK)
    cv.text_centred(foot2, W // 2, 982, 1, INK)
    return cv


def chunk(tag, data):
    c = struct.pack(">I", len(data)) + tag + data
    return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def write_png(cv, path):
    raw = b"".join(b"\x00" + bytes(cv.px[y * W * 3:(y + 1) * W * 3])
                   for y in range(H))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(png)
    return len(png)


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    size = write_png(draw(), os.path.join(out, "entry.png"))
    print(f"wrote entry.png {size} bytes")


if __name__ == "__main__":
    main()
