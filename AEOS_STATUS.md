# AEOS Status — La Bulle Bleue

**Active keyphrase:** make a full website for: Bulle Bleue à Chalon-sur-Saône  
**Run ID:** bullebleue-20261102-001  
**Rulebook:** AEOS v3  
**Current loop:** LOOP 016  
**Candidate:** bullebleue-loop-016-verified-apail-legal-identity-v1  
**Repository:** teyyara/bullebleue  
**Branch:** main (single-branch progression)  
**Latest implementation checkpoint:** 3990f99b3ee422783dacd6b94f6664b73ed81c4b  
**Status:** WAITING_FOR_CONTINUE

## Delivered in Loop 016

- Researched APAiL legal identity using the official JOAFE modification notice, the City of Chalon-sur-Saône association directory and a public RNA/SIRENE-derived record.
- Updated Mentions légales with the denomination published in the JOAFE notice dated 27 February 2019: “A.P.AI.L. — Amitié Partage Aide Logistique, Matérielle et Morale”.
- Added registry-listed identifiers RNA W712002504 and SIREN 519 970 743, with a confirmation caveat.
- Documented the address conflict: the JOAFE notice and municipal directory list 14 quai Gambetta; the SIRENE-derived listing updated 24 June 2026 shows 14 boulevard de la République. The page does not assert either as the current registered office.
- Kept the publication manager and actual host as pending; legal sign-off is still blocked until APAiL confirms those details and the current registered office.
- Updated provenance, assumptions, decision log, README, requirements, product contract and CR-009; extended the Python structural validator.

## Verification

- Remote source/readback audit: PASS — exact main-branch blobs checked.
- GitHub Actions: PASS — [run 41665188280](https://github.com/teyyara/bullebleue/actions/runs/41665188280), commit `3990f99b3ee422783dacd6b94f6664b73ed81c4b`.
- Python structural validator: PASS — legal denomination, identifiers, address conflict and source links asserted.
- Node syntax and interaction regression: PASS.
- Playwright Chromium: PASS — all nine pages at 320, 390, 768, 1024 and 1440 px (45 combinations); no horizontal overflow, failed local images, external requests or browser errors.
- No visual changes to the homepage/gallery were made in this loop; existing screenshot evidence remains the Loop 015 visual review.

## Open items

1. APAiL must confirm the current registered-office address; public sources disagree.
2. Confirm the responsible publisher's name and capacity.
3. Confirm the actual hosting provider, registered company name, address and contact details before legal sign-off.
4. Confirm current membership amount, process, documents and renewal conditions.
5. Confirm the 2024-referenced La Bulle Bleue venue and session schedule before presenting them as current.
6. Identifiable participant/group and children photographs remain unpublished pending image-specific releases.
7. Test the published `apail@live.fr` mailbox deliverability.
8. Cross-browser, assistive technology, physical-device, Lighthouse, ZAP and hosted checks remain outstanding.
9. Final visual/content acceptance by the association owner remains outstanding; no deployment is authorized.

No production deployment has been performed or authorized.

## Progression control

Loop 016 is checkpointed on main. The repository is set to WAITING_FOR_CONTINUE. Exactly one standalone CONTINUE authorizes Loop 017.
