# AEOS Status — Bulle Bleue - APAiL

**Active keyphrase:** make a full website for: Bulle Bleue à Chalon-sur-Saône  
**Run ID:** bullebleue-20261102-001  
**Rulebook:** AEOS v3  
**Current loop:** LOOP 022  
**Candidate:** bullebleue-loop-022-transparent-drawing-character-cutouts-v1  
**Repository:** teyyara/bullebleue · main  
**Implementation checkpoint:** 28583458561c261c593bd2a88f06412c66c337b3  
**Status:** WAITING_FOR_CONTINUE

## Delivered in Loop 022
- Prepared 20 individually addressable transparent SVG character cut-outs from drawings 6–9: six from drawing 6, four from drawing 7, one from drawing 8 and nine from drawing 9.
- Each SVG references its untouched original JPEG and uses a hand-traced clipping path. The characters preserve the supplied drawing pixels; they are not generated or redrawn.
- Excluded the pasted football photograph and cropped edge fragment in drawing 7 from the drawn-character set.
- Replaced the four rectangular drawing-sheet images in the sticky homepage story collage with individually positioned transparent figure groups. The four complete source JPEGs remain visible in the Jouer/créer collage.
- Added CR-014, REQ-064 and DEC-034, updated the asset/provenance register, and added structural/browser assertions.

## Verification
- GitHub Actions **PASS**: [run 42082401519](https://github.com/teyyara/bullebleue/actions/runs/42082401519).
- Python structural validator: **PASS** — validates all 20 SVGs, source references and original-sheet preservation.
- Node syntax/menu/story/reduced-motion tests: **PASS**.
- Playwright Chromium: **PASS** — nine public pages × five viewport widths (45 combinations); all 20 cut-outs load, all four original sheets remain present, and no overflow, failed image loads, page errors or console errors were reported.
- Screenshot artifact: [13440433219](https://github.com/teyyara/bullebleue/actions/runs/42082401519/artifacts/13440433219), 18 screenshots. Seven relevant desktop/mobile captures were manually opened and reviewed, including the welcome story, Se retrouver and Jouer/créer compositions.

## Next actionable TODO
Collect authentic young-person, parent and volunteer testimonials if the owner wants the current invitation prompts replaced. No testimonial text has been invented.

## Other open items
- Obtain final association-owner visual/content acceptance.
- Confirm registered office, publication manager, hosting provider, membership terms and current venue.
- Test apail@live.fr deliverability without an unsolicited message.
- Complete Firefox/WebKit/Safari, screen-reader, physical-device, Lighthouse, ZAP and hosted security/performance checks.

No production deployment has been performed or authorised. Hosting remains unconfigured.

## Progression control
Loop 022 is checkpointed on main. Exactly one standalone CONTINUE authorises LOOP 023.
