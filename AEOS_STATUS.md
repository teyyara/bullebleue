# AEOS Status — Bulle Bleue - APAiL

**Active keyphrase:** make a full website for: Bulle Bleue à Chalon-sur-Saône  
**Run ID:** bullebleue-20261102-001  
**Rulebook:** AEOS v3  
**Current loop:** LOOP 019  
**Candidate:** bullebleue-loop-019-owner-homepage-content-testimonials-and-visual-system-v1  
**Repository:** teyyara/bullebleue  
**Branch:** main (single-branch progression)  
**Implementation checkpoint:** 4babf6711d208a738f5eb5b7d9c13438380e83bc  
**Status:** WAITING_FOR_CONTINUE

## Delivered in Loop 019

- Standardised all nine public page titles, social preview titles, shared brand headers and footers to **Bulle Bleue - APAiL** (lowercase i); removed homepage chapter counters.
- Replaced the welcome banner with the owner's exact eyebrow, title and paragraph; made **Qui sommes-nous ?** a prominent banner action.
- Rebuilt **Se retrouver** with the complete owner copy, the selected `assets/se retrouver.jpg.jpeg` photo, Wednesday 14h30 and Saturday 15h session descriptions, and the cultural-outings description.
- Added **Ils en parlent** directly after Se retrouver. Published Miette's exact AG 2026 quotation as the only attributed testimonial. The young-person, parent and volunteer cards invite genuine future submissions; no invented quotes or testimonial face photographs.
- Adapted `assets/section-jouer-creer.html` as a four-drawing collage with organic and polaroid frames, Caveat captions and a mobile horizontal swipe.
- Added drawings 6–9 to the sticky artwork and changed their highlighted emphasis while the visitor scrolls between sections. The supplied design-merge image is used as a low-opacity background texture; its older embedded schedule is not presented as current.
- Updated **Derrière la Bulle** with the owner's association, volunteers, partner and engagement copy and the two requested actions.
- Applied Fredoka 600 headings, Atkinson Hyperlegible 400/700 reading text, and Caveat 600 accents. Increased section headings and added scroll-margin spacing for the sticky header.
- Preserved the Loop 018 photo distribution: the eleven `assets/posts` images stay on secondary pages (eight on Qui sommes-nous, three undated on Actualités). The homepage uses only the newly selected Se retrouver photo and the existing `gathering.jpeg` closing photograph.

## Verification

- Main-branch code checkpoint: `4babf6711d208a738f5eb5b7d9c13438380e83bc`.
- GitHub Actions **PASS**: [run 42068155012](https://github.com/teyyara/bullebleue/actions/runs/42068155012).
- Python structural/content validator: **PASS**.
- Node syntax, menu, scene-observer and reduced-motion regression: **PASS**.
- Playwright Chromium: **PASS** — nine public pages × five viewport widths (45 combinations); local images loaded, no horizontal overflow, no unexpected external requests, failed requests, page errors or console errors; navigation, scene transitions, reduced-motion and no-JavaScript checks passed.
- Visual screenshots: [Loop 019 artifact 13434598876](https://github.com/teyyara/bullebleue/actions/runs/42068155012/artifacts/13434598876), 18 screenshots uploaded. Ten current homepage desktop/mobile screenshots were manually opened and inspected, covering welcome, Se retrouver, Ils en parlent, Jouer/créer and Derrière la Bulle.
- The poster's old schedule is treated only as decoration. The current homepage session times reflect the owner's direct feedback of 5 November 2026.
- The owner supplied the new images and verbally authorised their use; the earlier project-wide image-use authorisation remains in force.

## Open items

1. Await genuine short testimonials from young people, parents and volunteers; retain “Témoignage à recueillir” prompts until supplied.
2. Create separate transparent character cut-outs from drawings 6–9. The current site uses the original complete drawings; character extraction is not claimed.
3. Obtain final owner visual/content acceptance.
4. Confirm the registered-office address, publication manager and hosting provider before legal sign-off.
5. Confirm membership fee, process, documents and renewal terms.
6. Confirm the current venue/location; the Se retrouver times shown above came directly from the owner's latest feedback.
7. Test `apail@live.fr` deliverability without an unsolicited message.
8. Complete Firefox/WebKit/Safari, manual screen-reader, physical-device, Lighthouse, ZAP and hosted performance/security checks.

No production deployment has been performed or authorised. Hosting remains unconfigured.

## Progression control

Loop 019 is checkpointed on main. Exactly one standalone `CONTINUE` authorises LOOP 020.
