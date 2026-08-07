#!/usr/bin/env python3
"""
Creative Edge Outdoor Living — brand lockup generator.

WHAT THIS BUILDS
----------------
  img/ce-wordmark.svg       the full lockup: monogram + CREATIVE EDGE / OUTDOOR LIVING
  img/ce-wordmark-1200.png  raster of the same, for schema logo / OG
  img/favicon-64.png        the real monogram, 64px
  favicon.png               the real monogram, 180px

THE MONOGRAM IS THE CLIENT'S REAL ASSET, NOT A RECREATION.
img/ce-monogram.svg was extracted from the client's own vector file
(assets/brand/CEL_logo_Vector.ai, page 2 = the dark colorway) with
build/extract_monogram.py. Geometry is untouched — the extraction only drops
the retired "Creative | edge landscaping Ltd" wordmark and the divider bar,
translates the remaining two paths to the origin, and changes FILLS.
⛔ Never redraw the hexagon by hand. If it needs to change, re-extract from
the .ai. A near-miss recreation of a client's own logo is worse than no logo.

PROOF IT IS THE SAME MARK: the extracted monogram's aspect ratio is 0.8632.
Measured off the vehicle wrap photo it is 0.8614 — a 0.2% delta.

WHY OSWALD AND NOT ARCHIVO
--------------------------
Every proportion below is MEASURED off the truck-wrap mockup, not guessed.
"CREATIVE EDGE" on the wrap has a width/cap-height ratio of 7.126. Archivo,
even at its narrowest width axis (62), is 8.19 — to force the match it needed
-0.22em tracking, which collides the letters into "CREATIVEEDGE". Oswald at
weight 700 is 7.65 natural and needs only -0.036em, and its stroke weight and
letterforms match the wrap. Both fonts are SIL OFL.

Text is converted to PATHS: no webfont download at runtime, no FOUT in a
sticky header, identical rendering everywhere, zero dependencies. That keeps
build.py's ownership promise intact — the output is a plain SVG.

USAGE:  python3 build/make_wordmark.py
"""
import pathlib
import re
import sys
import tempfile

try:
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
except ImportError:
    sys.exit("pip install fonttools")

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = pathlib.Path("/Users/johnmilne/apex_content/template/fonts/Oswald.ttf")
MONOGRAM = ROOT / "img" / "ce-monogram.svg"

BRAND = "#2BD11F"       # hue 116, sampled off the wrap. See css/site.css.
INK = "#FFFFFF"
DARK = "#0B0F12"

NAME = "CREATIVE EDGE"
DESC = "OUTDOOR LIVING"

# ---- CALIBRATED against IMG_2790 (truck wrap). Units: name cap height = 100.
# These started as raw pixel ratios measured off the wrap, then were solved by
# render-measure-adjust until the RENDERED lockup matched the photo, because
# nominal cap height is not what a photo measures: Oswald's round glyphs
# (C G O D) overshoot the cap line, so laying out to the nominal value left the
# name 4.3% narrow and the line gap 17% tight. Do not "restore" the raw ratios
# in the trailing comments - those are the inputs, these are the answers.
# Final fit vs the photo: mean deviation 0.70%, worst 2.74% (the name/descriptor
# gap, a sub-pixel difference at the compared scale). Monogram aspect 0.41%.
# Re-run build/verify via the comparison image in
# evidence/restyle_aug7/lockup_comparison.png if any of these change.
#
# The trailer photo (IMG_2791) is perspective-skewed enough that its two type
# rows overlap vertically, so it cannot be measured; the truck door is
# near-orthogonal and is the frame these came from.
NAME_W = 7.4347        # name width / name cap           (raw measure 7.1263)
DESC_RATIO = 0.4220    # desc cap / name cap             (raw measure 0.4316)
DESC_W = 10.7073       # desc width / desc cap           (raw measure 439/41)
GAP_RATIO = 0.1787     # name baseline -> desc cap top   (raw measure 0.1579)
RULE_RATIO = 0.0632    # green rule thickness / name cap (6 / 95)
PAD_RATIO = 0.6707     # rule -> desc text gap / desc cap  (27.5 / 41)
MONO_RATIO = 2.9034    # monogram height / name cap      (raw measure 2.8105)
MONO_GAP = 0.1169      # monogram -> type gap / mono h   (raw measure 0.1386)
V_OFFSET = 0.0412      # type block centre below monogram centre, / monogram h


def instanced():
    return instancer.instantiateVariableFont(TTFont(FONT), {"wght": 700})


def cap_height(font):
    return font["glyf"][font.getBestCmap()[ord("E")]].yMax


def run(font, text, size_px, track_px, x, baseline_y):
    """SVG path data + advance for `text` laid out at size_px with tracking."""
    gs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
    upm = font["head"].unitsPerEm
    scale = size_px / upm

    def ntos(v):                       # 2dp: full float precision triples size
        return f"{v:.2f}".rstrip("0").rstrip(".")

    parts, pen_x = [], x
    for ch in text:
        gname = cmap[ord(ch)]
        pen = SVGPathPen(gs, ntos=ntos)
        # y flips: font units go up, SVG goes down
        gs[gname].draw(TransformPen(pen, (scale, 0, 0, -scale, pen_x, baseline_y)))
        d = pen.getCommands()
        if d:
            parts.append(d)
        pen_x += hmtx[gname][0] * scale + track_px
    return " ".join(parts), (pen_x - track_px) - x


def solve_track(font, text, size_px, target_w):
    """Tracking (px) that makes `text` exactly target_w wide at size_px."""
    cmap, hmtx = font.getBestCmap(), font["hmtx"]
    upm = font["head"].unitsPerEm
    natural = sum(hmtx[cmap[ord(c)]][0] for c in text) * size_px / upm
    return (target_w - natural) / (len(text) - 1)


def monogram():
    """(inner svg markup, width, height) from the client's extracted vector."""
    s = MONOGRAM.read_text()
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', s)
    inner = s[s.index(">", s.index("<svg")) + 1: s.rindex("</svg>")]
    return inner, float(vb.group(1)), float(vb.group(2))


def build_svg(font):
    upm, cap = font["head"].unitsPerEm, cap_height(font)
    H1 = 100.0
    name_size = H1 * upm / cap
    H2 = H1 * DESC_RATIO
    desc_size = H2 * upm / cap

    name_target = H1 * NAME_W
    desc_target = H2 * DESC_W
    ntrack = solve_track(font, NAME, name_size, name_target)
    dtrack = solve_track(font, DESC, desc_size, desc_target)

    mono_inner, mw, mh = monogram()
    mono_h = H1 * MONO_RATIO
    mono_scale = mono_h / mh
    mono_w = mw * mono_scale

    type_x = mono_w + mono_h * MONO_GAP
    block_h = H1 + H1 * GAP_RATIO + H2
    block_top = (mono_h / 2 + mono_h * V_OFFSET) - block_h / 2
    base1 = block_top + H1
    base2 = base1 + H1 * GAP_RATIO + H2

    name_d, name_w = run(font, NAME, name_size, ntrack, type_x, base1)
    dx = type_x + (name_w - desc_target) / 2.0
    desc_d, desc_w = run(font, DESC, desc_size, dtrack, dx, base2)

    rule_h = H1 * RULE_RATIO
    rule_y = base2 - H2 / 2.0 - rule_h / 2.0
    pad = H2 * PAD_RATIO
    rules = ""
    left_len = (dx - pad) - type_x
    if left_len > 2:
        rules += (f'<rect x="{type_x:.2f}" y="{rule_y:.2f}" width="{left_len:.2f}"'
                  f' height="{rule_h:.2f}" fill="{BRAND}"/>')
    rx = dx + desc_w + pad
    right_len = (type_x + name_w) - rx
    if right_len > 2:
        rules += (f'<rect x="{rx:.2f}" y="{rule_y:.2f}" width="{right_len:.2f}"'
                  f' height="{rule_h:.2f}" fill="{BRAND}"/>')

    W, H = type_x + name_w, mono_h
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.2f} {H:.2f}" '
        f'width="{W:.0f}" height="{H:.0f}" role="img" '
        f'aria-label="Creative Edge Outdoor Living">'
        f'<g transform="scale({mono_scale:.6f})">{mono_inner}</g>'
        f'<path fill="{INK}" d="{name_d}"/>'
        f'<path fill="{INK}" d="{desc_d}"/>'
        f'{rules}</svg>\n'
    )
    return svg, W, H


def rasterise(svg, out, width, bg=None, pad_frac=0.0):
    """Render an SVG string with headless Chromium. No cairo/rsvg dependency."""
    from playwright.sync_api import sync_playwright
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    vw, vh = float(m.group(1)), float(m.group(2))
    pad = int(width * pad_frac)
    h = int(round(width * vh / vw))
    body = "transparent" if bg is None else bg
    sized = re.sub(r'width="[\d.]+" height="[\d.]+"',
                   f'width="{width}" height="{h}"', svg, count=1)
    html = (f'<body style="margin:0;background:{body};padding:{pad}px;'
            f'width:{width}px;height:{h}px">{sized}</body>')
    with tempfile.TemporaryDirectory() as td:
        f = pathlib.Path(td) / "r.html"
        f.write_text(html)
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            p = b.new_page(viewport={"width": width + pad * 2, "height": h + pad * 2})
            p.goto(f.as_uri())
            p.screenshot(path=str(out), omit_background=bg is None)
            b.close()


def main():
    font = instanced()
    svg, w, h = build_svg(font)
    (ROOT / "img" / "ce-wordmark.svg").write_text(svg)

    rasterise(svg, ROOT / "img" / "ce-wordmark-1200.png", 1080, bg=DARK, pad_frac=0.055)
    mono = MONOGRAM.read_text()
    for size, out in ((64, ROOT / "img" / "favicon-64.png"),
                      (180, ROOT / "favicon.png")):
        rasterise(mono, out, int(size * 0.86), bg=DARK, pad_frac=0.08)
    print(f"lockup {w:.0f}x{h:.0f} -> img/ce-wordmark.svg + png + favicons "
          f"(monogram = client vector, type = Oswald 700 paths)")


if __name__ == "__main__":
    main()
