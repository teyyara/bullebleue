#!/usr/bin/env python3
"""Dependency-free structural, content and asset guardrails for La Bulle Bleue."""
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang = None
        self.h1 = 0
        self.main = 0
        self.sections = []
        self.ids = set()
        self.links = []
        self.images = []
        self.description = False
        self.nav_labels = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html": self.lang = a.get("lang")
        if tag == "h1": self.h1 += 1
        if tag == "main": self.main += 1
        if tag == "section": self.sections.append(a.get("id", ""))
        if a.get("id"): self.ids.add(a["id"])
        if tag == "a" and a.get("href"): self.links.append(a["href"])
        if tag == "img": self.images.append(a)
        if tag == "meta" and a.get("name") == "description" and a.get("content"):
            self.description = True

def main():
    required = (
        "index.html", "styles.css", "script.js", "assets/favicon.svg",
        "tests/test_menu.js"
    )
    for relative in required:
        path = ROOT / relative
        assert path.is_file() and path.stat().st_size, f"missing required file: {relative}"

    html = (ROOT / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    js = (ROOT / "script.js").read_text(encoding="utf-8")
    parser = Parser()
    parser.feed(html)

    assert parser.lang == "fr", "document language must be French"
    assert parser.h1 == 1, "expected exactly one h1"
    assert parser.main == 1, "expected one main landmark"
    assert parser.description, "meta description is missing"
    assert parser.sections == ["accueil", "activites", "accueil-bienveillant", "association", "contact"], (
        f"expected five concise sections in reading order; got {parser.sections}"
    )
    assert all(value in html for value in ("La Bulle Bleue", "APAiL", "Chalon-sur-Saône", "dès 6 ans", "apail@live.fr"))
    assert "1995" in html and "2021" in html, "association / initiative history missing"
    assert all(href[1:] in parser.ids for href in parser.links if href.startswith("#")), "broken in-page link"
    assert "mailto:apail@live.fr" in html, "primary contact route missing"

    assert len(parser.images) == 0, "editorial redesign should not rely on stock-like placeholder illustrations"

    for asset in re.findall(r'(?:src|href)="/([^\"]+)"', html):
        assert (ROOT / asset).is_file(), f"missing referenced local asset: /{asset}"

    assert "Rempart" not in html and "14 Quai Gambetta" not in html, "disputed visitor address must remain unpublished"
    assert not any(term in html for term in ("14h30", "mercredi après-midi", "samedi après-midi")), "historical hours must remain unpublished"
    assert "sans jugement" in html, "welcome ethos missing"
    assert "https://www.facebook.com/p/Bulle-Bleue-APAiL-100066715807933/" in html, "the user-supplied official Facebook page should be linked"
    assert '<ol class="welcome-steps"' in html and '<li class="welcome-step">' in html, "first-contact steps should use ordered-list semantics"
    assert "brand-monogram" in html and "brand-mark" not in html, "provisional typographic brand mark missing"
    assert "prefers-reduced-motion" in css, "reduced-motion CSS fallback missing"
    assert "event.key !== 'Escape' || toggle.getAttribute('aria-expanded') !== 'true'" in js, "Escape must act only on an open menu"
    assert "IntersectionObserver" not in js, "decorative scroll reveal should not hide page content"
    assert "fonts.googleapis.com" not in css and "fonts.gstatic.com" not in css, "runtime font requests must remain local-system only"
    assert "linear-gradient" in css and "--paper:" in css and "--ink:" in css, "new visual background / palette missing"
    print("PASS: concise five-section structure, identity/contact, editorial no-placeholder-illustration rule, Facebook link, anchors, content safeguards and motion fallback")

if __name__ == "__main__":
    main()

