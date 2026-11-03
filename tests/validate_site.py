#!/usr/bin/env python3
"""Validate the Loop 012 public pages, article routes, shared navigation and sticky story."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote
import re

ROOT = Path(__file__).resolve().parents[1]
PAGES = (
    "index.html", "qui-sommes-nous.html", "actualites.html", "adherer.html",
    "contact.html", "mentions-legales.html",
    "actualite-2026-10-26.html", "actualite-2026-10-17.html", "actualite-2026-10-10.html",
)
NAV = ("index.html", "qui-sommes-nous.html", "actualites.html", "adherer.html", "contact.html")
EXPECTED_CURRENT = {
    "index.html": ("index.html", "page"),
    "qui-sommes-nous.html": ("qui-sommes-nous.html", "page"),
    "actualites.html": ("actualites.html", "page"),
    "adherer.html": ("adherer.html", "page"),
    "contact.html": ("contact.html", "page"),
    "mentions-legales.html": (None, None),
    "actualite-2026-10-26.html": ("actualites.html", "location"),
    "actualite-2026-10-17.html": ("actualites.html", "location"),
    "actualite-2026-10-10.html": ("actualites.html", "location"),
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
        self.nav_depth = 0
        self.nav_links = []
        self.nav_current = []
        self.footer_current = []
        self.images = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title":
            self.title = True
        if tag == "h1":
            self.h1 += 1
        if tag == "main":
            self.main += 1
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "meta" and a.get("name") == "description" and a.get("content"):
            self.description = True
        if tag == "nav" and a.get("id") == "navigation":
            self.nav_depth += 1
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
            if self.nav_depth:
                self.nav_links.append(a["href"])
                if a.get("aria-current"):
                    self.nav_current.append((a["href"], a["aria-current"]))
            elif a.get("aria-current") == "page":
                self.footer_current.append(a["href"])
        if tag == "img":
            self.images.append(a)
    def handle_endtag(self, tag):
        if tag == "nav" and self.nav_depth:
            self.nav_depth -= 1

def main():
    parsed = {}
    for page in PAGES:
        path = ROOT / page
        assert path.is_file() and path.stat().st_size > 1000, f"missing/empty page: {page}"
        html = path.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(html)
        parsed[page] = (html, parser)
        assert parser.lang == "fr" and parser.title and parser.description, f"{page}: French metadata"
        assert parser.h1 == 1 and parser.main == 1, f"{page}: expected one h1 and main"
        assert parser.nav_links == list(NAV), f"{page}: shared navigation/order {parser.nav_links}"
        current_href, current_type = EXPECTED_CURRENT[page]
        if current_href:
            assert parser.nav_current == [(current_href, current_type)], f"{page}: active navigation {parser.nav_current}"
        else:
            assert parser.nav_current == [], f"{page}: legal page must not claim a main-nav current page"
            assert parser.footer_current == ["mentions-legales.html"], f"{page}: legal footer current state"
        assert all(h[1:] in parser.ids for h in parser.links if h.startswith("#")), f"{page}: broken fragment"
        for href in parser.links:
            if href.startswith("#") or href.startswith(("mailto:", "tel:", "https://", "http://")):
                continue
            target = unquote(href.split("?", 1)[0].split("#", 1)[0]).lstrip("/")
            if target:
                assert (ROOT / target).is_file(), f"{page}: broken local link {href}"
        for img in parser.images:
            src = unquote(img.get("src", ""))
            if src.startswith("/"):
                src = src.lstrip("/")
                assert (ROOT / src).is_file(), f"{page}: missing image {src}"
            assert "alt" in img, f"{page}: image missing alt text"
        assert html.count('src="/assets/logo%20final.png"') == 2, f"{page}: official logo header/footer"
        assert "https://www.facebook.com/p/Bulle-Bleue-APAiL-100066715807933/" in html, f"{page}: exact Facebook page"
        assert "#1642A5" in html, f"{page}: logo-derived theme metadata"
    for obsolete in ("la-bulle.html", "activites.html", "apail.html"):
        assert not (ROOT / obsolete).exists(), f"obsolete page still published: {obsolete}"

    home = parsed["index.html"][0]
    assert len(home) < 9000, "homepage must remain concise"
    assert home.count('class="story-step"') == 3, "homepage has exactly three scroll chapters"
    assert 'src="/assets/illustrations/hero-community.svg"' in home
    assert "home-hero-photo" not in home and "/assets/posts/" not in home
    assert all(h in home for h in ("Qui sommes-nous ?", "actualites.html", "adherer.html", "contact.html"))

    news = parsed["actualites.html"][0]
    assert news.count('class="news-card"') == 3, "news overview must show exactly three cards"
    assert news.count("Voir plus") == 3
    for slug in ("actualite-2026-10-26.html", "actualite-2026-10-17.html", "actualite-2026-10-10.html"):
        assert slug in news and (ROOT / slug).is_file(), f"news route missing: {slug}"
    for page, date, topic in (
        ("actualite-2026-10-26.html", "26 octobre 2026", "cuisine"),
        ("actualite-2026-10-17.html", "17 octobre 2026", "40 ans"),
        ("actualite-2026-10-10.html", "10 octobre 2026", "Association Valentin Haüy"),
    ):
        html = parsed[page][0]
        assert date in html and topic in html, f"{page}: dated content"

    about = parsed["qui-sommes-nous.html"][0]
    assert all(term in about for term in ("1995", "2021", "enfants de plus de 6 ans", "les Bleuettes", "Sapala", "Maroc"))
    join = parsed["adherer.html"][0]
    assert "Demander les modalités d’adhésion" in join and "cotisation" in join.lower()
    assert "<form" not in join.lower(), "membership page must not collect unnecessary sensitive information"
    contact = parsed["contact.html"][0]
    assert all(term in contact for term in ("apail@live.fr", "30 Rempart Saint-Vincent", "11 mars 2024", "confirmer le lieu"))
    legal = parsed["mentions-legales.html"][0]
    assert all(term in legal for term in ("Page à compléter", "Responsable de publication", "Hébergement", "À communiquer par l’association", "à confirmer"))

    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    js = (ROOT / "script.js").read_text(encoding="utf-8")
    assert ".story-art{position:sticky" in css and "html.has-scroll-story .story-step.is-current .story-panel" in css
    assert "@media(prefers-reduced-motion:reduce)" in css and "@media(max-width:760px)" in css
    assert "storySteps" in js and "prefers-reduced-motion" in js and "has-scroll-story" in js
    assert all(token in css for token in ("--ink:#06195E", "--blue:#1642A5", "--blue-mid:#1C60CF", "--blue-bright:#2084DE", "--sky:#4EABEC", "--blue-pale:#D3DEF0"))
    for svg in ("hero-community.svg", "games.svg", "culture.svg", "discovery.svg"):
        data = (ROOT / "assets/illustrations" / svg).read_text(encoding="utf-8")
        palette = {"#06195E", "#1642A5", "#1C60CF", "#2084DE", "#4EABEC", "#587ABA", "#9DC0EA", "#D3DEF0", "#F3F7FE", "#FCFDFF"}
        colours = {c.upper() for c in re.findall(r"#[0-9A-Fa-f]{6}", data)}
        assert colours and colours <= palette, f"{svg}: illustration contains colours outside the official logo palette and documented surface tints: {colours - palette}"

    favicon = (ROOT / "assets/favicon.svg").read_text(encoding="utf-8")
    assert all(c in favicon for c in ("#06195E", "#1642A5", "#1C60CF", "#2084DE", "#F3F7FE"))
    print("PASS: 9 pages, shared accessible navigation, 3 dated article routes, 3-card news overview, scroll-story, reduced-motion fallback, local assets and logo palette.")

if __name__ == "__main__":
    main()
