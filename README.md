# Bulle Bleue - APAiL — Chalon-sur-Saône

Responsive French-language static website for La Bulle Bleue, an initiative of APAiL.

## Run locally

Static HTML, CSS and vanilla JavaScript. No package manager, build step, analytics, tracking, backend, CMS or paid dependencies. The owner-selected typefaces load through the free Google Fonts CSS service, with local system fallbacks.

    python3 -m http.server 8080

## Site map

- `index.html` — the homepage story with supplied mural artwork, kept at the top rather than fixed over later reading sections; owner-authored welcome, Se retrouver, Ils en parlent, Jouer/créer and DERRIÈRE LA BULLE sections; the owner-supplied se retrouver.jpg group photo and gathering.jpeg closing photograph. The eleven assets/posts photographs remain on Qui sommes-nous and Actualités, not the homepage.
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

The supplied mural and character artwork appear in the opening homepage composition only; the mural no longer remains fixed over later sections. The four complete original drawing sheets remain in the Jouer/créer collage, which scrolls horizontally on mobile. The “Mode calme” setting removes background bubbles and geometric backplates without hiding page content or documentary photographs. The cut-outs use hand-traced SVG clip paths over the original local JPEG pixels; they are not redraws or generated replacements. The site uses Fredoka 600 for headings, Atkinson Hyperlegible 400/700 for reading text and Caveat 600 for handwritten accents. Google Fonts is the only free remote font service; all illustration and documentary images remain local. The eleven assets/posts photographs stay off the homepage: eight remain on Qui sommes-nous and three in an undated strip on Actualités. Only se retrouver.jpg.jpeg and gathering.jpeg are documentary photos on the homepage. The association owner supplied the photo set and verbally authorised its visible use on the website, as relayed by the project user on 2026-11-05. JavaScript remains progressive enhancement; no-JavaScript and reduced-motion content stays visible.

## Actualités card art direction

The three dated story cards use distinct, smooth organic bubble silhouettes with matching illustration frames rather than rounded-rectangle surfaces. “Illustration” labels stay safely inside their frames at desktop and mobile. Their visual treatment becomes simpler in “Mode calme”.

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

Membership fees, current membership forms and process are not evidenced; the Adhérer page asks visitors to contact APAiL for current information. The legal page now records the association denomination published in the JOAFE modification notice of 27 February 2019 and the public RNA/SIREN identifiers. The registered-office address remains deliberately unconfirmed: the JOAFE notice and municipal directory list 14 quai Gambetta, while a 2026 SIRENE-derived record lists 14 boulevard de la République. The publication responsible person and actual hosting provider remain unknown. The Mentions légales page is still incomplete and must be validated by APAiL before publication.

The homepage does not publish any assets/posts photographs. Eight appear in the Qui sommes-nous activity gallery and three in an explicitly undated image strip on Actualités; gathering.jpeg remains the only documentary photograph on the homepage, beside the closing section. The association owner supplied all images and verbally authorised their visible use on the website; this is recorded as the project's permission basis.

## Validation

Run the structural, Node and browser checks locally:

    python3 tests/validate_site.py
    node --check script.js
    node --check tests/test_menu.js
    node tests/test_menu.js
    python -m pip install "playwright==1.57.0"
    python -m playwright install chromium
    python tests/test_browser.py

The read-only GitHub Actions workflow at `.github/workflows/quality.yml` runs these checks on pushes and pull requests to `main`; it has no deployment step. The Playwright suite checks all nine pages at 320, 390, 768, 1024 and 1440 px, including images, overflow, keyboard navigation, sticky-story transitions, reduced motion and no-JavaScript fallback. Its visual-review screenshots wait for the relevant story text transition and explicitly decode lazy images before capture; it records the homepage story and closing photograph plus desktop/mobile captures of Actualités and Qui sommes-nous.

A committed workflow or test is not itself a passing result: check the actual workflow run before treating the Python or browser checks as passed. A passing source/unit test does not replace manual accessibility inspection or owner acceptance. No production deployment has been performed or authorized.

## Current owner feedback and TODO

The playful bubble-style art direction, organic Actualités shapes and nine-drawing homepage collage are tracked in [TODO.md](TODO.md). The homepage stays light, while all eleven assets/posts photographs appear on the two relevant secondary pages under the association owner's verbal website-use authorization.


## Quality-gate maintenance

The structural validator checks that the TODO records the association owner's verbal website-image authorization using the literal phrase “verbally authorized”. Keep that exact wording when editing the checklist; it documents the same owner-provided permission basis and is also a regression assertion.


## Accessibility toolbar and social sharing

The Accessibility control is first in keyboard order after the skip link. On phones it sits in the shared header beside Menu instead of covering the reading area; on desktop it remains available at the lower left. General contact links use the predictable label “Nous contacter”. Open Graph image metadata uses the owner-selected group photograph through the public repository image URL. Photo-to-WebP conversion remains an open optimization item pending binary-safe conversion and size checks.

Read-aloud uses only the on-device neural French Pocket TTS voice. Its first-use download (approximately 134 MB) starts automatically as soon as a page opens; cached model files are reused on later visits when the browser retains them. Visitors can hear a short sample or the full page. Page text is synthesized locally and is not sent to a speech API.

The neural reader uses Pocket TTS teacher-forced continuation across 25-token text chunks: the previous raw text fragment and generated latent frames are passed forward, while Mimi is warmed with the previous chunk's final 12 frames. Original comma/colon punctuation is retained in the next continuation context; a comma is no longer rewritten as a full stop before the model receives the following words. Text segmentation follows Kyutai's boundary handling, including decimal numbers, titles and closing quotes. To avoid audio underruns on devices whose one-thread inference is slower than real-time playback, the reader collects all PCM packets for the selected passage, joins them into one audio buffer, and starts playback only after synthesis is complete. Automated checks cover continuation, punctuation preservation, latent packing, decoder-position advancement, automatic preload and single-buffer playback; physical-device listening remains necessary.
## Image delivery

The 17 raster assets rendered by the public pages now have WebP variants (3,056,544 bytes combined before, 1,754,162 bytes after; 42.6% smaller). Original supplied images remain available in the repository. The Open Graph sharing image deliberately remains JPEG for compatibility. Per-image measurements are in evidence/visual/webp-optimization-report.json.
