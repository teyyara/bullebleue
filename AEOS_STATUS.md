# AEOS Status — La Bulle Bleue

**Active keyphrase:** make a full website for: Bulle Bleue à Chalon-sur-Saône  
**Run ID:** bullebleue-20261102-001  
**Rulebook:** AEOS v3  
**Current loop:** LOOP 017  
**Candidate:** bullebleue-loop-017-playful-bubble-art-direction-v1  
**Repository:** teyyara/bullebleue  
**Branch:** main (single-branch progression)  
**Latest implementation checkpoint:** c57a2a87c55267dbb8409cfd522b8d5134ff608e  
**Status:** WAITING_FOR_CONTINUE

## Delivered in Loop 017

- Adopted the association owner's new direction: a playful, childlike, arts-led website rather than a restrained professional/editorial system.
- Added organic, irregular bubble geometry across shared page components, pill-shaped actions, soft pastel supporting colours around the official blue logo, and more informal typography. Local fonts prefer Comic Sans/Chalkboard/Comic Neue where available and fall back to a readable sans-serif; no remote font or paid dependency was added.
- Replaced the homepage placeholder SVG backdrop with a sticky collage using all five supplied drawings: `assets/dessin1.jpeg` through `assets/dessin5.jpeg`. All three scrolling story chapters remain in place.
- Recorded the owner feedback in `TODO.md`, CR-010, product contract v1.1, requirements, decisions, assumptions, asset register and content provenance.
- Kept the selected `assets/gathering.jpeg` out of public HTML. It is a recognizable group photograph and image-specific participant/guardian release evidence is not recorded; placement in the closing DERRIÈRE LA BULLE/contact section remains a tracked blocker.
- Kept the existing two close-up tabletop photos in the homepage activity gallery.

## Verification

- Final implementation commit: `c57a2a87c55267dbb8409cfd522b8d5134ff608e`.
- GitHub Actions: PASS — [run 41943584141](https://github.com/teyyara/bullebleue/actions/runs/41943584141) on the exact final implementation commit.
- Python structural validator: PASS.
- Node syntax and menu/story/reduced-motion tests: PASS.
- Playwright Chromium: PASS — nine public pages at 320, 390, 768, 1024 and 1440 px (45 page/viewport combinations); all local images loaded, five supplied drawings verified, no horizontal overflow, no failed/external requests, no console/page errors; story transitions, reduced-motion and no-JavaScript checks passed.
- Six screenshots uploaded and manually inspected: [visual review artifact 13377971069](https://github.com/teyyara/bullebleue/actions/runs/41943584141/artifacts/13377971069). Reviewed three desktop story states, mobile story, and desktop/mobile gallery. Desktop heading scale and pill contact action were checked.

## Open items

1. Add `gathering.jpeg` to the final DERRIÈRE LA BULLE/contact area only after the association documents image-specific permission for recognizable participants and guardian consent for identifiable minors.
2. Obtain the association owner's final visual/content acceptance and refine the design from her feedback.
3. Review every public page at desktop/mobile for any remaining rigid treatments and improve visual consistency.
4. Confirm the current registered-office address, publication manager and actual hosting provider before legal sign-off.
5. Confirm current membership fee, process, documents and renewal conditions.
6. Confirm whether the 2024-referenced venue and session schedule remain current.
7. Test `apail@live.fr` mailbox deliverability without sending an unsolicited message.
8. Complete Firefox/WebKit/Safari, manual screen-reader, physical-device, Lighthouse, ZAP and hosted performance/security checks.

No production deployment has been performed or authorized.

## Progression control

Loop 017 is checkpointed on main. The repository is set to WAITING_FOR_CONTINUE. Exactly one standalone CONTINUE authorizes Loop 018.
