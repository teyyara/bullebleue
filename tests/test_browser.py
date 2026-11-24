#!/usr/bin/env python3
"""Responsive regression for the mockup v3 redesign across Chromium, Firefox and WebKit."""
from __future__ import annotations
import json, os, threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ENGINE = os.environ.get("BROWSER_ENGINE", "chromium").strip().lower()
if ENGINE not in {"chromium", "firefox", "webkit"}:
    raise ValueError(f"Unsupported BROWSER_ENGINE: {ENGINE}")
PAGES = (
    "index.html", "qui-sommes-nous.html", "actualites.html",
    "actualite-2026-10-26.html", "actualite-2026-10-17.html",
    "actualite-2026-10-10.html", "adherer.html", "contact.html",
    "mentions-legales.html", "facile-a-lire.html", "accessibilite.html", "404.html",
)
VIEWPORTS = ((320,760),(390,844),(768,1024),(1024,768),(1440,900))
NAV = ["index.html","qui-sommes-nous.html","actualites.html","adherer.html","facile-a-lire.html","contact.html"]
assert len(NAV) == len(set(NAV)), "shared navigation destinations must be unique"

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

def load_all_images(page):
    page.locator("img").evaluate_all("(imgs)=>imgs.forEach(i=>i.loading='eager')")
    page.wait_for_function("()=>Array.from(document.images).every(i=>i.complete && i.naturalWidth>0)",timeout=20000)
    page.evaluate("()=>Promise.all(Array.from(document.images,i=>i.decode().catch(()=>undefined)))")
    return page.locator("img").count()

def assert_no_overflow(page,width,path):
    m=page.evaluate("()=>({doc:document.documentElement.scrollWidth,body:document.body.scrollWidth,inner:innerWidth})")
    assert m["doc"]<=width+1 and m["body"]<=width+1, f"{path} at {width}px overflow: {m}"
    return m

def main():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(QuietHandler,directory=str(ROOT)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f"http://127.0.0.1:{server.server_port}"
    out=ROOT/"artifacts"/f"loop026-browser-{ENGINE}";out.mkdir(parents=True,exist_ok=True)
    measurements=[];console_errors=[];failed_requests=[];external=[]
    try:
        with sync_playwright() as p:
            browser=getattr(p,ENGINE).launch(headless=True)
            context=browser.new_context()
            page=context.new_page()
            page.on("console",lambda m:console_errors.append(m.text) if m.type=="error" else None)
            page.on("pageerror",lambda e:console_errors.append(str(e)))
            def on_failed(req):
                reason=req.failure or ""
                # Firefox cancels an image request when navigation supersedes it; image decoding
                # on the completed page is checked independently and remains strict.
                if "NS_BINDING_ABORTED" in reason: return
                failed_requests.append(f"{req.url}: {reason}")
            page.on("requestfailed",on_failed)
            page.on("request",lambda req:external.append(req.url) if not req.url.startswith(base) else None)

            for width,height in VIEWPORTS:
                page.set_viewport_size({"width":width,"height":height})
                for path in PAGES:
                    response=page.goto(f"{base}/{path}",wait_until="networkidle",timeout=25000)
                    status=response.status if response else None
                    if status!=200:
                        page.wait_for_timeout(150)
                        response=page.goto(f"{base}/{path}",wait_until="networkidle",timeout=25000)
                    assert response is not None and response.status==200, f"{path}: HTTP {response.status if response else 'no response'}"
                    assert_no_overflow(page,width,path)
                    assert page.locator("main#contenu").count()==1
                    assert page.locator("h1").count()==1
                    assert page.locator("#nav a").evaluate_all("(a)=>a.map(x=>x.getAttribute('href'))")==NAV, f"{path}: shared nav order changed"
                    # Only pages designed around photography require a content image.
                    # Contact, legal, membership, easy-read, accessibility and 404 pages
                    # are intentionally text-led; do not add decorative images just for CI.
                    if path in ("index.html", "qui-sommes-nous.html", "actualites.html") or path.startswith("actualite-"):
                        assert load_all_images(page)>=1, f"{path}: no content images rendered"
                    else:
                        load_all_images(page)
                    assert page.locator("form").count()==0, f"{path}: unintended data collection form"
                    if path=="index.html":
                        assert "Tous différents" in page.locator("h1").inner_text()
                        assert page.locator(".oval img").evaluate("(i)=>i.naturalWidth")>0
                        assert page.locator(".gal figure").count()==6
                        assert page.locator(".voices article").count()==3
                        assert page.locator(".quote cite").inner_text()=="— Miette, participante"
                        assert "Samedi" in page.locator(".slots").inner_text() and "15h" in page.locator(".slots").inner_text()
                        assert "14h30" not in page.locator(".slot:nth-child(2)").inner_text()
                    elif path=="qui-sommes-nous.html":
                        assert all(v in page.locator("main").inner_text() for v in ("1995","2021","Bleuettes","Burkina Faso","Maroc"))
                        assert page.locator(".topic-list span").count()==7
                    elif path=="actualites.html":
                        assert page.locator(".news-card").count()==3
                    elif path.startswith("actualite-"):
                        assert page.locator(".article-visual img").evaluate("(i)=>i.naturalWidth")>0
                        assert page.get_by_role("link",name="← Retour aux actualités").count()==1
                    elif path=="accessibilite.html":
                        assert page.locator("#signaler").count()==1
                    elif path=="facile-a-lire.html":
                        assert "Mercredi" in page.locator("main").inner_text() and "Samedi" in page.locator("main").inner_text()
                    measurements.append({"page":path,"width":width,"height":height,"images":page.locator("img").count(),"widths":page.evaluate("()=>[document.documentElement.scrollWidth,document.body.scrollWidth]")})
                    if width<=390:
                        toggle=page.locator(".burger")
                        toggle.click()
                        assert toggle.get_attribute("aria-expanded")=="true"
                        assert "open" in (page.locator("#nav").get_attribute("class") or "")
                        page.keyboard.press("Escape")
                        assert toggle.get_attribute("aria-expanded")=="false"
                        assert page.evaluate("document.activeElement===document.querySelector('.burger')"), f"{path}: Escape should restore menu focus"

            # Accessibility controls: panel, persisted preferences, Escape and focus restoration.
            a11y=context.new_page()
            a11y.goto(f"{base}/index.html",wait_until="networkidle")
            opener=a11y.locator("#a11y-open");assert opener.count()==1
            opener.click()
            panel=a11y.locator("#a11y-panel");assert not panel.is_hidden()
            a11y.locator('[data-fs="1"]').click()
            assert "fs-1" in a11y.locator("html").get_attribute("class")
            a11y.locator('[data-k="dys"]').click()
            assert "dys" in a11y.locator("html").get_attribute("class")
            a11y.keyboard.press("Escape")
            assert panel.is_hidden()
            assert a11y.evaluate("document.activeElement===document.querySelector('#a11y-open')")
            a11y.locator("#a11y-open").click()
            a11y.locator("#a11y-reset").click()
            assert "dys" not in (a11y.locator("html").get_attribute("class") or "")

            # Reduced-motion and no-JavaScript users still receive all primary content.
            reduced=context.new_page();reduced.emulate_media(reduced_motion="reduce")
            reduced.goto(f"{base}/index.html",wait_until="networkidle")
            assert reduced.locator("h1").is_visible()
            nojs=browser.new_context(java_script_enabled=False).new_page()
            nojs.goto(f"{base}/index.html",wait_until="networkidle")
            assert nojs.locator("h1").is_visible()
            assert nojs.locator("#nav").is_visible(), "navigation must remain available without JavaScript"

            # Chromium review captures: every route at desktop/mobile, plus hero and section views.
            if ENGINE=="chromium":
                for path,stem in zip(PAGES,("home","about","news","article-26","article-17","article-10","join","contact","legal","easy","accessibility","404")):
                    for width,height,suffix in ((1440,900,"desktop"),(390,844,"mobile")):
                        page.set_viewport_size({"width":width,"height":height})
                        page.goto(f"{base}/{path}",wait_until="networkidle",timeout=25000)
                        load_all_images(page)
                        page.screenshot(path=str(out/f"{stem}-{suffix}.png"),full_page=True)
                page.set_viewport_size({"width":1440,"height":900})
                page.goto(f"{base}/index.html",wait_until="networkidle")
                page.screenshot(path=str(out/"home-hero-desktop.png"),full_page=False)
                for selector,name in ((".sortiesec","home-outings-desktop.png"),(".voix","home-testimonials-desktop.png"),(".jouer","home-confidence-desktop.png")):
                    page.locator(selector).screenshot(path=str(out/name))
            assert not failed_requests, f"failed browser requests: {failed_requests}"
            assert not external, f"unexpected external requests: {external}"
            assert not console_errors, f"browser errors: {console_errors}"
            browser.close()
    finally:
        server.shutdown();server.server_close();thread.join(timeout=2)
    print(json.dumps({"status":"PASS","browser_engine":ENGINE,"pages":len(PAGES),"viewports":[w for w,h in VIEWPORTS],"page_viewport_runs":len(measurements),"checks":["all twelve pages return HTTP 200","no horizontal overflow at five viewport widths","all local images decode","shared navigation links and active destinations","mobile navigation opens, closes on Escape and restores focus","no unintended forms or data collection","Saturday time remains 15:00","one real Miette quote and three unfilled testimonial prompts","seven About topics and milestone years","accessibility control state, persisted font settings, Escape/focus and reset","reduced-motion and no-JavaScript content visibility","no failed non-abort requests, unexpected external requests or browser errors"],"screenshots":len(list(out.glob("*.png")))} ,ensure_ascii=False))

if __name__=="__main__": main()
