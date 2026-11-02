# AEOS Status — La Bulle Bleue

**Active keyphrase:** make a full website for: Bulle Bleue à Chalon-sur-Saône  
**Run ID:** bullebleue-20261102-001  
**Rulebook:** AEOS v3  
**Current loop:** LOOP 007  
**Candidate:** bullebleue-loop-007-facebook-extraction-content-v1  
**Repository:** teyyara/bullebleue  
**Branch:** main (single-branch progression)  
**Parent at loop start:** b7ae5e67ee99027ba66ee48fc031a9ab1eaa0866  
**Implementation checkpoint:** 62ebc451af17d9c03923279d2911a1f94fa917e8  
**State:** WAITING_FOR_CONTINUE

## Objective

Replace the previous generic website content with a concise, source-led presentation based on the user-supplied `Bulle_Bleue_APAiL_contenu_facebook.md` file, which identifies the exact Bulle Bleue – APAiL Facebook page.

## Source reviewed

- File: `Bulle_Bleue_APAiL_contenu_facebook.md`
- Blob at loop start: `dec4ee6c3f4e0ea7c092ebe1760c4a35033e05bf`
- Length: 816 lines / 35,152 characters
- Extraction date stated in file: 2 November 2026
- Coverage: page information and text publications from May 2023 to October 2026
- Exact Facebook page: https://www.facebook.com/p/Bulle-Bleue-APAiL-100066715807933/

## Changes

- Rebuilt the page into six sections: accueil, publics, activités, actualités, APAiL and contact.
- Added the two audience groups from the extraction: children over 6 on Wednesday afternoons; autonomous teenagers and adults on Saturday afternoons.
- Displayed the stated 14 h 30 / 15 h times with a source/date note and a visible request to confirm before travelling.
- Added 30 Rempart Saint-Vincent, 71100 Chalon-sur-Saône, plus the garden access via rue Leriche near bastion Saint-Pierre. The page attributes these details to the Facebook presentation dated 11 March 2024 and asks visitors to confirm.
- Replaced generic activity descriptions with actual examples from the extraction: games, baby-foot, music, percussion, singing, arts, drawing, cooking, garden, outings, Ciné Relax, bowling, mediation animale and parent cafés.
- Added four dated highlights from September/October 2026.
- Expanded APAiL's 1995 history, the Bulle Bleue 2021 launch, reported solidarity activity in Sapala/Burkina Faso and Morocco, the volunteer name "les Bleuettes", and organisations cited in posts.
- Historical projects and cited organisations are explicitly not presented as necessarily current/contractual.
- No participant names or participant photos are used. The BB monogram is still provisional pending the official logo assets.

## Validation status

- The source file was read in full and content was reviewed against it.
- `tests/validate_site.py` was updated with the new six-section and source-content guardrails, but it was **not executed** during this isolated GitHub editing session.
- JavaScript was not changed; Loop 006 Node test results are not presented as a Loop 007 rerun.
- Chromium/browser visual review and screenshots were **not run** for Loop 007. The page is longer and must be checked locally at mobile, tablet and desktop widths.
- Cross-browser, screen-reader, manual accessibility, Lighthouse, ZAP and hosted performance checks remain outstanding.
- Mailbox deliverability remains untested.
- No production deployment has been performed or authorized.

## Operational information caveat

The Wednesday/Saturday times and local address/garden access are accurately transcribed from the supplied extraction, but the source presentation is dated 11 March 2024. Current validity must be confirmed with APAiL. The page makes that caveat visible.

## Progression control

Loop 007 is committed to `main`. The repository is now in `WAITING_FOR_CONTINUE`. Exactly one standalone `CONTINUE` authorizes Loop 008.
