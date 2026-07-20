# Phase 2 — How to Turn Off or Revert

Phase 2 added four features on top of the approved phase-1 site:

1. 24 per-brand landing pages + `brands.html` index (+ "Brands" nav item)
2. Floating WhatsApp button on every page
3. "Add to Enquiry" basket (products page & brand pages → prefills contact form)
4. Google Analytics 4 hooks with conversion events (inactive until an ID is set)

Everything is designed to be reversible in minutes, at two levels.

## Level 1 — Turn a single feature off (≈1 minute)

Edit `assets/js/config.js` and set the flag to `false`, then redeploy:

```js
whatsappFloat: false,   // hides the floating WhatsApp button
enquiryCart: false,     // hides all "Add to Enquiry" buttons and the basket
gaMeasurementId: "",    // "" keeps Google Analytics completely off
```

No other file needs to change. Brand pages have no flag — to hide them
without deleting, just remove the "Brands" link from the nav/footer in
`index.html` and rerun `python3 tools/build_pages.py`.

## Level 2 — Full rollback to the approved phase-1 site (≈2 minutes)

The last phase-1 commit is **`8813b76`**
("Make enquiry form deliver via email and WhatsApp").

```bash
git checkout claude/apt-controls-website-a5w6ia
git revert --no-edit 8813b76..HEAD   # undoes phase 2, keeps history
git push origin claude/apt-controls-website-a5w6ia
```

(or, to discard phase-2 history entirely:
`git reset --hard 8813b76 && git push --force-with-lease`)

## Regenerating pages

All inner pages, the 24 brand pages, `brands.html` and `sitemap.xml` are
generated from `tools/build_pages.py` + `tools/fragments/`. After editing
anything there (or the shared header/footer in `index.html`), run:

```bash
python3 tools/build_pages.py tools/fragments
```
