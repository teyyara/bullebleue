# La Bulle Bleue — Chalon-sur-Saône

Responsive French-language website for **La Bulle Bleue**, the welcome-and-connection initiative operated by **APAiL** in Chalon-sur-Saône.

## Run locally

This is a static site built with HTML, CSS and vanilla JavaScript. No package install, framework, remote font, analytics, tracking pixel or paid runtime dependency is required.

\`\`\`bash
python3 -m http.server 8080
\`\`\`

Open \`http://localhost:8080\`.

## Website

- \`index.html\` — one-page site, semantic sections, SEO metadata and organization JSON-LD.
- \`styles.css\` — responsive visual system, custom CSS illustrations, keyboard focus and reduced-motion support.
- \`script.js\` — accessible mobile navigation and current footer year.
- \`assets/favicon.svg\` — local SVG icon.
- \`tests/validate_site.py\` — dependency-free structural checks.
- \`evidence/\` — research dossier, contract, requirements, assumptions, risk, decisions and validation results.
- \`.aeos/\` and \`AEOS_STATUS.md\` — persistent progression state and status.

## Content safeguards

Public sources identify La Bulle Bleue as an APAiL initiative. The page describes the publicly reported audience and examples of activities. The public email \`apail@live.fr\` is shown with its source provenance; mailbox deliverability has not been tested.

Earlier sources say 30 Rempart Saint-Vincent; a 2025 report says 30 Rempart Saint-Pierre. Published Wednesday/Saturday afternoon times are historical. The site omits the disputed street address and current weekly schedule and asks visitors to confirm them with the association.

No sensitive-data form, diagnosis eligibility, medical promise, testimonial, phone number, price or registration guarantee has been invented.

## Validation limits

The structural validator and JavaScript syntax check pass. Chromium was exercised in-memory through Playwright using the actual HTML/CSS/JavaScript because sandbox policy blocked direct navigation to localhost and file URLs. This is candidate-level evidence, not a hosted production test.

Firefox, WebKit, actual Safari, manual screen-reader testing, Lighthouse, ZAP, host security headers and production smoke tests remain untested or unavailable. No host/domain was configured and no production deployment was performed.
