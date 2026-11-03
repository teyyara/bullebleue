# La Bulle Bleue — Chalon-sur-Saône

Responsive French-language static website for La Bulle Bleue, an initiative of APAiL.

## Run locally

Static HTML, CSS and vanilla JavaScript. No package manager, build step, remote fonts, analytics, tracking, backend, CMS or paid dependencies.

    python3 -m http.server 8080

## Site map

- `index.html` — sticky illustrated background with three successive scroll chapters, followed by two user-supplied activity photographs.
- `qui-sommes-nous.html` — La Bulle Bleue, its audience and activities, Les Bleuettes, APAiL history and reported solidarity work.
- `actualites.html` — three featured dated stories in editorial cards.
- `actualite-2026-10-26.html` — 26 October 2026, games at La Bulle Bleue.
- `actualite-2026-10-17.html` — 17 October 2026, Chalon dans la Rue.
- `actualite-2026-10-10.html` — 10 October 2026, discovery with Association Valentin Haüy.
- `adherer.html` — email-first request for current membership terms; no fee or process is invented.
- `contact.html` — email, Facebook and venue information with a source-date confirmation caveat.
- `mentions-legales.html` — draft legal page; missing association and hosting details require APAiL confirmation before publication.

The five primary navigation links are Accueil, Qui sommes-nous ?, Actualités, Adhérer and Nous contacter. Mentions légales appears in the shared footer. The former La Bulle, Activités and APAiL pages have been consolidated into Qui sommes-nous.

## Homepage motion and accessibility

The same original local SVG drawing stays sticky behind three text chapters as visitors scroll. Below it, a small gallery uses two user-supplied close-up photographs of shared tabletop activities; the photographs are not presented as dated event evidence. JavaScript uses IntersectionObserver only as progressive enhancement. All content is visible by default, and reduced-motion users do not receive hidden story states or scroll transitions. The sticky experience and new gallery still require current-browser visual review.

## News content and imagery

The three featured stories are sourced from the user-provided extraction of the exact Facebook page:

- 26 October 2026 — a full afternoon of games, including the kitchen.
- 17 October 2026 — the launch of the 40th anniversary of Chalon dans la Rue.
- 10 October 2026 — an experience with Association Valentin Haüy.

Each story has a dedicated article page. Local vector images are labelled as illustrations, not photographs of the specific events. The article's source note records the date and links to the Facebook page; no unverified individual post permalink is invented.

## Logo-derived visual identity

The transparent logo at `assets/logo final.png` is used in every page header and footer. Its palette was sampled directly in Loop 011 from visible pixels in the original 1052×1024 RGBA image. The main site and the Loop 012 story/news illustrations use the sampled blue family.

| Representative colour | Hex |
|---|---|
| Deep navy | `#06195E` |
| Cobalt | `#1642A5` |
| Primary blue | `#1C60CF` |
| Clear blue | `#2084DE` |
| Sky blue | `#4EABEC` |
| Steel blue | `#587ABA` |
| Icy blue | `#9DC0EA` |
| Pale highlight | `#D3DEF0` |

The reading surfaces `#F3F7FE` and `#FCFDFF` are documented near-white tints derived from the pale logo highlights, not literal sampled logo colours.

## Factual and legal boundaries

The primary content source is `Bulle_Bleue_APAiL_contenu_facebook.md`, the user-supplied extraction dated 2 November 2026. The 2024 venue and session information remains dated and must be confirmed by the association before travel.

Membership fees, current membership forms and process are not evidenced; the Adhérer page asks visitors to contact APAiL for current information. Legal association identity, registered-office address, publication responsible person and actual host details have not been supplied. The Mentions légales page is visibly marked as incomplete and must be completed and approved by APAiL before the site is published.

The homepage uses two close-up activity photographs from the supplied Facebook-page assets; no recognizable faces are visible in the selected frames. Group, children’s and other identifiable participant photographs remain unpublished until image-specific releases are documented. The owner-reported asset permission is recorded in the asset register.

## Validation

Run the structural, Node and browser checks locally:

    python3 tests/validate_site.py
    node --check script.js
    node --check tests/test_menu.js
    node tests/test_menu.js
    python -m pip install "playwright==1.57.0"
    python -m playwright install chromium
    python tests/test_browser.py

The read-only GitHub Actions workflow at `.github/workflows/quality.yml` runs these checks on pushes and pull requests to `main`; it has no deployment step. The Playwright suite checks all nine pages at 320, 390, 768, 1024 and 1440 px, including images, overflow, keyboard navigation, sticky-story transitions, reduced motion and no-JavaScript fallback. It uploads browser screenshots as a short-retention artifact.

A committed workflow or test is not itself a passing result: check the actual workflow run before treating the Python or browser checks as passed. A passing source/unit test does not replace manual accessibility inspection or owner acceptance. No production deployment has been performed or authorized.
