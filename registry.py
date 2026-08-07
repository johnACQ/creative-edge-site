"""
Page registry — the single source of truth for what pages exist.

Each entry maps to build/content/<slug>.html for its body. Titles and meta
descriptions live here so they can be reviewed in one place rather than hunted
across 17 files.

PARITY NOTE: the old WordPress site's 8 nav tabs were Home, About, Services,
Pools & Spas, Design, Our Work, Blog, Contact. All 8 are reproduced. Commercial
is added (John's call, Jul 31 2026). Privacy Policy and Thank You are carried
over as unlinked-from-nav utility pages, same as his site.
"""

PAGES = [
    # ---- the 9 nav pages -------------------------------------------------
    dict(slug="index",
         title="Outdoor Living Design &amp; Build | Creative Edge, Vernon BC",
         desc="Creative Edge designs and builds outdoor living across Vernon and the North Okanagan. Pools, retaining walls, hardscape, planting and lighting, all by one crew. Twenty years. Book a free design consult."),

    dict(slug="about",
         title="About Creative Edge Outdoor Living | Vernon BC Design-Build Crew",
         desc="Blaine Cusack trained in Landscape Architecture at NAIT in 2002 and spent two decades building yards before moving to the Okanagan. Meet the crew who design, build and maintain your outdoor space."),

    dict(slug="services",
         service=("Landscape Design, Build and Maintenance", "Landscaping"),
         title="Landscaping Services in Vernon BC | Design, Build, Maintain",
         desc="Six services under one roof: landscape design, full build, maintenance, softscaping, pools and spas, and landscape lighting. One crew from first call to finished yard."),

    dict(slug="pools",
         service=("Pool, Spa and Cold Plunge Installation", "Swimming pool installation"),
         title="Pools, Spas &amp; Cold Plunges Vernon BC | Authorized ImmerSpa Installer",
         desc="Custom in-ground pools, built-in spas and cold plunges designed into the whole yard, not dropped into it. Authorized ImmerSpa distributor and certified installer serving Vernon and the North Okanagan."),

    dict(slug="design",
         service=("Landscape Design", "Landscape design"),
         title="Landscape Design Packages | 2D &amp; 3D Plans, Vernon BC",
         desc="See your whole yard in 2D and 3D before anyone digs. Seven design packages from a single small space to a full property plan, each with planting, hardscape and lighting."),

    dict(slug="our-work",
         title="Our Work | Landscape Projects in Vernon &amp; the North Okanagan",
         desc="Completed pools, retaining walls, outdoor kitchens, putting greens and water features across Vernon and the North Okanagan. Design renders and finished builds."),

    dict(slug="commercial",
         service=("Commercial Landscaping", "Commercial landscaping"),
         title="Commercial Landscaping Vernon BC | Strata, Office &amp; Multi-Unit",
         desc="Commercial landscape design, construction and maintenance for strata, office and multi-unit properties across Vernon and the North Okanagan. One crew, scheduled work, one contact."),

    dict(slug="blog",
         title="Landscaping Advice for Okanagan Homeowners | Creative Edge",
         desc="Straight answers on landscape design, pools, retaining walls and what things actually cost in Vernon and the North Okanagan."),

    dict(slug="contact",
         title="Contact Creative Edge Outdoor Living | Vernon BC",
         desc="Call (250) 812 6112 or send us your project. We get back to you the same working day. Serving Vernon, Coldstream, Lavington, Armstrong, Enderby, Lumby, Salmon Arm and Sicamous."),

    # ---- service detail pages (linked from Services, not in nav) ---------
    dict(slug="retaining-walls",
         service=("Retaining Wall Construction", "Retaining wall construction"),
         title="Retaining Walls Vernon BC | Engineered, Drained, Built to Hold",
         desc="Retaining walls built with the drainage and base most quotes leave out. Serving Vernon and the North Okanagan. Two year limited warranty."),

    dict(slug="outdoor-living",
         service=("Outdoor Living Construction", "Outdoor living construction"),
         title="Outdoor Living Spaces Vernon BC | Kitchens, Firepits, Lighting",
         desc="Outdoor kitchens, firepits, patios and lighting designed as one space. Vernon and the North Okanagan, designed and built by one crew."),

    # ---- blog posts ------------------------------------------------------
    dict(slug="blog-landscape-design-vernon",
         title="Landscape Design &amp; Outdoor Living in Vernon BC | Creative Edge",
         desc="What actually makes a landscape project work in the North Okanagan: drainage, sun, slope and how you really use the space."),

    dict(slug="blog-immerspa-pools-spas",
         title="ImmerSpa Pools, Spas &amp; Cold Plunges | Creative Edge Outdoor Living",
         desc="We are an authorized ImmerSpa distributor and certified installer. What that means for your pool, spa or cold plunge in the Okanagan."),

    dict(slug="blog-spring-garden-refresh",
         title="Spring Garden Refresh: 5 Design Ideas for Your Okanagan Home",
         desc="Five things worth doing to an Okanagan yard in spring, and the one most people skip until it becomes expensive."),

    # ---- utility pages ---------------------------------------------------
    dict(slug="thank-you",
         title="Thanks, we have your details | Creative Edge Outdoor Living",
         desc="Your enquiry is in. We call back the same working day.",
         robots="noindex,follow"),

    dict(slug="terms",
         title="Terms of Use | Creative Edge Landscaping Ltd.",
         desc="The terms that cover your use of the Creative Edge Outdoor Living website. Not a contract for landscaping work.",
         robots="noindex,follow"),

    dict(slug="privacy-policy",
         title="Privacy Policy | Creative Edge Landscaping Ltd.",
         desc="How Creative Edge Landscaping Ltd. collects, uses and stores the information you send through this website.",
         robots="noindex,follow"),

    # ---- paid landing pages: noindex, NO NAV ----------------------------
    dict(slug="lp-pools",  nav=False, robots="noindex",
         title="Pool &amp; Backyard Design, Vernon BC | Creative Edge Outdoor Living",
         desc="Custom pools designed into the whole yard. Free design consult, Vernon and the North Okanagan."),

    dict(slug="lp-retaining-walls", nav=False, robots="noindex",
         title="Retaining Walls, Vernon BC | Creative Edge Outdoor Living",
         desc="Retaining walls built to hold. Free design consult, Vernon and the North Okanagan."),

    dict(slug="lp-outdoor-living", nav=False, robots="noindex",
         title="Outdoor Living Spaces, Vernon BC | Creative Edge",
         desc="Outdoor kitchens, firepits and lighting designed as one space. Free design consult."),
]
