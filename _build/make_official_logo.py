#!/usr/bin/env python3.11
"""
Creative Edge Outdoor Living: site logo assets from the CLIENT'S OFFICIAL files.

SOURCE (Brad Valair email "Creative Logo", 2026-11-27 21:56Z, Gmail 1a21f0311ac88406):
  ~/Desktop/apex_clients/creative_edge/assets/brand/official_2026-11-27/
    CreativeEdgeOutdoorLiving_Logo_White+Green.pdf
    CreativeEdgeOutdoorLiving_Logo_Black+Green.pdf
  (override the folder with CE_BRAND_SRC=...)
Both are Adobe Illustrator exports with ALL TEXT OUTLINED (pdffonts lists no
fonts), so the vectors are the exact artwork. This script only converts
formats and swaps the pdftocairo rgb(%) fills for the official hex values.
Nothing is redrawn, re-typeset or recoloured.

SUPERSEDES make_wordmark.py + extract_monogram.py (our Aug 2026 recreation:
real hexagon + Oswald all-caps text). Those are kept for history only.

OFFICIAL COLOURS. The PDFs are CMYK; poppler converts the green to
rgb(25%, 72.549%, 23.526%) = #40B93C and MuPDF to #38B449. The designer's own
RGB export (CreativeEdgeOutdoorLiving_Logo_Black+Green.png) uses #39B54A, so
that is the official RGB value and every output is forced to it:
  green  #39B54A
  black  rgb(13.73%, 12.16%, 12.55%) = #231F20
  white  #FFFFFF

OUTPUTS (site/img unless noted):
  ce-lockup-white.svg   dark backgrounds (the whole site): white + green
  ce-lockup-black.svg   light backgrounds: black + green
  ce-lockup-1200.png    black + green, transparent, 1200 wide: schema logo
                        (Google shows the schema logo on white)
  ce-lockup-white-1200.png  white + green transparent, for dark surfaces
  ce-monogram-official.png  white+green hexagon only, transparent, 512 tall
  favicon-64.png        monogram on the site's dark ground, 64x64 square
  ../favicon.png        same, 180x180 (apple-touch size)
  ce-logo-square-720.png        monogram on #231F20: GBP logo, FB/IG profile, Ads logo
  ce-logo-square-light-720.png  black+green monogram on white (light surfaces)
  ce-cover-1080x608.png         GBP cover: white+green lockup on #231F20
  ce-signature-monogram-132.png email-signature monogram, transparent

Run: python3.11 _build/make_official_logo.py   (from site/)
"""
import re
import subprocess
import tempfile
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

SITE = Path(__file__).resolve().parent.parent
import os
# The official PDFs are NOT committed (this repo is public, and the secret guard
# false-positives on compressed PDF bytes). Master copies live in the client dir.
SRC = Path(os.environ.get("CE_BRAND_SRC") or
           Path.home() / "Desktop/apex_clients/creative_edge/assets/brand/official_2026-11-27")
WHITE_PDF = SRC / "CreativeEdgeOutdoorLiving_Logo_White+Green.pdf"
BLACK_PDF = SRC / "CreativeEdgeOutdoorLiving_Logo_Black+Green.pdf"
IMG = SITE / "img"
GROUND = (12, 13, 16, 255)  # --bg #0c0d10

FILL_MAP = {
    "rgb(25%, 72.549438%, 23.526001%)": "#39B54A",  # designer RGB export, see below
    "rgb(13.729858%, 12.159729%, 12.548828%)": "#231F20",
    "rgb(100%, 100%, 100%)": "#FFFFFF",
}


_TWINS = {}


def svg_twin(pdf: Path) -> Path:
    if pdf not in _TWINS:
        out = Path(tempfile.mkdtemp()) / (pdf.stem + ".svg")
        pdf_to_svg(pdf, out, tighten=False)
        _TWINS[pdf] = out
    return _TWINS[pdf]


def pdf_to_svg(pdf: Path, out: Path, tighten: bool = True) -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "x.svg"
        subprocess.run(["pdftocairo", "-svg", str(pdf), str(tmp)], check=True)
        svg = tmp.read_text()
    for k, v in FILL_MAP.items():
        svg = svg.replace(k, v)
    left = set(re.findall(r"rgb\([^)]*\)", svg))
    assert not left, f"unmapped colours in {pdf.name}: {left}"
    if tighten:
        r = content_rect(pdf)
        svg = re.sub(r'viewBox="[^"]+"', f'viewBox="{r.x0:.3f} {r.y0:.3f} {r.width:.3f} {r.height:.3f}"', svg, count=1)
    if not tighten:
        out.write_text(svg)
        return
    # Let CSS size it: drop the pt width/height, keep the viewBox.
    svg = re.sub(r'(<svg[^>]*?) width="[^"]+" height="[^"]+"', r"\1", svg, count=1)
    svg = svg.replace("<svg ", '<svg role="img" aria-label="Creative Edge Outdoor Living" ', 1)
    out.write_text(svg)


def render(pdf: Path, width: int, clip=None) -> Image.Image:
    """Rasterise the hex-fixed SVG twin of `pdf` (same artboard, same geometry),
    so every PNG carries exactly the official #39B54A, not a CMYK conversion."""
    doc = fitz.open(svg_twin(pdf))
    page = doc[0]
    rect = clip or page.rect
    zoom = width / rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=rect, alpha=True)
    return Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)


def content_rect(pdf: Path) -> fitz.Rect:
    """The artwork's own bounds in pt. The Black+Green PDF has a padded artboard
    (792x210) while the White+Green one is tight, so always crop to the art."""
    page = fitz.open(pdf)[0]
    im = render(pdf, 4000)
    x0, y0, x1, y1 = im.getchannel("A").getbbox()
    s = page.rect.width / im.width
    return fitz.Rect(x0 * s, y0 * s, x1 * s, y1 * s)


def monogram_clip(pdf: Path) -> fitz.Rect:
    """Find the hexagon's right edge: first fully empty column run after it."""
    page = fitz.open(pdf)[0]
    im = render(pdf, 3000)
    a = im.getchannel("A")
    w, h = im.size
    cols = [any(a.getpixel((x, y)) > 8 for y in range(0, h, 2)) for x in range(w)]
    x = 0
    while x < w and not cols[x]:
        x += 1
    while x < w and cols[x]:
        x += 1  # inside the hexagon
    right = x / w * page.rect.width
    return fitz.Rect(0, 0, right, page.rect.height)


def monogram_clip_black() -> fitz.Rect:
    """Monogram of the Black+Green file: same method, starting at the art's left edge."""
    page = fitz.open(BLACK_PDF)[0]
    im = render(BLACK_PDF, 3000)
    a = im.getchannel("A"); w, h = im.size
    cols = [any(a.getpixel((x, y)) > 8 for y in range(0, h, 2)) for x in range(w)]
    x = 0
    while x < w and not cols[x]:
        x += 1
    left = x
    while x < w and cols[x]:
        x += 1
    s = page.rect.width / w
    return fitz.Rect(left * s, 0, x * s, page.rect.height)


def square_icon(mono: Image.Image, size: int, pad: float = 0.12) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), GROUND)
    inner = int(size * (1 - 2 * pad))
    m = mono.copy()
    m.thumbnail((inner, inner), Image.LANCZOS)
    canvas.alpha_composite(m, ((size - m.width) // 2, (size - m.height) // 2))
    return canvas


def main() -> None:
    pdf_to_svg(WHITE_PDF, IMG / "ce-lockup-white.svg")
    pdf_to_svg(BLACK_PDF, IMG / "ce-lockup-black.svg")
    black = render(BLACK_PDF, 1200, clip=content_rect(BLACK_PDF))
    white = render(WHITE_PDF, 1200, clip=content_rect(WHITE_PDF))
    black.save(IMG / "ce-lockup-1200.png", optimize=True)
    white.save(IMG / "ce-lockup-white-1200.png", optimize=True)

    clip = monogram_clip(WHITE_PDF)
    mono = render(WHITE_PDF, 2000, clip=clip)
    mono = mono.crop(mono.getchannel("A").getbbox())
    big = mono.copy()
    big.thumbnail((10_000, 512), Image.LANCZOS)
    big.save(IMG / "ce-monogram-official.png", optimize=True)
    square_icon(mono, 64, pad=0.06).save(IMG / "favicon-64.png", optimize=True)
    square_icon(mono, 180).save(SITE / "favicon.png", optimize=True)
    # Square + cover sizes for GBP, Facebook/Instagram, Google Ads, email
    # signature. Same treatment as CE's current profile picture (white
    # hexagon, green E, dark ground) but the official geometry and green, on
    # the official near-black. Hosted from img/ so GBP can fetch a public URL.
    INK = (0x23, 0x1F, 0x20, 255)
    def square(src, size, pad, ground):
        c = Image.new("RGBA", (size, size), ground)
        m = src.copy(); inner = int(size * (1 - 2 * pad))
        m.thumbnail((inner, inner), Image.LANCZOS)
        c.alpha_composite(m, ((size - m.width) // 2, (size - m.height) // 2))
        return c
    square(mono, 720, 0.16, INK).convert("RGB").save(IMG / "ce-logo-square-720.png", optimize=True)
    mono_black = render(BLACK_PDF, 2000, clip=monogram_clip_black())
    mono_black = mono_black.crop(mono_black.getchannel("A").getbbox())
    square(mono_black, 720, 0.16, (255, 255, 255, 255)).convert("RGB").save(
        IMG / "ce-logo-square-light-720.png", optimize=True)
    cover = Image.new("RGBA", (1080, 608), INK)
    lw = white.copy(); lw.thumbnail((760, 10_000), Image.LANCZOS)
    cover.alpha_composite(lw, ((1080 - lw.width) // 2, (608 - lw.height) // 2))
    cover.convert("RGB").save(IMG / "ce-cover-1080x608.png", optimize=True)
    sig = mono.copy(); sig.thumbnail((10_000, 132), Image.LANCZOS)
    sig.save(IMG / "ce-signature-monogram-132.png", optimize=True)
    print("monogram clip (pt):", clip, "aspect", round(mono.width / mono.height, 4))
    for f in ["ce-lockup-white.svg", "ce-lockup-black.svg", "ce-lockup-1200.png",
              "ce-lockup-white-1200.png", "ce-monogram-official.png", "favicon-64.png"]:
        print(f, (IMG / f).stat().st_size, "b")


if __name__ == "__main__":
    main()
