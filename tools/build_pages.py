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

# ---- product category landing pages ---------------------------------------
# slug: (name, group, description, [applications], [brand slugs], [spec tags])
CATS = {
    "temperature-controllers": ("Temperature Controllers", "Temperature",
        "PID and on-off temperature controllers regulate ovens, furnaces, extruders and process baths with precise setpoint control. We supply panel-mount controllers from compact 48x48 mm units to advanced profile controllers with communication options.",
        ["Plastic processing and extrusion", "Furnaces and heat treatment", "Packaging machinery", "Food processing and ovens"],
        ["omron", "autonics", "azbil"], ["PID / On-Off", "48x48 to 96x96 mm", "SSR & Relay Output", "RS-485 Modbus"]),
    "temperature-transmitters": ("Temperature Transmitters", "Temperature",
        "Head-mount and rail-mount temperature transmitters convert RTD and thermocouple signals to a stable 4-20 mA or digital output for reliable transmission to PLC and DCS systems.",
        ["Process plants and reactors", "Remote tank farms", "HVAC and utilities", "OEM skids"],
        ["wika", "azbil"], ["4-20 mA", "HART option", "Head / DIN-rail mount"]),
    "rtd-pt100-sensors": ("RTD Pt100 Sensors", "Temperature",
        "Resistance temperature detectors (RTD Pt100) offer accurate, stable temperature measurement for industrial processes. We supply element-only, head-type and cable-type assemblies with thermowells to suit your process connection.",
        ["Pharma and food hygienic processes", "Motors and bearings monitoring", "Process pipelines", "Cold storage"],
        ["wika"], ["Class A / B", "3-wire / 4-wire", "SS316 sheath", "Custom lengths"]),
    "thermocouples": ("Thermocouples", "Temperature",
        "Type K, J, T, R and S thermocouple assemblies for temperatures beyond RTD range — furnaces, kilns and molten processes. Supplied with compensating cables and ceramic or metal protection tubes.",
        ["Furnaces and kilns", "Foundries and heat treatment", "Boilers", "Glass and ceramics"],
        ["wika"], ["Type K / J / T / R / S", "Ceramic / SS sheath", "Compensating cable"]),
    "thermowells": ("Thermowells", "Temperature",
        "Machined barstock and fabricated thermowells protect temperature sensors from process pressure, flow and corrosion, allowing sensor replacement without shutting the line.",
        ["Chemical and process piping", "High-pressure lines", "Hygienic processes"],
        ["wika"], ["Threaded / Flanged / Weld-in", "SS316 / Exotic alloys"]),
    "pressure-gauges": ("Pressure Gauges", "Pressure",
        "Bourdon tube, diaphragm and capsule pressure gauges in industrial and process-grade builds — dry and glycerine-filled, from vacuum to high pressure ranges, with all standard process connections.",
        ["Pneumatics and compressors", "Hydraulic power packs", "Boilers and utilities", "Process skids"],
        ["wika"], ["40 to 250 mm dial", "Glycerine filled", "SS / Brass wetted parts", "Vacuum to 1000 bar"]),
    "pressure-transmitters": ("Pressure Transmitters", "Pressure",
        "Pressure transmitters convert process pressure to a 4-20 mA signal for control and monitoring. We supply gauge, absolute and differential pressure transmitters with a wide range of process connections and accuracies.",
        ["Process control loops", "Water treatment and pumping", "OEM machinery", "Tank level by hydrostatic head"],
        ["wika", "ifm"], ["4-20 mA / IO-Link", "0.5% to 0.075% accuracy", "Gauge / Absolute / DP"]),
    "pressure-switches": ("Pressure Switches", "Pressure",
        "Mechanical and electronic pressure switches provide reliable switching for pump control, alarms and machine protection, with adjustable setpoints and high switching accuracy.",
        ["Pump on-off control", "Compressor protection", "Lubrication systems", "Fire-fighting lines"],
        ["wika", "ifm", "telemecanique"], ["SPDT / DPDT", "Electronic with display", "IP65+"]),
    "diaphragm-seals": ("Diaphragm Seals", "Pressure",
        "Diaphragm seals isolate pressure instruments from corrosive, viscous or hygienic media, extending gauge and transmitter life while maintaining measurement accuracy.",
        ["Chemical dosing", "Pharma / hygienic (tri-clamp)", "Slurry and viscous media"],
        ["wika"], ["Threaded / Flanged / Tri-clamp", "SS316L, PTFE lining"]),
    "flow-meters": ("Flow Meters", "Flow",
        "Flow meters for liquids, gases and steam — electromagnetic, vortex, turbine and oval-gear technologies matched to your media, line size and accuracy requirement.",
        ["Water and effluent measurement", "Chemical dosing", "Fuel and oil monitoring", "Steam and compressed air"],
        ["ifm", "baumer"], ["Magnetic / Vortex / Turbine", "Digital display", "4-20 mA / Pulse"]),
    "flow-switches": ("Flow Switches", "Flow",
        "Flow switches protect pumps, motors and heat exchangers by detecting loss of flow — paddle, thermal-dispersion and calorimetric types for water, oil and air.",
        ["Pump dry-run protection", "Cooling water circuits", "HVAC systems"],
        ["ifm"], ["Paddle / Thermal", "Relay or PNP output", "Inline / Insertion"]),
    "rotameters": ("Rotameters", "Flow",
        "Variable-area flow meters (rotameters) give simple, reliable local flow indication for liquids and gases — glass tube and metal tube designs with optional alarms and transmitters.",
        ["Purge and seal water lines", "Gas flow indication", "Dosing systems"],
        ["wika"], ["Glass / Metal tube", "Alarm contacts", "Direct reading scales"]),
    "level-transmitters": ("Level Transmitters", "Level",
        "Continuous level measurement for tanks and silos using hydrostatic, ultrasonic, capacitive and radar technologies — with 4-20 mA and IO-Link outputs for PLC integration.",
        ["Storage tanks and silos", "Water and effluent treatment", "Chemical storage", "Food-grade vessels"],
        ["ifm", "pepperl-fuchs"], ["Hydrostatic / Ultrasonic / Radar", "4-20 mA / IO-Link"]),
    "level-switches": ("Level Switches", "Level",
        "Point level switches — float, vibrating fork, conductive and capacitive — for reliable high/low alarms and pump control in liquids and solids.",
        ["Overfill protection", "Pump control", "Dry-run protection", "Hopper level"],
        ["ifm", "pepperl-fuchs"], ["Float / Fork / Capacitive", "Side / Top mounting"]),
    "inductive-proximity-sensors": ("Inductive Proximity Sensors", "Sensors",
        "Inductive proximity sensors detect metal targets without contact — the workhorse of machine automation. We stock M8 to M30 barrels, flush and non-flush, standard and extended sensing ranges from world-leading makes.",
        ["Position sensing on machines", "Conveyor and material handling", "Automotive fixtures", "Packaging lines"],
        ["pepperl-fuchs", "autonics", "ifm", "omron", "balluff", "contrinex", "turck"], ["M8-M30 barrel", "PNP / NPN, NO / NC", "2-wire / 3-wire", "IP67+"]),
    "capacitive-sensors": ("Capacitive Sensors", "Sensors",
        "Capacitive proximity sensors detect non-metallic materials — plastics, liquids, powders and granules — through container walls, ideal for level detection and presence sensing.",
        ["Level detection through tank walls", "Plastics and wood detection", "Granule and powder hoppers"],
        ["pepperl-fuchs", "autonics", "ifm"], ["M12-M30", "Adjustable sensitivity", "PNP / NPN"]),
    "photoelectric-sensors": ("Photoelectric Sensors", "Sensors",
        "Through-beam, retro-reflective and diffuse photoelectric sensors for object detection at range — with laser, background-suppression and clear-object variants for demanding applications.",
        ["Packaging and bottling lines", "Object counting", "Web and sheet detection", "Palletizing"],
        ["autonics", "sick", "banner", "omron", "pepperl-fuchs", "leuze", "datalogic", "panasonic"], ["Through-beam / Diffuse", "Laser variants", "Background suppression"]),
    "ultrasonic-sensors": ("Ultrasonic Sensors", "Sensors",
        "Ultrasonic sensors detect objects and measure distance regardless of colour, transparency or surface — reliable in dusty and wet environments where optical sensors struggle.",
        ["Level in tanks and silos", "Transparent object detection", "Distance measurement", "Loop control"],
        ["banner", "pepperl-fuchs", "sick"], ["Analog + switching output", "30 mm to 8 m range"]),
    "fiber-optic-sensors": ("Fiber Optic Sensors", "Sensors",
        "Fiber optic sensors put a tiny sensing head where space is tight and the amplifier where you can reach it — precise small-part detection on fast machines.",
        ["Small parts on feeders", "Electronics assembly", "Tight machine spaces"],
        ["autonics", "sick", "panasonic", "banner"], ["Through-beam / Diffuse fibers", "Digital amplifiers"]),
    "rotary-encoders": ("Rotary Encoders", "Sensors",
        "Incremental and absolute rotary encoders provide speed and position feedback for motors, conveyors and positioning axes, in shaft and hollow-shaft designs.",
        ["Motor speed feedback", "Length measurement", "Positioning axes", "Elevators and cranes"],
        ["baumer", "autonics", "pepperl-fuchs"], ["Incremental / Absolute", "Shaft / Hollow shaft", "HTL / TTL / SSI"]),
    "safety-light-curtains": ("Safety Light Curtains", "Safety",
        "Type 2 and Type 4 safety light curtains guard operator access points on presses, robots and automated machinery — finger, hand and body resolution with muting and blanking options.",
        ["Power press guarding", "Robot cell access", "Packaging machinery", "Assembly stations"],
        ["sick", "banner", "leuze", "datalogic", "schmersal"], ["Type 2 / Type 4", "14-90 mm resolution", "Muting / Blanking"]),
    "safety-relays": ("Safety Relays", "Safety",
        "Safety relays monitor e-stops, gates and light curtains and switch machine power safely — the certified core of every machine safety circuit.",
        ["E-stop monitoring", "Gate/guard monitoring", "Two-hand control", "Light curtain interface"],
        ["pilz", "schmersal", "omron", "banner"], ["Cat. 3 / Cat. 4, PLe", "Force-guided contacts"]),
    "safety-interlock-switches": ("Safety Interlock Switches", "Safety",
        "Guard interlock and solenoid-locking switches keep hazardous machinery stopped until guards are closed — mechanical, coded-magnet and RFID-coded types with high manipulation resistance.",
        ["Guard doors and hatches", "Fenced robot cells", "Access covers"],
        ["schmersal", "euchner", "pilz"], ["Solenoid locking", "RFID coded", "Tongue / Hinge types"]),
    "limit-switches": ("Limit Switches", "Switchgear & Control",
        "Heavy-duty position and limit switches for machine end-of-travel detection — lever, roller, plunger and rod actuators in metal and thermoplastic bodies.",
        ["Cranes and hoists", "Machine end-of-travel", "Conveyors", "Valve position"],
        ["telemecanique", "omron", "schmersal"], ["Roller / Lever / Plunger", "Snap action", "IP66/67"]),
    "digital-panel-meters": ("Digital Panel Meters", "Panel Instruments",
        "Digital panel meters display process values, voltage, current, frequency and energy on the panel front — with alarms, retransmission and communication options.",
        ["Control panel metering", "Generator and energy panels", "Process displays"],
        ["autonics", "omron"], ["48x24 to 96x96 mm", "Alarm relays", "RS-485"]),
    "process-indicators": ("Process Indicators", "Panel Instruments",
        "Universal-input process indicators accept RTD, thermocouple and 4-20 mA signals and show the value clearly, with alarm setpoints and optional retransmission to SCADA.",
        ["Tank farm displays", "Furnace monitoring", "Weighbridge and batching"],
        ["autonics", "omron"], ["Universal input", "Alarm outputs", "Retransmission"]),
    "counters-timers": ("Counters & Timers", "Panel Instruments",
        "Preset counters, totalizers and multi-function timers for machine sequencing, batch counting and production totals — panel-mount and DIN-rail formats.",
        ["Batch counting", "Production totalizing", "Machine sequencing", "Star-delta timing"],
        ["autonics", "omron"], ["LCD / LED", "Preset outputs", "Multi-function"]),
    "smps-power-supplies": ("SMPS Power Supplies", "Power",
        "Switch-mode power supplies deliver clean 24 V DC for sensors, PLCs and panel electronics — DIN-rail and panel-mount units from 15 W to 960 W with protection built in.",
        ["Control panel 24 V DC", "Sensor and PLC supply", "LED and instrumentation power"],
        ["delta", "omron", "autonics"], ["24 V DC, 1-40 A", "DIN-rail mount", "Overload protection"]),
    "vfd-drives": ("VFD / AC Drives", "Power",
        "Variable frequency drives control motor speed to save energy and improve process control — from compact micro drives to fan/pump and heavy-duty vector drives.",
        ["Pumps and fans", "Conveyors", "Machine spindles", "HVAC"],
        ["delta"], ["0.4 to 355 kW", "V/f and vector control", "Built-in braking"]),
    "enclosure-heaters": ("Enclosure & Panel Heaters", "Heating & Cooling",
        "Anti-condensation heaters keep control panels and outdoor enclosures dry, protecting electronics from moisture and corrosion — with thermostats and hygrostats for automatic control.",
        ["Outdoor panels and kiosks", "Coastal and humid sites", "Switchgear rooms"],
        ["itec"], ["10-400 W", "Thermostat control", "DIN-rail mount"]),
    "relays-contactors": ("Relays & Contactors", "Switchgear & Control",
        "Plug-in relays, contactor relays and power contactors for switching control circuits and motor loads — with sockets, accessories and timer variants.",
        ["Motor switching", "Control logic", "Heating loads", "Interposing duty"],
        ["omron", "telemecanique"], ["5 A to 800 A", "AC / DC coils", "1-4 pole"]),
    "push-buttons-pilot-devices": ("Push Buttons & Pilot Devices", "Switchgear & Control",
        "Push buttons, selector switches, emergency-stop devices and pilot lights in 22 mm standard — the operator interface of every control panel, in metal and plastic ranges.",
        ["Machine control stations", "Control desks", "E-stop stations"],
        ["telemecanique", "omron", "autonics"], ["22 mm standard", "Illuminated options", "E-stop mushroom"]),
    "cooling-fans": ("Panel Cooling Fans", "Heating & Cooling",
        "Axial fans and filter-fan units remove heat from control panels, extending the life of drives and power supplies — with matching exhaust filters and accessories.",
        ["VFD and PLC panels", "Server and telecom cabinets", "Power electronics"],
        ["ebm-papst"], ["Axial / Centrifugal", "230 V AC / 24 V DC", "Filter fan units"]),
    "ph-conductivity-analyzers": ("pH & Conductivity Analyzers", "Analytical",
        "Online pH, ORP and conductivity measurement for water treatment and process quality — electrodes, transmitters and complete analyzer loops.",
        ["Water and effluent treatment", "Boiler water quality", "CIP monitoring", "Chemical processes"],
        ["azbil"], ["pH / ORP / EC", "4-20 mA output", "Panel or field mount"]),
}

CAT_BODY = """  <!-- Page hero -->
  <section class="page-hero">
    <div class="wrap">
      <div class="crumbs"><a href="index.html">Home</a> / <a href="products.html">Products</a> / {name}</div>
      <h1>{name} — Supplier in Indore–Dewas</h1>
      <p>{name} from world-leading brands, supplied with correct model selection, genuine-product assurance and support since 1993.</p>
    </div>
  </section>

  <section class="section tint">
    <div class="wrap split">
      <div class="reveal">
        <span class="kicker">{group}</span>
        <h2>{name}, Selected Right for Your Application</h2>
        <p class="lead">{desc}</p>
        <ul class="checklist">
{apps}
        </ul>
        <div class="tags" style="margin-bottom: 26px;">
{tags}
        </div>
        <div class="hero-actions">
          <a class="btn btn-primary" href="contact.html">
            Get a Quote
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>
          </a>
          <button type="button" class="btn btn-navy" data-enquiry="{name}">Add to Enquiry List</button>
        </div>
      </div>
      <div class="reveal">
        <h3 style="font-size:1.05rem; margin-bottom:16px;">Available Makes</h3>
        <div class="logo-grid" style="grid-template-columns: repeat(2, 1fr);">
{brandcells}
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="section-head reveal">
        <span class="kicker">Related Products</span>
        <h2>More in {group}</h2>
      </div>
      <div class="tags reveal">
{related}
      </div>
    </div>
  </section>

  <section class="section" style="padding-top: 0;">
    <div class="wrap">
      <div class="cta-band reveal">
        <div>
          <h2>Need {lname} for your plant?</h2>
          <p>Share your application or a model number — we'll recommend the right make and quote quickly.</p>
        </div>
        <a class="btn btn-primary" href="contact.html">
          Send an Enquiry
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>
        </a>
      </div>
    </div>
  </section>
"""

CHECK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>'

for slug, (name, group, desc, apps, cat_brands, tags) in CATS.items():
    fname = f"{slug}.html"
    canonical = f"{BASE}/{fname}"
    apps_html = "\n".join(f"          <li>{CHECK_SVG}{a}</li>" for a in apps)
    tags_html = "\n".join(f'          <span class="tag">{t}</span>' for t in tags)
    cells = "\n".join(
        f'          <a class="logo-cell" href="brand-{b}.html"><img src="assets/img/brands/{b}.png" alt="{BRANDS[b][0]}" loading="lazy"></a>'
        for b in cat_brands)
    related = "\n".join(
        f'        <a class="tag" href="{s}.html">{CATS[s][0]}</a>'
        for s in CATS if s != slug and CATS[s][1] == group) or '        <a class="tag" href="products.html">All Products</a>'
    title = f"{name} Supplier &amp; Dealer in Indore–Dewas (M.P.) | Apt Controls"
    page_desc = f"Buy {name.lower()} in Indore–Dewas, Madhya Pradesh from Apt Controls — {desc[:120].rstrip('.')}. Genuine products, quotations &amp; support since 1993."
    keywords = f"{name.lower()} supplier Indore, {name.lower()} dealer Madhya Pradesh, {name.lower()} distributor India, buy {name.lower()}, {name.lower()} price Indore"
    head = make_head(title, page_desc, keywords, canonical,
                     crumb(("Home", BASE + "/"), ("Products", BASE + "/products.html"), (name, canonical)))
    body = CAT_BODY.format(name=name, lname=name.lower(), group=group, desc=desc,
                           apps=apps_html, tags=tags_html, brandcells=cells, related=related)
    (root / fname).write_text(head + header + body + "\n" + footer)
    written.append(fname)
print(f"wrote {len(CATS)} category pages")

# inject category links into the products page placeholder
cat_links = "\n".join(f'        <a class="tag" href="{s}.html">{CATS[s][0]}</a>' for s in CATS)
prod_page = root / "products.html"
prod_page.write_text(prod_page.read_text().replace("<!--CATEGORY_LINKS-->", cat_links))

# ---- blog / insights -------------------------------------------------------
art_dir = frag_dir.parent / "articles"
articles = []
if art_dir.is_dir():
    for art in sorted(art_dir.glob("*.html")):
        text = art.read_text()
        m = re.match(r"<!--TITLE:(.*?)-->\n<!--DESC:(.*?)-->\n<!--KEYWORDS:(.*?)-->\n<!--DATE:(.*?)-->\n<!--LABEL:(.*?)-->\n", text, re.S)
        title, desc, keywords, date, label = (m.group(i).strip() for i in range(1, 6))
        body_html = text[m.end():]
        fname = f"blog-{art.stem}.html"
        canonical = f"{BASE}/{fname}"
        short = title.split("|")[0].split("—")[0].strip()
        article_ld = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": short,
            "description": re.sub(r"&amp;", "&", desc),
            "datePublished": date,
            "dateModified": date,
            "author": {"@type": "Organization", "name": "Apt Controls", "url": BASE + "/"},
            "publisher": {"@type": "Organization", "name": "Apt Controls", "logo": {"@type": "ImageObject", "url": BASE + "/assets/img/logo.png"}},
            "mainEntityOfPage": canonical,
        }
        page_body = f"""  <!-- Page hero -->
  <section class="page-hero">
    <div class="wrap">
      <div class="crumbs"><a href="index.html">Home</a> / <a href="blog.html">Insights</a> / {label}</div>
      <h1>{short}</h1>
      <p class="article-meta">{label} · Published {date} · Apt Controls Team</p>
    </div>
  </section>

  <section class="section">
    <div class="wrap article">
{body_html}
      <div class="article-cta">
        <p><strong>Need help selecting?</strong> Our team has matched instruments to applications since 1993 — <a href="contact.html">send us your requirement</a> or call <a href="tel:+918878114492">+91 88781 14492</a>.</p>
      </div>
    </div>
  </section>
"""
        head = make_head(title, desc, keywords, canonical,
                         crumb(("Home", BASE + "/"), ("Insights", BASE + "/blog.html"), (short, canonical)))
        head = head.replace("</head>", f'  <script type="application/ld+json">\n{json.dumps(article_ld, indent=2)}\n  </script>\n</head>')
        (root / fname).write_text(head + header + page_body + "\n" + footer)
        written.append(fname)
        articles.append((fname, short, desc, date, label))
    # blog index
    cards = "\n".join(f"""        <a class="card reveal" href="{f}" style="display:block;">
          <span class="kicker">{label}</span>
          <h3>{short}</h3>
          <p>{desc}</p>
          <p style="margin-top:12px; font-size:0.82rem; color:var(--ink-faint);">{date} · Apt Controls Team</p>
        </a>""" for f, short, desc, date, label in sorted(articles, key=lambda a: a[3], reverse=True))
    blog_body = f"""  <!-- Page hero -->
  <section class="page-hero">
    <div class="wrap">
      <div class="crumbs"><a href="index.html">Home</a> / Insights</div>
      <h1>Insights &amp; Selection Guides</h1>
      <p>Practical guides from three decades of matching instruments to applications — written for the engineers who keep plants running.</p>
    </div>
  </section>

  <section class="section tint">
    <div class="wrap">
      <div class="grid cols-2">
{cards}
      </div>
    </div>
  </section>
"""
    canonical = f"{BASE}/blog.html"
    head = make_head(
        "Insights — Instrumentation Selection Guides &amp; Technical Articles | Apt Controls",
        "Practical selection guides for pressure transmitters, temperature sensors, proximity sensors, safety light curtains, calibration and more — from Apt Controls, industrial instrumentation distributor since 1993.",
        "instrument selection guide, pressure transmitter selection, RTD vs thermocouple, proximity sensor types, safety light curtain guide, instrument calibration importance",
        canonical, crumb(("Home", BASE + "/"), ("Insights", canonical)))
    (root / "blog.html").write_text(head + header + blog_body + "\n" + footer)
    written.append("blog.html")
    print(f"wrote blog.html + {len(articles)} articles")

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
