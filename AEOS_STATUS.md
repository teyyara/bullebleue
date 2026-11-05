# AEOS Status — Bulle Bleue - APAiL

**Active keyphrase:** make a full website for: Bulle Bleue à Chalon-sur-Saône  
**Run ID:** bullebleue-20261102-001  
**Rulebook:** AEOS v3  
**Current loop:** LOOP 020  
**Candidate:** bullebleue-loop-020-organic-news-blob-contours-v1  
**Repository:** teyyara/bullebleue · main  
**Implementation checkpoint:** 3d7d8683d0ec471e03a31ac2ba4aeb7f200571a9  
**Status:** WAITING_FOR_CONTINUE

## Delivered in Loop 020
- Three dated Actualités cards now read as organic bubbles rather than rounded rectangles.
- Each card has its own smooth Bézier contour (96 points) and distinct pastel surface.
- Illustration frames use matching organic contours; dates, categories, headlines and CTAs remain readable.
- Desktop Illustration labels move upper-right; mobile labels remain lower-right.
- Dated routes and the separate undated three-photo community strip are unchanged.

## Verification
- Final code checkpoint: `3d7d8683d0ec471e03a31ac2ba4aeb7f200571a9`.
- GitHub Actions **PASS**: [run 42072524668](https://github.com/teyyara/bullebleue/actions/runs/42072524668).
- Python structural validator **PASS**; Node syntax/interaction tests **PASS**.
- Playwright Chromium **PASS** — nine pages × five widths (45); unique card/image contours, desktop badge placement, no overflow or browser errors.
- Visual artifact: [Loop 020 screenshots 13436352631](https://github.com/teyyara/bullebleue/actions/runs/42072524668/artifacts/13436352631) (18 screenshots).
- Final Actualités desktop/mobile screenshots manually inspected.

## Open items
1. Final owner visual/content acceptance.
2. Genuine young-person, parent and volunteer testimonials if supplied.
3. Transparent cut-outs from drawings 6–9; complete originals currently used.
4. Confirm registered office, publication manager and hosting provider.
5. Confirm membership terms and renewal conditions.
6. Confirm current venue/location.
7. Test `apail@live.fr` deliverability without an unsolicited message.
8. Firefox/WebKit/Safari, screen-reader, physical-device, Lighthouse, ZAP and hosted checks.

No production deployment has been performed or authorised. Hosting remains unconfigured.

## Progression control
Loop 020 is checkpointed on main. Exactly one standalone `CONTINUE` authorises LOOP 021.
