#!/usr/bin/env python3
"""Dependency-free structure, content and source-provenance checks."""
from html.parser import HTMLParser
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
FACEBOOK="https://www.facebook.com/p/Bulle-Bleue-APAiL-100066715807933/"

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.lang=None; self.h1=0; self.main=0
        self.sections=[]; self.ids=set(); self.links=[]; self.images=[]; self.description=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="html": self.lang=a.get("lang")
        if tag=="h1": self.h1+=1
        if tag=="main": self.main+=1
        if tag=="section": self.sections.append(a.get("id",""))
        if a.get("id"): self.ids.add(a["id"])
        if tag=="a" and a.get("href"): self.links.append(a["href"])
        if tag=="img": self.images.append(a)
        if tag=="meta" and a.get("name")=="description" and a.get("content"): self.description=True

def main():
    required=("index.html","styles.css","script.js","assets/favicon.svg","tests/test_menu.js","Bulle_Bleue_APAiL_contenu_facebook.md")
    for name in required:
        p=ROOT/name
        assert p.is_file() and p.stat().st_size, f"missing required file: {name}"
    html=(ROOT/"index.html").read_text(encoding="utf-8")
    css=(ROOT/"styles.css").read_text(encoding="utf-8")
    js=(ROOT/"script.js").read_text(encoding="utf-8")
    source=(ROOT/"Bulle_Bleue_APAiL_contenu_facebook.md").read_text(encoding="utf-8")
    p=Parser(); p.feed(html)
    assert p.lang=="fr" and p.h1==1 and p.main==1 and p.description
    expected=["accueil","publics","activites","actualites","association","contact"]
    assert p.sections==expected, f"unexpected section sequence: {p.sections}"
    assert all(h[1:] in p.ids for h in p.links if h.startswith("#")), "broken anchor"
    assert len(p.images)==0, "participant/social photographs are not approved yet"
    assert html.count(FACEBOOK)==3, "Facebook route should appear in JSON-LD, contact and footer"
    assert html.count("mailto:apail@live.fr")>=2
    required_copy=("30 Rempart Saint-Vincent","rue Leriche","14 h 30","15 h","Enfants de plus de 6 ans","Adolescents et adultes","Jeux & convivialité","Médiation animale","Ciné Relax","26 octobre 2026","17 octobre 2026","10 octobre 2026","Association Valentin Haüy","1995","2021","Sapala","Moulay-Bousselham","Dcheira","les Bleuettes","Hypersuper TDAH France","2 novembre 2026")
    missing=[x for x in required_copy if x not in html]
    assert not missing, f"missing Facebook-derived content: {missing}"
    assert "Source : https://www.facebook.com/p/Bulle-Bleue-APAiL-100066715807933/" in source
    assert "02/11/2026" in source
    assert "confirmer les horaires" in html and "Confirmez le lieu" in html
    assert "ne constituent pas un programme hebdomadaire garanti" in html
    assert "ne signifient pas que chaque projet est encore en cours" in html
    for asset in re.findall(r'(?:src|href)="/([^"]+)"',html):
        assert (ROOT/asset).is_file(), f"missing local asset /{asset}"
    assert "prefers-reduced-motion" in css
    assert "event.key !== 'Escape' || toggle.getAttribute('aria-expanded') !== 'true'" in js
    assert "fonts.googleapis.com" not in css and "fonts.gstatic.com" not in css
    assert "11 mars 2024" in html and "Structures citées" in html
    print("PASS: six sections, source-led content, source/age caveats, Facebook/email routes, anchors, assets and accessibility safeguards")

if __name__=="__main__": main()
