# AEOS Status — Bulle Bleue - APAiL

**Active keyphrase:** make a full website for: Bulle Bleue à Chalon-sur-Saône  
**Run ID:** bullebleue-20261102-001  
**Rulebook:** AEOS v3  
**Current loop:** LOOP 021  
**Candidate:** bullebleue-loop-021-restore-authorization-validator-wording-v1  
**Repository:** teyyara/bullebleue · main  
**Implementation checkpoint:** 6b18ef0ad08cde38389d9a784d6ec30d34156508  
**Status:** WAITING_FOR_CONTINUE

## Delivered in Loop 021
- Restored the exact words “verbally authorized” in the existing TODO item that documents the association owner's permission for the supplied website images.
- Root cause was a spelling mismatch only: the checklist used “authorised”, while the structural validator checks the exact American-English phrase “verbally authorized”.
- No image, website copy, styling, permission scope or other source code changed.

## Verification
- GitHub Actions **PASS**: [run 42075194025](https://github.com/teyyara/bullebleue/actions/runs/42075194025).
- Python structural validator: **PASS**.
- Node syntax/menu/story/reduced-motion tests: **PASS**.
- Playwright Chromium: **PASS** — nine pages × five viewport widths (45); no overflow, failed image loads, page errors or console errors.
- Screenshot artifact [13438196192](https://github.com/teyyara/bullebleue/actions/runs/42075194025/artifacts/13438196192) uploaded by the workflow. It was not manually inspected; no visual change was made in this loop.

## Next actionable TODO
Prepare transparent individual character cut-outs from drawings 6–9. The website currently uses the complete supplied drawings; separate transparent cut-outs have not yet been produced.

## Other open items
- Obtain authentic young-person, parent and volunteer testimonials if supplied.
- Obtain final association-owner visual/content acceptance.
- Confirm registered office, publication manager, hosting provider, membership terms and current venue.
- Test `apail@live.fr` deliverability without an unsolicited message.
- Complete Firefox/WebKit/Safari, screen-reader, physical-device, Lighthouse, ZAP and hosted security/performance checks.

No production deployment has been performed or authorised. Hosting remains unconfigured.

## Progression control
Loop 021 is checkpointed on main. Exactly one standalone `CONTINUE` authorises LOOP 022.
