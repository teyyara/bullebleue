#!/usr/bin/env python3
"""Dependency-free structural/content guardrails for La Bulle Bleue."""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

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
        if tag == "html": self.lang = a.get("lang")
        if tag == "h1": self.h1 += 1
        if tag == "main": self.main += 1
        if a.get("id"): self.ids.add(a["id"])
        if tag == "a" and a.get("href"): self.links.append(a["href"])
        if tag == "meta" and a.get("name") == "description" and a.get("content"): self.description = True

def main():
    for path in ("index.html", "styles.css", "script.js", "assets/favicon.svg"):
        if not (ROOT / path).is_file() or not (ROOT / path).stat().st_size:
            raise SystemExit(f"FAIL: missing {path}")
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    js = (ROOT / "script.js").read_text(encoding="utf-8")
    p = Parser(); p.feed(html)
    assert p.lang == "fr", "document language"
    assert p.h1 == 1, "exactly one h1"
    assert p.main == 1, "one main landmark"
    assert p.description, "meta description"
    assert "La Bulle Bleue" in html and "APAiL" in html and "Chalon-sur-Saône" in html
    assert "dès 6 ans" in html and "apail@live.fr" in html
    broken = [x for x in p.links if x.startswith("#") and x[1:] not in p.ids]
    assert not broken, f"broken anchors: {broken}"
    for src in re.findall(r'(?:src|href)=["\\'](/[^"\\']+)', html):
        assert (ROOT / src.lstrip("/")).exists(), f"missing local asset: {src}"
    assert "Rempart" not in html and "14 Quai Gambetta" not in html, "disputed address"
    assert "14h30" not in html and "mercredi après-midi" not in html and "samedi après-midi" not in html, "historical hours"
    assert "mailto:apail@live.fr" in html
    assert "prefers-reduced-motion" in css
    assert "aria-expanded" in js and "Escape" in js
    print("PASS: structure, French language, landmarks, anchors, assets, content safeguards, reduced motion and keyboard hooks")

if __name__ == "__main__":
    main()
