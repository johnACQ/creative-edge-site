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
         title="Landscaping in Vernon BC | Design &amp; Build | Creative Edge",
         desc="Creative Edge designs and builds outdoor living across Vernon and the North Okanagan. Pools, retaining walls, hardscape, planting and lighting, all by one crew. Twenty years. Book a free design consult."),

    dict(slug="about",
         title="About Creative Edge Outdoor Living | Vernon BC Design-Build Crew",
         desc="Blaine Cusack took the Landscape Architecture Tech program at NAIT in 2002 and spent two decades building yards before moving to the Okanagan. Meet the crew who design, build and maintain your outdoor space."),

    dict(slug="services",
         service=("Landscape Design, Build and Maintenance", "Landscaping"),
         title="Landscaping Services in Vernon BC | Design, Build, Maintain",
         desc="Eight services under one roof: landscape design, full build, maintenance, softscaping, landscape lighting, pools, spas and cold plunges. One crew from first call to finished yard."),

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
         desc="Call (250) 812 6112 or send us your project. We get back to you the same working day. Serving Vernon, Coldstream, Lavington, Armstrong, Enderby, Lumby, Salmon Arm, Sicamous, Kamloops, Kelowna and Penticton."),

    # ---- service detail pages (linked from Services, not in nav) ---------
    dict(slug="retaining-walls",
         service=("Retaining Wall Construction", "Retaining wall construction"),
         title="Retaining Walls Vernon BC | Engineered, Drained, Built to Hold",
         desc="Retaining walls built with the drainage and base most quotes leave out. Serving Vernon and the North Okanagan."),

    dict(slug="outdoor-living",
         service=("Outdoor Living Construction", "Outdoor living construction"),
         title="Outdoor Living Spaces Vernon BC | Kitchens, Firepits, Lighting",
         desc="Outdoor kitchens, firepits, patios and lighting designed as one space. Vernon and the North Okanagan, designed and built by one crew."),

    # ---- blog posts ------------------------------------------------------
    # date = the day the post goes live (America/Vancouver). build.py skips any
    # post dated in the future, so the weekly GitHub Action (.github/workflows/
    # weekly-blog.yml) publishes a staged post simply by rebuilding on its date.
    # card = the blog.html index card; the build generates the cards, newest
    # first. Never hand-edit cards into content/blog.html.
    dict(slug="blog-retaining-walls-why-they-fail", date="2026-10-07",
         card=dict(img="img/ce-work-backyard-dusk.jpg", w=1024, h=683,
                   alt="Two tiers of lit block retaining wall above a lawn and paver path at dusk",
                   title="Why retaining walls fail, and what to ask before you sign a quote",
                   excerpt="Almost always it is the base or the drainage, and both are buried by the time the job is done. Five questions to ask whoever quotes your wall."),
         title="Why Retaining Walls Fail, and What to Ask Before You Sign | Creative Edge",
         desc="Most retaining walls fail at the base or the drainage. Five questions to ask whoever quotes your wall in Vernon and the North Okanagan, before you sign."),

    dict(slug="blog-pool-planning-next-summer", date="2026-10-07",
         card=dict(img="img/ce-work-water-night.jpg", w=1024, h=683,
                   alt="Lit water feature spilling onto river rock at night",
                   title="Want a pool or cold plunge next summer? Start in the fall",
                   excerpt="Design, permits and scheduling all happen before anyone digs. Why the fall conversation is the one that gets you in the water for the summer."),
         title="Want a Pool or Cold Plunge Next Summer? Start in the Fall | Creative Edge",
         desc="Design, permits and scheduling all happen before anyone digs. Why a fall start gets you in the water next summer in Vernon and the North Okanagan."),

    dict(slug="blog-landscape-design-vernon", date="2026-07-31",
         card=dict(img="img/ce-render-aerial-night.jpg", w=1600, h=900,
                   alt="Aerial night view of a lit landscape design",
                   title="Landscape design and outdoor living in Vernon, BC",
                   excerpt="Why the drawing matters more than the plant list, and the four site conditions that decide whether a yard works here: drainage, sun, slope and how you really use it."),
         title="Landscape Design &amp; Outdoor Living in Vernon BC | Creative Edge",
         desc="What actually makes a landscape project work in the North Okanagan: drainage, sun, slope and how you really use the space."),

    dict(slug="blog-immerspa-pools-spas", date="2026-07-31",
         card=dict(img="img/ce-render-pool-dusk.jpg", w=1600, h=900,
                   alt="Infinity edge pool at dusk",
                   title="ImmerSpa pools, spas and cold plunges",
                   excerpt="We are an authorized ImmerSpa distributor and a certified installer. What that actually means for your pool or plunge, and where a fibreglass unit beats a poured one."),
         title="ImmerSpa Pools, Spas &amp; Cold Plunges | Creative Edge Outdoor Living",
         desc="We are an authorized ImmerSpa distributor and certified installer. What that means for your pool, spa or cold plunge in the Okanagan."),

    dict(slug="blog-spring-garden-refresh", date="2026-07-31",
         card=dict(img="img/ce-render-putting-green.jpg", w=1600, h=900,
                   alt="Putting green with boulders and planting beds",
                   title="Spring garden refresh: 5 ideas for your Okanagan home",
                   excerpt="Five things worth doing to a yard in spring, and the one most people put off until it turns into a much bigger bill."),
         title="Spring Garden Refresh: 5 Design Ideas for Your Okanagan Home",
         desc="Five things worth doing to an Okanagan yard in spring, and the one most people skip until it becomes expensive."),

    dict(slug="blog-plan-spring-build-over-winter", date="2026-10-19",
         card=dict(img="img/ce-render-valley-dining.jpg", w=1600, h=900,
                   alt="Design render of an outdoor dining terrace, kitchen and pool looking out over an Okanagan valley",
                   title="The yard you want next summer gets decided this winter",
                   excerpt="Walk it, number it, draw it, book it. The four steps that happen before anyone digs, and why winter is the time to get them done."),
         title="Plan Your Backyard Build Over Winter, Vernon BC | Creative Edge",
         desc="Most people call about a backyard once the snow melts. How to walk, price, design and book your build over winter in Vernon and the North Okanagan."),
    dict(slug="blog-outdoor-kitchen-before-you-build", date="2026-10-26",
         card=dict(img="img/ce-render-kitchen-golden.jpg", w=1600, h=891,
                   alt="Design render of an outdoor kitchen with a built-in grill and stone counter beside lounge seating and a pool at golden hour",
                   title="Outdoor kitchens: what to decide before you build one",
                   excerpt="The grill is the easy part. Run the dinner test before anything gets drawn, and your kitchen ends up somewhere you actually use it."),
         title="Outdoor Kitchens: What to Decide Before You Build | Creative Edge",
         desc="The grill is the easy part. Where your outdoor kitchen sits, where everyone eats and what runs under the patio decide whether you use it. Vernon BC."),
    dict(slug="blog-2d-3d-landscape-design", date="2026-11-02",
         card=dict(img="img/ce-render-pergola-water.jpg", w=1600, h=900,
                   alt="3D design render of a covered seating pavilion beside a pool with a lit water feature at dusk",
                   title="2D and 3D landscape design: what you get and why it saves money",
                   excerpt="One drawing does three jobs: preview, price and plan. What every package includes, and how to choose between 2D and 3D."),
         title="2D and 3D Landscape Design: What You Actually Get | Creative Edge",
         desc="What a 2D and 3D landscape design includes, how revisions work, and how to choose between 2D and 3D before anyone digs. Vernon and the North Okanagan."),
    dict(slug="blog-building-on-a-slope-north-okanagan", date="2026-11-09",
         card=dict(img="img/ce-render-covered-living.jpg", w=1200, h=675,
                   alt="Design render of curved terraced walls, steps and planting climbing a slope beside a house",
                   title="Building on a slope in the North Okanagan: levels, steps and drainage",
                   excerpt="Your slope is not the problem. Why levels, steps and water get decided together, and what your site visit should cover."),
         title="Building on a Slope: Levels, Steps and Drainage, Vernon BC | Creative Edge",
         desc="Most lots around Vernon have some slope. How levels, steps and drainage turn it into yard you use, and what your site visit should cover."),
    dict(slug="blog-fire-pit-gathering-space", date="2026-11-16",
         card=dict(img="img/ce-render-pool-firepit.jpg", w=1200, h=675,
                   alt="Design render of a sunken fire pit lounge with built-in seating in front of a pool with a linear fire feature",
                   title="Fire pits: build the gathering space, not just the fire",
                   excerpt="You gather around the seats, not the fire. The four decisions that turn a fire pit into the place your evening ends."),
         title="Fire Pits and Gathering Spaces: Get the Layout Right | Creative Edge",
         desc="A fire pit is easy to buy. The spot, the seating, the walk out and the light decide whether you use it. Fire pit and gathering space design, Vernon BC."),
    dict(slug="blog-landscape-lighting-plan-it-in", date="2026-11-23",
         card=dict(img="img/ce-wall-tiers-dusk.jpg", w=1600, h=900,
                   alt="Two levels of block wall at dusk with lit water features, steps and a path light above a lawn",
                   title="Landscape lighting: plan it in, don't staple it on",
                   excerpt="Lighting left to the end ends up stapled to a fence. How to plan it in three passes: features, paths and where you sit."),
         title="Landscape Lighting: Plan It In, Don't Staple It On | Creative Edge",
         desc="Lighting added after the build ends up stapled to a fence. How to plan landscape lighting into your yard in three passes. Vernon and the North Okanagan."),

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

    # Kelowna pools (John 2026-10-22 after the Blaine meeting): Kelowna city only,
    # POOL BUILDS ONLY. The Service node's areaServed is Kelowna alone (3rd tuple
    # item); the business node keeps the full town list like every other page.
    dict(slug="lp-kelowna-pools", nav=False, robots="noindex",
         service=("Pool Installation in Kelowna", "Swimming pool installation", ["Kelowna"]),
         title="Pool Builds in Kelowna BC | Creative Edge Outdoor Living",
         desc="In-ground pools designed and built for Kelowna homes. Free pool consult and a real budget number on the first visit."),
]
