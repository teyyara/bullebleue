# AEOS Status — La Bulle Bleue

**Active keyphrase:** make a full website for: Bulle Bleue à Chalon-sur-Saône  
**Run ID:** bullebleue-20261102-001  
**Rulebook:** AEOS v3  
**Current loop:** LOOP 012  
**Candidate:** bullebleue-loop-012-owner-led-information-architecture-sticky-home-news-v1  
**Repository:** teyyara/bullebleue  
**Branch:** main (single-branch progression)  
**Implementation checkpoint:** c3a556b58e01f1c6751c66fc3bf84a63740387ff  
**Status:** WAITING_FOR_CONTINUE

## Owner direction implemented

On 3 November 2026, the user relayed the association owner's requested information architecture and editorial direction. Loop 012 implements that request.

## Delivered in Loop 012

- Replaced the old six-destination navigation with five clear primary links: Accueil, Qui sommes-nous ?, Actualités, Adhérer and Nous contacter. Mentions légales is available from the shared footer.
- Consolidated the previous La Bulle, Activités and APAiL pages into one dedicated Qui sommes-nous page, preserving source-grounded identity, audience, activity examples, volunteer information and historical solidarity context.
- Rebuilt the homepage around one local illustrated community backdrop that remains sticky while three text chapters take their turn as the visitor scrolls.
- Added progressive IntersectionObserver enhancement for the homepage. The opening panel is active immediately, before the first observer callback; content is visible in the non-enhanced default and remains visible for reduced-motion users or browsers without IntersectionObserver.
- Rebuilt Actualités as a compact editorial overview with exactly three rectangular cards and three Voir plus actions. Each card opens its own dedicated dated article page: 26 October, 17 October and 10 October 2026.
- Used original local SVG illustrations on Actualités and individual articles. They are labelled as illustrations, not as documentary photographs of the specific events.
- Added Adhérer with an email request for up-to-date membership terms. No fee, mandatory document, form or renewal conditions are invented.
- Added Nous contacter with the published email/Facebook route and an explicit source-date caveat on the historical venue information.
- Added Mentions légales as a clearly marked draft. The exact legal designation, registered office, publication manager and hosting-provider details remain pending APAiL confirmation.
- Removed the old la-bulle.html, activites.html and apail.html page entry points.
- Recoloured the four placed illustrations using only sampled logo blues and documented near-white surface tints; strengthened the validator to reject non-brand SVG colours.
- Updated tests, README, contract, requirements, decisions, assumptions, source provenance, asset register and CR-006.

## Source and factual boundaries

The primary content source remains the user-supplied extraction `Bulle_Bleue_APAiL_contenu_facebook.md` from the exact Facebook page, extracted 2 November 2026. The three featured news items retain their original dates and factual scope.

The address and Wednesday/Saturday schedule remain grounded in a Facebook presentation dated 11 March 2024; visitors are asked to confirm them with APAiL before travelling. Membership terms were not present in the source, so the Adhérer page requests current terms. Legal/hosting fields are visibly pending and the legal page is not release-ready.

No identifiable-participant photographs are used in the Loop 012 public templates. News imagery is illustrative and explicitly labelled as such.

## Verification

- Remote source/tree audit: PASS — all nine page files read back from the exact main branch; French language, page title/description, one H1 and one main landmark, five-link navigation, active page/section states, logo in header/footer, Facebook/footer legal route and internal page links checked.
- Homepage/story audit: PASS — three text chapters, one sticky local SVG, progressive scroll observer and reduced-motion/no-observer fallback found in exact remote source.
- News audit: PASS — exactly three cards, exactly three Voir plus actions, all three distinct article routes, exact source dates and illustration labels verified.
- Asset audit: PASS — all referenced root-relative assets are present; all placed SVG hex colours are restricted to the official logo palette and documented light tints.
- Membership/legal safeguards: PASS — no invented membership fees/forms; legal identity/host unknowns are explicitly labelled pending.
- Python validator: NOT RUN against a complete local checkout.
- Node syntax and regression tests: NOT RUN.
- Current-candidate browser screenshots and responsive visual review: NOT RUN. No rendered visual or no-horizontal-overflow PASS is claimed.

## Open items

1. Run the Python validator and Node.js syntax/interaction tests against the current candidate.
2. Render all nine pages across desktop, tablet and mobile widths; inspect sticky background/text transitions and news cards, and capture current screenshots.
3. APAiL must supply its exact legal name, registered office, publication-responsible person and hosting-provider details before legal sign-off.
4. APAiL can provide current membership fees/process/forms if it wants these displayed.
5. Confirm the schedule and venue before treating the 2024 details as current.
6. Confirm any image-specific participant/guardian releases before using recognisable participant photos.

No production deployment has been performed or authorized.

## Progression control

Loop 012 is checkpointed on `main`. The repository is set to `WAITING_FOR_CONTINUE`. Exactly one standalone `CONTINUE` authorizes Loop 013.
