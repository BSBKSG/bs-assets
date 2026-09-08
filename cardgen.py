#!/usr/bin/env python3
"""Branded quote-card generator for B&S Bookkeeping social posts."""
import sys, json
from PIL import Image, ImageDraw, ImageFont

GF = "/usr/share/fonts/truetype/google-fonts/"
NAVY   = (13, 30, 58)
NAVY_2 = (20, 41, 74)
GOLD   = (196, 154, 40)
PAPER  = (245, 245, 241)
MUTED  = (150, 165, 190)

S = 800
K = S / 1080.0          # design was drawn at 1080; scale everything
M = round(92 * K)


def f(name, size):
    return ImageFont.truetype(GF + name, size)


def track(d, xy, text, font, fill, sp):
    """Draw text with manual letter-spacing."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + sp
    return x - xy[0] - sp


def wrap_to_width(d, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def make_card(headline, eyebrow, out_path):
    img = Image.new("RGB", (S, S), NAVY)
    d = ImageDraw.Draw(img)

    # faint ledger rules
    for y in range(M + round(150*K), S - round(210*K), round(46*K)):
        d.line([(M, y), (S - M, y)], fill=NAVY_2, width=1)

    # gold corner rule, top-left
    d.line([(M, M), (M + round(96*K), M)], fill=GOLD, width=max(2, round(4*K)))
    d.line([(M, M), (M, M + round(96*K))], fill=GOLD, width=max(2, round(4*K)))

    fe = f("Poppins-Medium.ttf", round(25*K))
    track(d, (M, M + round(130*K)), eyebrow.upper(), fe, GOLD, 3.2*K)

    max_w = S - 2 * M
    for size in [round(v*K) for v in (74, 68, 62, 56, 50, 45)]:
        fh = f("Lora-Variable.ttf", size)
        lines = wrap_to_width(d, headline, fh, max_w)
        lh = int(size * 1.34)
        if len(lines) * lh <= 520*K:
            break

    top, bottom = M + round(200*K), S - M - round(130*K)
    y = top + max(0, ((bottom - top) - len(lines) * lh) // 2)
    for ln in lines:
        d.text((M, y), ln, font=fh, fill=PAPER)
        y += lh

    fy = S - M - round(74*K)
    d.line([(M, fy - round(46*K)), (S - M, fy - round(46*K))], fill=GOLD, width=2)

    fb = f("Poppins-Bold.ttf", round(25*K))
    track(d, (M, fy), "B&S BOOKKEEPING", fb, PAPER, 2.6*K)

    fr = f("Poppins-Regular.ttf", round(24*K))
    d.text((M, fy + round(38*K)),
           "bsbooksg.com  ·  WhatsApp +65 8912 0656", font=fr, fill=MUTED)

    img.quantize(palette=brand_palette(), dither=Image.NONE).save(
        out_path, "PNG", optimize=True)
    return out_path


def brand_palette():
    """Fixed 12-colour palette. Keeps navy/gold/paper EXACT (an adaptive
    palette merges the gold away, it covers so little area) while cutting the
    file to ~12KB so the base64 upload payload stays small."""
    def blend(a, b, t):
        return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))

    pal = [NAVY, NAVY_2, GOLD, PAPER, MUTED]
    pal += [blend(NAVY, PAPER, t) for t in (0.2, 0.4, 0.6, 0.8)]
    pal += [blend(NAVY, GOLD, t) for t in (0.35, 0.7)]
    pal += [blend(NAVY, MUTED, 0.5)]

    p = Image.new("P", (1, 1))
    p.putpalette([c for col in pal for c in col] + [0, 0, 0] * (256 - len(pal)))
    return p


if __name__ == "__main__":
    spec = json.loads(sys.argv[1])
    print(make_card(spec["headline"], spec["eyebrow"], spec["out"]))
