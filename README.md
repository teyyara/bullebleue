# La Bulle Bleue — Chalon-sur-Saône

A concise, responsive French-language editorial website for La Bulle Bleue, the local welcome and connection initiative run by APAiL in Chalon-sur-Saône.

## Run locally

The site uses plain HTML, CSS and vanilla JavaScript. It has no package manager, framework, build step, remote font request, analytics, tracking pixel or paid dependency.

    python3 -m http.server 8080

Then open http://localhost:8080 in a browser.

## Current page structure

The Loop 006 redesign contains five main sections:

1. Accueil — concise hero, audience and welcome statement.
2. Les activités — four short, numbered editorial activity rows.
3. L’accueil — brief welcome message and three first-contact steps.
4. L’APAiL — concise parent-association history.
5. Contact — email route, current venue/times caveat and Facebook link.

The previous dated social-mirror story mosaic, repeated approach/first-step/volunteer sections and generic illustrated activity cards have been removed to shorten the page and improve hierarchy.

## Visual identity status

The current identity is provisional, not an official APAiL brand reproduction. It uses a restrained deep mineral/ink blue, warm paper ivory, muted teal, clay and aged ochre palette informed by public descriptions of welcome, listening, solidarity and sharing. No official HEX palette or type manual was verified.

The typographic BB monogram is a temporary mark. The user supplied the exact Bulle Bleue - APAiL Facebook page at https://www.facebook.com/p/Bulle-Bleue-APAiL-100066715807933/, and that URL is linked in the contact panel and footer. Facebook page/profile-image retrieval was blocked in the current research environment. A FindGlocal mirror surfaced another page ID (100620708811103), which does not match the supplied ID (100066715807933); its logo or images are not treated as belonging to the supplied page. No participant or press photograph is reused.

## Factual boundaries

Public reporting describes La Bulle Bleue as an APAiL initiative launched in 2021, with children from age 6, teenagers and adults among the audience. APAiL was founded in 1995. The website keeps the exact activity venue and current weekly hours unpublished because available public sources conflict or are historical. Visitors are asked to confirm current details directly with the association.

The site uses apail@live.fr as a historically published contact email; deliverability has not been tested. It does not request diagnoses or other sensitive information.

## Files

- index.html — one-page content, semantics, metadata and Organization JSON-LD.
- styles.css — editorial palette, texture, typographic hierarchy and responsive layout.
- script.js — keyboard-operable mobile navigation and footer year.
- assets/favicon.svg — local provisional favicon.
- assets/illustrations/ — previous original SVG illustrations retained in the repository archive; not referenced in Loop 006 page markup.
- tests/validate_site.py — dependency-free structural and content checks.
- tests/test_menu.js — dependency-free menu interaction regression.
- evidence/ — research, provenance, requirements, decisions and validation records.
- .aeos/ and AEOS_STATUS.md — progression state and checkpoint.

## Validation

    python3 tests/validate_site.py
    node --check script.js
    node --check tests/test_menu.js
    node tests/test_menu.js

Loop 006 was rendered in Chromium 144 with Playwright at 12 viewport widths. It was not hosted or deployed. Firefox, WebKit, Safari, manual screen-reader checks and hosted performance/security checks remain outstanding.

## Deployment

No production deployment has been performed or authorized.
