# La Bulle Bleue — Chalon-sur-Saône

A lightweight, responsive French-language website for **La Bulle Bleue**, the welcome-and-connection initiative run by the association **APAiL** in Chalon-sur-Saône.

## Run locally

The site is plain HTML, CSS and JavaScript. It has no package manager, framework, build step, remote font, analytics, tracking pixel or paid dependency.

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080` in a browser.

## Website structure

- `index.html` — one-page website, semantic sections, SEO metadata and organization JSON-LD.
- `styles.css` — responsive visual system, custom CSS illustrations, keyboard focus and reduced-motion support.
- `script.js` — accessible mobile navigation, current footer year and progressive scroll-reveal enhancement.
- `assets/` — local SVG favicon and original editorial illustrations (hero, games, garden, discovery, culture, solidarity).
- `tests/validate_site.py` — dependency-free structural/content checks.
- `tests/test_menu.js` — dependency-free keyboard and mobile-menu interaction regression tests.
- `evidence/` — research dossier, project contract, assumptions, decisions, validation outputs and screenshots.
- `.aeos/` and `AEOS_STATUS.md` — project progression state and boss-facing status.

## Content and publication safeguards

The intended organization is APAiL's **La Bulle Bleue** in Chalon-sur-Saône, not the unrelated theatre company with a similar name. Public reporting describes an association-led welcome space for children from age 6, teenagers and adults. Recent public-post examples include games, garden moments, archery, accessibility discovery, outings and music. Dated examples are not a permanent or guaranteed programme.

The published email `apail@live.fr` is included as the primary contact route. The exact activity address differs between older and newer public sources, and the available opening times are historical. The website therefore does **not** publish a street address or weekly schedule; it asks visitors to confirm the venue, current dates and times directly with the association.

The redesign uses original SVG illustrations. They are labelled as illustrations and do not depict real APAiL participants or specific events. Social/press photographs are not reused until rights and consent are documented.

No application form is present. The site does not ask visitors to disclose diagnoses, health details or other sensitive information online. No testimonials, phone number, pricing, registration guarantee or medical promise has been invented.

## Deployment

No production deployment has been performed or authorized in this loop. No domain or hosting target was supplied. The site is static and should be deployable by a static hosting provider, but production headers, canonical URL, sitemap, host configuration and production verification remain pending identification of the actual deployment target.

## Local validation

```bash
python3 tests/validate_site.py
node --check script.js
node tests/test_menu.js
```

The evidence folder distinguishes candidate-level browser checks from production checks. Chromium was exercised in-memory through Playwright because the sandbox blocks direct navigation to localhost and file URLs. This does not count as a hosted production smoke test.
