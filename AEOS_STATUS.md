# AEOS Status — La Bulle Bleue

**Active keyphrase:** make a full website for: Bulle Bleue à Chalon-sur-Saône  
**Run ID:** bullebleue-20261102-001  
**Rulebook:** AEOS v3  
**Current loop:** LOOP 015  
**Candidate:** bullebleue-loop-015-accurate-story-and-gallery-visual-evidence-v1  
**Repository:** teyyara/bullebleue  
**Branch:** main (single-branch progression)  
**Latest code checkpoint:** 3a20b49f9faf93afc14cd93e8950def56b328c81  
**Status:** WAITING_FOR_CONTINUE

## Delivered in Loop 015

- Retrieved and manually inspected the three Loop 014 screenshots. Found that the gallery was captured before lazy-loaded images rendered and that the final story panel was captured mid-fade. Full-page screenshots also distorted the sticky story's viewport behavior.
- Kept the public homepage, lazy-loading behavior and story animation unchanged. Fixed the test/capture process rather than changing working site behavior.
- Added screenshot helpers that wait for the requested chapter to be active and its panel opacity to reach at least 0.99.
- Captured each of the three desktop story chapters in a normal viewport, then captured the gallery section on desktop and mobile after forcing image load and awaiting image decode.
- Updated the CI artifact name/path, browser test output, README, requirements, product contract and decision log.

## Verification

- Remote source/readback audit: PASS — exact main-branch blobs checked.
- GitHub Actions: PASS — [run 41661941172](https://github.com/teyyara/bullebleue/actions/runs/41661941172), commit `3a20b49f9faf93afc14cd93e8950def56b328c81`.
- Python structural validator: PASS.
- Node syntax checks and interaction regression: PASS.
- Playwright Chromium: PASS — all nine pages across 320, 390, 768, 1024 and 1440 px (45 page/viewport combinations); no horizontal overflow, missing local images, external requests, failed requests or browser errors.
- Screenshot artifact: [bulle-bleue-loop015-visual-review](https://github.com/teyyara/bullebleue/actions/runs/41661941172/artifacts/13241898121). Six screenshots generated and uploaded.
- Manual visual review: PASS — all six PNGs downloaded and inspected. All three chapter panels show their text fully; the two supplied photographs render correctly with captions in desktop and mobile gallery captures. No obvious screenshot/rendering issue remained.
- Scope note: this is a manual review of six CI captures, not final acceptance by APAiL or cross-browser/physical-device certification.

## Open items

1. Final visual and content acceptance by the association owner remains outstanding.
2. APAiL must supply its exact legal designation, registered office, publication manager and hosting-provider details before legal sign-off.
3. Current membership amount, process, documents and renewal conditions are unknown.
4. Confirm the 2024-referenced session schedule and venue details before presenting them as current.
5. Identifiable participant/group and children photographs remain unpublished pending image-specific participant/guardian releases.
6. Test the published `apail@live.fr` mailbox deliverability.
7. Firefox/WebKit, manual screen-reader, physical-device, Lighthouse, ZAP and hosted performance/security checks remain outstanding.
8. Domain/hosting configuration remains unknown; production deployment is unauthorized.

No production deployment has been performed or authorized.

## Progression control

Loop 015 is checkpointed on main. The repository is set to WAITING_FOR_CONTINUE. Exactly one standalone CONTINUE authorizes Loop 016.
