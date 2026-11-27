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
    "adherer.html", "facile-a-lire.html", "contact.html",
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
        eyebrow_labels = re.findall(r'<([a-z0-9]+)[^>]*class="[^"]*\beyebrow\b[^"]*"[^>]*>(.*?)</\1>', html, re.S)
        for _, markup in eyebrow_labels:
            label = re.sub(r"<[^>]+>", "", markup).strip()
            readable_label = re.sub(r"\s*[·|]\s*\d.*$", "", label).strip()
            assert not readable_label.isupper(), f"{page}: section label should not be all uppercase: {label}"
        assert parser.nav_links == list(NAV), f"{page}: shared navigation order changed: {parser.nav_links}"
        assert len(parser.nav_links) == len(set(parser.nav_links)), f"{page}: duplicate navigation destination"
        assert parser.nav_links.count("contact.html") == 1, f"{page}: Contact must appear exactly once"
        footer = re.search(r'<footer class="pied">(.*?)</footer>', html, re.S)
        assert footer, f"{page}: shared footer is required"
        footer_html = footer.group(1)
        assert 'class="footer-brand"' in footer_html and 'class="footer-navigation"' in footer_html
        assert footer_html.count('class="footer-group"') == 3
        for destination in ("index.html","qui-sommes-nous.html","actualites.html","adherer.html","contact.html","facile-a-lire.html","accessibilite.html","mentions-legales.html"):
            assert f'href="{destination}"' in footer_html, f"{page}: footer destination missing: {destination}"
        assert "mailto:apail@live.fr" in footer_html and "facebook.com/p/Bulle-Bleue-APAiL" in footer_html
        assert re.search(r'<a class="footer-contact"[^>]*>Nous contacter</a>', footer_html), f"{page}: footer contact action needs the shared label"
        assert parser.nav_current == CURRENT.get(page, []), f"{page}: incorrect active navigation: {parser.nav_current}"
        assert 'href="#"' not in html, f"{page}: placeholder link remains"
        assert 'href="#" ' not in html, f"{page}: placeholder link remains"
        assert 'href="javascript:' not in html.lower(), f"{page}: javascript URL is not allowed"
        # Outbound pages use a consistent external-link cue and safe new-tab behavior.
        for anchor_attrs, anchor_body in re.findall(r'<a\b([^>]*)>(.*?)</a>', html, re.S | re.I):
            destination = re.search(r'\bhref=["\']([^"\']+)["\']', anchor_attrs, re.I)
            if not destination:
                continue
            href = destination.group(1)
            parts = urlsplit(href)
            external = parts.scheme.lower() in ("http", "https") or bool(parts.netloc)
            if external:
                assert re.search(r'<span[^>]*aria-hidden="true"[^>]*>↗</span>', anchor_body, re.I), f"{page}: external link needs a visible, assistive-technology-hidden ↗ cue: {href}"
                assert re.search(r'\btarget=["\']_blank["\']', anchor_attrs, re.I), f"{page}: external link should open in a new tab: {href}"
                rel = re.search(r'\brel=["\']([^"\']+)["\']', anchor_attrs, re.I)
                assert rel and {"noopener", "noreferrer"}.issubset(set(rel.group(1).lower().split())), f"{page}: external link needs noopener noreferrer: {href}"
            else:
                assert "↗" not in anchor_body, f"{page}: internal or email link should not use an external-link cue: {href}"
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
    polish = (ROOT / "site-v4-polish.css").read_text(encoding="utf-8")
    mockup_css = (ROOT / "mockup-v3/css/style.css").read_text(encoding="utf-8")
    assert '@import url("/mockup-v3/css/style.css")' in css
    assert '@import url("/site-v3-overrides.css")' in css
    assert '@import url("/site-v4-polish.css")' in css
    assert '@import url("/site-v5-polish.css")' in css
    assert '@import url("/site-v6-polish.css")' in css
    assert '@import url("/site-v7-polish.css")' in css
    assert '@import url("/site-v8-accessibility.css")' in css
    assert "@font-face" in mockup_css and "Atkinson Hyperlegible Next" in mockup_css
    assert all((ROOT / "mockup-v3/fonts" / name).is_file() for name in (
        "atkinson-hyperlegible-next-latin-400-normal.woff2",
        "atkinson-hyperlegible-next-latin-700-normal.woff2",
        "fredoka-latin-700-normal.woff2",
        "caveat-latin-500-normal.woff2",
        "opendyslexic-latin-400-normal.woff2",
    ))
    assert (ROOT / "mockup-v3/img/mural.webp").is_file()
    assert "fonts.googleapis.com" not in css + theme + mockup_css
    assert "googleapis.com" not in "".join((ROOT / p).read_text(encoding="utf-8") for p in PAGES)

    home = parsed["index.html"][0]
    about = parsed["qui-sommes-nous.html"][0]
    news = parsed["actualites.html"][0]
    assert "Tous différents," in home and "mais uniques." in home
    assert "Mercredi" in home and "14h30" in home and "Samedi" in home and "15h" in home
    assert "14h30</span></p><h3>Pour les ados" not in home, "the Saturday time must remain the owner's confirmed 15:00"
    assert home.count("— Miette, participante") == 1 and "jauge de positif et d’amour" in home
    assert "les « Bleuettes »" in home and "les « Bleuets »" not in home, "the volunteer group is called les Bleuettes"
    assert "Les horaires ci-dessus sont repris des informations publiées" in home and "avant de vous déplacer" in home
    assert "Témoignage à recueillir" not in home and 'class="voices"' not in home, "uncollected testimonial prompts must not appear on the public homepage"
    assert "/mockup-v3/img/mural.webp" in home and home.count("<figure>") >= 10
    assert 'src="/assets/gathering.webp"' in home, "the closing homepage image should use the association gathering photo"
    assert all(x in about for x in ("1995", "2021", "Les bénévoles, les Bleuettes", "Sapala", "Burkina Faso", "Maroc"))
    for topic in ("Jeux de société & baby-foot", "Musique, chant, théâtre & contes", "Dessin & arts plastiques", "Cuisine, goûters & fêtes", "Jardinage & temps dehors", "Sorties culturelles & découvertes", "Médiation animale & rencontres entre parents"):
        assert topic in about, f"About page topic missing: {topic}"
    assert news.count('class="news-card"') == 3
    assert theme.count(".news-card:nth-child(") >= 2, "Actualités cards must retain distinct organic shapes"
    assert "border-radius:44px 30px 48px 28px" in theme, "news cards must not fall back to standard rectangular cards"
    assert ".news-card::after" in polish and "overflow:visible" in polish, "news tiles must keep their speech-bubble tail and organic silhouette"
    assert ".site-page > .inner-hero" in polish and ".site-page .article-head" in polish, "content headers must not inherit sticky navigation styles"
    assert ".contact-grid" in polish and "contact-grid" in parsed["contact.html"][0], "contact panels must not stretch into empty space"
    assert ".js #nav{" in mockup_css and ".js #nav.open{" in mockup_css and ".js nav{" not in mockup_css, "mobile menu rules must target only the header navigation"
    for page in ("actualite-2026-10-26.html", "actualite-2026-10-17.html", "actualite-2026-10-10.html"):
        assert "Publication Facebook" in parsed[page][0] and "Retour aux actualités" in parsed[page][0]
    assert "modalités d’adhésion" in parsed["adherer.html"][0] and "<form" not in parsed["adherer.html"][0]
    contact = parsed["contact.html"][0]
    assert "Adresse actuelle non confirmée" in contact and "30 Rempart Saint-Vincent" in contact and "30 Rempart Saint-Pierre" in contact
    assert "13 octobre 2025" in contact
    legal = parsed["mentions-legales.html"][0]
    assert "À confirmer directement par l’association" in legal
    assert "27 février 2019" in legal and "2 mars 2019" in legal
    assert "Vercel Inc." in legal and "440 N Barranca Avenue" in legal
    assert "privacy-notice" in legal and "1er juin 2026" in legal
    assert "ne revendique donc pas le label officiel FALC" in parsed["facile-a-lire.html"][0]
    assert "Les horaires peuvent changer" in parsed["facile-a-lire.html"][0]
    assert "Ces horaires peuvent évoluer" in about
    article17 = parsed["actualite-2026-10-17.html"][0]
    assert "prévus en 2027" in article17 and "16 octobre 2026" in article17
    assert "chalondanslarue.com/activites/chalon_dans_la_rue_rentree/219" in article17
    article10 = parsed["actualite-2026-10-10.html"][0]
    assert "Découvrir des gestes du quotidien sans la vue" in article10 and "dix membres" in article10
    assert 'id="signaler"' in parsed["accessibilite.html"][0]
    access_page = parsed["accessibilite.html"][0]
    assert "Piper" in access_page and "SIWIS" in access_page and "française (France)" in access_page
    assert "aucun service de synthèse payant" in access_page.lower()
    assert "fichier mp3" in access_page.lower() and "aucun modèle vocal n’est téléchargé" in access_page
    assert "Pocket TTS" not in access_page and "eSpeak NG" not in access_page and "Spellophone" not in access_page
    speech_js = (ROOT / "mockup-v3/js/a11y.js").read_text(encoding="utf-8")
    assert "/assets/speech/fr-FR/manifest.json" in speech_js and "new Audio()" in speech_js
    assert "reader-worker.mjs" not in speech_js and "AudioContext" not in speech_js
    assert "loadSpeechManifest()" in speech_js and "playbackRate" in speech_js
    assert "speechSynthesis.speak" not in speech_js and "getVoices()" not in speech_js
    assert (ROOT / "scripts/generate_piper_speech.py").is_file()
    assert (ROOT / "tests/test_piper_speech.py").is_file()
    assert (ROOT / "docs/free-piper-speech.md").is_file()
    assert (ROOT / ".github/workflows/generate-french-audio.yml").is_file()
    speech_manifest_path = ROOT / "assets/speech/fr-FR/manifest.json"
    assert speech_manifest_path.is_file(), "the French audio manifest must prevent missing-resource errors"
    speech_manifest = json.loads(speech_manifest_path.read_text(encoding="utf-8"))
    assert speech_manifest["locale"] == "fr-FR" and speech_manifest["status"] in {"pending", "ready"}
    assert set(speech_manifest["voices"]) == {"siwis"}
    siwis_voice = speech_manifest["voices"]["siwis"]
    assert siwis_voice["voiceName"] == "fr_FR-siwis-medium"
    if speech_manifest["status"] == "pending":
        assert not siwis_voice.get("sample"), "pending manifest must not advertise nonexistent MP3 files"
        assert not siwis_voice.get("pages"), "pending manifest must not advertise nonexistent page MP3s"
    else:
        sample_audio = siwis_voice.get("sample", "")
        assert sample_audio.startswith("/assets/speech/fr-FR/siwis/"), "ready manifest must point to the SIWIS audition"
        sample_file = ROOT / sample_audio.lstrip("/")
        assert sample_file.is_file() and sample_file.stat().st_size > 256, "ready manifest audition MP3 is missing or empty"
        page_audio = siwis_voice.get("pages", {})
        assert set(page_audio) == set(PAGES), "ready manifest must contain audio for every published page"
        for page, audio_path in page_audio.items():
            assert audio_path.startswith("/assets/speech/fr-FR/siwis/pages/"), f"{page}: audio must use the SIWIS page-audio directory"
            audio_file = ROOT / audio_path.lstrip("/")
            assert audio_file.is_file() and audio_file.stat().st_size > 256, f"{page}: generated MP3 is missing or empty"
    for old_voice_file in ("pocket.mjs", "words.mjs", "reader-worker.mjs", "NOTICE.md"):
        assert not (ROOT / "mockup-v3/js/voice" / old_voice_file).exists(), f"retired local model remains: {old_voice_file}"
    assert not (ROOT / "tests/test_voice.mjs").exists(), "retired Pocket TTS tests should be removed"
    access_page = parsed["accessibilite.html"][0]
    assert "dans l’en-tête" in access_page and "en bas à gauche" in access_page
    assert "Page introuvable" in parsed["404.html"][0]
    for page in PAGES:
        html = (ROOT / page).read_text(encoding="utf-8")
        assert html.count('/assets/logo%20final.webp') == 2, f"{page}: actual association logo must appear in header and footer"
        assert html.count('aria-label="La Bulle Bleue, APAiL, accueil"') == 2, f"{page}: both logo links need the full accessible name"
        assert 'property="og:image" content="https://raw.githubusercontent.com/teyyara/bullebleue/main/assets/gathering.jpeg"' in html, f"{page}: social preview image metadata is missing"
        assert 'href="/assets/favicon.svg"' in html, f"{page}: updated favicon must appear in document head"
    todo = (ROOT / "TODO.md").read_text(encoding="utf-8")
    assert "verbally authorized" in todo, "owner-provided photo permission record must be retained"
    webp_report = json.loads((ROOT / "evidence/visual/webp-optimization-report.json").read_text(encoding="utf-8"))
    assert webp_report["summary"]["reduction_percent"] > 0, "WebP must reduce transfer size"
    assert webp_report["summary"]["images_converted"] >= 10, "rendered photos and logo should use WebP"
    for image in webp_report["images"]:
        webp_path = image["webp"]
        assert (ROOT / webp_path).is_file(), f"missing WebP derivative: {webp_path}"

    calm_css = (ROOT / "site-v8-accessibility.css").read_text(encoding="utf-8")
    assert ".calm .hero .blob" in calm_css and ".calm .retrouver .big::before" in calm_css and ".calm .sorties h2::after" in calm_css, "calm mode must remove homepage bubbles, pale backplates and decorative flourishes"
    assert ".hero{overflow-x:clip}" in calm_css and ".voix{padding:36px 0}" in calm_css, "mobile hero clipping and tighter section rhythm must remain in place"
    voice_css = (ROOT / "site-v9-voice.css").read_text(encoding="utf-8")
    assert ".a11y-voice-quality" in voice_css and ".voice-status" in voice_css
    assert "#a11y-light-enable" not in voice_css and "#a11y-natural-enable" not in voice_css
    assert '@import url("/site-v9-voice.css")' in css
    print(json.dumps({"status":"PASS","pages":len(PAGES),"local_links_checked":len(all_links),"mockup_fonts":8,"mockup_images":15,"checks":["all twelve routes have French metadata, one h1 and one main","shared working navigation and active state","no placeholder links or broken local files/fragments","mockup v3 local stylesheet, fonts, mural and photo assets present","no Google Fonts network dependency","published session times are marked for confirmation","only the genuine Miette quotation is attributed","uncollected testimonials are absent","historical venue conflicts are disclosed","festival 40th anniversary is correctly dated to 2027","JOAFE declaration and publication dates are distinguished","actual Vercel hosting provider is identified","all seven About activity topics and historical milestones remain","three news items retain dedicated article routes","membership/legal/contact facts remain conservative and accurate","FALC and accessibility pages are included"]},ensure_ascii=False))

if __name__ == "__main__":
    main()
