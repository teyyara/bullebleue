# La Bulle Bleue — Chalon-sur-Saône

Responsive French-language static website for La Bulle Bleue, an initiative of APAiL.

## Run locally

Static HTML, CSS and vanilla JavaScript. No package manager, build step, remote fonts, analytics, tracking, backend, CMS or paid dependencies.

    python3 -m http.server 8080

## Site map

- `index.html` — sticky illustrated background with three successive scroll chapters.
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

The same original local SVG drawing stays sticky behind three text chapters as visitors scroll. JavaScript uses IntersectionObserver only as progressive enhancement. All content is visible by default, and reduced-motion users do not receive hidden story states or scroll transitions. The sticky experience still requires current-browser visual review.

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

No identifiable-participant Facebook photographs are used in the current Loop 012 pages. The owner-reported asset permission is recorded in the asset register.

## Validation

    python3 tests/validate_site.py
    node --check script.js
    node --check tests/test_menu.js
    node tests/test_menu.js

A passing source or unit test does not replace browser rendering, accessibility inspection or owner acceptance. No production deployment has been performed or authorized.
