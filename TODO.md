# Bulle Bleue - APAiL — Owner feedback and production TODO

**Last updated:** 26 November 2026  
**Repository:** teyyara/bullebleue · main

## Loop 032 — Mobile accessibility and calmer presentation
- [x] Move the Accessibility control into the mobile header beside Menu; remove the fixed bottom overlay on phones.
- [x] Put Accessibility first in keyboard order immediately after “Aller au contenu”; retain visible focus and Escape/focus restoration.
- [x] Give header and footer logo links the accessible name “La Bulle Bleue, APAiL, accueil”.
- [x] Keep the homepage mural in the opening composition only; it no longer stays fixed over later sections.
- [x] Make “Les sorties” an ordinary text list rather than non-functional button-like pills.
- [x] Prevent the homepage title from overflowing with increased letter spacing, dyslexia font or very large text settings.
- [x] Increase small labels and footer text to at least 16 px and remove unnecessary all-caps styling.
- [x] Use the predictable “Nous contacter” label for general contact actions and remove arrows from internal links.
- [x] Add Open Graph image metadata for social previews using the owner-selected group photograph.
- [x] Remove decorative bubbles, pale geometric backplates and the outings flourish in “Mode calme” while preserving content and documentary photos.
- [x] Clip the mobile mural at the viewport edge under increased text spacing and reduce excess vertical gaps between homepage sections.
- [x] Create WebP derivatives for 17 rendered raster assets and measure the result: 3,056,544 bytes to 1,754,162 bytes (42.6% smaller); original uploads retained.
- [ ] Complete screen-reader and real-device checks with people who use the relevant accessibility settings.

## Loop 031 — Real brand assets across all routes
- [x] Replace the generic CSS-dot wordmark with the association's supplied transparent logo in the shared header and footer on all twelve routes.
- [x] Switch every route from the older placeholder favicon to the current Bulle Bleue bubble favicon.
- [x] Add static checks for logo/favicon paths and browser checks that both logo instances load successfully.
- [ ] Inspect desktop and mobile captures for logo sizing, crop and spacing; verify Chromium, Firefox and WebKit.


## Loop 030 — Anchor and accessibility clarity
- [x] Correct the Accessibility page so it does not claim the floating control stays bottom-left on phones.
- [x] Add sticky-header clearance to in-page anchor destinations.
- [x] Respect the operating system's reduced-motion preference for smooth scrolling, including when JavaScript is unavailable.
- [x] Add browser coverage for anchor placement and reduced-motion scrolling.
- [ ] Inspect refreshed screenshots and confirm all three browser engines pass.


## Loop 029 — Site-wide visual cleanup
- [x] Replace the stretched flex footer on all twelve routes with a structured brand area and grouped navigation.
- [x] Add clear Découvrir, Participer and Informations utiles link groups, an email action, and a compact copyright/location row.
- [x] Remove the repeated per-section “Écouter” pills; retain full-page speech playback in the Accessibility panel.
- [x] Add static and responsive regression checks for the shared footer and uncluttered reading flow.
- [ ] Complete the refreshed Chromium/Firefox/WebKit responsive run and inspect the new screenshots.
- [ ] Merge the reviewed, green pull request into main as requested; no manual Vercel deployment.


## Loop 027 — Page-by-page factual accuracy audit
- [x] Removed the three empty testimonial prompts; kept only Miette's supplied quotation and attribution.
- [x] Corrected the volunteer-group name to “les Bleuettes”.
- [x] Marked Wednesday 14h30 / Saturday 15h as published information that must be reconfirmed before travel.
- [x] Corrected the Chalon dans la Rue anniversary context: the 16 October 2026 launch began preparations for the 40th anniversary in 2027.
- [x] Narrowed the Association Valentin Haüy story to the ten members' reported activities (playing, moving and writing without sight).
- [x] Disclosed the conflicting 2024 and 2025 venue references instead of presenting either street address as current.
- [x] Corrected the JOAFE declaration/publication date distinction and identified Vercel as the deployment/hosting platform.
- [ ] Confirm all current opening hours and the visitor entrance with APAiL.
- [ ] Have APAiL validate the legal notices, registered office, publication manager and hosting wording before production.
- [ ] Run the updated structural, JavaScript and three-engine responsive checks; inspect refreshed screenshots.

## Loop 026 — Owner mockup v3 refinement (preview branch)
- [x] Inspected the complete `bulle-bleue-site-v3.zip` reference, including all mockup pages, styles, scripts, local typefaces and image assets.
- [x] Integrated the mockup's mural, local fonts, warm/readable type hierarchy, palette and accessibility options in the v3 candidate already present on `main`.
- [x] Removed the duplicate “Nous contacter” link from all 12 routes, keeping a single CTA and preserving the active state on Contact.
- [x] Restored three distinct organic bubble silhouettes for the Actualités teasers, retaining their original links, content and images.
- [x] Corrected the image regression rule so text-led utility pages are not required to contain decorative photos.
- [x] Kept owner-confirmed session times (Wednesday 14h30, Saturday 15h), the genuine Miette quotation, existing association stories and all legal/content caveats.
- [ ] Finish Chromium/Firefox/WebKit and structural validation on the preview branch; inspect the generated screenshots.
- [ ] Receive final association-owner visual approval before any merge or production deployment.

## Loop 025 — Cross-browser responsive regression
- [x] Made the existing Playwright browser suite selectable between Chromium, Firefox and WebKit.
- [x] Updated CI to install and run all three engines against all nine public pages at 320, 390, 768, 1024 and 1440 px.
- [x] Kept all existing layout, image, navigation, sticky-story, reduced-motion and browser-error assertions active in each engine.
- [x] Corrected the computed-style test to return explicit properties consistently across browser engines.
- [x] Added a diagnostic retry to the local route response check; a persistent non-200 response still fails.
- [x] Python, Node and all three Playwright engine suites PASS: 135 page/viewport combinations, with no overflow, failed local image, unexpected request or browser error.
- [x] Captured 30 Chromium screenshots; manually reviewed the About desktop and mobile views.

## Loop 024 — About page and sitewide detail polish
- [x] Reworked all seven “Jouer, créer, découvrir” activity topics as clearly spaced cards with even gutters and readable line wrapping.
- [x] Removed the old divider behind the About activity cards.
- [x] Changed the responsive activity grid to two columns on wider screens and one column on mobile.
- [x] Removed fixed document-level decorative dots that appeared detached from content on long pages; retained intentional component-level decoration.
- [x] Added structural and Playwright assertions for the About layout and page-wide background treatment.
- [x] Python, Node and Playwright PASS across nine pages × five viewport widths (45 combinations); 30 screenshots captured and six manually reviewed.

## Loop 023 — Fine design polish: spacing, numbering and alignment
- [x] Removed the decorative 01/02 labels beside the About page audience groups; preserved the factual 1995 and 2021 timeline dates.
- [x] Restyled the two audience groups as consistent cards on desktop/tablet and a clean single-column stack on mobile.
- [x] Centered the capped-width Adhérer closing note and legal-information reading column.
- [x] Aligned the Contact page's two main cards and their lower information callouts.
- [x] Aligned the Adhérer email button and companion contact link on a shared desktop baseline; preserved natural mobile stacking.
- [x] Refined breadcrumb spacing, page-section rhythm, legal definition-list spacing, audience-card typography and Actualités card metadata/title alignment.
- [x] Added structural and responsive browser assertions; Python, Node and Playwright PASS across nine pages × five viewport widths.
- [x] Captured 30 desktop/mobile screenshots across all pages; manually reviewed seven relevant views.


## Loop 022 — Transparent character cut-outs from drawings 6–9
- [x] Created 20 individually addressable transparent SVG character cut-outs: six from drawing 6, four clearly drawn figures from drawing 7, one from drawing 8 and nine from drawing 9.
- [x] Each cut-out uses a hand-traced SVG clip path over the corresponding untouched original JPEG; the supplied drawing pixels are preserved rather than redrawn.
- [x] Excluded the pasted football photograph and cropped edge fragment in drawing 7 from the drawn-character set.
- [x] Positioned the individual figures in the sticky homepage story artwork with transparent backgrounds and no paper-card frame.
- [x] Kept all four complete original drawings in the Jouer/créer collage.
- [x] Added structural and browser assertions; Python, Node and Playwright all PASS across nine pages × five viewport widths.
- [x] Uploaded 18 screenshots and manually reviewed seven relevant desktop/mobile captures.

## Loop 021 — Restore validator-compatible owner authorization wording
- [x] Keep the explicit project record that the association owner has verbally authorized use of the supplied images for the public website.
- [x] Restore the exact phrase “verbally authorized” required by `tests/validate_site.py`; this is a documentation/validator compatibility correction only.

## Loop 020 — True organic Actualités bubbles
- [x] Three distinct smooth Bézier bubble silhouettes replace rounded-rectangle-like article surfaces.
- [x] Matching organic contours applied to all three illustration frames.
- [x] Titles, dates, categories, summaries and CTAs remain readable.
- [x] Desktop Illustration labels moved upper-right; mobile labels remain lower-right.
- [x] Dated stories/routes and separate undated community strip preserved.
- [x] Source/browser assertions added for unique card/image contours and desktop badge placement.
- [x] Final desktop/mobile Actualités screenshots reviewed.

## Loop 019 — Homepage story, voices and art direction
- [x] Bulle Bleue - APAiL identity, owner welcome and Se retrouver copy; no chapter counters.
- [x] Selected Se retrouver group photo, Wednesday 14h30 / Saturday 15h and outing information.
- [x] Ils en parlent after Se retrouver; only Miette's real AG 2026 quote is attributed.
- [x] Other testimonial cards remain prompts; no invented quotes or face photos.
- [x] Four-drawing Jouer/créer collage with horizontal mobile swipe.
- [x] Drawings 6–9 added to scroll-reactive artwork; merged poster image used as subdued background texture only.
- [x] Derrière la Bulle copy and volunteer/membership actions.
- [x] Fredoka, Atkinson Hyperlegible and Caveat applied.
- [x] Eleven assets/posts photos stay on secondary pages; homepage uses only Se retrouver and gathering documentary photos.
- [x] The association owner has verbally authorized use of the supplied images for the public website.

## Still open
- [ ] Genuine young-person, parent and volunteer testimonials if the owner wants prompts replaced.
- [ ] Final association-owner visual/content acceptance.
- [ ] Confirm registered office, publication manager and hosting provider.
- [ ] Confirm membership fee, procedure, forms and renewals.
- [ ] Confirm current venue/location; weekly times came from owner feedback.
- [ ] Test apail@live.fr deliverability without an unsolicited message.
- [x] Playwright Chromium, Firefox and WebKit responsive matrix across all nine pages and five viewport widths.
- [ ] Verify on native macOS/iOS Safari; complete screen-reader, physical-device, Lighthouse, ZAP and hosted checks.
- [ ] No production deployment until explicitly authorised and hosting confirmed.
