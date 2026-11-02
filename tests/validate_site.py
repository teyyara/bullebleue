#!/usr/bin/env python3
"""Dependency-free structural, asset and content guardrails for La Bulle Bleue."""
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
        self.ids = set()
        self.links = []
        self.images = []
        self.description = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "h1":
            self.h1 += 1
        if tag == "main":
            self.main += 1
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "img":
            self.images.append(a)
        if tag == "meta" and a.get("name") == "description" and a.get("content"):
            self.description = True

def main():
    required = (
        "index.html", "styles.css", "script.js", "assets/favicon.svg",
        "assets/illustrations/hero-community.svg", "assets/illustrations/games.svg",
        "assets/illustrations/garden.svg", "assets/illustrations/discovery.svg",
        "assets/illustrations/culture.svg", "assets/illustrations/solidarity.svg",
        "tests/test_menu.js"
    )
    for path in required:
        item = ROOT / path
        assert item.is_file() and item.stat().st_size, f"missing required file: {path}"

    html = (ROOT / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    js = (ROOT / "script.js").read_text(encoding="utf-8")
    parser = Parser()
    parser.feed(html)

    assert parser.lang == "fr", "document language must be French"
    assert parser.h1 == 1, "expected exactly one h1"
    assert parser.main == 1, "expected one main landmark"
    assert parser.description, "meta description is missing"
    assert all(text in html for text in ("La Bulle Bleue", "APAiL", "Chalon-sur-Saône", "dès 6 ans", "apail@live.fr"))
    assert 'id="la-vie-a-la-bulle"' in html, "recent activity story section missing"
    assert "10 octobre 2026" in html and "3 octobre 2026" in html, "dated activity examples missing"

    broken = [href for href in parser.links if href.startswith("#") and href[1:] not in parser.ids]
    assert not broken, f"broken in-page anchors: {broken}"

    for asset in re.findall(r'(?:src|href)="/([^"]+)"', html):
        assert (ROOT / asset).is_file(), f"missing local asset: /{asset}"

    assert len(parser.images) >= 6, "image-led asset set not present"
    for image in parser.images:
        assert image.get("alt") is not None and image.get("alt").strip(), "every informative image needs alt text"
        assert image.get("width") and image.get("height"), "images need intrinsic dimensions"
        assert image.get("src", "").startswith("/"), "images must be local assets, not third-party hotlinks"

    assert "Rempart" not in html and "14 Quai Gambetta" not in html, "disputed address must remain unpublished"
    assert not any(term in html for term in ("14h30", "mercredi après-midi", "samedi après-midi")), "historical hours must remain unpublished"
    assert "mailto:apail@live.fr" in html, "primary email CTA missing"
    assert "prefers-reduced-motion" in css and "prefers-reduced-motion" in js, "reduced-motion fallback missing"
    assert "IntersectionObserver" in js and "has-reveal" in css, "scroll reveal enhancement missing"
    assert "toggle.getAttribute('aria-expanded') !== 'true'" in js, "Escape should only close an open menu"
    print("PASS: structure, content provenance guardrails, local illustration assets, alt text, dimensions, reduced motion and anchors")

if __name__ == "__main__":
    main()
