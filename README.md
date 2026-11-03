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

## Logo-derived visual identity

The transparent logo at `assets/logo final.png` is used in every page header and footer. Its palette was sampled directly in Loop 011 from visible pixels in the original 1052×1024 RGBA image. Transparent pixels were excluded; an alpha-weighted eight-cluster analysis was run on a deterministic sample of 120,000 visible pixels. Shares below are approximate portions of visible pixels; each hex is the nearest actual source pixel to its cluster centre.

| Representative colour | Hex | Approx. share |
|---|---|---:|
| Deep navy | `#06195E` | 8.1% |
| Cobalt | `#1642A5` | 14.9% |
| Primary blue | `#1C60CF` | 23.3% |
| Clear blue | `#2084DE` | 21.4% |
| Sky blue | `#4EABEC` | 7.7% |
| Steel blue | `#587ABA` | 4.6% |
| Icy blue | `#9DC0EA` | 13.2% |
| Pale highlight | `#D3DEF0` | 6.8% |

The reading surfaces `#F3F7FE` and `#FCFDFF` are near-white tints derived from the pale logo highlights, not literal sampled logo colours. The previous warm clay/ochre palette has been retired. The same colour direction is reflected in the favicon, page headers, backgrounds, links, cards, focus states and buttons.

## Source and factual boundaries
The primary source is `Bulle_Bleue_APAiL_contenu_facebook.md`, the user-supplied extraction of https://www.facebook.com/p/Bulle-Bleue-APAiL-100066715807933/, dated 2 November 2026.

The Wednesday 14:30 / Saturday 15:00 times and the 30 Rempart Saint-Vincent address/garden access via rue Leriche are transcribed from the Facebook presentation dated 11 March 2024. Visitors are asked to confirm before travelling.

Activities are examples, not a fixed weekly programme. News retains original dates. Burkina Faso/Morocco projects are reported history, not claims that each remains active. Organisations are cited in posts, not necessarily permanent partners. The published email `apail@live.fr` comes from prior public-source research; deliverability is untested.

Four close-up activity photographs with no identifiable faces are used on the homepage and activities page. Other supplied photographs that show recognisable participants, including children, remain out of the public layout pending confirmation of any image-specific participant/guardian releases. The user reports that the owner authorised use of Facebook-page assets.

## Validation
    python3 tests/validate_site.py
    node --check script.js
    node --check tests/test_menu.js
    node tests/test_menu.js

No production deployment has been performed or authorized.
