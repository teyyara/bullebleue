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
                    brand=page.locator("img.brand-mark")
                    assert brand.count()==2, f"{path}: association emblem must appear in header and footer"
                    assert brand.evaluate_all("(imgs)=>imgs.every(i=>i.complete && i.naturalWidth>0)"), f"{path}: association emblem image must load"
                    assert page.locator("header .logo b").inner_text()=="Bulle Bleue" and page.locator("header .logo small").inner_text()=="APAiL", f"{path}: readable association wordmark must accompany the emblem"
                    assert page.locator('link[rel="icon"]').get_attribute("href")=="/assets/favicon.svg", f"{path}: current bubble favicon must be used"
                    # Content headers must not inherit sticky site-navigation behaviour.
                    intro_header=page.locator("main.site-page > header.inner-hero")
                    if intro_header.count():
                        assert intro_header.evaluate("(el)=>getComputedStyle(el).position")=="relative", f"{path}: page intro must scroll with content"
                    article_header=page.locator("main.site-page .article-head")
                    if article_header.count():
                        assert article_header.evaluate("(el)=>getComputedStyle(el).position")=="relative", f"{path}: article title must scroll with content"
                    # Speech playback stays in the Accessibility panel rather than
                    # appearing as a repeated pill after every section heading.
                    assert page.locator("main .listen").count()==0, f"{path}: repeated section audio controls should not clutter the reading flow"
                    footer=page.locator("footer.pied")
                    assert footer.count()==1
                    assert footer.locator(".footer-brand .logo").count()==1
                    assert footer.locator(".footer-group").count()==3
                    assert footer.locator(".footer-navigation a").count()==9
                    assert footer.locator(".footer-contact").inner_text().strip()=="Nous contacter"
                    assert footer.locator(".footer-group a").evaluate_all("(links)=>links.every(a=>parseFloat(getComputedStyle(a).fontSize)>=16 && a.getBoundingClientRect().height>=44)"), f"{path}: footer navigation links must remain at least 16 px and 44 px tall"
                    assert footer.locator(".footer-bottom small, .footer-bottom span").evaluate_all("(items)=>items.every(el=>parseFloat(getComputedStyle(el).fontSize)>=16)"), f"{path}: footer legal/location text must remain at least 16 px"
                    if width<=620:
                        mobile_footer_layout=footer.locator(".footer-navigation").evaluate("(el)=>{const nav=el.getBoundingClientRect(),g=[...el.children].map(x=>x.getBoundingClientRect());const overlap=Math.min(g[0].bottom,g[1].bottom)-Math.max(g[0].top,g[1].top);return {display:getComputedStyle(el).display,sideBySide:g[1].left>g[0].left&&g[0].right<=g[1].left+4,verticalOverlap:overlap>0,thirdBelow:g[2].top>Math.max(g[0].bottom,g[1].bottom),thirdSpans:g[2].width>=nav.width*.9};}")
                        assert mobile_footer_layout["display"]=="grid" and mobile_footer_layout["sideBySide"] and mobile_footer_layout["verticalOverlap"] and mobile_footer_layout["thirdBelow"] and mobile_footer_layout["thirdSpans"], f"{path}: footer groups should form two balanced columns on mobile: {mobile_footer_layout}"
                        utility_links_layout=footer.locator(".footer-group:last-child ul").evaluate("(el)=>{const columns=getComputedStyle(el).gridTemplateColumns.trim().split(' ').filter(Boolean).length;const items=[...el.children].map(x=>x.getBoundingClientRect());return {columns,firstRow:Math.abs(items[0].top-items[1].top)<3,secondRow:items[2].top>items[0].top+8};}")
                        assert utility_links_layout["columns"]==2 and utility_links_layout["firstRow"] and utility_links_layout["secondRow"], f"{path}: utility links should use two readable columns on mobile: {utility_links_layout}"
                    assert page.locator("#nav a").evaluate_all("(a)=>a.map(x=>x.getAttribute('href'))")==NAV, f"{path}: shared nav order changed"
                    if width <= 620:
                        a11y_control = page.locator("#a11y-open")
                        assert a11y_control.evaluate("(el)=>el.getBoundingClientRect().width <= 52"), f"{path}: mobile accessibility control should stay compact"
                        assert page.get_by_role("button", name="Accessibilité").count() == 1, f"{path}: mobile accessibility control must keep its accessible name"
                        assert a11y_control.evaluate("(el)=>el.closest('header .bar')!==null && getComputedStyle(el).position!=='fixed'"), f"{path}: mobile Accessibility control must be in the header, not fixed over content"
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
                        assert page.locator(".derriere .photo img").get_attribute("src")=="/assets/gathering.webp"
                        assert page.locator(".voices").count()==0
                        assert "Témoignage à recueillir" not in page.locator("main").inner_text()
                        assert page.locator(".quote cite").inner_text()=="— Miette, participante"
                        assert "Samedi" in page.locator(".slots").inner_text() and "15h" in page.locator(".slots").inner_text()
                        assert "14h30" not in page.locator(".slot:nth-child(2)").inner_text()
                        assert "avant de vous déplacer" in page.locator("main").inner_text()
                    elif path=="qui-sommes-nous.html":
                        assert all(v in page.locator("main").inner_text() for v in ("1995","2021","Bleuettes","Burkina Faso","Maroc"))
                        assert page.locator(".topic-list span").count()==7
                        if width==390:
                            assert page.locator(".history-stats").evaluate("(el)=>getComputedStyle(el).gridTemplateColumns.split(' ').length")==2
                    elif path=="actualites.html":
                        assert page.locator(".news-card").count()==3
                        assert page.locator(".news-card .listen").count()==0, "read-aloud control must not be inserted into the first news card"
                        assert page.locator(".news-card").first.evaluate("(el)=>getComputedStyle(el).overflow")=="visible"
                        assert page.locator(".news-card").first.evaluate("(el)=>getComputedStyle(el,'::after').content") not in ("none","normal","")
                    elif path.startswith("actualite-"):
                        assert page.locator(".article-visual img").evaluate("(i)=>i.naturalWidth")>0
                        assert page.get_by_role("link",name="← Retour aux actualités").count()==1
                        if path=="actualite-2026-10-17.html":
                            article_text=page.locator("main").inner_text()
                            assert "2027" in article_text and "16 octobre 2026" in article_text
                        if path=="actualite-2026-10-10.html":
                            assert "dix membres" in page.locator("main").inner_text()
                    elif path=="contact.html":
                        contact_text=page.locator("main").inner_text()
                        if width>=1024:
                            left_height=page.locator(".contact-grid .content-card").nth(0).evaluate("(el)=>el.getBoundingClientRect().height")
                            right_height=page.locator(".contact-grid .content-card").nth(1).evaluate("(el)=>el.getBoundingClientRect().height")
                            assert left_height<right_height*.9, f"contact page: email panel is stretched by empty space ({left_height}px vs {right_height}px)"
                        assert "30 Rempart Saint-Vincent" in contact_text and "30 Rempart Saint-Pierre" in contact_text
                        assert "Adresse actuelle non confirmée" in contact_text
                    elif path=="mentions-legales.html":
                        legal_text=page.locator("main").inner_text()
                        assert "Vercel Inc." in legal_text and "2 mars 2019" in legal_text
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
            a11y.keyboard.press("Tab")
            assert a11y.evaluate("document.activeElement.matches('.skip')"), "skip link should be first in keyboard order"
            a11y.keyboard.press("Tab")
            assert a11y.evaluate("document.activeElement===document.querySelector('#a11y-open')"), "Accessibility should follow the skip link in keyboard order"
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
            assert not panel.is_hidden(), "reset should leave the accessibility panel open"
            a11y.locator('[data-k="calm"]').click()
            assert "calm" in (a11y.locator("html").get_attribute("class") or "")
            assert a11y.evaluate("getComputedStyle(document.querySelector('.hero .blob')).display==='none' && getComputedStyle(document.querySelector('.retrouver .big'),'::before').display==='none' && getComputedStyle(document.querySelector('.deco')).display==='none'"), "calm mode should remove homepage decorative backgrounds"
            a11y.locator("#a11y-reset").click()
            assert "calm" not in (a11y.locator("html").get_attribute("class") or "")

            # French read-aloud uses its own browser-side eSpeak engine. The device
            # deliberately exposes English only; the native speech API must never be called.
            speech_module_url="https://cdn.jsdelivr.net/npm/@spelling-creator/spellophone@0.2.1/dist/browser.js"
            speech_module="""export async function createEspeak(options) {
              const state=globalThis.__localSpeechTest;
              state.engineOptions=options;
              if(state.failEngine) throw new Error('mock engine network failure');
              return {
                async loadVoice(language){state.voice=language;},
                synthesize(text,options){
                  state.sent.push({text,options});
                  return {samples:new Int16Array([1600,800,-300,-900,400,1200]),sampleRate:22050};
                }
              };
            }
            export function toFloat32(samples){return Float32Array.from(samples,value=>value/32768);}
            """
            audio_mock="""(() => {
              const state=window.__localSpeechTest={engineOptions:null,voice:null,sent:[],starts:0,stops:0,nativeCalls:0,autoEnd:true,failEngine:false};
              Object.defineProperty(window,'speechSynthesis',{configurable:true,value:{
                getVoices(){return [{name:'English only',lang:'en-US',localService:true}];},
                speak(){state.nativeCalls++;},cancel(){}
              }});
              class MockAudioContext {
                constructor(){this.state='running';this.destination={};state.contexts=(state.contexts||0)+1;}
                resume(){state.resumed=(state.resumed||0)+1;return Promise.resolve();}
                createBuffer(channels,length,sampleRate){return {numberOfChannels:channels,length,sampleRate,copyToChannel(values){state.lastBuffer=Array.from(values);}};}
                createBufferSource(){
                  const source={buffer:null,onended:null,connect(){},start(){state.starts++;if(state.autoEnd)setTimeout(()=>this.onended&&this.onended(),0);},
                    stop(){state.stops++;setTimeout(()=>this.onended&&this.onended(),0);}};
                  state.sources=state.sources||[];state.sources.push(source);return source;
                }
              }
              Object.defineProperty(window,'AudioContext',{configurable:true,value:MockAudioContext});
            })();"""
            speech=context.new_page()
            speech.add_init_script(audio_mock)
            speech.route(speech_module_url,lambda route:route.fulfill(status=200,content_type="application/javascript",headers={"Access-Control-Allow-Origin":"*","Cache-Control":"no-store"},body=speech_module))
            speech.goto(f"{base}/index.html",wait_until="networkidle")
            speech.locator("#a11y-open").click()
            read_button=speech.locator("#a11y-voice .listen")
            assert read_button.count()==1, "read-aloud must be offered even without a French system voice"
            read_button.click()
            speech.wait_for_function("window.__localSpeechTest.sent.length>0 && window.__localSpeechTest.starts>0")
            speech.wait_for_function("document.querySelector('#a11y-voice .listen').getAttribute('aria-pressed')==='false' && document.querySelector('[role=status]').textContent.includes('Lecture terminée.')")
            local_playback=speech.evaluate("()=>({options:window.__localSpeechTest.engineOptions,voice:window.__localSpeechTest.voice,sent:window.__localSpeechTest.sent,starts:window.__localSpeechTest.starts,nativeCalls:window.__localSpeechTest.nativeCalls,lastBuffer:window.__localSpeechTest.lastBuffer})")
            assert local_playback["options"]["cdn"]=="jsdelivr" and "fr" in local_playback["options"]["languages"], f"the French engine must load its French language data: {local_playback}"
            assert local_playback["voice"]=="fr-fr", f"the dedicated French (France) eSpeak voice must be selected: {local_playback}"
            assert local_playback["sent"] and any(item["text"].strip() for item in local_playback["sent"]), f"page text should be synthesized into audio: {local_playback}"
            assert all(125<=item["options"]["rate"]<=210 for item in local_playback["sent"]), f"speech speed must map to valid eSpeak rates: {local_playback}"
            assert local_playback["starts"]>0 and local_playback["nativeCalls"]==0 and local_playback["lastBuffer"], f"French audio must play through Web Audio without using system voices: {local_playback}"

            # Playback can be cancelled during a long reading. No later chunk may start.
            cancelled=context.new_page()
            cancelled.add_init_script(audio_mock.replace("autoEnd:true","autoEnd:false"))
            cancelled.route(speech_module_url,lambda route:route.fulfill(status=200,content_type="application/javascript",headers={"Access-Control-Allow-Origin":"*","Cache-Control":"no-store"},body=speech_module))
            cancelled.goto(f"{base}/index.html",wait_until="networkidle")
            cancelled.locator("#a11y-open").click()
            cancel_button=cancelled.locator("#a11y-voice .listen")
            cancel_button.click()
            cancelled.wait_for_function("window.__localSpeechTest.starts===1")
            cancel_button.click()
            cancelled.wait_for_function("window.__localSpeechTest.stops===1 && document.querySelector('#a11y-voice .listen').getAttribute('aria-pressed')==='false'")
            cancelled.wait_for_timeout(150)
            cancel_state=cancelled.evaluate("()=>({starts:window.__localSpeechTest.starts,stops:window.__localSpeechTest.stops,status:document.querySelector('[role=status]').textContent})")
            assert cancel_state["starts"]==1 and cancel_state["stops"]==1 and cancel_state["status"]=="Lecture arrêtée.", f"cancelling local audio must stop the current chunk and prevent later chunks: {cancel_state}"

            # A CDN/network failure is announced accessibly and never falls back to English.
            unavailable=context.new_page()
            unavailable.add_init_script(audio_mock.replace("failEngine:false","failEngine:true"))
            unavailable.route(speech_module_url,lambda route:route.fulfill(status=200,content_type="application/javascript",headers={"Access-Control-Allow-Origin":"*","Cache-Control":"no-store"},body=speech_module))
            unavailable.goto(f"{base}/index.html",wait_until="networkidle")
            unavailable.locator("#a11y-open").click()
            unavailable.locator("#a11y-voice .listen").click()
            unavailable.wait_for_function("document.querySelector('[role=status]').textContent.includes('Vérifiez votre connexion')",timeout=5000)
            failed_playback=unavailable.evaluate("()=>({button:document.querySelector('#a11y-voice .listen').getAttribute('aria-pressed'),nativeCalls:window.__localSpeechTest.nativeCalls,status:document.querySelector('[role=status]').textContent})")
            assert failed_playback["button"]=="false" and failed_playback["nativeCalls"]==0, f"failed local engine loading should reset its control without English fallback: {failed_playback}"

            # Increased letter/word spacing and dyslexia settings must not clip the homepage title.
            spacing=context.new_page()
            for width,height in ((320,812),(1440,900)):
                spacing.set_viewport_size({"width":width,"height":height})
                spacing.goto(f"{base}/index.html",wait_until="networkidle")
                for classes in (["sp"],["dys","fs-3"]):
                    spacing.evaluate("(values)=>document.documentElement.classList.add(...values)",classes)
                    title_metrics=spacing.evaluate("()=>{const h=document.querySelector('.hero .card h1'),r=h.getBoundingClientRect();const over=[...document.body.querySelectorAll('*')].map(e=>{const b=e.getBoundingClientRect();return {tag:e.tagName,cls:typeof e.className==='string'?e.className:'',right:Math.round(b.right),left:Math.round(b.left),w:Math.round(b.width)}}).filter(x=>x.w>0&&(x.right>innerWidth+1||x.left< -1)).slice(0,8);return {doc:document.documentElement.scrollWidth,inner:innerWidth,right:r.right,scroll:h.scrollWidth,client:h.clientWidth,wrap:getComputedStyle(h).overflowWrap,word:getComputedStyle(h).wordBreak,hyphens:getComputedStyle(h).hyphens,over};}")
                    assert title_metrics["doc"]<=width+1, f"page develops horizontal overflow with accessibility spacing: {title_metrics}"
                    assert title_metrics["right"]<=width+1, f"hero title overflows with accessibility spacing: {title_metrics}"
                    assert title_metrics["scroll"]<=title_metrics["client"]+1, f"hero title is clipped with accessibility spacing: {title_metrics}"
                    assert title_metrics["wrap"]=="normal" and title_metrics["word"]=="normal" and title_metrics["hyphens"]=="none", f"hero title should wrap at spaces, not split words: {title_metrics}"
                    spacing.evaluate("()=>document.documentElement.classList.remove('sp','dys','fs-3')")
            spacing.close()

            # Reduced-motion and no-JavaScript users still receive all primary content.
            reduced=context.new_page();reduced.emulate_media(reduced_motion="reduce")
            reduced.goto(f"{base}/index.html",wait_until="networkidle")
            assert reduced.locator("h1").is_visible()
            assert reduced.evaluate("getComputedStyle(document.documentElement).scrollBehavior")=="auto", "system reduced-motion must disable smooth scrolling"

            # In-page anchors must leave their destination clear of the sticky header.
            anchor_page=context.new_page()
            anchor_page.set_viewport_size({"width":390,"height":844})
            anchor_page.emulate_media(reduced_motion="reduce")
            anchor_page.goto(f"{base}/index.html",wait_until="networkidle")
            anchor_page.locator('a[href="#se-retrouver"]').click()
            anchor_page.wait_for_function("()=>{const target=document.querySelector('#se-retrouver');const header=document.querySelector('body>header');return target&&header&&target.getBoundingClientRect().top>=header.getBoundingClientRect().bottom+6}")
            anchor_offset=anchor_page.evaluate("()=>({top:document.querySelector('#se-retrouver').getBoundingClientRect().top,header:document.querySelector('body>header').getBoundingClientRect().bottom})")
            assert anchor_offset["top"]<=120, f"anchor offset should stay visually compact: {anchor_offset}"
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
    print(json.dumps({"status":"PASS","browser_engine":ENGINE,"pages":len(PAGES),"viewports":[w for w,h in VIEWPORTS],"page_viewport_runs":len(measurements),"checks":["all twelve pages return HTTP 200","no horizontal overflow at five viewport widths","all local images decode","shared navigation links and active destinations","mobile navigation opens, closes on Escape and restores focus","no unintended forms or data collection","Saturday time remains 15:00","one genuine Miette quote and no empty testimonial prompts","seven About topics and milestone years","accessibility control state, persisted font settings, Escape/focus and reset","reduced-motion and no-JavaScript content visibility","no failed non-abort requests, unexpected external requests or browser errors"],"screenshots":len(list(out.glob("*.png")))} ,ensure_ascii=False))

if __name__=="__main__": main()
