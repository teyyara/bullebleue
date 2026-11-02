# AEOS Status — La Bulle Bleue

**Active keyphrase:** `make a full website for: Bulle Bleue à Chalon-sur-Saône`  
**Run ID:** `bullebleue-20261102-001`  
**Rulebook:** AEOS v3  
**Current loop:** LOOP 002  
**Candidate:** `bullebleue-loop-002-menu-accessibility-v1`  
**Repository:** `teyyara/bullebleue`  
**Branch:** `main` (single-branch progression)  
**Previous verified remote head:** `d05ed5b6163019033130dd83d9be633acadee53b`  
**Loop 002 implementation checkpoint:** `998ae654471a71c9ce11aa48e1951764fe72e517`  
**Evidence manifest reconciliation commit:** `62348c46a35547bbcea414e8250ebdc31218b693`  
**State:** `WAITING_FOR_CONTINUE`

## Loop 002 objective

Correct keyboard focus behavior for Escape in the mobile navigation and add a durable, dependency-free regression test.

## Changes

- Escape is now ignored when `aria-expanded` is not `true`.
- When the menu is actually open, Escape closes it and restores focus to the menu trigger.
- Selecting a navigation link and clicking outside continue to close the menu without unexpected focus movement.
- Added `tests/test_menu.js`, a Node.js VM-based regression test using deterministic DOM interaction doubles.
- Updated README test instructions, structural validator, requirements, risk, decision, learning and evidence records.

## Validation

- `python3 tests/validate_site.py`: PASS.
- `node --check script.js`: PASS.
- `node --check tests/test_menu.js`: PASS.
- `node tests/test_menu.js`: PASS; closed Escape inert, open Escape closes/restores focus, repeated Escape inert, nav selection closes, outside click closes.
- The previous Chromium and responsive checks remain evidence from Loop 001; no new browser-engine claim is made in this loop.

## Limitations / open items

- Firefox, WebKit, actual Safari and screen-reader environments are unavailable.
- Current APAiL venue and weekly hours remain unverified and omitted.
- Domain/host is not configured; no production deployment or smoke test.
- Candidate is not release-certified.

## Run locally

```bash
python3 -m http.server 8080
python3 tests/validate_site.py
node --check script.js
node tests/test_menu.js
```

## Progression control

Loop 002 is complete. The remote checkpoint is verified and the system is now `WAITING_FOR_CONTINUE`. Exactly one standalone `CONTINUE` authorizes Loop 003.
