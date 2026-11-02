#!/usr/bin/env python3
"""Validate the multi-page information architecture and shared navigation."""
from html.parser import HTMLParser
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
PAGES=("index.html","la-bulle.html","activites.html","actualites.html","apail.html","contact.html")
class PageParser(HTMLParser):
 def __init__(self):
  super().__init__(); self.lang=None; self.title=False; self.description=False; self.h1=0; self.main=0; self.ids=set(); self.links=[]; self.nav_depth=0; self.nav_links=[]; self.current_nav=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="html": self.lang=a.get("lang")
  if tag=="title": self.title=True
  if tag=="h1": self.h1+=1
  if tag=="main": self.main+=1
  if a.get("id"): self.ids.add(a["id"])
  if tag=="meta" and a.get("name")=="description" and a.get("content"): self.description=True
  if tag=="nav" and a.get("id")=="navigation": self.nav_depth+=1
  if tag=="a" and a.get("href"):
   self.links.append(a["href"])
   if self.nav_depth:
    self.nav_links.append(a["href"])
    if a.get("aria-current")=="page": self.current_nav.append(a["href"])
 def handle_endtag(self,tag):
  if tag=="nav" and self.nav_depth: self.nav_depth-=1
def main():
 for page in PAGES:
  path=ROOT/page; assert path.is_file() and path.stat().st_size>1000, f"missing/empty page: {page}"
  html=path.read_text(encoding="utf-8"); p=PageParser(); p.feed(html)
  assert p.lang=="fr" and p.title and p.description, f"{page}: language/title/description"
  assert p.h1==1 and p.main==1, f"{page}: expected one h1 and main"
  assert p.nav_links==list(PAGES), f"{page}: shared navigation/order {p.nav_links}"
  assert p.current_nav==[page], f"{page}: active nav state"
  assert all(h[1:] in p.ids for h in p.links if h.startswith("#")), f"{page}: broken fragment"
  for href in p.links:
   if re.match(r"^(index|la-bulle|activites|actualites|apail|contact)\.html$",href): assert (ROOT/href).is_file(), f"{page}: broken local link {href}"
  for asset in re.findall(r'(?:src|href)="/([^"]+)"',html): assert (ROOT/asset).is_file(), f"{page}: missing local asset {asset}"
  assert "https://www.facebook.com/p/Bulle-Bleue-APAiL-100066715807933/" in html
 home=(ROOT/"index.html").read_text(encoding="utf-8")
 assert len(home)<9000, "homepage too long"
 assert all(page in home for page in PAGES[1:])
 assert "30 Rempart Saint-Vincent" not in home and "Sapala" not in home
 audience=(ROOT/"la-bulle.html").read_text(encoding="utf-8")
 assert all(x in audience for x in ("Enfants de plus de 6 ans","Adolescents et adultes","14 h 30","15 h","11 mars 2024","confirmer les horaires"))
 activities=(ROOT/"activites.html").read_text(encoding="utf-8")
 assert all(x in activities for x in ("Jeux & convivialité","Musique & scène","Arts & création","Cuisine & fêtes","Jardin & nature","Ciné Relax","Médiation animale"))
 news=(ROOT/"actualites.html").read_text(encoding="utf-8")
 assert all(x in news for x in ("26 octobre 2026","17 octobre 2026","10 octobre 2026","20 septembre 2026"))
 apail=(ROOT/"apail.html").read_text(encoding="utf-8")
 assert all(x in apail for x in ("1995","2021","Sapala","Moulay-Bousselham","Dcheira","les Bleuettes","Association Valentin Haüy"))
 contact=(ROOT/"contact.html").read_text(encoding="utf-8")
 assert all(x in contact for x in ("apail@live.fr","30 Rempart Saint-Vincent","rue Leriche","11 mars 2024","Confirmez le lieu"))
 css=(ROOT/"styles.css").read_text(encoding="utf-8"); js=(ROOT/"script.js").read_text(encoding="utf-8")
 assert "prefers-reduced-motion" in css and "@media(max-width:980px)" in css
 assert 'aria-current="page"]' in css
 assert "event.key !== 'Escape' || toggle.getAttribute('aria-expanded') !== 'true'" in js
 print("PASS: six pages, shared navigation, active-page state, metadata, content allocation, concise homepage, local links and accessibility safeguards")
if __name__=="__main__": main()
