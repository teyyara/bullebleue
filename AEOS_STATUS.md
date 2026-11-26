## Delivered in Loop 039 — teacher-forced continuity across speech chunks
- Replaced independent chunk restarts with Pocket TTS continuation: the next chunk receives the previous chunk's text and generated latent frames.
- Warmed each fresh Mimi decoder state with the previous chunk's final 12 latent frames and advanced its decoder step counter before new audio is decoded.
- Used the 25-token continuation chunk budget and retained the rolling audio buffer from Loop 038.
- Added regression tests for BOS/latent sequence packing, prompt continuation, 16-step-per-latent Mimi position advancement and multi-sentence chunk sizing.
- Listen to a long page on a physical device to confirm the word-to-word flow and paragraph transitions; measure the extra continuation prefill on slower mobile hardware.

## Delivered in Loop 038 — continuous neural speech playback
- Buffered a rolling 2.25 seconds of generated Pocket TTS audio before playback and joined small inference packets into larger Web Audio buffers.
- Schedule queued buffers continuously rather than starting each model packet as soon as it arrives; stop/cancel still halts scheduled audio.
- Added a simulated delayed-packet browser test that asserts adjacent scheduled blocks have no silence between them.
- Corrected the accessibility fallback visibility assertion to match the neural-default selection.
- Physical-device listening on a long page remains necessary to confirm that the buffering reserve is sufficient on older/slower devices.

## Delivered in Loop 037 — neural French reader as the default
- Changed the accessibility reader's initial selection from the mechanical eSpeak NG voice to the on-device neural French Pocket TTS voice.
- Kept the approximately 134 MB model/runtime download disclosed and deferred until the visitor starts reading.
- Preserved eSpeak NG as an explicit lightweight fallback and made the reset control restore the neural voice selection.
- Added browser assertions for the default voice selection, first-use download disclosure, fallback selection and reset behaviour.
- Physical-device listening and older-mobile performance checks remain pending; automated tests do not establish subjective voice quality.

## Delivered in Loop 031 — real brand assets across all routes
- Replaced the generic CSS-dot symbol with the association's supplied bubble emblem and retained a clear “Bulle Bleue / APAiL” wordmark beside it in the shared header and footer on all twelve routes.
- Updated each route to use the current bubble favicon from `/assets/favicon.svg`.
- Added static path checks and browser checks that both emblems load and the wordmark remains readable.
- Cross-browser visual verification pending.

## Delivered in Loop 031 — real brand assets across all routes
- Replaced the generic CSS-dot logo with the supplied association PNG in the shared header and footer across all twelve routes.
- Updated each route to use the current bubble favicon from `/assets/favicon.svg`.
- Added static assertions for shared logo/favicon paths and browser assertions that both logo images load.
- Responsive visual review and cross-browser validation pending.

## Delivered in Loop 030 — anchor and accessibility clarity
- Updated the Accessibility page location note to match both desktop and phone layouts.
- Added a consistent scroll offset so in-page links do not land underneath the sticky header.
- Added a CSS reduced-motion fallback for smooth scrolling that also works without JavaScript.
- Added browser regression checks for anchor clearance and reduced-motion behavior.
- Validation and refreshed screenshots pending.

## Delivered in Loop 029 — site-wide visual cleanup
- Replaced the stretched footer on all twelve routes with a structured brand area and grouped discovery, participation, and accessibility/legal navigation.
- Added a clear email action, responsive link columns, and a compact copyright/location row.
- Removed repeated inline audio controls after every section heading; full-page speech playback remains available from the Accessibility panel.
- Added structural and responsive regression checks for the shared footer and reading flow.
- Browser validation and refreshed screenshots pending.
- No merge or manual deployment yet.

## Delivered in Loop 027 — factual accuracy audit
- Removed uncollected testimonial prompts from the homepage; only Miette's sourced quotation remains.
- Corrected the volunteer group name to “les Bleuettes”.
- Marked published weekly times as subject to confirmation before travel; kept the source-supplied Wednesday 14h30 and Saturday 15h without claiming independent current confirmation.
- Corrected the October 2026 Chalon dans la Rue story: the 16 October launch opened preparations for the 40th anniversary in 2027.
- Narrowed the Association Valentin Haüy article to the specific activities reported by the ten participants.
- Disclosed conflicting visitor-address reports from 2024 and 2025, without guessing the current venue.
- Distinguished the 27 February 2019 association declaration from the 2 March 2019 JOAFE publication/update and identified Vercel as the hosting/deployment platform.
- The registered-office address and legal publication manager remain association-confirmation items.


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
**Current loop:** LOOP 027  
**Candidate:** bullebleue-loop-026-mockup-v3-polish · accuracy audit  
**Repository:** teyyara/bullebleue · main  
**Implementation checkpoint:** 1b7fd73d494321db421c065470226452d3b1d797  
**Status:** ACCURACY FIXES IMPLEMENTED ON PREVIEW BRANCH — VERIFICATION PENDING

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
