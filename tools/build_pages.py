#!/usr/bin/env python3
"""Assemble inner pages from index.html chrome + fragments, generate brand
landing pages, the brands index and sitemap.xml."""
import datetime, json, pathlib, re, sys

root = pathlib.Path(__file__).resolve().parents[1]
BASE = "https://aptcontrols.net"
index = (root / "index.html").read_text()

header = index[index.index("  <!-- Top bar -->"):index.index("  <!-- Hero -->")]
footer = index[index.index("  <!-- Footer -->"):]

BUSINESS_LD = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "@id": BASE + "/#business",
    "name": "Apt Controls",
    "url": BASE + "/",
    "logo": BASE + "/assets/img/logo.png",
    "image": BASE + "/assets/img/og-image.png",
    "description": "Independent, family-owned distributor of industrial process control instruments, electrical, electronics and automation products, representing world-leading brands since 1993.",
    "foundingDate": "1993",
    "telephone": "+91-8878114492",
    "email": "enquiry@aptcontrols.net",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "113, Ram Nagar Extension, A.B. Road",
        "addressLocality": "Dewas",
        "addressRegion": "Madhya Pradesh",
        "postalCode": "455001",
        "addressCountry": "IN",
    },
    "geo": {"@type": "GeoCoordinates", "latitude": 22.9676, "longitude": 76.0534},
    "areaServed": "India",
    "sameAs": [
        "https://in.linkedin.com/company/aptcontrols",
        "https://www.facebook.com/AptControls/",
    ],
}

PAGE_NAMES = {
    "about.html": "About Us",
    "products.html": "Products",
    "brands.html": "Brands",
    "services.html": "Services",
    "contact.html": "Contact Us",
    "thank-you.html": "Thank You",
}

# slug -> (display name, product lines)
BRANDS = {
    "wika": ("WIKA", "Pressure gauges, pressure transmitters, temperature gauges, thermowells and diaphragm seals"),
    "autonics": ("Autonics", "Proximity and photoelectric sensors, temperature controllers, counters, timers, panel meters and encoders"),
    "pepperl-fuchs": ("Pepperl+Fuchs", "Inductive, capacitive and photoelectric proximity sensors, ultrasonic sensors and rotary encoders"),
    "sick": ("SICK", "Photoelectric sensors, fiber-optic sensors, safety light curtains and encoders"),
    "telemecanique": ("Telemecanique Sensors", "Limit switches, proximity sensors, pressure switches and pilot devices"),
    "omron": ("Omron", "Temperature controllers, timers, counters, relays, proximity and photoelectric sensors"),
    "ifm": ("ifm electronic", "Inductive sensors, flow sensors, pressure and level sensors, and IO-Link solutions"),
    "banner": ("Banner Engineering", "Photoelectric and ultrasonic sensors, LED indicators and machine safety devices"),
    "balluff": ("Balluff", "Inductive and photoelectric sensors, linear position sensors and connectivity products"),
    "baumer": ("Baumer", "Rotary encoders, inductive and photoelectric sensors, and process instrumentation"),
    "turck": ("Turck", "Inductive and capacitive sensors, connectivity solutions and fieldbus I/O"),
    "pilz": ("Pilz", "Safety relays, safety controllers and emergency-stop solutions"),
    "panasonic": ("Panasonic Industry", "Photoelectric, laser and fiber sensors, timers, counters and relays"),
    "leuze": ("Leuze", "Optical sensors, safety light curtains and positioning systems"),
    "schmersal": ("Schmersal", "Safety switches, solenoid interlocks and position switches"),
    "euchner": ("Euchner", "Safety interlocks, transponder-coded safety switches and enabling switches"),
    "delta": ("Delta", "AC drives (VFDs), SMPS power supplies, HMIs and industrial automation products"),
    "ebm-papst": ("ebm-papst", "Axial and centrifugal fans, blowers and cooling solutions for panels and equipment"),
    "azbil": ("Azbil", "Process instrumentation, temperature controllers and control valves"),
    "datalogic": ("Datalogic", "Photoelectric sensors, safety light curtains and identification products"),
    "contrinex": ("Contrinex", "Inductive and photoelectric sensors, including miniature and high-pressure ranges"),
    "module": ("Module", "Power semiconductor modules — IGBT, thyristor and diode modules"),
    "osna": ("Osna", "Industrial control and power products"),
    "itec": ("iTEC", "Industrial control products and components"),
}

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="keywords" content="{keywords}">
  <link rel="canonical" href="{canonical}">
  <meta name="geo.region" content="IN-MP">
  <meta name="geo.placename" content="Dewas">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Apt Controls">
  <meta property="og:locale" content="en_IN">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{base}/assets/img/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{base}/assets/img/og-image.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Sora:wght@600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/styles.css">
  <noscript><style>.reveal {{ opacity: 1; transform: none; }}</style></noscript>
  <link rel="icon" type="image/png" href="assets/img/fv-icon.png">
  <script type="application/ld+json">
{business_ld}
  </script>
  <script type="application/ld+json">
{breadcrumb_ld}
  </script>
</head>
<body>

"""


def make_head(title, desc, keywords, canonical, breadcrumb, noindex=False):
    head = HEAD.format(
        title=title, desc=desc, keywords=keywords, canonical=canonical, base=BASE,
        business_ld=json.dumps(BUSINESS_LD, indent=2),
        breadcrumb_ld=json.dumps(breadcrumb, indent=2),
    )
    if noindex:
        head = head.replace('<link rel="canonical"',
                            '<meta name="robots" content="noindex">\n  <link rel="canonical"')
    return head


def crumb(*steps):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": url}
            for i, (name, url) in enumerate(steps)
        ],
    }


written = []

# ---- fragment-based pages -------------------------------------------------
frag_dir = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).parent / "fragments"

for frag in sorted(frag_dir.glob("*.html")):
    text = frag.read_text()
    m = re.match(r"<!--TITLE:(.*?)-->\n<!--DESC:(.*?)-->\n<!--KEYWORDS:(.*?)-->\n(<!--NOINDEX-->\n)?", text, re.S)
    title, desc, keywords = (m.group(i).strip() for i in (1, 2, 3))
    noindex = bool(m.group(4))
    body = text[m.end():]
    canonical = f"{BASE}/{frag.name}"
    head = make_head(title, desc, keywords, canonical,
                     crumb(("Home", BASE + "/"), (PAGE_NAMES[frag.name], canonical)),
                     noindex)
    (root / frag.name).write_text(head + header + body + "\n" + footer)
    if not noindex:
        written.append(frag.name)
    print(f"wrote {frag.name}")

# ---- brand landing pages --------------------------------------------------
BRAND_BODY = """  <!-- Page hero -->
  <section class="page-hero">
    <div class="wrap">
      <div class="crumbs"><a href="index.html">Home</a> / <a href="brands.html">Brands</a> / {name}</div>
      <h1>{name} — Dealer &amp; Supplier in Indore–Dewas</h1>
      <p>Genuine {name} products supplied by Apt Controls, your instrumentation partner in Madhya Pradesh since 1993.</p>
    </div>
  </section>

  <section class="section tint">
    <div class="wrap split">
      <div class="brand-hero-logo reveal">
        <img src="assets/img/brands/{slug}.png" alt="{name} logo">
      </div>
      <div class="reveal">
        <span class="kicker">Genuine Products · Trusted Supply</span>
        <h2>{name} Products, Genuine &amp; In Stock</h2>
        <p class="lead">{lines}.</p>
        <p>We supply the full {name} range with correct model selection for your application, genuine-product assurance and support that continues after the sale — calibration, maintenance and fast replacements.</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="contact.html">
            Get a {name} Quote
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>
          </a>
          <button type="button" class="btn btn-navy" data-enquiry="{name} products">Add to Enquiry List</button>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="section-head center reveal">
        <span class="kicker">Why Buy {name} from Apt Controls</span>
        <h2>Three Decades of Instrumentation Trust</h2>
      </div>
      <div class="grid cols-3">
        <div class="card reveal">
          <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg></div>
          <h3>100% Genuine</h3>
          <p>Every {name} product we supply is genuine, with proper documentation and warranty support.</p>
        </div>
        <div class="card reveal">
          <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg></div>
          <h3>Right Model, First Time</h3>
          <p>Share your application — we specify the correct {name} model, ratings and accessories.</p>
        </div>
        <div class="card reveal">
          <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/></svg></div>
          <h3>Fast Delivery &amp; Support</h3>
          <p>Timely delivery across the Dewas–Indore belt and India, backed by calibration and maintenance services.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section tint">
    <div class="wrap">
      <div class="section-head center reveal">
        <span class="kicker">More Brands</span>
        <h2>Other Makes We Deal In</h2>
      </div>
      <div class="logo-grid reveal">
{others}
      </div>
      <div style="text-align:center; margin-top: 26px;">
        <a class="btn btn-navy" href="brands.html">View All Brands</a>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="cta-band reveal">
        <div>
          <h2>Need {name} products or a cross-reference?</h2>
          <p>Send us the model number or your application details — we'll quote quickly with the right part.</p>
        </div>
        <a class="btn btn-primary" href="contact.html">
          Send an Enquiry
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>
        </a>
      </div>
    </div>
  </section>
"""

slugs = list(BRANDS)
for slug, (name, lines) in BRANDS.items():
    fname = f"brand-{slug}.html"
    canonical = f"{BASE}/{fname}"
    sibs = [s for s in slugs if s != slug][:6]
    others = "\n".join(
        f'        <a class="logo-cell" href="brand-{s}.html"><img src="assets/img/brands/{s}.png" alt="{BRANDS[s][0]}" loading="lazy"></a>'
        for s in sibs)
    title = f"{name} Dealer &amp; Supplier in Indore–Dewas (M.P.) | Apt Controls"
    desc = f"Buy genuine {name} products in Indore–Dewas, Madhya Pradesh — {lines}. Quotations, calibration &amp; support from Apt Controls, instrumentation distributor since 1993."
    keywords = f"{name} dealer Indore, {name} distributor India, {name} supplier Madhya Pradesh, {name} price, buy {name} products, {name} stockist Dewas"
    head = make_head(title, desc, keywords, canonical,
                     crumb(("Home", BASE + "/"), ("Brands", BASE + "/brands.html"), (name, canonical)))
    body = BRAND_BODY.format(name=name, slug=slug, lines=lines, others=others)
    (root / fname).write_text(head + header + body + "\n" + footer)
    written.append(fname)
print(f"wrote {len(BRANDS)} brand pages")

# ---- brands index page ----------------------------------------------------
cells = "\n".join(
    f'        <a class="logo-cell reveal" href="brand-{s}.html" title="{BRANDS[s][0]}"><img src="assets/img/brands/{s}.png" alt="{BRANDS[s][0]}" loading="lazy"></a>'
    for s in slugs)
brands_body = f"""  <!-- Page hero -->
  <section class="page-hero">
    <div class="wrap">
      <div class="crumbs"><a href="index.html">Home</a> / Brands</div>
      <h1>Brands We Deal In</h1>
      <p>Twenty-four world-leading instrumentation and automation makes — genuine products, correct selection and after-sales support from one trusted source.</p>
    </div>
  </section>

  <section class="section tint">
    <div class="wrap">
      <div class="logo-grid">
{cells}
      </div>
      <p class="brand-note">All product and brand names are trademarks of their respective owners. Click a brand to see what we supply.</p>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="cta-band reveal">
        <div>
          <h2>Don't see the make you need?</h2>
          <p>We can source additional brands and suggest equivalent products — send us the model number.</p>
        </div>
        <a class="btn btn-primary" href="contact.html">
          Ask Us
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>
        </a>
      </div>
    </div>
  </section>
"""
canonical = f"{BASE}/brands.html"
head = make_head(
    "Brands We Deal In — 24 Global Instrumentation Makes | Apt Controls Indore",
    "Apt Controls supplies genuine products from WIKA, Omron, SICK, Pepperl+Fuchs, Autonics, ifm, Banner, Balluff, Turck, Pilz, Delta, ebm-papst &amp; more in Indore–Dewas, Madhya Pradesh.",
    "industrial automation brands dealer Indore, instrumentation brands distributor India, WIKA Omron SICK dealer, sensor brands supplier Madhya Pradesh",
    canonical, crumb(("Home", BASE + "/"), ("Brands", canonical)))
(root / "brands.html").write_text(head + header + brands_body + "\n" + footer)
written.append("brands.html")
print("wrote brands.html")

# ---- sitemap.xml ----------------------------------------------------------
today = datetime.date.today().isoformat()
prio = {"products.html": "0.9", "brands.html": "0.9", "services.html": "0.8", "contact.html": "0.8", "about.html": "0.7"}
urls = [f"""  <url>
    <loc>{BASE}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>"""]
for page in sorted(set(written)):
    urls.append(f"""  <url>
    <loc>{BASE}/{page}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>{prio.get(page, "0.6")}</priority>
  </url>""")
(root / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "\n".join(urls) + "\n</urlset>\n")
print(f"wrote sitemap.xml ({len(urls)} URLs)")
