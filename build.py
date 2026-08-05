#!/usr/bin/env python3
"""
Creative Edge Landscaping — static site generator.

WHY THIS EXISTS
---------------
The site is 17+ plain HTML pages sharing one header, one nav, one footer and
12.8KB of CSS. Hand-maintaining that means a nav change is 17 edits and one of
them gets missed. This script owns the shared chrome; page bodies live in
build/content/<slug>.html and are pure HTML with no template syntax.

THE OWNERSHIP PROMISE IS PRESERVED. Output is plain HTML + one plain CSS file.
It renders anywhere, with or without this script. Blaine can take the folder and
host it on anything. The generator is a convenience for us, never a dependency
for him. Do not introduce a runtime build step, a JS framework, or a CDN.

USAGE:  python3 build.py          # writes every page to the site root
        python3 build.py --check  # verify only, exit 1 on drift
"""
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
CONTENT = ROOT / "build" / "content"


def asset(rel):
    """Append a content hash so a changed stylesheet is never served stale.

    GitHub Pages sends cache-control: max-age=600 on css/site.css, and browsers
    routinely hold it longer. Because the filename never changes, a CSS edit can
    leave a returning visitor on the OLD stylesheet with the NEW markup — which
    is exactly how the About stat cards rendered as bare unstyled text for John
    on 2026-07-31 while the live file was already correct. The hash changes
    whenever the file does, so the browser is forced to refetch.
    """
    f = ROOT / rel
    h = hashlib.sha1(f.read_bytes()).hexdigest()[:10] if f.exists() else "dev"
    return f"{rel}?v={h}"

PHONE_HREF = "+12508126112"
PHONE_TEXT = "(250) 812 6112"
IG = "https://www.instagram.com/creative_edge_landscaping_/"

# ⛔ STAGING FLAG — flip to False AT THE DOMAIN CUTOVER, the same minute you
# delete robots.txt. Leave it True and the real site launches invisible.
#
# WHY IT EXISTS (found live 2026-08-05): this repo's robots.txt is never read.
# A crawler only reads robots.txt at the HOST ROOT, and
# https://johnacq.github.io/robots.txt is a 404 — a GitHub Pages *project*
# repo cannot serve one. So while these pages sat on the staging URL with the
# default index,follow they were fully crawlable: a complete duplicate of
# creativeedgelandscaping.ca on someone else's domain. The meta tag below is
# the only thing that actually blocks it. Do not trust the robots.txt file.
STAGING = True

# The 8 locked towns. Kelowna, Peachland and Kamloops are DELIBERATELY ABSENT —
# one-trade-per-town is a public term and Kelowna is another client's territory.
# The old WordPress site advertised all three; dropping them is intentional.
# See okanagan_territory_lock_kdt_creative_edge_jul29. Do not re-add.
TOWNS = ["Vernon", "Coldstream", "Lavington", "Armstrong",
         "Enderby", "Lumby", "Salmon Arm", "Sicamous"]

# Nav is the source of truth for site structure. Order matches his old site's
# nav, with Commercial added. Mobile nav is a horizontal scroller, so the extra
# tab costs nothing.
NAV = [
    ("index.html",          "Home"),
    ("about.html",          "About"),
    ("services.html",       "Services"),
    ("pools.html",          "Pools &amp; Spas"),
    ("design.html",         "Design"),
    ("our-work.html",       "Our Work"),
    ("commercial.html",     "Commercial"),
    ("blog.html",           "Blog"),
    ("contact.html",        "Contact"),
]

# Canonical host for structured data. NON-www deliberately: the live server
# 301s www -> apex today, so www would name a URL that redirects. Schema @id is
# an identity, so it must be the URL that actually resolves after cutover.
CANONICAL = "https://creativeedgelandscaping.ca"

# Legal name from the footer/privacy page; `name` is the real-world trading name
# that must match GBP EXACTLY (playbook 03: one canonical NAP everywhere).
# ⛔ NO aggregateRating here, ever. Both his GBP listings have ZERO reviews —
# a rating in schema with nothing behind it is fabricated markup and a Google
# structured-data penalty. It goes in when real reviews exist, not before.
# ⛔ NO streetAddress: he is a service-area business, address hidden on GBP
# (N6.4). addressLocality/Region/Country only, plus areaServed.
def business_schema():
    towns = ",".join(
        '{"@type":"City","name":"%s"}' % t for t in TOWNS)
    return (
        '{"@type":["LocalBusiness","HomeAndConstructionBusiness"],'
        f'"@id":"{CANONICAL}/#business",'
        '"name":"Creative Edge Landscaping",'
        '"legalName":"Creative Edge Landscaping Ltd.",'
        f'"url":"{CANONICAL}/",'
        f'"telephone":"+1{PHONE_HREF.lstrip("+1")}",'
        f'"image":"{CANONICAL}/img/ce-logo-dark.png",'
        f'"logo":"{CANONICAL}/img/ce-logo-dark.png",'
        '"address":{"@type":"PostalAddress","addressLocality":"Vernon",'
        '"addressRegion":"BC","addressCountry":"CA"},'
        f'"areaServed":[{towns}],'
        '"founder":{"@type":"Person","name":"Blaine Cusack"},'
        f'"sameAs":["{IG}"]}}'
    )


def schema_block(slug, service):
    """One @graph per page: the business, plus a Service node where the page is
    a money service. Service.provider points at the business @id so every page
    reinforces one entity instead of minting nine unrelated businesses."""
    nodes = [business_schema()]
    if service:
        name, stype = service
        nodes.append(
            '{"@type":"Service",'
            f'"@id":"{CANONICAL}/{slug}.html#service",'
            f'"name":"{name}","serviceType":"{stype}",'
            f'"provider":{{"@id":"{CANONICAL}/#business"}},'
            f'"areaServed":{{"@type":"City","name":"Vernon"}},'
            f'"url":"{CANONICAL}/{slug}.html"}}'
        )
    graph = ",".join(nodes)
    return ('\n<script type="application/ld+json">'
            f'{{"@context":"https://schema.org","@graph":[{graph}]}}'
            '</script>')


TRACKING_NOTE = """<!-- ============================================================
     TRACKING
     Google Ads: account 9265315772, conversion action 7704636228
       "Submit lead form" (primary, one-per-click). Event fires in
       js/site.js on lead submit: send_to AW-18360839838/TmuOCMTW7dkcEJ7dkLNE
     GA4: account "Creative Edge Landscaping", stream 15360314212
       (www.creativeedgelandscaping.ca), measurement ID G-0YEVFG52V0.
     Meta pixel: still BLOCKED. The pixel on creativeedgelandscaping.ca
       (872232952291575) is of UNKNOWN OWNERSHIP (likely the old agency).
       DO NOT wire it until Blaine confirms ownership (asked Jul 31 email).
     ============================================================ -->
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-18360839838"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'AW-18360839838');
gtag('config', 'G-0YEVFG52V0');
</script>"""


def head(title, desc, robots="index,follow", schema=""):
    # Single choke point: every page, whatever the registry says, goes noindex
    # while STAGING is on. See the STAGING comment at the top of this file.
    if STAGING:
        robots = "noindex,nofollow"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="{robots}">
<link rel="icon" type="image/png" href="img/favicon-64.png">
{TRACKING_NOTE}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{asset('css/site.css')}">{schema}
</head>
<body id="top">"""


def header(active, nav=True):
    # Paid landing pages get the logo and phone but NO nav. That is deliberate:
    # a 1:1 attention ratio is the whole point of an LP. Do not "helpfully" add
    # the nav back to an lp-* page.
    navblock = ""
    if nav:
        links = "\n    ".join(
            f'<a href="{h}"{" aria-current=\"page\"" if h == active else ""}>{label}</a>'
            for h, label in NAV
        )
        navblock = f"""
  <nav class="mainnav">
    {links}
  </nav>"""
    return f"""<header>
  <a href="index.html"><img class="logo" src="img/ce-logo-dark.png" width="464" height="128" alt="Creative Edge Landscaping"></a>{navblock}
  <a class="tel" href="tel:{PHONE_HREF}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke-width="2"><path d="M22 16.9v3a2 2 0 01-2.2 2 19.8 19.8 0 01-8.6-3 19.5 19.5 0 01-6-6 19.8 19.8 0 01-3-8.6A2 2 0 014.1 2h3a2 2 0 012 1.7c.1.9.3 1.8.6 2.6a2 2 0 01-.5 2.1L8 11.5a16 16 0 006 6l1.1-1.1a2 2 0 012.1-.5c.8.3 1.7.5 2.6.6a2 2 0 011.7 2z"/></svg><span>Call </span>{PHONE_TEXT}</a>
</header>"""


def footer(with_nav=True):
    # "Fully insured" is BACKED: Blaine confirmed to John on 2026-07-31 that the
    # policy is current, and is sending the certificate. Restored on that basis.
    # If it ever turns out to be lapsed, this line plus the hero trust chip, the
    # form trust line and the FAQ answer all come straight back out — that is
    # exactly what KDT cost us ("$5M insured" over a 294-day-expired COI).
    cols = "".join(
        f'<a href="{h}">{label}</a><span>·</span>' for h, label in NAV
    ).rstrip("<span>·</span>")
    navrow = (f'\n  <div class="wrap fl" style="margin-top:12px">{cols}</div>'
              if with_nav else "")
    return f"""<footer>
  <div class="wrap fl">
    <span>Creative Edge Landscaping Ltd.</span><span>·</span><span>Fully insured</span><span>·</span>
    <span>2 year limited warranty</span><span>·</span><span>Vernon &amp; the North Okanagan</span><span>·</span>
    <span><a href="tel:{PHONE_HREF}">{PHONE_TEXT}</a></span>
  </div>{navrow}
  <div class="wrap fl" style="margin-top:12px">
    <a href="{IG}" rel="noopener">Instagram</a><span>·</span>
    <a href="privacy-policy.html">Privacy Policy</a><span>·</span>
    <a href="terms.html">Terms</a><span>·</span>
    <span>&copy; 2026 Creative Edge Landscaping Ltd.</span>
  </div>
</footer>"""


def build_page(slug, title, desc, robots="index,follow", nav=True, service=None):
    body = (CONTENT / f"{slug}.html").read_text()
    parts = [
        head(title, desc, robots, schema_block(slug, service)),
        header(f"{slug}.html", nav=nav),
        body.rstrip(),
        footer(with_nav=nav),
        f'<script src="{asset("js/site.js")}" defer></script>\n</body>\n</html>',
    ]
    return "\n".join(parts) + "\n"


def main():
    check = "--check" in sys.argv
    import registry
    written, drift = 0, []
    for spec in registry.PAGES:
        out = ROOT / f"{spec['slug']}.html"
        html = build_page(spec["slug"], spec["title"], spec["desc"],
                          spec.get("robots", "index,follow"),
                          spec.get("nav", True),
                          spec.get("service"))
        if check:
            if not out.exists() or out.read_text() != html:
                drift.append(spec["slug"])
        else:
            out.write_text(html)
            written += 1
    if check:
        print(f"drift: {drift}" if drift else "all pages match content sources")
        sys.exit(1 if drift else 0)
    print(f"built {written} pages")


if __name__ == "__main__":
    main()
