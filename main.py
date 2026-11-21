#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There.

Draws one invented passport spread for the Republic of Krzvania — a desert
caravan-route republic — and writes it to /output/entry.png (1024x1024).

Holder: Amina Rashid, licensed caravan guide, licence C-0917. Every date is
internally consistent: issued 12 FEB 2024, every stamp after issue, expiry
11 FEB 2034 (issue + 10 years), MRZ check digits per ICAO 9303, stamps paired
arrival/departure on matching dates, visa valid 01-30 SEP 2025 covering the
09-27 SEP 2025 Mirazh trip. No network at runtime; the portrait is read from
portrait.jpg beside this file (with a drawn silhouette fallback).
"""

import hashlib
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

# ---------------------------------------------------------------- data ----
SURNAME = "RASHID"
GIVEN = "AMINA"
PASSPORT_NO = "KZ4829107"
CODE = "KRZ"
NATIONALITY = "KRZVANIAN"
DOB = "17 JUN 1990"
DOB_MRZ = "900617"
SEX = "F"
BIRTHPLACE = "VRKHAN"
ISSUE = "12 FEB 2024"
EXPIRY = "11 FEB 2034"
EXPIRY_MRZ = "340211"
AUTHORITY = "CARAVAN REGISTRY, VRKHAN"
PERSONAL_NO = "1706 1990 55"
PERSONAL_MRZ = "1706199055<<<<"
MRZ_L1 = "P<KRZRASHID<<AMINA" + "<" * 26
MRZ_L2 = "KZ48291074KRZ9006175F34021111706199055<<<<51"

# ---------------------------------------------------------------- palette --
CREAM = (245, 239, 224)
CREAM_DARK = (238, 229, 205)
PAPER = (250, 246, 235)
INK = (28, 32, 58)          # deep indigo, the document's main ink
INDIGO = (31, 42, 82)
INDIGO_SOFT = (58, 68, 110)
OCHRE = (176, 124, 38)
OCHRE_SOFT = (198, 152, 74)
GREY = (110, 108, 96)
RED = (148, 38, 44)         # Krzvania home stamps
BLUE = (36, 84, 138)        # Tazir stamps
GREEN = (46, 110, 68)       # Mirazh stamps
GUILLOCHE = (226, 212, 178)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)

W, H = 1024, 1024
PAGE_W, PAGE_H = 494, 996
GAP = 12
MARGIN = 14

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_SANS = lambda s: font("DejaVuSans.ttf", s)
F_SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
F_MONO = lambda s: font("DejaVuSansMono.ttf", s)
F_MONO_B = lambda s: font("DejaVuSansMono-Bold.ttf", s)


def text(draw, xy, s, f, fill=INK, anchor="la"):
    draw.text(xy, s, font=f, fill=fill, anchor=anchor)


def text_w(draw, s, f):
    box = draw.textbbox((0, 0), s, font=f)
    return box[2] - box[0]


def ls_text(draw, xy, s, f, fill=INK, spacing=2, anchor="la"):
    """Draw text with letter-spacing (for small-caps labels)."""
    x, y = xy
    for ch in s:
        draw.text((x, y), ch, font=f, fill=fill, anchor="la")
        x += draw.textlength(ch, font=f) + spacing
    return x


def wrap(draw, s, f, max_w):
    """Greedy word wrap, returns list of lines."""
    lines, cur = [], ""
    for word in s.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def guilloche(page, x0, y0, x1, y1):
    """Faint wavy security lines across a page region."""
    d = ImageDraw.Draw(page, "RGBA")
    step = 9
    for yy in range(y0, y1, step):
        pts = []
        for xx in range(x0, x1 + 1, 8):
            pts.append((xx, yy + 2.2 * math.sin((xx - x0) / 26.0)))
        d.line(pts, fill=GUILLOCHE + (110,), width=1)
    # faint large watermark circle behind the data area
    d.ellipse([x0 + 150, y0 + 330, x0 + 400, y0 + 580],
              outline=(196, 178, 140, 90), width=1)
    d.ellipse([x0 + 175, y0 + 355, x0 + 375, y0 + 555],
              outline=(196, 178, 140, 70), width=1)


def emblem(draw, cx, cy, r, ink=INDIGO):
    """Republic of Krzvania emblem: ring, sun over three dunes."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ink, width=3)
    draw.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6],
                 outline=ink, width=1)
    # sun
    draw.ellipse([cx - 6, cy - r + 12, cx + 6, cy - r + 24], fill=ink)
    # dunes
    for k, (a0, a1, yy) in enumerate(((200, 340, 0), (195, 345, 7),
                                     (190, 350, 14))):
        draw.arc([cx - r + 12, cy - r + 22 + yy, cx + r - 12,
                  cy + r - 6 + yy], a0, a1, fill=ink, width=2)


# ------------------------------------------------------------ data page ---
def load_portrait(w, h):
    """Passport photo from portrait.jpg beside this file, else a silhouette."""
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "portrait.jpg")
    if os.path.exists(path):
        im = Image.open(path).convert("RGB")
        return ImageOps.fit(im, (w, h), Image.LANCZOS)
    im = Image.new("RGB", (w, h), (214, 210, 198))
    d = ImageDraw.Draw(im)
    d.ellipse([w * 0.30, h * 0.08, w * 0.70, h * 0.48], fill=(120, 110, 96))
    d.ellipse([w * 0.12, h * 0.52, w * 0.88, h * 1.05], fill=(120, 110, 96))
    return im


def field(draw, x, y, label, value, vfont, label_w=0):
    text(draw, (x, y), label, F_SANS(11), fill=GREY)
    text(draw, (x, y + 14), value, vfont, fill=BLACK)


def data_page(page):
    d = ImageDraw.Draw(page, "RGBA")
    x0, y0 = 16, 14
    guilloche(page, x0, y0, PAGE_W - 16, PAGE_H - 110)
    d = ImageDraw.Draw(page, "RGBA")

    # passport number, top right
    text(d, (PAGE_W - 18, 16), PASSPORT_NO, F_MONO_B(13), fill=INDIGO,
         anchor="ra")

    # emblem + titles
    emblem(d, PAGE_W // 2, 38, 19)
    text(d, (PAGE_W // 2, 64), "REPUBLIC OF KRZVANIA", F_SERIF_B(26),
         fill=INDIGO, anchor="ma")
    text(d, (PAGE_W // 2, 94), "REPUBLIKA KRZVANIJA", F_SERIF_B(13),
         fill=INDIGO_SOFT, anchor="ma")
    lx = PAGE_W // 2 - 78
    ls_text(d, (lx, 114), "PASAR", F_SANS_B(11), fill=INDIGO, spacing=6)
    dot_x = lx + 62
    d.ellipse([dot_x, 118, dot_x + 4, 122], fill=INDIGO)
    ls_text(d, (dot_x + 12, 114), "PASSPORT", F_SANS_B(11), fill=INDIGO,
            spacing=6)
    d.line([(x0, 134), (PAGE_W - 16, 134)], fill=INDIGO, width=1)

    # type / code / passport number row
    y = 146
    field(d, x0, y, "TIP / TYPE", "P", F_SANS_B(17))
    field(d, 96, y, "KOD / CODE", CODE, F_SANS_B(17))
    field(d, 196, y, "PAS NR. / PASSPORT NO.", PASSPORT_NO, F_SANS_B(17))

    # portrait, left
    px, py, pw, ph = x0, 202, 148, 186
    photo = load_portrait(pw, ph)
    page.paste(photo, (px, py))
    d.rectangle([px, py, px + pw, py + ph], outline=INDIGO, width=2)
    d = ImageDraw.Draw(page, "RGBA")

    # fields, right of portrait
    fx = 182
    field(d, fx, 202, "FAMAR / SURNAME", SURNAME, F_SANS_B(19))
    field(d, fx, 246, "ANVAR / GIVEN NAMES", GIVEN, F_SANS_B(19))
    field(d, fx, 290, "VATENAR / NATIONALITY", NATIONALITY, F_SANS_B(19))
    field(d, fx, 334, "DUNVAR / DATE OF BIRTH", DOB, F_SANS_B(17))
    field(d, 396, 334, "KESH / SEX", SEX, F_SANS_B(17))

    # signature under portrait (script-ish, slight tilt via shear-free draw)
    sig = Image.new("RGBA", (180, 36), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sig)
    sd.text((4, 4), "Amina Rashid", font=F_SERIF_B(19), fill=INK)
    sig = sig.rotate(-2, resample=Image.BICUBIC, expand=True)
    page.paste(sig, (x0, 398), sig)
    text(d, (x0, 430), "IMZAR / HOLDER'S SIGNATURE", F_SANS(10), fill=GREY)

    # lower fields, full width
    field(d, x0, 458, "DUNVAR-ESH / PLACE OF BIRTH", BIRTHPLACE, F_SANS_B(17))
    field(d, x0, 502, "ISHAR / DATE OF ISSUE", ISSUE, F_SANS_B(17))
    field(d, 246, 502, "ISHDAL / DATE OF EXPIRY", EXPIRY, F_SANS_B(17))
    field(d, x0, 546, "DAFTAR / AUTHORITY", AUTHORITY, F_SANS_B(15))
    field(d, x0, 590, "SHAKH NR. / PERSONAL NO.", PERSONAL_NO, F_SANS_B(17))

    # ghost image, bottom right of data area
    ghost = load_portrait(92, 92).convert("L")
    ghost = ImageOps.colorize(ghost, black=(245, 239, 224),
                              white=(120, 110, 96))
    ghost.putalpha(110)
    page.paste(ghost, (PAGE_W - 112, 544), ghost)
    d.rectangle([PAGE_W - 112, 544, PAGE_W - 20, 636], outline=GREY, width=1)
    d = ImageDraw.Draw(page, "RGBA")

    # observations box
    oy = 644
    d.rectangle([x0, oy, PAGE_W - 16, oy + 84], outline=INDIGO, width=1)
    text(d, (x0 + 10, oy + 8), "MERKAR / OBSERVATIONS", F_SANS_B(11),
         fill=INDIGO)
    obs = ("Holder is a licensed caravan guide, licence C-0917. "
           "Desert crossing endorsement on page 5.")
    yy = oy + 28
    for line in wrap(d, obs, F_SANS(13), PAGE_W - 36):
        text(d, (x0 + 10, yy), line, F_SANS(13), fill=BLACK)
        yy += 18

    # MRZ strip
    mz_y = PAGE_H - 108
    d.rectangle([0, mz_y, PAGE_W, PAGE_H], fill=WHITE)
    d.line([(0, mz_y), (PAGE_W, mz_y)], fill=INDIGO, width=1)
    text(d, (14, mz_y + 12), MRZ_L1, F_MONO(17), fill=BLACK)
    text(d, (14, mz_y + 38), MRZ_L2, F_MONO(17), fill=BLACK)


# ----------------------------------------------------------- visas page ---
def stamp_layer(w, h, country, native, kind, date, post, color, angle):
    """One entry/exit stamp on its own transparent layer, slightly rotated."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([3, 3, w - 4, h - 4], radius=8, outline=color + (225,),
                        width=2)
    d.line([(10, 26), (w - 11, 26)], fill=color + (200,), width=1)
    text(d, (w // 2, 6), country, F_SANS_B(15), fill=color + (235,),
         anchor="ma")
    text(d, (w // 2, 30), native, F_SANS(9), fill=color + (210,), anchor="ma")
    arrow = "->" if kind == "ARRIVAL" else "<-"
    text(d, (w // 2, 42), kind + " " + arrow, F_SANS_B(11),
         fill=color + (235,), anchor="ma")
    text(d, (w // 2, 54), date, F_MONO_B(14), fill=color + (235,), anchor="ma")
    text(d, (w // 2, 68), post, F_SANS(8), fill=color + (210,), anchor="ma")
    return layer.rotate(angle, resample=Image.BICUBIC, expand=False)


def round_stamp(r, lines, color, angle):
    """Round toll stamp: two rings + centred lines, padded so rotation
    never clips the text at the layer edges."""
    pad = 20
    size = r * 2 + pad * 2
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = cy = size // 2
    d.ellipse([pad, pad, size - pad - 1, size - pad - 1],
              outline=color + (225,), width=3)
    d.ellipse([pad + 8, pad + 8, size - pad - 9, size - pad - 9],
              outline=color + (200,), width=1)
    y = cy - 32
    for s, f, step in lines:
        text(d, (cx, y), s, f, fill=color + (235,), anchor="ma")
        y += step
    return layer.rotate(angle, resample=Image.BICUBIC, expand=False)


def visas_page(page):
    d = ImageDraw.Draw(page, "RGBA")
    guilloche(page, 16, 14, PAGE_W - 16, PAGE_H - 16)
    d = ImageDraw.Draw(page, "RGBA")

    text(d, (16, 16), "VIZAR", F_SERIF_B(22), fill=INDIGO)
    text(d, (108, 16), "·", F_SERIF_B(22), fill=INDIGO)
    text(d, (126, 16), "VISAS", F_SERIF_B(22), fill=INDIGO)
    text(d, (PAGE_W - 18, 18), "5", F_SANS(14), fill=GREY, anchor="ra")

    # ---- desert crossing endorsement box
    ey, eh = 52, 160
    d.rectangle([16, ey, PAGE_W - 16, ey + eh], outline=INDIGO, width=2)
    text(d, (28, ey + 10), "DESERT CROSSING ENDORSEMENT", F_SANS_B(14),
         fill=INDIGO)
    text(d, (28, ey + 32), "MERKA — VRKHAN, ISSUED 12 FEB 2024",
         F_SANS_B(11), fill=INDIGO_SOFT)
    body = ("ERG CROSSINGS CLOSED JUN–AUG WITHOUT WATER PERMIT. BEARER "
            "MUST REGISTER AT THE WELL STATION BEFORE EACH CROSSING. "
            "VALID WITH GUIDE LICENCE C-0917.")
    yy = ey + 56
    for line in wrap(d, body, F_SANS(12), PAGE_W - 64):
        text(d, (28, yy), line, F_SANS(12), fill=BLACK)
        yy += 17

    # round caravan toll stamp, overlapping the box corner
    toll = round_stamp(46, [
        ("CARAVAN", F_SANS_B(11), 15),
        ("18 KRD", F_SANS_B(20), 20),
        ("TOLL PAID", F_SANS_B(11), 14),
        ("08 APR 2024", F_MONO_B(10), 0),
    ], RED, -6)
    page.paste(toll, (PAGE_W - 146, 146), toll)
    d = ImageDraw.Draw(page, "RGBA")

    # ---- stamps, block A: the April 2024 Tazir trip
    trips_a = [
        ("KRZVANIA", "Republika Krzvanija", "DEPARTURE", "08 APR 2024",
         "VRKHAN", RED, -2),
        ("TAZIR", "Tazir Jumhuriyati", "ARRIVAL", "08 APR 2024",
         "TAZIR GATE", BLUE, 2),
        ("TAZIR", "Tazir Jumhuriyati", "DEPARTURE", "19 APR 2024",
         "TAZIR GATE", BLUE, -1),
        ("KRZVANIA", "Republika Krzvanija", "ARRIVAL", "19 APR 2024",
         "VRKHAN", RED, 1),
    ]
    # ---- stamps, block B: the September 2025 Mirazh trip (visa covers it)
    trips_b = [
        ("KRZVANIA", "Republika Krzvanija", "DEPARTURE", "09 SEP 2025",
         "VRKHAN", RED, 2),
        ("MIRAZH", "Mirazh Tasavald", "ARRIVAL", "09 SEP 2025",
         "ERG POST", GREEN, -2),
        ("MIRAZH", "Mirazh Tasavald", "DEPARTURE", "27 SEP 2025",
         "ERG POST", GREEN, 1),
        ("KRZVANIA", "Republika Krzvanija", "ARRIVAL", "27 SEP 2025",
         "VRKHAN", RED, -1),
    ]
    sw, sh, gap = 222, 86, 12
    for block, y0 in ((trips_a, 268), (trips_b, 660)):
        for i, (country, native, kind, date, post, color, angle) in \
                enumerate(block):
            x = 16 + (i % 2) * (sw + gap)
            y = y0 + (i // 2) * (sh + gap)
            layer = stamp_layer(sw, sh, country, native, kind, date, post,
                                color, angle)
            page.paste(layer, (x, y), layer)
    d = ImageDraw.Draw(page, "RGBA")

    # ---- Mirazh visitor visa box (between the two trips)
    vy, vh = 476, 160
    d.rectangle([16, vy, PAGE_W - 16, vy + vh], fill=(232, 240, 228),
                outline=GREEN, width=2)
    text(d, (28, vy + 10), "MIRAZH · VISITOR VISA · MIRAZH TASAVALD",
         F_SANS_B(13), fill=GREEN)
    d.line([(28, vy + 32), (PAGE_W - 28, vy + 32)], fill=GREEN, width=1)
    field(d, 28, vy + 44, "TYPE", "C · SINGLE ENTRY", F_SANS_B(14))
    field(d, 262, vy + 44, "DURATION OF STAY", "30 DAYS", F_SANS_B(14))
    field(d, 28, vy + 86, "VALID FROM", "01 SEP 2025", F_SANS_B(14))
    field(d, 262, vy + 86, "UNTIL", "30 SEP 2025", F_SANS_B(14))
    field(d, 28, vy + 122, "ISSUED AT", "VRKHAN, 18 AUG 2025",
         F_SANS_B(13))
    field(d, 262, vy + 122, "FEE", "25 MZD", F_SANS_B(14))

    text(d, (PAGE_W - 18, PAGE_H - 22), PASSPORT_NO, F_MONO(11), fill=GREY,
         anchor="ra")


# ------------------------------------------------------------------ main --
def build():
    img = Image.new("RGB", (W, H), INDIGO)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=(10, 12, 28), width=4)
    left = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    data_page(left)
    right = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    visas_page(right)
    img.paste(left, (MARGIN, MARGIN))
    img.paste(right, (MARGIN + PAGE_W + GAP, MARGIN))
    # centre spine shadow
    d = ImageDraw.Draw(img)
    d.line([(MARGIN + PAGE_W + GAP // 2, MARGIN),
            (MARGIN + PAGE_W + GAP // 2, MARGIN + PAGE_H)],
           fill=(10, 12, 28), width=2)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img = build()
    img.save(out, "PNG", optimize=True)
    data = open(out, "rb").read()
    print(f"wrote {out}: {img.size[0]}x{img.size[1]}, "
          f"{len(data)} bytes, sha256 "
          f"{hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
