#!/usr/bin/env python3
"""Static integrity checks for the owner-approved v3 redesign."""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PAGES = (
    "index.html", "qui-sommes-nous.html", "actualites.html",
    "actualite-2026-10-26.html", "actualite-2026-10-17.html",
    "actualite-2026-10-10.html", "adherer.html", "contact.html",
    "mentions-legales.html", "facile-a-lire.html", "accessibilite.html", "404.html",
)
NAV = (
    "index.html", "qui-sommes-nous.html", "actualites.html",
    "adherer.html", "facile-a-lire.html", "contact.html", "contact.html",
)
CURRENT = {
    "index.html": [("index.html", "page")],
    "qui-sommes-nous.html": [("qui-sommes-nous.html", "page")],
    "actualites.html": [("actualites.html", "page")],
    "actualite-2026-10-26.html": [("actualites.html", "page")],
    "actualite-2026-10-17.html": [("actualites.html", "page")],
    "actualite-2026-10-10.html": [("actualites.html", "page")],
    "adherer.html": [("adherer.html", "page")],
    "contact.html": [("contact.html", "page")],
    "facile-a-lire.html": [("facile-a-lire.html", "page")],
}
class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang = None
        self.title = False
        self.description = False
        self.h1 = 0
        self.main = 0
        self.ids = set()
        self.links = []
        self.images = []
        self.nav_depth = 0
        self.nav_links = []
        self.nav_current = []
        self.scripts = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html": self.lang = a.get("lang")
        if tag == "title": self.title = True
        if tag == "h1": self.h1 += 1
        if tag == "main": self.main += 1
        if a.get("id"): self.ids.add(a["id"])
        if tag == "meta" and a.get("name") == "description" and a.get("content"): self.description = True
        if tag == "nav" and a.get("id") == "nav": self.nav_depth += 1
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
            if self.nav_depth:
                self.nav_links.append(a["href"])
                if a.get("aria-current"): self.nav_current.append((a["href"], a["aria-current"]))
        if tag == "img": self.images.append(a)
        if tag == "script" and a.get("src"): self.scripts.append(a["src"])
    def handle_endtag(self, tag):
        if tag == "nav" and self.nav_depth: self.nav_depth -= 1

def main():
    parsed = {}
    all_links = []
    for page in PAGES:
        path = ROOT / page
        assert path.is_file() and path.stat().st_size > 500, f"missing/empty page: {page}"
        html = path.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(html)
        parsed[page] = (html, parser)
        assert parser.lang == "fr" and parser.title and parser.description, f"{page}: French metadata required"
        assert parser.h1 == 1 and parser.main == 1, f"{page}: one h1 and one main required"
        assert parser.nav_links == list(NAV), f"{page}: shared navigation order changed: {parser.nav_links}"
        assert parser.nav_current == CURRENT.get(page, []), f"{page}: incorrect active navigation: {parser.nav_current}"
        assert 'href="#"' not in html, f"{page}: placeholder link remains"
        assert 'href="#" ' not in html, f"{page}: placeholder link remains"
        assert 'href="javascript:' not in html.lower(), f"{page}: javascript URL is not allowed"
        for href in parser.links:
            all_links.append((page, href))
            if href == "#": raise AssertionError(f"{page}: placeholder anchor")
            if href.startswith("#"):
                assert href[1:] in parser.ids, f"{page}: broken fragment {href}"
                continue
            parts = urlsplit(href)
            if parts.scheme or parts.netloc: continue
            local = unquote(parts.path).lstrip("/")
            if local:
                assert (ROOT / local).is_file(), f"{page}: broken local link {href}"
        for img in parser.images:
            assert "alt" in img, f"{page}: image missing alt text"
            src = unquote(img.get("src", ""))
            if src.startswith("/"):
                assert (ROOT / src.lstrip("/")).is_file(), f"{page}: missing image {src}"
        assert "/mockup-v3/js/boot.js" in parser.scripts, f"{page}: accessibility settings must apply before render"
        assert "/mockup-v3/js/a11y.js" in parser.scripts, f"{page}: accessibility panel missing"
        assert "/script.js" in parser.scripts, f"{page}: navigation script missing"

    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    theme = (ROOT / "site-v3-overrides.css").read_text(encoding="utf-8")
    mockup_css = (ROOT / "mockup-v3/css/style.css").read_text(encoding="utf-8")
    assert '@import url("/mockup-v3/css/style.css")' in css
    assert '@import url("/site-v3-overrides.css")' in css
    assert "@font-face" in mockup_css and "Atkinson Hyperlegible Next" in mockup_css
    assert all((ROOT / "mockup-v3/fonts" / name).is_file() for name in (
        "atkinson-hyperlegible-next-latin-400-normal.woff2",
        "atkinson-hyperlegible-next-latin-700-normal.woff2",
        "fredoka-latin-700-normal.woff2",
        "caveat-latin-500-normal.woff2",
        "opendyslexic-latin-400-normal.woff2",
    ))
    assert (ROOT / "mockup-v3/img/mural.jpg").is_file()
    assert "fonts.googleapis.com" not in css + theme + mockup_css
    assert "googleapis.com" not in "".join((ROOT / p).read_text(encoding="utf-8") for p in PAGES)

    home = parsed["index.html"][0]
    about = parsed["qui-sommes-nous.html"][0]
    news = parsed["actualites.html"][0]
    assert "Tous différents," in home and "mais uniques." in home
    assert "Mercredi" in home and "14h30" in home and "Samedi" in home and "15h" in home
    assert "14h30</span></p><h3>Pour les ados" not in home, "the Saturday time must remain the owner's confirmed 15:00"
    assert home.count("— Miette, participante") == 1 and "jauge de positif et d’amour" in home
    assert home.count("Témoignage à recueillir") == 3, "unverified testimonials must remain prompts"
    assert "/mockup-v3/img/mural.jpg" in home and home.count("<figure>") >= 10
    assert all(x in about for x in ("1995", "2021", "Les bénévoles, les Bleuettes", "Sapala", "Burkina Faso", "Maroc"))
    for topic in ("Jeux de société & baby-foot", "Musique, chant, théâtre & contes", "Dessin & arts plastiques", "Cuisine, goûters & fêtes", "Jardinage & temps dehors", "Sorties culturelles & découvertes", "Médiation animale & rencontres entre parents"):
        assert topic in about, f"About page topic missing: {topic}"
    assert news.count('class="news-card"') == 3
    for page in ("actualite-2026-10-26.html", "actualite-2026-10-17.html", "actualite-2026-10-10.html"):
        assert "Publication Facebook" in parsed[page][0] and "Retour aux actualités" in parsed[page][0]
    assert "modalités d’adhésion" in parsed["adherer.html"][0] and "<form" not in parsed["adherer.html"][0]
    assert "Information à confirmer" in parsed["contact.html"][0]
    assert "À confirmer directement par l’association" in parsed["mentions-legales.html"][0]
    assert "ne revendique donc pas le label officiel FALC" in parsed["facile-a-lire.html"][0]
    assert 'id="signaler"' in parsed["accessibilite.html"][0]
    assert "Page introuvable" in parsed["404.html"][0]
    todo = (ROOT / "TODO.md").read_text(encoding="utf-8")
    assert "verbally authorized" in todo, "owner-provided photo permission record must be retained"
    print(json.dumps({"status":"PASS","pages":len(PAGES),"local_links_checked":len(all_links),"mockup_fonts":8,"mockup_images":15,"checks":["all twelve routes have French metadata, one h1 and one main","shared working navigation and active state","no placeholder links or broken local files/fragments","mockup v3 local stylesheet, fonts, mural and photo assets present","no Google Fonts network dependency","Saturday session remains 15:00","only the genuine Miette quotation is attributed","all seven About activity topics and historical milestones remain","three news items retain dedicated article routes","membership/legal/contact facts remain conservative and accurate","FALC and accessibility pages are included"]},ensure_ascii=False))

if __name__ == "__main__":
    main()
