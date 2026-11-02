# AEOS Status — La Bulle Bleue

**Active keyphrase:** make a full website for: Bulle Bleue à Chalon-sur-Saône  
**Run ID:** bullebleue-20261102-001  
**Rulebook:** AEOS v3  
**Current loop:** LOOP 006  
**Candidate:** bullebleue-loop-006-concise-editorial-redesign-v1  
**Repository:** teyyara/bullebleue  
**Branch:** main (single-branch progression)  
**Previous verified remote head:** 7cb370c336531b6b8bb7bb55c82734d90b99cda9  
**Implementation checkpoint commit:** cddcca654c67229c71d68a89fcdb24f8ac5a374a  
**State:** WAITING_FOR_CONTINUE

## Loop 006 objective

Shorten the page and replace the generic pastel/illustrated-card treatment with a more distinctive professional editorial identity, using verified research about Bulle Bleue - APAiL and the exact Facebook page supplied by the user where accessible.

## Changes

- Rebuilt the page into five main sections: hero, activities, welcome/first contact, APAiL history and contact.
- Removed the long dated story mosaic and duplicated approach, first-step and volunteer sections.
- Replaced repeated illustrated cards with four compact numbered editorial activity rows.
- Introduced a deep mineral/ink-blue, warm-paper, muted teal, clay and ochre design system with a restrained CSS texture and background geometry. This is an evidence-informed design interpretation, not an official published palette.
- Changed the typographic hierarchy to EB Garamond/Cabin with considered platform fallbacks; there are no remote font requests or paid font dependencies.
- Added the exact user-supplied Facebook page URL in both the contact panel and footer.
- Kept the BB typographic monogram explicitly provisional. The Facebook page and profile-image endpoint could not be fetched; a third-party mirror surfaced a different page ID and was not used for assets.
- Removed informative image placements from the current page markup. The earlier original SVG files remain in the repository archive but are not referenced by the Loop 006 page.

## Validation

- Python structural/content validator: PASS — five intended sections, one h1, one main, valid anchors, identity/contact content, Facebook route, no disputed visitor address or historical hours, no placeholder images.
- JavaScript syntax: PASS — node --check script.js and node --check tests/test_menu.js.
- Menu interaction: PASS — node tests/test_menu.js; menu opens, Escape closes and restores focus, link and outside click close correctly.
- Chromium 144 Playwright: PASS at 320, 360, 390, 430, 760, 768, 900, 901, 960, 1024, 1440 and 1920 px.
- No horizontal overflow at any tested width; no console or page errors.
- The exact supplied Facebook URL appears twice in the DOM.
- Fresh desktop, tablet and mobile full-page screenshots were captured and hashed. They are local review artifacts, not site assets.

## Research and brand-source boundary

The exact Facebook page supplied by the user is linked on the website:
https://www.facebook.com/p/Bulle-Bleue-APAiL-100066715807933/

The page could not be fetched by the available research environment, and the profile-picture endpoint was also blocked. A FindGlocal mirror surfaced a different page ID (100620708811103); it is not treated as the same page. No Facebook logo, cover image or participant/press photo has been copied. The current BB mark and colours remain provisional until official assets and reuse permissions can be verified.

Verified public reporting informs the website’s concise welcome/listening/activity wording and palette direction, but not an official brand guide:
- City of Chalon, Objectif Chalon no. 42, 2022, p. 17.
- Info-Chalon, 25 August 2021.
- Info-Chalon, 8 September 2024.
- Info-Chalon, 13 October 2025.

## Remaining limitations

- Chromium only; Firefox, WebKit, actual Safari and physical-device checks remain outstanding.
- Manual screen-reader/assistive-tech testing, axe-core, Lighthouse, ZAP and hosted performance checks have not been completed.
- EB Garamond and Cabin were available in the test browser but are not bundled; platform fallback typography may differ.
- Facebook page contents/logo are not verifiable in this environment. The exact URL is linked, but its live destination has not been validated.
- Exact current visitor venue and weekly hours remain unknown/conflicting and are deliberately unpublished.
- Mailbox deliverability is untested.
- No hosting domain configured; no production smoke test.
- Final human acceptance remains outstanding.

## Deployment

No production deployment has been performed or authorized. The candidate is not release-certified.

## Progression control

Loop 006 is implemented and checkpointed. The system is now WAITING_FOR_CONTINUE. Exactly one standalone CONTINUE authorizes Loop 007.
