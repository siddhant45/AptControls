# Apt Controls — Company Website

Static website for **Apt Controls**, an independent, family-owned distributor of
industrial process control instruments, electrical, electronics and automation
products based in Dewas (M.P.), India — serving industry since 1993.

Rebuilt as a modern replacement for the previous site at [aptcontrols.net](https://aptcontrols.net/).

## Pages

| Page | Purpose |
| --- | --- |
| `index.html` | Home — hero, stats, product highlights, brands, services, industries |
| `about.html` | Company story, values, what we do |
| `products.html` | Full product range (12+ categories) and brands represented |
| `services.html` | Supply & distribution, calibration, maintenance, selection guidance |
| `contact.html` | Contact details, enquiry form, location map |

## Tech

- Plain HTML, CSS and vanilla JavaScript — no build step, no framework.
- Shared styles in `assets/css/styles.css`, interactions in `assets/js/main.js`
  (mobile nav, active-link highlighting, scroll-reveal, enquiry form via `mailto:`).
- Fully responsive; fonts loaded from Google Fonts (Inter + Sora).

## Local preview

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

Deployable as-is to any static host (GitHub Pages, Netlify, shared hosting, …).
