#!/usr/bin/env python3
"""
Extract the CE hexagon monogram from the client's own vector file.

PROVENANCE. Source is Blaine's own artwork, found in the client's Drive:
  ~/Desktop/apex_clients/creative_edge/assets/brand/CEL_logo_Vector.ai
It is a PDF-1.6 compatible .ai, 2 pages, 300x150pt:
  page 1 = light colorway (black hexagon, green E, black/green wordmark)
  page 2 = dark colorway  (WHITE hexagon, green E, white/green wordmark)  <- used

Page 2 is used because the site is dark end to end and its hexagon is already
white, matching the vehicle wrap exactly.

WHAT THIS DOES, AND WHAT IT REFUSES TO DO.
Poppler's pdftocairo emits a flat SVG of 31 absolute paths, no groups or clips.
The monogram is the only art right of x=225pt: path[1] the white hexagon and
path[2] the green E. Everything left of that is the RETIRED lockup — the
"Creative | edge landscaping Ltd" wordmark and the green divider bar — and is
dropped, because "Landscaping" is out of the brand.

The two kept paths are copied VERBATIM. The only transforms are:
  - a translate() to move the bbox to the origin, which does not alter geometry
  - fill swaps: the hexagon stays #FFFFFF, the E goes from the file's #18A844
    to the new brand green #2BD11F

⛔ Geometry is never redrawn, resampled or traced. If the mark ever needs to
change, change it here and re-run — do not hand-edit img/ce-monogram.svg.

NOTE ON #18A844: that is the green inside the client's own vector, and it is
byte-identical to the site's OLD --brand token. It sits at hue 138. The new
wrap green measures hue 116. That is why the restyle did not simply reuse the
old value or the designer's #0FB735 (hue 134) — both belong to the retired
palette, not the new one.

USAGE:  python3 build/extract_monogram.py     # rewrites img/ce-monogram.svg
REQUIRES: poppler (`brew install poppler`) for pdftocairo.
"""
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
AI = pathlib.Path.home() / "Desktop/apex_clients/creative_edge/assets/brand/CEL_logo_Vector.ai"
OUT = ROOT / "img" / "ce-monogram.svg"

BRAND = "#2BD11F"
WHITE = "#FFFFFF"
MONOGRAM_X_MIN = 225.0     # everything right of this is the mark; left is the old wordmark
NUM = re.compile(r"-?\d+\.?\d*")


def main():
    if not AI.exists():
        sys.exit(f"missing source artwork: {AI}")
    if not subprocess.run(["which", "pdftocairo"], capture_output=True).stdout:
        sys.exit("pdftocairo not found - brew install poppler")

    with tempfile.TemporaryDirectory() as td:
        svg_path = pathlib.Path(td) / "p2.svg"
        subprocess.run(["pdftocairo", "-svg", "-f", "2", "-l", "2", str(AI), str(svg_path)],
                       check=True)
        src = svg_path.read_text()

    paths = re.findall(r'<path[^>]*?fill="rgb\(([^)]*)\)"[^>]*?d="([^"]*)"[^>]*?/>', src)
    keep = []
    for fill, d in paths:
        v = [float(x) for x in NUM.findall(d)]
        if min(v[0::2]) >= MONOGRAM_X_MIN:
            keep.append((fill, d))
    if len(keep) != 2:
        sys.exit(f"expected 2 monogram paths (hexagon + E), got {len(keep)}. "
                 f"The source artwork changed - inspect before trusting this.")

    xs, ys = [], []
    for _, d in keep:
        v = [float(x) for x in NUM.findall(d)]
        xs += v[0::2]
        ys += v[1::2]
    x0, y0, w, h = min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)

    body = []
    for fill, d in keep:
        r, g, b = (float(p.strip().rstrip("%")) for p in fill.split(","))
        col = WHITE if (r > 95 and g > 95 and b > 95) else BRAND
        body.append(f'<path fill-rule="nonzero" fill="{col}" d="{d}"/>')

    OUT.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.3f} {h:.3f}" '
        f'width="{w:.3f}" height="{h:.3f}" role="img" '
        f'aria-label="Creative Edge monogram">'
        f'<g transform="translate({-x0:.6f},{-y0:.6f})">' + "".join(body) + "</g></svg>\n")
    print(f"img/ce-monogram.svg  {w:.3f} x {h:.3f}  aspect {w/h:.4f} "
          f"(wrap photo measures 0.8614)")


if __name__ == "__main__":
    main()
