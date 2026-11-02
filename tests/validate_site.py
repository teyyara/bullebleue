#!/usr/bin/env python3
"""Dependency-free structural/content guardrails for La Bulle Bleue."""
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
        if tag == "meta" and a.get("name") == "description" and a.get("content"):
            self.description = True

def main():
    for path in ("index.html", "styles.css", "script.js", "assets/favicon.svg", "tests/test_menu.js"):
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
    broken = [href for href in parser.links if href.startswith("#") and href[1:] not in parser.ids]
    assert not broken, f"broken in-page anchors: {broken}"

    for asset in re.findall(r'(?:src|href)="/([^"]+)"', html):
        assert (ROOT / asset).is_file(), f"missing local asset: /{asset}"

    assert "Rempart" not in html and "14 Quai Gambetta" not in html, "disputed address must remain unpublished"
    assert not any(term in html for term in ("14h30", "mercredi après-midi", "samedi après-midi")), "historical hours must remain unpublished"
    assert "mailto:apail@live.fr" in html, "primary email CTA missing"
    assert "prefers-reduced-motion" in css, "reduced motion preference missing"
    assert "aria-expanded" in js and "Escape" in js, "keyboard menu behavior incomplete"
    assert "toggle.getAttribute('aria-expanded') !== 'true'" in js, "Escape should only close an open menu"
    print("PASS: structure, French language, landmarks, anchors, local assets, content safeguards, reduced motion and keyboard hooks")

if __name__ == "__main__":
    main()
