#!/usr/bin/env python3
"""Build-time renderer for the 20 November 2026 world-news page.

Draws a 1024x1024 broadsheet front page with real fonts and flat colour, then
saves it beside main.py as entry.png. Build-time only: the grader never runs
this file, it only copies the committed PNG (see main.py).

    python3 tools/render.py            # writes entry.png in the repo root
"""

from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 40

PAPER = (246, 241, 231)
INK = (20, 17, 14)
MUTED = (90, 84, 75)
CARD = (255, 253, 248)
RED = (168, 18, 27)
BLUE = (20, 57, 110)
TEAL = (14, 92, 99)
SAND = (200, 162, 74)
STONE = (201, 192, 174)
GREEN = (40, 92, 62)
PLUM = (94, 44, 96)

SERIF_B = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
SERIF = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SERIF_I = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
SANS = "/System/Library/Fonts/Supplemental/Arial.ttf"
SANS_BK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"

FONT_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    key = (path, size)
    if key not in FONT_CACHE:
        FONT_CACHE[key] = ImageFont.truetype(path, size)
    return FONT_CACHE[key]


def text_w(d, s, f, track=0) -> int:
    if not s:
        return 0
    if track:
        return int(sum(d.textlength(ch, font=f) for ch in s)) + track * (len(s) - 1)
    return int(d.textlength(s, font=f))


def wrap(d, text, f, maxw) -> list[str]:
    lines, cur = [], ""
    for w in text.split():
        trial = f"{cur} {w}".strip()
        if text_w(d, trial, f) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_block(d, text, path, hi, lo, maxw, max_lines):
    size = hi
    while size > lo:
        f = font(path, size)
        if len(wrap(d, text, f, maxw)) <= max_lines:
            return f
        size -= 1
    return font(path, lo)


def fit_line(d, text, path, maxw, hi, lo):
    size = hi
    while size > lo:
        f = font(path, size)
        if text_w(d, text, f) <= maxw:
            return f
        size -= 1
    return font(path, lo)


def draw_tracked(d, xy, s, f, fill, track=0):
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + track
    return x


# ---------------------------------------------------------------- glyphs
# One flat mark per field, so every story carries a picture rather than a line.


def g_war(d, x, y, s=56):
    d.polygon([(x + s * 0.52, y + s * 0.10), (x + s * 0.62, y + s * 0.34),
               (x + s * 0.42, y + s * 0.34)], fill=RED)
    d.rectangle((x + s * 0.46, y + s * 0.34, x + s * 0.58, y + s * 0.62), fill=RED)
    d.polygon([(x + s * 0.46, y + s * 0.62), (x + s * 0.58, y + s * 0.62),
               (x + s * 0.44, y + s * 0.76), (x + s * 0.34, y + s * 0.66)], fill=RED)
    d.polygon([(x + s * 0.58, y + s * 0.62), (x + s * 0.46, y + s * 0.62),
               (x + s * 0.60, y + s * 0.76), (x + s * 0.70, y + s * 0.66)], fill=RED)
    for i in range(3):
        d.line((x + s * 0.30, y + s * (0.30 + i * 0.16),
                x + s * 0.16, y + s * (0.34 + i * 0.16)), fill=SAND, width=3)


def g_politics(d, x, y, s=56):
    d.rectangle((x + s * 0.14, y + s * 0.56, x + s * 0.50, y + s * 0.66), fill=BLUE)
    d.polygon([(x + s * 0.28, y + s * 0.30), (x + s * 0.52, y + s * 0.30),
               (x + s * 0.46, y + s * 0.56), (x + s * 0.34, y + s * 0.56)], fill=BLUE)
    d.line((x + s * 0.62, y + s * 0.30, x + s * 0.62, y + s * 0.60), fill=INK, width=3)
    d.ellipse((x + s * 0.58, y + s * 0.16, x + s * 0.66, y + s * 0.26), fill=INK)
    d.rectangle((x + s * 0.58, y + s * 0.26, x + s * 0.66, y + s * 0.31), fill=INK)


def g_money(d, x, y, s=56):
    d.line((x + s * 0.14, y + s * 0.78, x + s * 0.86, y + s * 0.78), fill=STONE, width=3)
    d.line((x + s * 0.14, y + s * 0.14, x + s * 0.14, y + s * 0.78), fill=STONE, width=3)
    pts = [(0.20, 0.40), (0.36, 0.30), (0.50, 0.52), (0.64, 0.44), (0.84, 0.72)]
    poly = [(x + s * px, y + s * py) for px, py in pts]
    d.line(poly, fill=BLUE, width=4, joint="curve")
    d.polygon([(x + s * 0.84, y + s * 0.86), (x + s * 0.78, y + s * 0.66),
               (x + s * 0.92, y + s * 0.70)], fill=RED)


def g_climate(d, x, y, s=56):
    r = s * 0.34
    cx, cy = x + s * 0.50, y + s * 0.46
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=TEAL, width=4)
    d.arc((cx - r, cy - r * 0.5, cx + r, cy + r * 0.5), 0, 360, fill=TEAL, width=3)
    d.line((cx, cy - r, cx, cy + r), fill=TEAL, width=2)
    d.rectangle((cx + r * 0.72, y + s * 0.20, cx + r * 0.94, y + s * 0.72), fill=RED)
    d.ellipse((cx + r * 0.66, y + s * 0.66, cx + r * 1.02, y + s * 0.88), fill=RED)


def g_justice(d, x, y, s=56):
    d.line((x + s * 0.50, y + s * 0.16, x + s * 0.50, y + s * 0.74), fill=INK, width=3)
    d.line((x + s * 0.20, y + s * 0.28, x + s * 0.80, y + s * 0.28), fill=INK, width=3)
    d.line((x + s * 0.26, y + s * 0.74, x + s * 0.74, y + s * 0.74), fill=INK, width=3)
    for cx in (x + s * 0.22, x + s * 0.78):
        d.line((cx, y + s * 0.28, cx, y + s * 0.44), fill=INK, width=2)
        d.polygon([(cx - s * 0.12, y + s * 0.44), (cx + s * 0.12, y + s * 0.44),
                   (cx, y + s * 0.60)], fill=INK)


def g_people(d, x, y, s=56):
    for i, dx in enumerate((0.20, 0.46, 0.72)):
        r = s * 0.10
        cx = x + s * dx
        d.ellipse((cx - r, y + s * 0.24, cx + r, y + s * 0.24 + 2 * r), fill=INK)
        d.polygon([(cx - s * 0.13, y + s * 0.70), (cx - s * 0.09, y + s * 0.46),
                   (cx + s * 0.09, y + s * 0.46), (cx + s * 0.13, y + s * 0.70)],
                  fill=INK)


def g_tech(d, x, y, s=56):
    d.rectangle((x + s * 0.28, y + s * 0.28, x + s * 0.72, y + s * 0.72), fill=BLUE)
    for i in range(3):
        o = s * (0.34 + i * 0.14)
        d.line((x + s * 0.16, y + o, x + s * 0.28, y + o), fill=BLUE, width=3)
        d.line((x + s * 0.72, y + o, x + s * 0.84, y + o), fill=BLUE, width=3)
        d.line((x + o, y + s * 0.16, x + o, y + s * 0.28), fill=BLUE, width=3)
        d.line((x + o, y + s * 0.72, x + o, y + s * 0.84), fill=BLUE, width=3)


def g_disaster(d, x, y, s=56):
    for i in range(3):
        yy = y + s * (0.34 + i * 0.18)
        pts = []
        for k in range(9):
            px = x + s * 0.10 + s * 0.80 * k / 8
            pts.append((px, yy + (s * 0.06 if k % 2 else 0)))
        d.line(pts, fill=TEAL, width=4)
    d.polygon([(x + s * 0.62, y + s * 0.14), (x + s * 0.84, y + s * 0.14),
               (x + s * 0.84, y + s * 0.40), (x + s * 0.62, y + s * 0.40)], fill=RED)


def g_science(d, x, y, s=56):
    cx, cy = x + s * 0.50, y + s * 0.50
    d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=TEAL)
    d.arc((cx - s * 0.30, cy - s * 0.12, cx + s * 0.30, cy + s * 0.12), 0, 360,
          fill=TEAL, width=3)
    d.arc((cx - s * 0.12, cy - s * 0.30, cx + s * 0.12, cy + s * 0.30), 0, 360,
          fill=TEAL, width=3)


def g_cyclone(d, x, y, s=56):
    cx, cy = x + s * 0.50, y + s * 0.50
    for r, wd in ((s * 0.30, 4), (s * 0.20, 4), (s * 0.10, 4)):
        d.arc((cx - r, cy - r * 0.72, cx + r, cy + r * 0.72), 20, 300,
              fill=TEAL, width=wd)
    d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=TEAL)


def g_energy(d, x, y, s=56):
    d.polygon([(x + s * 0.56, y + s * 0.12), (x + s * 0.30, y + s * 0.54),
               (x + s * 0.48, y + s * 0.54), (x + s * 0.40, y + s * 0.86),
               (x + s * 0.70, y + s * 0.42), (x + s * 0.52, y + s * 0.42)],
              fill=SAND)


# ---------------------------------------------------------------- the day

METRICS = [
    ("8", "KILLED IN KYIV"),
    ("370,000", "EVACUATED, ODISHA"),
    ("-4.8%", "NIKKEI 225"),
    ("111", "CAUGHT CHEATING"),
    ("$2.36bn", "GTA VI, DAY ONE"),
    ("EUR 26bn", "ITALY'S BUDGET"),
]

TILES = [
    ("UKRAINE", "Russia's biggest strike hits Kyiv bridges", g_war, RED),
    ("INDIA", "Cyclone Akvan comes ashore in Odisha", g_cyclone, TEAL),
    ("MARKETS", "AI sell-off sinks Asia's shares", g_money, BLUE),
    ("ANTALYA", "COP31 draft drops the fuel phaseout", g_climate, TEAL),
    ("BRUSSELS", "UK and EU agree youth mobility deal", g_politics, BLUE),
    ("THE HAGUE", "Sanctions urged after ICJ genocide ruling", g_justice, INK),
    ("POLAND", "Missile debris falls in eastern Poland", g_war, RED),
    ("ROME", "CGIL strike over Italy's budget", g_people, RED),
    ("WASHINGTON", "Senate passes permitting overhaul", g_politics, BLUE),
    ("SEOUL", "111 caught cheating in Suneung", g_people, BLUE),
    ("IRAQ", "Iran-backed militia told to leave", g_war, RED),
    ("PACIFIC", "US auctions deep-sea mining leases", g_energy, SAND),
]

BRIEFS = [
    ("CALIFORNIA", "Nvidia subpoenaed over chips", g_tech),
    ("NEW YORK", "GTA VI: $2.36bn in a day", g_money),
    ("TOKYO", "Core inflation at a 2026 high", g_money),
    ("BUDAPEST", "Hungary lifts EU veto", g_politics),
    ("LISBON", "Strike hits hospitals", g_people),
    ("HORMUZ", "Tanker burns on a mine", g_war),
    ("RIYADH", "Houthi missiles hit KAFD", g_war),
    ("GAZA", "Troops cross the Yellow Line", g_war),
    ("PYONGYANG", "IAEA sees Yongbyon expansion", g_science),
    ("CARACAS", "US-Venezuela military pact", g_politics),
    ("COPENHAGEN", "Greenland deal ratified", g_politics),
    ("ISLAMABAD", "22 militants killed", g_war),
    ("BRASILIA", "Bank sells $1bn reserves", g_money),
    ("SINGAPORE", "TikTok deepfake detection", g_tech),
    ("BOGOTA", "Tax reform protests", g_people),
    ("FRANKFURT", "Lufthansa to cut 1,000 jobs", g_money),
    ("AMAZON", "Lula recognises Raoni's land", g_climate),
    ("SENEGAL", "Boat capsizes; dozens missing", g_disaster),
    ("GENEVA", "IMF: debt near 100% of GDP", g_money),
    ("MOGADISHU", "Somalia expels UAE ambassador", g_politics),
    ("HARARE", "250,000 landmines destroyed", g_disaster),
    ("NAIROBI", "Runner banned three years", g_people),
    ("PORT-AU-PRINCE", "34 gang suspects killed", g_war),
    ("DHAKA", "Hasina backers riot", g_people),
    ("ULAANBAATAR", "Mongolia's president resigns", g_politics),
    ("LOS ANGELES", "El Nino flood risk", g_disaster),
    ("VATICAN", "Christmas tree raised", g_people),
    ("SYDNEY", "Marathon title stripped", g_people),
    ("ADDIS ABABA", "Artillery near Badme", g_war),
    ("BERLIN", "Youth strike on rearmament", g_people),
]

REGIONS = [
    ("EUROPE", 13, BLUE),
    ("ASIA", 8, RED),
    ("AMERICAS", 9, GREEN),
    ("MIDEAST", 4, PLUM),
    ("AFRICA", 5, SAND),
    ("PACIFIC", 2, TEAL),
    ("GLOBAL", 1, MUTED),
]

TOTAL = len(TILES) + len(BRIEFS)


def build() -> Image.Image:
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    f_kick = font(SANS_BK, 19)
    draw_tracked(d, (M, 26), "WORLD NEWS · ONE DAY", f_kick, INK, track=2)
    right = f"{TOTAL} STORIES · 7 REGIONS"
    rw = text_w(d, right, f_kick, track=2)
    draw_tracked(d, (W - M - rw, 26), right, f_kick, MUTED, track=2)

    date = "FRIDAY 20 NOVEMBER 2026"
    f_date = fit_line(d, date, SERIF_B, W - 2 * M, 88, 54)
    dw = text_w(d, date, f_date)
    d.text(((W - dw) / 2, 52), date, font=f_date, fill=INK)
    date_bottom = 52 + int(f_date.size * 1.02)
    d.rectangle((M, date_bottom + 4, W - M, date_bottom + 9), fill=INK)

    f_strap = font(SERIF_I, 19)
    strap = "Reported by Reuters, AP, BBC, AFP, PTI and CNBC · every story from this one day"
    d.text(((W - text_w(d, strap, f_strap)) / 2, date_bottom + 15), strap,
           font=f_strap, fill=MUTED)

    # ---- metrics bar ---------------------------------------------
    bar_top = date_bottom + 44
    bar_h = 64
    cell_w = (W - 2 * M) / len(METRICS)
    d.rectangle((M, bar_top, W - M, bar_top + bar_h), fill=CARD)
    d.rectangle((M, bar_top, W - M, bar_top + 3), fill=INK)
    f_val = font(SANS_BK, 26)
    f_lab = font(SANS_BK, 13)
    for i, (val, lab) in enumerate(METRICS):
        cx = M + cell_w * i
        d.text((cx + 12, bar_top + 6), val, font=f_val,
               fill=RED if i < 3 else BLUE)
        for j, ln in enumerate(wrap(d, lab, f_lab, int(cell_w) - 22)[:2]):
            d.text((cx + 12, bar_top + 37 + j * 14), ln, font=f_lab, fill=MUTED)
        if i:
            d.line((cx, bar_top + 8, cx, bar_top + bar_h - 8), fill=STONE, width=1)

    # ---- twelve illustrated tiles --------------------------------
    tiles_top = bar_top + bar_h + 12
    cols, gap = 3, 10
    tile_w = (W - 2 * M - (cols - 1) * gap) // cols
    tile_h = 74
    rows = (len(TILES) + cols - 1) // cols
    f_num = font(SANS_BK, 15)
    f_place = font(SANS_BK, 15)
    for idx, (place, head, glyph, accent) in enumerate(TILES):
        r, c = divmod(idx, cols)
        x = M + c * (tile_w + gap)
        y = tiles_top + r * (tile_h + gap)
        d.rectangle((x, y, x + tile_w, y + tile_h), fill=CARD, outline=STONE, width=1)
        d.rectangle((x, y, x + 56, y + 56), fill=(240, 235, 224))
        glyph(d, x + 2, y + 2, 52)
        d.text((x + 60, y + 6), f"{idx + 1}", font=f_num, fill=accent)
        draw_tracked(d, (x + 78, y + 7), place, f_place, MUTED, track=1)
        hf = fit_block(d, head, SERIF_B, 18, 15, tile_w - 66, 2)
        lines = wrap(d, head, hf, tile_w - 66)
        assert len(lines) <= 2, f"tile headline too long: {place}"
        hy = y + 26
        for ln in lines:
            d.text((x + 60, hy), ln, font=hf, fill=INK)
            hy += 18
    tiles_bottom = tiles_top + rows * tile_h + (rows - 1) * gap

    # ---- region bar ----------------------------------------------
    reg_top = tiles_bottom + 12
    seg_w = (W - 2 * M) / len(REGIONS)
    d.rectangle((M, reg_top, W - M, reg_top + 26), fill=STONE)
    f_seg = font(SANS_BK, 15)
    for i, (name, n, col) in enumerate(REGIONS):
        x = M + seg_w * i
        d.rectangle((x, reg_top, x + seg_w - 2, reg_top + 26), fill=col)
        label = f"{n}"
        d.text((x + 10, reg_top + 6), label, font=f_seg, fill=PAPER)
    f_reg = font(SANS_BK, 13)
    for i, (name, n, col) in enumerate(REGIONS):
        x = M + seg_w * i
        d.text((x + 10, reg_top + 28), name, font=f_reg, fill=MUTED)

    # ---- briefs, two columns -------------------------------------
    briefs_top = reg_top + 50
    d.rectangle((M, briefs_top, W - M, briefs_top + 3), fill=INK)
    cols_b = 2
    rows_b = (len(BRIEFS) + cols_b - 1) // cols_b
    col_w = (W - 2 * M - 14) // cols_b
    lh = 21
    f_b_place = font(SANS_BK, 13)
    f_b_text = font(SERIF, 15)
    y0 = briefs_top + 10
    for idx, (place, head, glyph) in enumerate(BRIEFS):
        col, row = divmod(idx, rows_b)
        x = M + col * (col_w + 14)
        y = y0 + row * lh
        d.rectangle((x, y + 5, x + 5, y + 10), fill=MUTED)
        px = draw_tracked(d, (x + 11, y + 1), place, f_b_place, INK, track=1)
        d.text((px + 7, y), head, font=f_b_text, fill=INK)
        assert px + 7 + text_w(d, head, f_b_text) <= x + col_w, \
            f"brief overflows: {place} / {head}"
    briefs_bottom = y0 + (rows_b - 1) * lh + 18

    # ---- date check ----------------------------------------------
    box_top = H - 58
    assert briefs_bottom <= box_top - 6, f"briefs overrun the footer ({briefs_bottom})"
    d.rectangle((M, box_top, W - M, H - 12), outline=RED, width=2)
    f_dc_lab = font(SANS_BK, 14)
    d.text((M + 12, box_top + 8), "DATE CHECK", font=f_dc_lab, fill=RED)
    f_dc = font(SANS, 14)
    note = ("Every story above happened, or was first reported, on Friday 20 November 2026. "
            "The Shenzhen summit, Anthropic's debut and the ICJ verdict broke earlier and are left out.")
    nx = M + 118
    for j, ln in enumerate(wrap(d, note, f_dc, W - nx - M - 12)[:2]):
        d.text((nx, box_top + 8 + j * 16), ln, font=f_dc, fill=MUTED)
    return img


def main() -> int:
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir,
                       "entry.png")
    img = build().convert("RGB")
    img.save(out, format="PNG", optimize=True, compress_level=9)
    print(f"wrote {os.path.normpath(out)} {img.size} {os.path.getsize(out)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
