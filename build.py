#!/usr/bin/env python3
"""
Creative Edge Outdoor Living — static site generator.

BRAND (locked 2026-08-07). The business trades as CREATIVE EDGE with the
descriptor OUTDOOR LIVING. "Landscaping" is OUT of the brand name: headers,
footers, titles, meta, alt text. It stays only as a lowercase word describing
a service ("landscape design", "commercial landscaping"), because that is what
the work is and what people search.

Two things deliberately keep the old string and must NOT be "fixed":
  1. the LEGAL ENTITY, "Creative Edge Landscaping Ltd." — the company was not
     renamed at the BC registry, so the copyright notice, the terms page and
     the privacy page name the entity that actually holds the rights and the
     obligations. schema legalName follows the same rule.
  2. the LEGAL ENTITY stays even though the DOMAIN moved to
     creativeedgeoutdoorliving.ca on 2026-08 (full migration, runbook in the
     client dir). The old domain 301s here forever.

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
STAGING = False

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
CANONICAL = "https://creativeedgeoutdoorliving.ca"

# Legal name from the footer/privacy page; `name` is the real-world trading name
# that must match GBP EXACTLY (playbook 03: one canonical NAP everywhere).
# ⚠️ OPEN AS OF 2026-08-07: `name` now carries the locked new brand, but the GBP
# business title still reads "Creative Edge Landscaping". Until GBP is retitled
# the two disagree, which is why `alternateName` keeps the old string here — it
# lets Google reconcile the two names instead of seeing an unrelated business.
# Retitling GBP is an N6.3 change and belongs to the local-SEO pass, not to this
# file. Delete alternateName once GBP has been retitled and has settled.
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
        '"name":"Creative Edge Outdoor Living",'
        '"alternateName":"Creative Edge Landscaping",'
        '"legalName":"Creative Edge Landscaping Ltd.",'
        f'"url":"{CANONICAL}/",'
        f'"telephone":"+1{PHONE_HREF.lstrip("+1")}",'
        f'"image":"{CANONICAL}/img/ce-wordmark-1200.png",'
        f'"logo":"{CANONICAL}/img/ce-wordmark-1200.png",'
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
       (GA4 stream 15360314212 - created as www.creativeedgelandscaping.ca,
       carries creativeedgeoutdoorliving.ca after the 2026-08 domain migration,
       Phase 2.3 of the runbook), measurement ID G-0YEVFG52V0.
     Meta pixel 872232952291575: OWNED BY BLAINE'S BUSINESS (resolved
       2026-08-15, Events Manager dataset read). Head carries base pixel
       + PageView ONLY. `Lead` fires SERVER-SIDE via Railway CAPI on
       qualified submits — never add fbq('track','Lead') here, it would
       double-fire against the CAPI event.
     ============================================================ -->
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-18360839838"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'AW-18360839838');
gtag('config', 'G-0YEVFG52V0');
</script>
<script>
!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '872232952291575');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none" alt=""
src="https://www.facebook.com/tr?id=872232952291575&ev=PageView&noscript=1"/></noscript>"""


def head(title, desc, robots="index,follow", schema="", canon=""):
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
<link rel="canonical" href="{canon}">
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
    # LOCKUP. img/ce-wordmark.svg = the client's OWN hexagon monogram (extracted
    # from CEL_logo_Vector.ai with build/extract_monogram.py, geometry untouched,
    # fills recoloured to the new brand) + CREATIVE EDGE / OUTDOOR LIVING set in
    # Oswald 700 and converted to paths. No webfont, no FOUT, renders anywhere.
    # Proportions are calibrated against the vehicle wrap: 0.70% mean deviation.
    # Regenerate: python3 build/extract_monogram.py && python3 build/make_wordmark.py
    return f"""<header>
  <a href="index.html"><img class="logo" src="{asset('img/ce-wordmark.svg')}" width="1028" height="290" alt="Creative Edge Outdoor Living"></a>{navblock}
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
    # Row 1 names the BUSINESS, so it carries the trading brand. The copyright
    # line below names the LEGAL ENTITY and keeps "Creative Edge Landscaping
    # Ltd." — that is who actually holds the copyright, and the company was not
    # renamed at the registry. Do not "tidy" the two into one string.
    return f"""<footer>
  <div class="wrap fl">
    <span>Creative Edge Outdoor Living</span><span>·</span><span>Fully insured</span><span>·</span>
    <span>Vernon &amp; the North Okanagan</span><span>·</span>
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
        head(title, desc, robots, schema_block(slug, service),
             canon=f"{CANONICAL}/" if slug == "index" else f"{CANONICAL}/{slug}.html"),
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

    # ---- sitemap.xml -------------------------------------------------------
    # Only pages the registry actually lets Google index. The paid LPs, the
    # thank-you page and the legal pages are noindex on purpose — listing them
    # here would contradict their own meta tag and waste crawl budget.
    urls = []
    for spec in registry.PAGES:
        if "noindex" in spec.get("robots", "index,follow"):
            continue
        slug = spec["slug"]
        loc = f"{CANONICAL}/" if slug == "index" else f"{CANONICAL}/{slug}.html"
        urls.append(f"  <url><loc>{loc}</loc>"
                    f"<priority>{'1.0' if slug == 'index' else '0.8'}</priority></url>")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n</urlset>\n")
    print(f"wrote sitemap.xml ({len(urls)} indexable urls)")

    # ---- legacy URL redirects ---------------------------------------------
    # ⛔ DO NOT DELETE. Google still shows sitelinks for the OLD WordPress site
    # (Contact Us / OUR WORK / About Us / DESIGN / Our services / Outdoor
    # Living), and those point at directory URLs like /about/. This site serves
    # .html files, so every one of them 404s [v 2026-08-13 - all 9 probed, all 404].
    # Anyone clicking Creative Edge in Google would hit a dead page.
    #
    # GitHub Pages has no server-side redirects, so each legacy path gets a stub
    # index.html: instant meta-refresh for humans, rel=canonical so Google
    # consolidates the old URL onto the new one, noindex so the stub itself
    # never ranks. Extra aliases that may never have existed are harmless.
    REDIRECTS = {
        "about": "about.html",
        "about-us": "about.html",
        "contact": "contact.html",
        "contact-us": "contact.html",
        "our-work": "our-work.html",
        "work": "our-work.html",
        "gallery": "our-work.html",
        "portfolio": "our-work.html",
        "design": "design.html",
        "landscape-design": "design.html",
        "services": "services.html",
        "our-services": "services.html",
        "outdoor-living": "outdoor-living.html",
        "outdoor-living-spaces": "outdoor-living.html",
        "pools": "pools.html",
        "pools-spas": "pools.html",
        "retaining-walls": "retaining-walls.html",
        "commercial": "commercial.html",
        "blog": "blog.html",
        "news": "blog.html",
        "home": "",
    }
    made = 0
    for old, new in REDIRECTS.items():
        target = f"{CANONICAL}/{new}" if new else f"{CANONICAL}/"
        d = ROOT / old
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(
            '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<meta http-equiv="refresh" content="0; url={target}">\n'
            f'<link rel="canonical" href="{target}">\n'
            '<meta name="robots" content="noindex,follow">\n'
            '<title>Redirecting…</title>\n'
            f'<script>window.location.replace("{target}");</script>\n'
            '</head>\n<body>\n'
            f'<p>This page has moved. <a href="{target}">Continue to Creative Edge Outdoor Living</a>.</p>\n'
            '</body>\n</html>\n')
        made += 1
    print(f"wrote {made} legacy-URL redirect stubs")

    # ---- 404 --------------------------------------------------------------
    # GitHub Pages serves /404.html for anything unmatched. Without it a bad
    # link shows GitHub's own branded 404, which looks like the site is broken.
    (ROOT / "404.html").write_text(build_page(
        "404-body", "Page not found | Creative Edge Outdoor Living",
        "That page has moved. Find outdoor living, pools, retaining walls and "
        "contact details for Creative Edge in Vernon and the North Okanagan.",
        robots="noindex,follow") if (CONTENT / "404-body.html").exists() else
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="robots" content="noindex,follow">\n'
        '<title>Page not found | Creative Edge Outdoor Living</title>\n'
        f'<link rel="stylesheet" href="{asset("css/site.css")}">\n'
        '</head>\n<body id="top">\n'
        '<section class="band"><div class="wrap" style="max-width:720px;text-align:center;padding:80px 0">\n'
        '<p class="kicker">Creative Edge Outdoor Living</p>\n'
        '<h1>That page has <span class="em">moved</span></h1>\n'
        '<p class="lede">We rebuilt the site, so some older links no longer work. '
        'Everything is still here, just in a new spot.</p>\n'
        f'<p style="margin-top:28px"><a class="btn" href="{CANONICAL}/">Go to the homepage</a></p>\n'
        '<p style="margin-top:18px">Or jump straight to '
        f'<a href="{CANONICAL}/outdoor-living.html">outdoor living</a>, '
        f'<a href="{CANONICAL}/pools.html">pools</a>, '
        f'<a href="{CANONICAL}/retaining-walls.html">retaining walls</a> or '
        f'<a href="{CANONICAL}/contact.html">contact us</a>.</p>\n'
        f'<p style="margin-top:24px">Prefer to talk? <a href="tel:{PHONE_HREF}">{PHONE_TEXT}</a></p>\n'
        '</div></section>\n</body>\n</html>\n')
    print("wrote 404.html")

    # ---- robots.txt --------------------------------------------------------
    # Replaces the staging Disallow. On the custom domain this file IS read
    # (host root), unlike on the github.io project URL where it was a no-op.
    (ROOT / "robots.txt").write_text(
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {CANONICAL}/sitemap.xml\n")
    print("wrote robots.txt (allow + sitemap)")

    # ---- cross-client leak guard ------------------------------------------
    # ⛔ DO NOT REMOVE. Three real leaks shipped to live client sites before this
    # existed, all written as helpful engineering comments by someone who forgot
    # the file is public:
    #   2026-08-30  this site served KDT's name + a territory carve-up
    #   2026-08-31  js/site.js served "KDT's $452/week of zero"
    #   2026-08-31  thank-you.html named Dustin
    # The checker is SHARED (apex_tooling/leak_guard.py) and reads the client
    # roster from the spine, so it covers clients signed after this was written.
    # It is deliberately non-fatal here: this build is run mid-measurement-window
    # and a hard exit could leave a half-written site. It shouts instead.
    try:
        import subprocess, os
        guard = os.path.expanduser("~/apex_tooling/leak_guard.py")
        r = subprocess.run(
            [sys.executable, guard, str(ROOT), "--client", "creative_edge"],
            capture_output=True, text=True, timeout=120)
        if r.returncode == 1:
            print("\n" + "=" * 70)
            print("⛔ CROSS-CLIENT LEAK IN THIS BUILD — DO NOT DEPLOY")
            print(r.stdout.strip()[:2000])
            print("=" * 70)
        else:
            print(r.stdout.strip().splitlines()[-1] if r.stdout.strip()
                  else "leak guard: clean")
    except Exception as e:                      # never let the guard break a build
        print(f"⚠️  leak guard did not run ({e}) — check by hand before deploying")


if __name__ == "__main__":
    main()
