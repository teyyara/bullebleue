# AEOS Status — La Bulle Bleue

**Active keyphrase:** make a full website for: Bulle Bleue à Chalon-sur-Saône  
**Run ID:** bullebleue-20261102-001  
**Rulebook:** AEOS v3  
**Current loop:** LOOP 008  
**Candidate:** bullebleue-loop-008-source-integrity-and-interaction-verification-v1  
**Repository:** teyyara/bullebleue  
**Branch:** main (single-branch progression)  
**Starting remote head:** 87ea22114ddebf210bd6ea0f205d6e77517ac604  
**Code change:** None — QA/evidence-only loop  
**State:** WAITING_FOR_CONTINUE

## Objective

Close the remaining Loop 007 verification gap by reading the exact current main-branch source files, auditing the content and responsive CSS declarations, and running the exact remote JavaScript interaction regression.

## Results

### Source-level content and integrity audit — PASS

Read-only assertions against the current GitHub blobs confirmed:

- French document, one H1, one main landmark, six sections in the expected order, and all in-page links resolve.
- The exact 816-line user-supplied Facebook extraction and 2 November 2026 source date remain present.
- All required page content is present: both audience groups, Wednesday and Saturday times, venue/garden location, activity examples, four dated highlights, APAiL history, solidarity examples, Les Bleuettes and cited organisations.
- Venue/time source-date note and confirmation request remain visible.
- Activities are explicitly examples, not a fixed weekly promise.
- Historic international projects are not represented as necessarily active; cited organisations are a non-exhaustive list.
- The exact Facebook URL appears in three places: JSON-LD sameAs, contact and footer; JSON-LD parses.
- No photo placements were introduced; local root-relative references resolve to the stylesheet, script and favicon.
- Responsive CSS declarations exist for audience cards, activity grid (3 → 2 → 1), news grid (4 → 2 → 1), mobile association stacking and reduced-motion preferences.

This is source inspection, not rendered layout measurement.

### JavaScript syntax and menu regression — PASS

Exact remote Git blobs were copied to a local isolated test directory and their SHA-1s matched the GitHub source:

- script.js: aa2ae008fdfa8c6eb1a0f6004938627104553b61
- tests/test_menu.js: 051d0dec5655cbf2b2017e840c096ec4fc63fc6e

Node.js 22.16.0 commands passed:

    node --check script.js
    node --check tests/test_menu.js
    node tests/test_menu.js

Result: menu keyboard/outside-click behavior, progressive reveal and reduced-motion fallback all pass.

## Remaining validation limitations

- The Python HTMLParser validator tests/validate_site.py was not executed against a complete local checkout.
- Full-page Chromium/Playwright review of the current six-section page was not run. No rendered overflow pass, screenshot or browser-error claim is made.
- CSS responsive breakpoints were inspected in source only; mobile/tablet/desktop rendered composition remains unverified.
- Firefox/WebKit/Safari, manual screen-reader/assistive-tech checks, physical-device tests, Lighthouse, ZAP and hosted checks remain outstanding.
- Mailbox deliverability remains untested.
- Current operational accuracy of venue and timetable still needs confirmation from APAiL.
- Official logo/photos remain pending; no unapproved participant image is used.
- No production deployment has been performed or authorized.

## Progression control

Loop 008 is a QA/evidence-only checkpoint; no product code changed. The remote repository is set to WAITING_FOR_CONTINUE. Exactly one standalone CONTINUE authorizes Loop 009.