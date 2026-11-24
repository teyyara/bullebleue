## Delivered in Loop 026 — owner mockup v3 refinement
- The current site was found to already contain the full first-pass v3 mockup implementation. This loop makes targeted polish changes rather than rebuilding the site.
- The complete mockup archive was inspected. Its mural, locally hosted fonts, navy/blue-grey palette and accessibility direction are already integrated in the v3 candidate.
- Removed the duplicate Contact navigation item from all twelve routes. The Contact page's current-page marker remains on the single orange CTA.
- Replaced the Actualités teasers' standard rectangular treatment with three distinct organic bubble contours and soft pale surfaces.
- Updated regression coverage so text-led utility routes do not need decorative images, and so unique navigation destinations and organic card styling remain protected.
- Kept owner-confirmed Wednesday 14h30 and Saturday 15h sessions; no FALC certification, full WCAG audit, legal office or membership terms are invented.
- Changes are isolated on `loop026-mockup-v3-polish`; no merge or manual deployment has been performed.
- Automated verification and screenshot review are pending.

# AEOS Status — Bulle Bleue - APAiL

**Active keyphrase:** make a full website for: Bulle Bleue à Chalon-sur-Saône  
**Run ID:** bullebleue-20261102-001  
**Rulebook:** AEOS v3  
**Current loop:** LOOP 026  
**Candidate:** bullebleue-loop-026-mockup-v3-polish  
**Repository:** teyyara/bullebleue · main  
**Implementation checkpoint:** 1b7fd73d494321db421c065470226452d3b1d797  
**Status:** PREVIEW BRANCH IMPLEMENTED — AUTOMATED VERIFICATION PENDING

## Delivered in Loop 025
- Extended the responsive Playwright suite so the same browser checks can run in Chromium, Firefox and WebKit using the `BROWSER_ENGINE` selector.
- Updated GitHub Actions to install all three engines and run the full suite separately for each engine; the Chromium run retains the 30-image visual-review artifact while the Firefox/WebKit runs provide independent runtime coverage.
- Made a computed-style assertion engine-neutral and added one diagnostic retry to the local HTTP route check; persistent non-200 responses still fail.
- Python structural validator and Node menu/story/reduced-motion tests: **PASS**.
- Chromium: **PASS**, nine pages × five viewports (45 combinations).
- Firefox: **PASS**, nine pages × five viewports (45 combinations).
- Playwright WebKit: **PASS**, nine pages × five viewports (45 combinations).
- Combined responsive browser matrix: **135 page/viewport combinations**, with no horizontal overflow, missing local images, failed requests or browser/page errors.
- Screenshot artifact: [13511744695](https://github.com/teyyara/bullebleue/actions/runs/42237625691/artifacts/13511744695), 30 Chromium screenshots. About desktop and mobile captures manually opened and reviewed.

## Important coverage boundary
Playwright WebKit on the Ubuntu CI runner is Safari-family engine coverage, not a test of native Safari on macOS or iOS. Native Safari, physical mobile devices, manual screen-reader testing, Lighthouse, ZAP and hosted checks remain open.

## Next actionable TODO
Continue with owner-dependent items only when APAiL supplies or confirms missing facts and genuine testimonial material. Do not invent testimonials, legal details, membership terms or venue information.

## Delivered in Loop 024
- Rebuilt the seven topics under “Jouer, créer, découvrir” as roomy, individually bordered cards, with a balanced two-column desktop layout and a single-column mobile stack.
- Removed the leftover horizontal divider from the About activity list; all seven activity labels and surrounding owner-supplied copy remain unchanged.
- Removed the fixed-position decorative dots from the whole-document background so they no longer drift beside unrelated content on long pages. Decorations attached to illustrations, cards and sections remain intact.
- Added structural and browser regression checks for the seven About topics, responsive grid, card gutters, divider removal and page-background treatment.
- Captured 30 screenshots across the nine public page routes and manually inspected six representative desktop/mobile views.

## Verification
- GitHub Actions **PASS**: [run 42233632591](https://github.com/teyyara/bullebleue/actions/runs/42233632591).
- Python structural validator: **PASS**.
- Node syntax/menu/story/reduced-motion tests: **PASS**.
- Playwright Chromium: **PASS** — nine pages × five viewports (45 combinations); no horizontal overflow, failed local images, failed requests, page errors or console errors. New responsive About-card and document-background assertions passed.
- Screenshot artifact: [13508939018](https://github.com/teyyara/bullebleue/actions/runs/42233632591/artifacts/13508939018), 30 screenshots. Six captures manually opened and reviewed: About desktop/mobile, Actualités desktop, Contact desktop, Adhérer desktop and Mentions légales mobile.

## Next actionable TODO
Continue with owner-dependent items only when the association supplies or confirms the missing facts and genuine testimonial material. Do not invent testimonials, legal details, membership terms or venue information.

## Delivered in Loop 023
- Removed the decorative “01” and “02” sequence labels from the About page audience groups; the historical 1995 and 2021 timeline milestones remain as factual dates.
- Reworked the audience groups into clean, evenly spaced cards at desktop/tablet and a single-column stack on mobile.
- Centered the capped-width Adhérer closing note and legal-information column within their page shells.
- Made Contact's primary and location panels equal-height flex columns and aligned their lower information callouts; kept the email action intrinsic-width.
- Aligned the Adhérer email button and companion contact link to a shared bottom baseline on desktop, with natural stacked behaviour on mobile.
- Tightened breadcrumb-to-title spacing, section vertical rhythm, audience-card type spacing, legal definition-list spacing, and Actualités metadata/title baselines.
- Added structural and responsive-browser assertions. Expanded visual capture to 30 screenshots, including all three article routes and Adhérer, Contact and Mentions légales at desktop/mobile sizes.

## Verification
- GitHub Actions **PASS**: [run 42229730798](https://github.com/teyyara/bullebleue/actions/runs/42229730798).
- Python structural validator: **PASS**.
- Node syntax/menu/story/reduced-motion tests: **PASS**.
- Playwright Chromium: **PASS** — nine public pages × five viewport widths (45 combinations); no horizontal overflow, failed image loads, page errors or console errors. Centering, number removal, Contact card alignment and Adhérer action baseline assertions passed.
- Screenshot artifact: [13507472174](https://github.com/teyyara/bullebleue/actions/runs/42229730798/artifacts/13507472174), 30 screenshots. Seven relevant desktop/mobile captures were manually opened and reviewed.

## Next actionable TODO
Collect authentic young-person, parent and volunteer testimonials if the owner wants the current invitation prompts replaced. No testimonial text has been invented.

## Other open items
- Obtain final association-owner visual/content acceptance.
- Confirm registered office, publication manager, hosting provider, membership terms and current venue.
- Test apail@live.fr deliverability without an unsolicited message.
- Playwright Firefox and WebKit have passed in Loop 025. Verify on native macOS/iOS Safari; complete screen-reader, physical-device, Lighthouse, ZAP and hosted security/performance checks.

No production deployment has been performed or authorised. Hosting remains unconfigured.

## Progression control
Loop 025 is checkpointed on main. Exactly one standalone CONTINUE authorises LOOP 026.
