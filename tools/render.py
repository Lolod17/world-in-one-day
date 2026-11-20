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
M = 40                      # page margin
COLW = 304                  # width of one of the three splash columns
GUTTER = 16

PAPER = (246, 241, 231)
INK = (20, 17, 14)
MUTED = (90, 84, 75)
CARD = (255, 253, 248)
RED = (168, 18, 27)
BLUE = (20, 57, 110)
TEAL = (14, 92, 99)
SAND = (200, 162, 74)
SLATE = (46, 50, 60)
STONE = (201, 192, 174)
RIVER = (126, 154, 163)

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


def text_w(draw: ImageDraw.ImageDraw, s: str, f: ImageFont.FreeTypeFont,
           track: int = 0) -> int:
    if not s:
        return 0
    if track:
        return int(sum(draw.textlength(ch, font=f) for ch in s)) + track * (len(s) - 1)
    return int(draw.textlength(s, font=f))


def wrap(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont,
         maxw: int) -> list[str]:
    """Greedy wrap on spaces; returns the lines that fit maxw."""
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if text_w(draw, trial, f) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_block(draw, text, path, max_size, min_size, maxw, max_lines, step=1):
    """Largest font size at which the text wraps into at most max_lines."""
    size = max_size
    while size > min_size:
        f = font(path, size)
        if len(wrap(draw, text, f, maxw)) <= max_lines:
            return f
        size -= step
    return font(path, min_size)


def fit_line(draw, text, path, maxw, hi, lo):
    """Largest font size that keeps one word-line within maxw."""
    size = hi
    while size > lo:
        f = font(path, size)
        if text_w(draw, text, f) <= maxw:
            return f
        size -= 1
    return font(path, lo)


def draw_tracked(draw, xy, s, f, fill, track=0):
    x, y = xy
    for ch in s:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + track
    return x


# ---------------------------------------------------------------- artwork


def art_bridge(d: ImageDraw.ImageDraw, box) -> None:
    """Night river with a struck bridge and two incoming missiles."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=SLATE)
    d.rectangle((x0, y0 + int(h * 0.62), x1, y1), fill=RIVER)
    d.rectangle((x0, y0 + int(h * 0.60), x1, y0 + int(h * 0.64)), fill=INK)
    deck_y = y0 + int(h * 0.50)
    d.rectangle((x0, deck_y, x1, deck_y + 7), fill=INK)
    span = w / 3.0
    for i in range(3):
        cx0 = x0 + span * i
        d.arc((cx0 + 6, deck_y + 6, cx0 + span - 6, deck_y + int(h * 0.34)),
              180, 360, fill=INK, width=5)
    for i in range(4):
        px = x0 + span * i
        d.rectangle((px - 3, deck_y, px + 3, y0 + int(h * 0.66)), fill=INK)
    d.rectangle((x0, y0 + int(h * 0.30), x1, y0 + int(h * 0.30) + 4),
                fill=(70, 76, 88))
    for sx, sy, ex, ey in ((x0 + w * 0.06, y0 + h * 0.04, x0 + w * 0.44, deck_y - 6),
                           (x1 - w * 0.02, y0 + h * 0.12, x0 + w * 0.70, deck_y - 10)):
        d.line((sx, sy, ex, ey), fill=(236, 232, 222), width=4)
        d.line((sx, sy, ex, ey), fill=RED, width=2)
    cx, cy = x0 + w * 0.56, deck_y - 4
    for dx, dy in ((16, 0), (-16, 0), (0, 15), (0, -15), (11, 11), (-11, 11),
                   (11, -11), (-11, -11)):
        d.line((cx, cy, cx + dx, cy + dy), fill=SAND, width=3)
    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(248, 226, 154))
    d.rectangle((cx - 3, deck_y + 8, cx + 3, y1), fill=(120, 40, 34))


def art_cyclone(d: ImageDraw.ImageDraw, box) -> None:
    """Storm spiral over a teal sea, land to the right, track arrow inland."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=TEAL)
    d.polygon([(x0 + w * 0.74, y1), (x0 + w * 0.80, y0 + h * 0.30),
               (x1, y0 + h * 0.16), (x1, y1)], fill=SAND)
    cx, cy = x0 + w * 0.40, y0 + h * 0.52
    for r, wd in ((66, 9), (44, 8), (22, 7)):
        d.arc((cx - r, cy - r * 0.72, cx + r, cy + r * 0.72), 20, 300,
              fill=(255, 255, 255), width=wd)
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=(255, 255, 255))
    ax0, ay0 = x0 + w * 0.40, y0 + h * 0.30
    ax1, ay1 = x0 + w * 0.88, y0 + h * 0.34
    d.line((ax0, ay0, ax1, ay1), fill=(255, 255, 255), width=3)
    d.polygon([(ax1 + 12, ay1 + 2), (ax1 - 6, ay1 - 7), (ax1 - 6, ay1 + 11)],
              fill=(255, 255, 255))
    for i in range(20):
        rx = x0 + 8 + (i * 37) % (w - 16)
        ry = y0 + 10 + (i * 53) % int(h * 0.32)
        d.line((rx, ry, rx + 5, ry + 10), fill=(214, 236, 236), width=2)


def art_chart(d: ImageDraw.ImageDraw, box) -> None:
    """A market chart breaking down, labelled with the day's fall."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=CARD)
    pct = "-4.8%"
    f_pct = font(SANS_BK, 36)
    d.text((x1 - 14 - text_w(d, pct, f_pct), y0 + 2), pct, font=f_pct, fill=RED)
    plot_top = y0 + int(h * 0.48)
    plot_h = h - (plot_top - y0) - 10
    for i in range(1, 4):
        gy = plot_top + plot_h * i / 4.0
        d.line((x0 + 12, gy, x1 - 12, gy), fill=STONE, width=1)
    pts = [(0.00, 0.10), (0.14, 0.02), (0.28, 0.26), (0.42, 0.20),
           (0.56, 0.44), (0.70, 0.38), (0.84, 0.66), (1.00, 0.86)]
    poly = [(x0 + 14 + (w - 28) * px, plot_top + plot_h * py) for px, py in pts]
    d.line(poly, fill=BLUE, width=5, joint="curve")
    for px, py in poly[:-1]:
        d.ellipse((px - 3, py - 3, px + 3, py + 3), fill=BLUE)
    d.line(poly[-2] + poly[-1], fill=RED, width=8)
    ex, ey = poly[-1]
    d.polygon([(ex + 2, ey + 11), (ex - 16, ey - 2), (ex + 5, ey - 11)], fill=RED)


# ---------------------------------------------------------------- the day


SPLASH = [
    {
        "art": art_bridge,
        "place": "UKRAINE",
        "head": "Russia's biggest strike of the war hits three Kyiv bridges",
        "deck": "400 drones and 110 missiles; 8 killed and power cut across the west.",
        "source": "REUTERS · BBC",
        "accent": RED,
    },
    {
        "art": art_cyclone,
        "place": "INDIA",
        "head": "Cyclone Akvan comes ashore in Odisha",
        "deck": "370,000 evacuated before landfall near Gopalpur; 70-80 km/h winds.",
        "source": "IMD · PTI",
        "accent": RED,
    },
    {
        "art": art_chart,
        "place": "MARKETS",
        "head": "AI sell-off sinks Asia's shares",
        "deck": "Tokyo fell 4.8%, SoftBank 16%; Seoul halted sell orders on its index.",
        "source": "CNBC · AL JAZEERA",
        "accent": BLUE,
    },
]

CARDS = [
    ("BRUSSELS", "UK and EU agree youth mobility deal", BLUE),
    ("ANTALYA", "COP31 climate draft drops phaseout", BLUE),
    ("ROME", "CGIL strike over Italy's budget", RED),
    ("POLAND", "Missile debris falls in eastern Poland", RED),
]

BRIEFS = [
    ("WASHINGTON", "Senate passes permitting bill", BLUE),
    ("SEOUL", "111 caught cheating in Suneung", BLUE),
    ("IRAQ", "Iran-backed militia told to leave", RED),
    ("CALIFORNIA", "Nvidia subpoenaed on China chips", BLUE),
    ("PACIFIC", "US auctions deep-sea mining leases", BLUE),
    ("THE HAGUE", "Sanctions urged after ICJ ruling", BLUE),
    ("SUDAN", "Drone strike kills 10 at gold mine", RED),
    ("NEW YORK", "GTA VI takes $2.36bn on day one", BLUE),
    ("TOKYO", "Core inflation at a 2026 high", BLUE),
    ("BUDAPEST", "Hungary lifts veto on Ukraine talks", BLUE),
    ("LISBON", "Public-sector strike hits hospitals", RED),
    ("HORMUZ", "Tanker burns after hitting a mine", RED),
    ("RIYADH", "Houthi missiles hit KAFD district", RED),
    ("GAZA", "Troops cross the Yellow Line", RED),
    ("PYONGYANG", "IAEA sees Yongbyon expansion", RED),
    ("CARACAS", "US and Venezuela sign military pact", BLUE),
    ("COPENHAGEN", "Greenland security deal ratified", BLUE),
    ("ISLAMABAD", "22 militants killed in border raids", RED),
    ("BRASILIA", "Central bank sells $1bn of reserves", BLUE),
    ("SINGAPORE", "TikTok adds deepfake detection", BLUE),
    ("BOGOTA", "Thousands march against tax reform", RED),
    ("FRANKFURT", "Lufthansa to cut 1,000 jobs", BLUE),
    ("AMAZON", "Lula recognises Chief Raoni's land", BLUE),
    ("SENEGAL", "Boat capsizes; dozens missing", RED),
    ("GENEVA", "IMF sees debt near 100% of GDP", BLUE),
    ("MOGADISHU", "Somalia expels UAE ambassador", BLUE),
]

TOTAL_STORIES = len(SPLASH) + len(CARDS) + len(BRIEFS)


def build() -> Image.Image:
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead -------------------------------------------------
    f_kick = font(SANS_BK, 20)
    draw_tracked(d, (M, 30), "WORLD NEWS · ONE DAY", f_kick, INK, track=2)
    right = f"{TOTAL_STORIES} STORIES · 7 REGIONS"
    f_kick_r = font(SANS_BK, 20)
    rw = text_w(d, right, f_kick_r, track=2)
    draw_tracked(d, (W - M - rw, 30), right, f_kick_r, MUTED, track=2)

    date = "FRIDAY 20 NOVEMBER 2026"
    f_date = fit_line(d, date, SERIF_B, W - 2 * M, 92, 56)
    dw = text_w(d, date, f_date)
    d.text(((W - dw) / 2, 58), date, font=f_date, fill=INK)

    date_bottom = 58 + int(f_date.size * 1.02)
    d.rectangle((M, date_bottom + 5, W - M, date_bottom + 11), fill=INK)

    f_strap = font(SERIF_I, 21)
    strap = "Reported by Reuters, AP, BBC, AFP, PTI and CNBC · every story from this one day"
    d.text(((W - text_w(d, strap, f_strap)) / 2, date_bottom + 19), strap,
           font=f_strap, fill=MUTED)

    top = date_bottom + 50

    # ---- three splashes ------------------------------------------
    ART_H = 118
    H_HEAD, H_DECK = 35, 19
    SRC_H = 18
    f_deck = font(SANS, H_DECK)
    lh_deck = int(H_DECK * 1.22)

    splash_bottom = top
    for i, s in enumerate(SPLASH):
        x = M + i * (COLW + GUTTER)
        art_box = (x, top, x + COLW, top + ART_H)
        s["art"](d, art_box)
        d.rectangle((x, top, x + COLW, top + ART_H), outline=INK, width=2)
        f_tag = font(SANS_BK, 18)
        tag_w = text_w(d, s["place"], f_tag, track=2) + 16
        d.rectangle((x + 8, top + 8, x + 8 + tag_w, top + 34), fill=s["accent"])
        draw_tracked(d, (x + 16, top + 12), s["place"], f_tag, PAPER, track=2)

        hf = fit_block(d, s["head"], SERIF_B, H_HEAD, 28, COLW, 3)
        hlines = wrap(d, s["head"], hf, COLW)
        y = top + ART_H + 12
        for ln in hlines:
            d.text((x, y), ln, font=hf, fill=INK)
            y += int(hf.size * 1.09)
        y += 5
        dlines = wrap(d, s["deck"], f_deck, COLW)
        assert len(dlines) <= 3, f"deck too long: {s['place']} {len(dlines)}"
        for ln in dlines:
            d.text((x, y), ln, font=f_deck, fill=INK)
            y += lh_deck
        f_src = font(SANS_BK, SRC_H)
        draw_tracked(d, (x, y + 5), s["source"], f_src, s["accent"], track=1)
        splash_bottom = max(splash_bottom, y + 5 + SRC_H)

    # ---- four cards, one row -------------------------------------
    grid_top = splash_bottom + 16
    card_h, card_gap = 74, 14
    card_w = (W - 2 * M - 3 * card_gap) // 4
    f_num = font(SANS_BK, 18)
    f_place = font(SANS_BK, 16)
    for idx, (place, head, accent) in enumerate(CARDS):
        x = M + idx * (card_w + card_gap)
        d.rectangle((x, grid_top, x + card_w, grid_top + card_h), fill=CARD,
                    outline=STONE, width=1)
        d.rectangle((x, grid_top, x + card_w, grid_top + 5), fill=accent)
        d.text((x + 11, grid_top + 12), f"{idx + 4}", font=f_num, fill=accent)
        draw_tracked(d, (x + 38, grid_top + 14), place, f_place, MUTED, track=1)
        hf = fit_block(d, head, SERIF_B, 19, 16, card_w - 22, 2)
        lines = wrap(d, head, hf, card_w - 22)
        assert len(lines) <= 2, f"card headline too long: {place}"
        hy = grid_top + 33
        for ln in lines:
            d.text((x + 11, hy), ln, font=hf, fill=INK)
            hy += 19
    grid_bottom = grid_top + card_h

    # ---- the rest of the day, two columns ------------------------
    briefs_top = grid_bottom + 14
    d.rectangle((M, briefs_top, W - M, briefs_top + 4), fill=INK)
    f_label = font(SANS_BK, 18)
    draw_tracked(d, (M, briefs_top + 7), "ALSO ON THE DAY", f_label, MUTED, track=2)
    rows = (len(BRIEFS) + 1) // 2
    f_b_place = font(SANS_BK, 16)
    f_b_text = font(SERIF, 19)
    col_w = (W - 2 * M - 26) // 2
    lh_b = 23
    y0 = briefs_top + 32
    for idx, (place, head, accent) in enumerate(BRIEFS):
        col, row = idx // rows, idx % rows
        x = M + col * (col_w + 26)
        y = y0 + row * lh_b
        d.rectangle((x, y + 5, x + 6, y + 11), fill=accent)
        px = draw_tracked(d, (x + 15, y + 1), place, f_b_place, INK, track=1)
        d.text((px + 9, y - 1), head, font=f_b_text, fill=INK)
        assert px + 9 + text_w(d, head, f_b_text) <= x + col_w, \
            f"brief overflows its column: {place} / {head}"
    briefs_bottom = y0 + (rows - 1) * lh_b + 22

    # ---- footer --------------------------------------------------
    foot_rule = max(briefs_bottom + 10, H - 46)
    assert foot_rule + 42 <= H, f"footer overruns the page (rule at {foot_rule})"
    d.rectangle((M, foot_rule, W - M, foot_rule + 3), fill=STONE)
    f_foot = font(SANS, 17)
    foot = ("Date check: every story above happened, or was first reported, on "
            "Friday 20 November 2026; reporting that first broke earlier, such as "
            "the Shenzhen summit, is left out.")
    flines = wrap(d, foot, f_foot, W - 2 * M)
    assert len(flines) <= 2, "footer too long"
    fy = foot_rule + 8
    for ln in flines:
        d.text((M, fy), ln, font=f_foot, fill=MUTED)
        fy += 19

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
