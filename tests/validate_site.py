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
    assert len(home) < 18000, "homepage should remain airy and concise"
    assert home.count('class="story-step ') == 3, "homepage has exactly three scroll chapters"
    drawings = ("dessin1.jpeg", "dessin2.jpeg", "dessin3.jpeg", "dessin4.jpeg", "dessin5.jpeg", "dessin6.jpeg", "dessin7.jpeg", "dessin8.jpeg", "dessin9.jpeg")
    assert home.count('class="drawing-sticker') == 9, "homepage collage uses exactly nine supplied drawings"
    for drawing in drawings:
        assert f'src="/assets/{drawing}"' in home, f"missing supplied homepage drawing: {drawing}"
    assert "hero-community.svg" not in home, "placeholder SVG hero is retired"
    assert "assets/posts/" not in home and "home-photo-section" not in home, "activity photos must be distributed to other pages, not crowded onto the homepage"
    assert home.count('src="/assets/gathering.jpeg"') == 1, "homepage has only the owner-selected closing gathering photo"
    assert home.count('class="home-after-photo"') == 1, "closing contact area includes the gathering photograph"
    assert (ROOT / "TODO.md").is_file(), "owner feedback must remain tracked in TODO.md"
    assert "verbally authorized" in (ROOT / "TODO.md").read_text(encoding="utf-8"), "owner's verbal image-use authorization is recorded"
    assert "home-hero-photo" not in home

    about = parsed["qui-sommes-nous.html"][0]
    about_photos = (
        "735543787_1361390089428172_5312506833854343201_n.jpg",
        "783036041_1408453024721878_3578205087320603775_n.jpg",
        "858642199_1459855032915010_3703135960600555271_n.jpg",
        "860039147_1459854696248377_603952803324221168_n.jpg",
        "860071516_1459854822915031_8736563633377469815_n.jpg",
        "861826539_1459854896248357_2220258804161137760_n.jpg",
        "863353686_1459854766248370_1734709857082262774_n.jpg",
        "863442942_1459854946248352_2630610521884942198_n.jpg",
    )
    assert about.count('class="community-photo-card"') == 8, "about page contains eight relevant activity photos"
    for photo in about_photos:
        assert f'src="/assets/posts/{photo}"' in about, f"missing activity photo on about page: {photo}"

    news = parsed["actualites.html"][0]
    group_photos = (
        "830754903_1438852398348607_8575046537706443389_n.jpg",
        "844190417_1446490757584771_1709901819062193861_n.jpg",
        "854414257_1451277357106111_100552518532689623_n.jpg",
    )
    assert news.count('class="community-photo-card"') == 3, "news page has a separate three-photo community strip"
    for photo in group_photos:
        assert f'src="/assets/posts/{photo}"' in news, f"missing undated community photo on news page: {photo}"
    assert "ne sont pas rattachées aux trois actualités datées" in news, "community photographs must not be misattributed to dated news"
    assert sum(f'src="/assets/posts/{photo}"' in page for page, _ in parsed.values() for photo in about_photos + group_photos) == 11, "all eleven supplied photographs appear across the two relevant secondary pages"
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
    assert all(term in legal for term in ("Page à compléter", "A.P.AI.L.", "Amitié Partage Aide Logistique, Matérielle et Morale", "W712002504", "519 970 743", "14, quai Gambetta", "14, boulevard de la République", "Responsable de publication", "Hébergement", "à confirmer"))
    assert "https://www.journal-officiel.gouv.fr/associations/detail-annonce/associations_b/20190009/1308" in legal
    assert "https://www.chalon.fr/annuaires-de-batimentsstructures/cartographie-des-associations-256/apail-aide-logistique-materielle-et-morale-2052.html" in legal

    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    js = (ROOT / "script.js").read_text(encoding="utf-8")
    assert ".story-art{position:sticky" in css and "html.has-scroll-story .story-step.is-current .story-panel" in css
    assert "--joy-coral:#FF8D83" in css and "--playful-font:" in css
    assert "border-radius:999px" in css and ".drawing-mural" in css and ".drawing-sticker--five" in css
    assert '"Fredoka"' in css and '"Atkinson Hyperlegible"' in css and '"Caveat"' in css
    assert ',system-ui,sans-serif' in css and '"Caveat",cursive;' in css
    assert ".main-nav .nav-contact{padding:10px 17px;border:2px solid #fff;border-radius:999px" in css
    assert ".story-panel h1,.story-panel h2{font-family:var(--playful-font);font-size:clamp(42px,4.6vw,60px)" in css
    assert ".page-intro{\n color:var(--joy-ink)" in css and ".solidarity-note{\n color:var(--joy-ink)" in css
    assert ".story-panel h1 em,.story-panel h2 em{color:var(--joy-blue)}" in css
    assert ".news-card::before" in css and "clip-path:polygon(" in css
    assert "news-card:nth-child(2)::before" in css and "news-card:nth-child(3)::before" in css
    assert "news-card:nth-child(2) .news-card-image" in css and "news-card:nth-child(3) .news-card-image" in css
    assert ".community-photo-grid--activities{grid-template-columns:repeat(4,minmax(0,1fr))}" in css
    assert ".community-photo-grid--gatherings{grid-template-columns:repeat(3,minmax(0,1fr))}" in css
    assert "@media(max-width:760px)" in css and ".home-photo-grid{grid-template-columns:1fr" in css
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
    # LOOP 019 owner-content, asset, testimonial and typography acceptance.
    assert "Bulle Bleue - APAiL" in home and "Tous différents, mais uniques." in home
    assert "Une association basée à CHALON-SUR-SAÔNE" in home
    assert "story-index" not in home and "01 / 03" not in home
    for text in ("Un lieu où l’on peut être soi.", "Mercredi · 14h30", "Samedi · 15h", "Sorties thématiques et culturelles", "séances Ciné Relax adaptées"):
        assert text in home, f"homepage owner copy missing: {text}"
    assert 'src="/assets/se%20retrouver.jpg.jpeg"' in home
    assert 'id="ils-en-parlent"' in home and "Ce que la Bulle change pour eux." in home
    assert "Miette, participante" in home and "Je remplis ma jauge de positif et d’amour" in home
    assert home.count('class="voice-card ') == 3 and home.count("Témoignage à recueillir") == 3
    assert "Vous aussi, vous fréquentez la Bulle ? Racontez-nous" in home
    for drawing in ("dessin6.jpeg", "dessin7.jpeg", "dessin8.jpeg", "dessin9.jpeg"):
        assert f'src="/assets/{drawing}"' in home, f"new owner drawing missing: {drawing}"
    assert "Prendre confiance" in home and "bb-collage" in home and "assets/posts/" not in home
    # LOOP 022: original sheets stay in the four-card collage; the sticky illustration uses 20 transparent per-character assets.
    expected_cutouts = {6: 6, 7: 4, 8: 1, 9: 9}
    cutout_files = sorted((ROOT / "assets/characters").glob("dessin*.svg"))
    assert len(cutout_files) == sum(expected_cutouts.values()), f"expected 20 individual cut-outs, found {len(cutout_files)}"
    for drawing, expected_count in expected_cutouts.items():
        files = sorted((ROOT / "assets/characters").glob(f"dessin{drawing}-*.svg"))
        assert len(files) == expected_count, f"drawing {drawing}: expected {expected_count} cut-outs, found {len(files)}"
        for cutout in files:
            svg = cutout.read_text(encoding="utf-8")
            assert "<clipPath" in svg and 'clip-path="url(#character-cutout)"' in svg, f"{cutout.name}: transparent silhouette clipping is required"
            assert f'href="../dessin{drawing}.jpeg"' in svg, f"{cutout.name}: original artwork must remain the pixel source"
            assert svg.count("<path ") == 1 and "<rect" not in svg, f"{cutout.name}: one hand-traced silhouette and no opaque background expected"
    for drawing in expected_cutouts:
        assert f'src="/assets/dessin{drawing}.jpeg"' in home, f"complete original drawing {drawing} must remain in Jouer/créer"
    for text in ("Une association, des bénévoles engagés.", "les « Bleuets » et « Bleuettes »", "Devenir bénévole", "Adhérer à l’APAiL"):
        assert text in home, f"homepage owner copy missing: {text}"
    for page, (html, _) in parsed.items():
        assert "Bulle Bleue - APAiL" in html, f"{page}: exact site identity in page metadata"
        assert "fonts.googleapis.com/css2?family=Atkinson" in html, f"{page}: owner typography stylesheet"
    print("PASS: 9 pages, owner-approved homepage copy, nine drawings, genuine testimonial only, adapted collage, eleven-photo secondary distribution, exact typography, reduced-motion, local assets and logo palette.")

if __name__ == "__main__":
    main()
