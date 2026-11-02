# La Bulle Bleue — Chalon-sur-Saône

Responsive French-language information website for La Bulle Bleue, an initiative of APAiL in Chalon-sur-Saône.

## Run locally
The site uses static HTML, CSS and vanilla JavaScript. No package manager, build step, remote fonts, analytics, tracking or paid dependencies are required.

    python3 -m http.server 8080

## Content source
The current website is grounded in `Bulle_Bleue_APAiL_contenu_facebook.md`, a user-supplied extraction of the exact page https://www.facebook.com/p/Bulle-Bleue-APAiL-100066715807933/ made on 2 November 2026. It includes page information and text posts from May 2023 to October 2026. The website curates the material rather than reproducing all 816 lines.

The page covers:
1. Accueil and purpose.
2. Publics and the published Wednesday/Saturday times.
3. Activities observed in the posts.
4. Selected dated highlights from September/October 2026.
5. APAiL history, solidarity work, volunteer group and organisations cited.
6. Contact, venue and garden access.

## Factual boundaries
Wednesday 14:30 / Saturday 15:00 and the 30 Rempart Saint-Vincent address/garden access via rue Leriche are taken from the page presentation dated 11 March 2024 and the supplied extraction. The site shows that source context and asks visitors to confirm before travelling.

Activities are examples, not a fixed weekly programme. News items keep their dates. Burkina Faso/Morocco projects are reported history, not claims that every project is still active. Organisations are described as cited in posts, not necessarily as permanent partners.

The published email `apail@live.fr` is retained from prior public-source research; deliverability has not been tested. The official logo and documentary photos have not been added; the BB monogram remains provisional. No participant names or photographs are published.

## Validation
    python3 tests/validate_site.py
    node --check script.js
    node --check tests/test_menu.js
    node tests/test_menu.js

No production deployment has been performed or authorized.
