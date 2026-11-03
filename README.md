# La Bulle Bleue — Chalon-sur-Saône

Responsive French-language multi-page website for La Bulle Bleue, an initiative of APAiL.

## Run locally
Static HTML, CSS and vanilla JavaScript. No package manager, build step, remote fonts, analytics, tracking or paid dependencies.

    python3 -m http.server 8080

## Site map
- `index.html` — concise homepage and navigation hub.
- `la-bulle.html` — audiences, published session times and first-contact context.
- `activites.html` — activity examples.
- `actualites.html` — selected dated updates.
- `apail.html` — APAiL history, reported solidarity work, volunteers and organisations cited in posts.
- `contact.html` — email, Facebook, address, garden access and confirmation notes.

Every page shares the same navigation and footer. The active page uses `aria-current="page"`; the compact menu supports keyboard interaction.

## Source and factual boundaries
The primary source is `Bulle_Bleue_APAiL_contenu_facebook.md`, the user-supplied extraction of https://www.facebook.com/p/Bulle-Bleue-APAiL-100066715807933/, dated 2 November 2026.

The Wednesday 14:30 / Saturday 15:00 times and the 30 Rempart Saint-Vincent address/garden access via rue Leriche are transcribed from the Facebook presentation dated 11 March 2024. Visitors are asked to confirm before travelling.

Activities are examples, not a fixed weekly programme. News retains original dates. Burkina Faso/Morocco projects are reported history, not claims that each remains active. Organisations are cited in posts, not necessarily permanent partners. The published email `apail@live.fr` comes from prior public-source research; deliverability is untested.

The transparent official logo supplied by the user is stored at `assets/logo final.png` and is used in every page header and footer. Four close-up activity photographs with no identifiable faces are used on the homepage and activities page. Other supplied photographs that show recognisable participants, including children, remain out of the public layout pending confirmation of any image-specific participant/guardian releases. The user reports that the owner authorised use of Facebook-page assets. The exact logo colour palette has not yet been sampled because the 1 MB PNG was not returned by the available repository file reader; the current CSS colour tokens therefore remain provisional and must not be described as logo-extracted.

## Validation
    python3 tests/validate_site.py
    node --check script.js
    node --check tests/test_menu.js
    node tests/test_menu.js

No production deployment has been performed or authorized.
