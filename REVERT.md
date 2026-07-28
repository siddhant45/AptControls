# Version Checkpoints — How to Roll Back to Any Version

Every phase of the site is a recorded checkpoint. You can return the site
to **any** of these versions in about two minutes, without losing history.

## Checkpoints (oldest → newest)

| Checkpoint | Commit | What the site contains at this point |
| --- | --- | --- |
| **v1 — Phase 1** | `8813b76` | 6 pages, original photos/branding, SEO meta & schema, enquiry form with email + WhatsApp delivery |
| **v2 — Phase 2** | `f5e50d9` | v1 + 24 brand pages, Brands nav, floating WhatsApp, enquiry basket, GA hooks, build tooling in `tools/` |
| **v2.1 — GEO** | `5a7898b` | v2 + llms.txt, homepage FAQ + FAQPage schema, AI-crawler rules |
| **v3 — Phase 3** | *(latest)* | v2.1 + ~34 product-category landing pages, Insights blog (6 articles), expanded internal linking |

## Roll back to any checkpoint (keeps history — recommended)

```bash
git checkout claude/apt-controls-website-a5w6ia
git revert --no-edit <commit>..HEAD     # e.g. git revert --no-edit 5a7898b..HEAD  → back to v2.1
git push origin claude/apt-controls-website-a5w6ia
```

- Back to **v2.1** (undo phase 3 only): `git revert --no-edit 5a7898b..HEAD`
- Back to **v2** (also undo GEO): `git revert --no-edit f5e50d9..HEAD`
- Back to **v1** (bare approved site): `git revert --no-edit 8813b76..HEAD`

Reverts are themselves commits, so you can "revert the revert" to go
forward again — nothing is ever lost.

## Roll forward again after a revert

```bash
git revert --no-edit <the revert commits>   # or simply:
git reset --hard <checkpoint-commit> && git push --force-with-lease
```

## Turn a single feature off instead (≈1 minute)

`assets/js/config.js` has per-feature switches — no rollback needed:

```js
whatsappFloat: false,   // hides the floating WhatsApp button
enquiryCart: false,     // hides all "Add to Enquiry" buttons and the basket
gaMeasurementId: "",    // "" keeps Google Analytics completely off
```

Category/brand/blog pages have no flag — to hide them without a rollback,
remove their links from the nav/footer in `index.html` and rerun the build.

## Regenerating pages

All inner pages, brand pages, category pages, blog pages and `sitemap.xml`
are generated from `tools/build_pages.py` (+ `tools/fragments/`,
`tools/articles/`). After any edit there or to the shared header/footer in
`index.html`, run:

```bash
python3 tools/build_pages.py
```
