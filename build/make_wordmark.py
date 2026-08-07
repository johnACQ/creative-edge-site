#!/usr/bin/env python3
"""
Creative Edge Outdoor Living — typographic wordmark generator.

WHY THIS EXISTS
---------------
The brand relaunched (Aug 2026) as CREATIVE EDGE with the descriptor OUTDOOR
LIVING. The vector files for the CE hexagon monogram are still with Blaine's
designer, so this is a WORDMARK-ONLY INTERIM lockup: type only, no monogram.

⛔ DO NOT add a hexagon, a monogram, or any attempt at the CE mark here. A
near-miss recreation of a client's own logo is worse than no logo. When the
designer's vector files land, the SVG this writes gets REPLACED by the real
artwork, not edited.

Text is converted to PATHS on purpose: no webfont download at runtime, no FOUT
in a sticky header, and the mark renders identically everywhere with zero
dependencies. That keeps the ownership promise in build.py intact — the output
is a plain SVG anyone can open.

Font: Archivo (SIL Open Font License 1.1), variable, instanced at
wght=800 / wdth=87 to match the semi-condensed bold on the vehicle wrap.

USAGE:  python3 build/make_wordmark.py
        (writes img/ce-wordmark.svg, img/ce-wordmark-1200.png,
         img/favicon-64.png, favicon.png)
"""
import pathlib
import subprocess
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
VAR_FONT = pathlib.Path("/Users/johnmilne/apex_content/template/fonts/Archivo.ttf")

# Sampled from the two locked brand mockups (vehicle wrap + trailer), white
# balanced against the white wordmark in the same frame: median hue 116.
BRAND = "#2BD11F"
INK = "#FFFFFF"
DARK = "#0B0F12"

NAME = "CREATIVE EDGE"
DESC = "OUTDOOR LIVING"

NAME_TRACK = 0.030   # em, gentle. The wrap letters sit slightly open.
DESC_TRACK = 0.300   # em, wide. This is the signature of the lockup.
DESC_RATIO = 0.330   # descriptor cap height / name cap height, from the wrap
GAP_RATIO = 0.320    # vertical gap / name cap height
RULE_RATIO = 0.075   # rule thickness / name cap height
PAD_RATIO = 0.90     # space between rule end and descriptor / descriptor cap


def instanced():
    f = TTFont(VAR_FONT)
    return instancer.instantiateVariableFont(f, {"wght": 800, "wdth": 87})


def cap_height(font):
    """Cap height from the 'E' bounding box, which is what we actually align."""
    gs = font.getGlyphSet()
    glyf = font["glyf"]
    gname = font.getBestCmap()[ord("E")]
    return glyf[gname].yMax


def run(font, text, size_px, track_em, x, baseline_y, upm):
    """Return (svg path data, advance width in px) for text laid out at size_px."""
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    scale = size_px / upm
    track_px = track_em * size_px
    parts, pen_x = [], x
    # Round to 2dp. Full float precision triples the file size for sub-pixel
    # detail no screen can render.
    def ntos(v):
        return f"{v:.2f}".rstrip("0").rstrip(".")

    for ch in text:
        gname = cmap[ord(ch)]
        pen = SVGPathPen(gs, ntos=ntos)
        # y flips: font units go up, SVG goes down.
        tp = TransformPen(pen, (scale, 0, 0, -scale, pen_x, baseline_y))
        gs[gname].draw(tp)
        d = pen.getCommands()
        if d:
            parts.append(d)
        pen_x += hmtx[gname][0] * scale + track_px
    pen_x -= track_px  # no trailing track after the last glyph
    return " ".join(parts), pen_x - x


def build_svg(font):
    upm = font["head"].unitsPerEm
    cap = cap_height(font)

    # Work in a coordinate space where the NAME cap height is 100 units.
    H1 = 100.0
    name_size = H1 * upm / cap          # font size that yields cap height 100
    H2 = H1 * DESC_RATIO
    desc_size = H2 * upm / cap

    pad = 0.0
    base1 = pad + H1
    name_d, name_w = run(font, NAME, name_size, NAME_TRACK, pad, base1, upm)

    base2 = base1 + H1 * GAP_RATIO + H2
    desc_d, desc_w = run(font, DESC, desc_size, DESC_TRACK, 0, base2, upm)
    # centre the descriptor under the name
    dx = pad + (name_w - desc_w) / 2.0
    desc_d, _ = run(font, DESC, desc_size, DESC_TRACK, dx, base2, upm)

    # Green rules flanking the descriptor, as on the wrap.
    rule_h = H1 * RULE_RATIO
    rule_y = base2 - H2 / 2.0 - rule_h / 2.0
    gap = H2 * PAD_RATIO
    left_len = (dx - gap) - pad
    right_x = dx + desc_w + gap
    right_len = (pad + name_w) - right_x

    total_w = name_w + pad * 2
    total_h = base2 + pad

    rules = ""
    if left_len > 4:
        rules += (f'<rect x="{pad:.1f}" y="{rule_y:.1f}" width="{left_len:.1f}" '
                  f'height="{rule_h:.1f}" fill="{BRAND}"/>')
    if right_len > 4:
        rules += (f'<rect x="{right_x:.1f}" y="{rule_y:.1f}" width="{right_len:.1f}" '
                  f'height="{rule_h:.1f}" fill="{BRAND}"/>')

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w:.1f} {total_h:.1f}" '
        f'width="{total_w:.0f}" height="{total_h:.0f}" role="img" '
        f'aria-label="Creative Edge Outdoor Living">'
        f'<path fill="{INK}" d="{name_d}"/>'
        f'<path fill="{INK}" d="{desc_d}"/>'
        f'{rules}'
        f'</svg>\n'
    )
    return svg, total_w, total_h


def build_raster(font, total_w, total_h):
    """Schema/OG logo + favicons. Same type, no monogram."""
    from PIL import Image, ImageDraw, ImageFont
    with tempfile.TemporaryDirectory() as td:
        static = pathlib.Path(td) / "archivo-800-87.ttf"
        font.save(static)

        # --- 1200px wordmark on the brand near-black -------------------
        # Side padding so the schema/OG logo is not flush to the edge.
        W = 1080
        pad_x = 60
        scale = W / total_w
        H = int(round(total_h * scale))
        pad_y = int(H * 0.34)
        img = Image.new("RGB", (W + pad_x * 2, H + pad_y * 2), DARK)
        d = ImageDraw.Draw(img)
        upm = font["head"].unitsPerEm
        cap = cap_height(font)
        H1 = 100.0 * scale
        name_px = int(round(H1 * upm / cap))
        H2 = H1 * DESC_RATIO
        desc_px = int(round(H2 * upm / cap))
        fn = ImageFont.truetype(str(static), name_px)
        fd = ImageFont.truetype(str(static), desc_px)

        def draw_tracked(text, f, track_px, x, y, fill):
            for ch in text:
                d.text((x, y), ch, font=f, fill=fill, anchor="ls")
                x += d.textlength(ch, font=f) + track_px
            return x

        base1 = pad_y + H1
        draw_tracked(NAME, fn, NAME_TRACK * name_px, pad_x, base1, INK)

        def width_of(text, f, track_px):
            return sum(d.textlength(c, font=f) + track_px for c in text) - track_px

        dw = width_of(DESC, fd, DESC_TRACK * desc_px)
        base2 = base1 + H1 * GAP_RATIO + H2
        dx = pad_x + (W - dw) / 2
        draw_tracked(DESC, fd, DESC_TRACK * desc_px, dx, base2, INK)
        rule_h = max(2, int(H1 * RULE_RATIO))
        ry = int(base2 - H2 / 2 - rule_h / 2)
        gap = H2 * PAD_RATIO
        if dx - gap > pad_x + 6:
            d.rectangle([pad_x, ry, int(dx - gap), ry + rule_h], fill=BRAND)
        rx = int(dx + dw + gap)
        if (W + pad_x) - rx > 6:
            d.rectangle([rx, ry, W + pad_x, ry + rule_h], fill=BRAND)
        img.save(ROOT / "img" / "ce-wordmark-1200.png", optimize=True)

        # --- favicons: flat brand-green tile, near-black CE ------------
        # Typographic only. Deliberately NOT the hexagon monogram.
        for size, out in ((64, ROOT / "img" / "favicon-64.png"),
                          (180, ROOT / "favicon.png")):
            fi = Image.new("RGB", (size, size), BRAND)
            di = ImageDraw.Draw(fi)
            fs = int(size * 0.60)
            ff = ImageFont.truetype(str(static), fs)
            di.text((size / 2, size / 2), "CE", font=ff, fill=DARK, anchor="mm")
            fi.save(out, optimize=True)


def main():
    font = instanced()
    svg, w, h = build_svg(font)
    (ROOT / "img" / "ce-wordmark.svg").write_text(svg)
    build_raster(font, w, h)
    print(f"wordmark {w:.0f}x{h:.0f} -> img/ce-wordmark.svg + png + favicons")


if __name__ == "__main__":
    main()
