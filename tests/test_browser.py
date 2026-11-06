#!/usr/bin/env python3
"""Current-candidate browser checks for navigation, layout, media and sticky homepage story."""
from __future__ import annotations

import json
import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BROWSER_ENGINE = os.environ.get("BROWSER_ENGINE", "chromium").strip().lower()
if BROWSER_ENGINE not in {"chromium", "firefox", "webkit"}:
    raise ValueError(f"Unsupported BROWSER_ENGINE: {BROWSER_ENGINE}")

PAGES = (
    "index.html",
    "qui-sommes-nous.html",
    "actualites.html",
    "actualite-2026-10-26.html",
    "actualite-2026-10-17.html",
    "actualite-2026-10-10.html",
    "adherer.html",
    "contact.html",
    "mentions-legales.html",
)
VIEWPORTS = (
    (320, 760),
    (390, 844),
    (768, 1024),
    (1024, 768),
    (1440, 900),
)
NAV = (
    "index.html",
    "qui-sommes-nous.html",
    "actualites.html",
    "adherer.html",
    "contact.html",
)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass


def assert_no_horizontal_overflow(page, width: int, path: str) -> dict:
    metrics = page.evaluate(
        """() => ({
          viewport: window.innerWidth,
          document: document.documentElement.scrollWidth,
          body: document.body.scrollWidth,
          height: document.documentElement.scrollHeight
        })"""
    )
    assert metrics["document"] <= width + 1, (
        f"{path} at {width}px: document overflow {metrics}"
    )
    assert metrics["body"] <= width + 1, (
        f"{path} at {width}px: body overflow {metrics}"
    )
    return metrics


def check_images(page, path: str) -> int:
    page.locator("img").evaluate_all(
        "(images) => images.forEach((image) => { image.loading = 'eager'; })"
    )
    page.wait_for_function(
        "() => Array.from(document.images).every((image) => image.complete && image.naturalWidth > 0)",
        timeout=15000,
    )
    return page.locator("img").count()


def wait_for_story_panel(page, index: int) -> None:
    page.wait_for_function(
        """(index) => {
          const steps = document.querySelectorAll(".story-step");
          const panel = steps[index]?.querySelector(".story-panel");
          return Boolean(
            steps[index]?.classList.contains("is-current") &&
            panel &&
            Number.parseFloat(getComputedStyle(panel).opacity) >= 0.99
          );
        }""",
        arg=index,
        timeout=6000,
    )


def prepare_screenshot_images(page) -> int:
    page.locator("img").evaluate_all(
        "(images) => images.forEach((image) => { image.loading = 'eager'; })"
    )
    page.wait_for_function(
        "() => Array.from(document.images).every((image) => image.complete && image.naturalWidth > 0)",
        timeout=15000,
    )
    page.evaluate(
        "() => Promise.all(Array.from(document.images, (image) => image.decode().catch(() => undefined)))"
    )
    return page.locator("img").count()

def main() -> None:
    handler = partial(QuietHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    screenshot_dir = ROOT / "artifacts" / f"loop025-browser-{BROWSER_ENGINE}"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    measurements: list[dict] = []

    try:
        with sync_playwright() as playwright:
            browser = getattr(playwright, BROWSER_ENGINE).launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            console_errors: list[str] = []
            failed_requests: list[str] = []
            external_requests: list[str] = []
            page.on(
                "console",
                lambda message: console_errors.append(message.text)
                if message.type == "error"
                else None,
            )
            page.on("pageerror", lambda error: console_errors.append(str(error)))
            page.on(
                "requestfailed",
                lambda request: failed_requests.append(
                    f"{request.url}: {request.failure}"
                ),
            )
            page.on(
                "request",
                lambda request: external_requests.append(request.url)
                if not request.url.startswith(base_url) and not any(host in request.url for host in ("fonts.googleapis.com", "fonts.gstatic.com"))
                else None,
            )

            for width, height in VIEWPORTS:
                page.set_viewport_size({"width": width, "height": height})
                for path in PAGES:
                    response = page.goto(
                        f"{base_url}/{path}", wait_until="networkidle", timeout=20000
                    )
                    assert response is not None and response.status == 200, (
                        f"{path}: route did not return HTTP 200"
                    )
                    assert_no_horizontal_overflow(page, width, path)
                    body_background = page.locator("body").evaluate("(el) => getComputedStyle(el).backgroundImage")
                    assert body_background == "none", f"{path}: page-level decorative dots must not float beside unrelated content: {body_background}"
                    image_count = check_images(page, path)
                    if path == "index.html":
                        drawing_count = page.locator(".story-art .drawing-sticker").count()
                        assert drawing_count == 9, f"homepage must display all nine supplied drawings, found {drawing_count}"
                        cutout_groups = page.locator(".story-art .drawing-character-group")
                        assert cutout_groups.count() == 4, "four supplied drawing groups must use transparent character cut-outs"
                        assert page.locator(".story-art .character-cutout").count() == 20, "all 20 separate character cut-outs must render"
                        for drawing, expected in {6: 6, 7: 4, 8: 1, 9: 9}.items():
                            actual = page.locator(f".story-art .drawing-character-group--{drawing} .character-cutout").count()
                            assert actual == expected, f"drawing {drawing}: expected {expected} character cut-outs, got {actual}"
                        group_style = cutout_groups.first.evaluate("(el) => getComputedStyle(el)")
                        assert group_style["borderTopWidth"] == "0px" and group_style["backgroundColor"] == "rgba(0, 0, 0, 0)", "cut-out groups must not retain paper-card borders/backgrounds"
                        assert page.locator('img[src*="/assets/posts/"]').count() == 0, "homepage must stay light and contain no activity gallery"
                        heading_font = page.locator(".story-panel h1").evaluate("(el) => getComputedStyle(el).fontFamily")
                        assert "Fredoka" in heading_font, f"owner-specified Fredoka heading font is missing: {heading_font}"
                        contact_radius = page.locator("#navigation .nav-contact").evaluate("(el) => getComputedStyle(el).borderRadius")
                        assert contact_radius == "999px", f"header contact action must be fully pill-shaped: {contact_radius}"
                        assert page.locator(".home-after-photo img").count() == 1, "gathering.jpeg must appear in the closing composition"
                        assert page.locator(".home-testimonials .voice-card").count() == 3, "homepage must show three explicitly-labelled profile prompts"
                        assert page.locator(".quote-feature footer").inner_text() == "— Miette, participante", "only the verified Miette quote is attributed"
                        assert page.locator(".bb-collage figure").count() == 4, "Jouer, créer collage must contain four artwork cards"
                        assert page.locator(".story-index").count() == 0, "homepage chapter counters must be removed"
                        assert page.locator(".se-photo img").count() == 1, "Se retrouver must show the owner-selected photo"
                        assert "Mercredi · 14h30" in page.locator(".se-schedule-grid").inner_text()
                        assert "Samedi · 15h" in page.locator(".se-schedule-grid").inner_text()
                    if path == "qui-sommes-nous.html":
                        audience_cards = page.locator(".about-audience-list > div")
                        assert audience_cards.count() == 2, "About page must retain both audience groups"
                        assert page.locator(".about-audience-list > div > span").count() == 0, "decorative 01/02 audience numbering must not remain"
                        assert "1995" in page.locator(".timeline-points").inner_text() and "2021" in page.locator(".timeline-points").inner_text(), "historical timeline dates must remain"
                        activity_cards = page.locator(".community-photo-grid--activities .community-photo-card")
                        assert activity_cards.count() == 8, "about page must hold eight activity photos"
                        activity_topics = page.locator(".about-activities .activity-words li")
                        assert activity_topics.count() == 7, "About must keep all seven activity topics"
                        activity_list = page.locator(".about-activities .activity-words")
                        assert activity_list.evaluate("(el) => getComputedStyle(el).borderTopWidth") == "0px", "About activity cards must not sit on a stray divider line"
                        grid_columns = activity_list.evaluate("(el) => getComputedStyle(el).gridTemplateColumns.trim().split(/\\s+/).length")
                        assert grid_columns == (1 if width <= 760 else 2), f"About activity cards must use a clean mobile stack and two-column wider grid, got {grid_columns} columns at {width}px"
                        assert float(activity_list.evaluate("(el) => getComputedStyle(el).rowGap.replace('px','')")) >= 10, "About activity cards need visible vertical breathing room"
                        assert float(activity_list.evaluate("(el) => getComputedStyle(el).columnGap.replace('px','')")) >= (0 if width <= 760 else 12), "About activity cards need a clear horizontal gutter"
                        assert activity_topics.first.evaluate("(el) => getComputedStyle(el).borderTopWidth") == "3px", "each activity topic must have its own clean card border"
                        assert page.locator(".page-intro").evaluate("(el) => getComputedStyle(el).color") == "rgb(20, 41, 104)", "pastel page intro must use deep readable navy text"
                        assert page.locator(".page-intro-lede").evaluate("(el) => getComputedStyle(el).color") == "rgb(52, 72, 120)", "page intro lede must not inherit white text on a light background"
                        assert page.locator(".solidarity-note > p:not(.section-kicker)").first.evaluate("(el) => getComputedStyle(el).color") == "rgb(62, 82, 122)", "solidarity note body text must use readable dark text on its pastel surface"
                    if path == "adherer.html":
                        centering_error = page.locator(".join-bottom").evaluate("(el) => { const r = el.getBoundingClientRect(); const p = el.parentElement.getBoundingClientRect(); return Math.abs((r.left + r.right) / 2 - (p.left + p.right) / 2); }")
                        assert centering_error < 2, f"Adhérer closing note must be centered, offset={centering_error}px"
                        if width >= 981:
                            primary_action = page.locator(".join-main > .button").bounding_box()
                            details_action = page.locator(".join-details > .inline-arrow").bounding_box()
                            assert abs((primary_action["y"] + primary_action["height"]) - (details_action["y"] + details_action["height"])) < 3, "Adhérer card actions must share a bottom baseline on desktop"
                    if path == "mentions-legales.html":
                        centering_error = page.locator(".legal-page").evaluate("(el) => { const r = el.getBoundingClientRect(); const p = el.parentElement.getBoundingClientRect(); return Math.abs((r.left + r.right) / 2 - (p.left + p.right) / 2); }")
                        assert centering_error < 2, f"legal text column must be centered, offset={centering_error}px"
                    if path == "contact.html" and width >= 981:
                        primary = page.locator(".contact-primary").bounding_box()
                        location = page.locator(".contact-location").bounding_box()
                        assert abs((primary["y"] + primary["height"]) - (location["y"] + location["height"])) < 2, "side-by-side contact cards must end on the same baseline"
                    if path == "actualites.html":
                        assert page.locator(".community-photo-grid--gatherings .community-photo-card").count() == 3, "news page has three un-dated community images"
                        assert page.locator(".news-card").count() == 3, "news page keeps its three dated stories"
                        assert page.locator(".news-card h2").first.evaluate("(el) => getComputedStyle(el).color") == "rgb(20, 41, 104)", "news titles must use readable navy"
                        assert page.locator(".news-grid").evaluate("(el) => getComputedStyle(el).borderTopWidth") == "0px", "legacy rectangular news-grid frame must be removed"
                        assert page.locator(".news-grid").evaluate("(el) => getComputedStyle(el).backgroundColor") == "rgba(0, 0, 0, 0)", "news-grid wrapper must remain transparent behind blob cards"
                        blob_shapes = page.locator(".news-card").evaluate_all(
                            "(cards) => cards.map((card) => getComputedStyle(card, '::before').clipPath)"
                        )
                        assert len(set(blob_shapes)) == 3, f"each dated news card needs its own organic silhouette: {blob_shapes}"
                        assert all(shape.startswith("polygon(") for shape in blob_shapes), f"news-card backgrounds must use organic clipped contours, not only rounded rectangles: {blob_shapes}"
                        image_shapes = page.locator(".news-card-image").evaluate_all(
                            "(images) => images.map((image) => getComputedStyle(image).clipPath)"
                        )
                        assert len(set(image_shapes)) == 3, f"news illustration frames need their own organic contours: {image_shapes}"
                        if width > 760:
                            badge_positions = page.locator(".news-card-image .image-kind").evaluate_all(
                                "(badges) => badges.map((badge) => ({top: badge.getBoundingClientRect().top, imageTop: badge.parentElement.getBoundingClientRect().top, imageHeight: badge.parentElement.getBoundingClientRect().height}))"
                            )
                            assert all((badge["top"] - badge["imageTop"]) < badge["imageHeight"] / 2 for badge in badge_positions), f"desktop illustration labels must stay within the upper half of the organic image frames: {badge_positions}"

                    nav_links = page.locator("#navigation a").evaluate_all(
                        "(links) => links.map((link) => link.getAttribute('href'))"
                    )
                    assert nav_links == list(NAV), f"{path}: primary nav order changed"

                    if width <= 980:
                        toggle = page.locator(".menu-toggle")
                        toggle.click()
                        assert toggle.get_attribute("aria-expanded") == "true"
                        assert "is-open" in (
                            page.locator("#navigation").get_attribute("class") or ""
                        )
                        page.keyboard.press("Escape")
                        assert toggle.get_attribute("aria-expanded") == "false"
                        assert page.evaluate(
                            "document.activeElement === document.querySelector('.menu-toggle')"
                        ), f"{path}: Escape did not restore focus"

                    measurements.append(
                        {
                            "page": path,
                            "width": width,
                            "height": height,
                            "images": image_count,
                            "layout": page.evaluate(
                                """() => ({
                                  viewport: window.innerWidth,
                                  document: document.documentElement.scrollWidth,
                                  body: document.body.scrollWidth
                                })"""
                            ),
                        }
                    )

            # Capture each sticky-story state after its opacity transition has finished.
            # Full-page screenshots are misleading for sticky scrollytelling: the sticky
            # artwork is only pinned in the real viewport, not repeated down a tall capture.
            page.set_viewport_size({"width": 1440, "height": 900})
            page.goto(f"{base_url}/index.html", wait_until="networkidle")
            page.wait_for_function(
                "() => document.documentElement.classList.contains('has-scroll-story')"
            )
            assert page.locator(".story-step.is-current").count() == 1
            sticky_top = page.locator(".story-art").evaluate(
                "(element) => getComputedStyle(element).top"
            )
            assert sticky_top == "76px", f"unexpected desktop sticky offset: {sticky_top}"
            prepare_screenshot_images(page)
            wait_for_story_panel(page, 0)
            page.screenshot(
                path=str(screenshot_dir / "home-story-01-desktop.png"),
                full_page=False,
            )

            for index in (1, 2):
                step = page.locator(".story-step").nth(index)
                step.scroll_into_view_if_needed()
                page.wait_for_function(
                    "(index) => document.querySelectorAll('.story-step.is-current').length === 1 && document.querySelectorAll('.story-step')[index].classList.contains('is-current')",
                    arg=index,
                    timeout=6000,
                )
                wait_for_story_panel(page, index)
                assert page.locator(".story-art").evaluate(
                    "(element) => Math.abs(element.getBoundingClientRect().top - 76) < 2"
                ), f"desktop story artwork did not remain sticky at chapter {index + 1}"
                page.screenshot(
                    path=str(screenshot_dir / f"home-story-0{index + 1}-desktop.png"),
                    full_page=False,
                )

            # The homepage stays deliberately light: story drawings, then the selected closing gathering photo.
            desktop_closing = page.locator(".home-after")
            desktop_closing.scroll_into_view_if_needed()
            prepare_screenshot_images(page)
            assert desktop_closing.locator(".home-after-photo img").evaluate("(img) => img.naturalWidth") > 0
            desktop_closing.screenshot(
                path=str(screenshot_dir / "home-closing-desktop.png")
            )

            # Owner-added homepage sections and their scroll-reactive artwork states.
            for selector, scene, filename in (
                ("#se-retrouver", "se-retrouver", "home-se-retrouver-desktop.png"),
                ("#ils-en-parlent", "temoignages", "home-testimonials-desktop.png"),
                ("#jouer-creer", "jouer", "home-jouer-creer-desktop.png"),
                (".story-step--derriere", "derriere", "home-derriere-desktop.png"),
            ):
                section = page.locator(selector)
                section.scroll_into_view_if_needed()
                page.wait_for_function(
                    "(scene) => document.querySelector('.story-art').dataset.scene === scene",
                    arg=scene,
                    timeout=6000,
                )
                section.screenshot(path=str(screenshot_dir / filename))

            # Inspect the actual news cards and undated community strip, not just the homepage.
            page.goto(f"{base_url}/actualites.html", wait_until="networkidle")
            prepare_screenshot_images(page)
            page.screenshot(path=str(screenshot_dir / "news-desktop.png"), full_page=True)
            page.set_viewport_size({"width": 390, "height": 844})
            page.goto(f"{base_url}/actualites.html", wait_until="networkidle")
            prepare_screenshot_images(page)
            page.screenshot(path=str(screenshot_dir / "news-mobile.png"), full_page=True)

            # Inspect the eight activity photos in their natural home on the About page.
            page.set_viewport_size({"width": 1440, "height": 900})
            page.goto(f"{base_url}/qui-sommes-nous.html", wait_until="networkidle")
            prepare_screenshot_images(page)
            page.screenshot(path=str(screenshot_dir / "about-desktop.png"), full_page=True)
            page.set_viewport_size({"width": 390, "height": 844})
            page.goto(f"{base_url}/qui-sommes-nous.html", wait_until="networkidle")
            prepare_screenshot_images(page)
            page.screenshot(path=str(screenshot_dir / "about-mobile.png"), full_page=True)

            # Mobile captures keep the same sticky story and selected closing photo.
            page.set_viewport_size({"width": 390, "height": 844})
            page.goto(f"{base_url}/index.html", wait_until="networkidle")
            assert_no_horizontal_overflow(page, 390, "index.html (sticky story)")
            page.wait_for_function(
                "() => document.documentElement.classList.contains('has-scroll-story')"
            )
            prepare_screenshot_images(page)
            wait_for_story_panel(page, 0)
            page.screenshot(
                path=str(screenshot_dir / "home-story-01-mobile.png"),
                full_page=False,
            )
            mobile_closing = page.locator(".home-after")
            mobile_closing.scroll_into_view_if_needed()
            prepare_screenshot_images(page)
            assert mobile_closing.locator(".home-after-photo img").evaluate("(img) => img.naturalWidth") > 0
            mobile_closing.screenshot(
                path=str(screenshot_dir / "home-closing-mobile.png")
            )

            # Viewport captures reflect the actual sticky-header experience on mobile.
            for selector, scene, filename in (
                ("#se-retrouver", "se-retrouver", "home-se-retrouver-mobile.png"),
                ("#ils-en-parlent", "temoignages", "home-testimonials-mobile.png"),
                ("#jouer-creer", "jouer", "home-jouer-creer-mobile.png"),
                (".story-step--derriere", "derriere", "home-derriere-mobile.png"),
            ):
                page.evaluate(
                    "(selector) => { const target = document.querySelector(selector); if (target) window.scrollTo(0, window.scrollY + target.getBoundingClientRect().top - 92); }",
                    selector,
                )
                page.wait_for_function(
                    "(scene) => document.querySelector('.story-art').dataset.scene === scene",
                    arg=scene,
                    timeout=6000,
                )
                page.wait_for_timeout(650)
                page.screenshot(path=str(screenshot_dir / filename))

            # Secondary page detail captures: all article routes and the Adhérer, Contact and legal layouts.
            for path, stem in (
                ("actualite-2026-10-26.html", "article-26-octobre"),
                ("actualite-2026-10-17.html", "article-17-octobre"),
                ("actualite-2026-10-10.html", "article-10-octobre"),
                ("adherer.html", "adhesion"),
                ("contact.html", "contact"),
                ("mentions-legales.html", "mentions-legales"),
            ):
                for width, height, suffix in ((1440, 900, "desktop"), (390, 844, "mobile")):
                    page.set_viewport_size({"width": width, "height": height})
                    page.goto(f"{base_url}/{path}", wait_until="networkidle")
                    prepare_screenshot_images(page)
                    page.screenshot(
                        path=str(screenshot_dir / f"{stem}-{suffix}.png"),
                        full_page=True,
                    )

            # Reduced-motion users keep every story panel readable without JS motion classes.
            reduced = context.new_page()
            reduced.emulate_media(reduced_motion="reduce")
            reduced.goto(f"{base_url}/index.html", wait_until="networkidle")
            assert not reduced.locator("html").evaluate(
                "(element) => element.classList.contains('has-scroll-story')"
            )
            panel_opacities = reduced.locator(".story-panel").evaluate_all(
                "(panels) => panels.map((panel) => getComputedStyle(panel).opacity)"
            )
            assert panel_opacities == ["1", "1", "1"], (
                f"reduced-motion story panels are not all visible: {panel_opacities}"
            )

            # Without JavaScript all three story chapters are still available.
            no_js_context = browser.new_context(java_script_enabled=False)
            no_js = no_js_context.new_page()
            no_js.goto(f"{base_url}/index.html", wait_until="networkidle")
            no_js_opacities = no_js.locator(".story-panel").evaluate_all(
                "(panels) => panels.map((panel) => getComputedStyle(panel).opacity)"
            )
            assert no_js_opacities == ["1", "1", "1"], (
                f"no-JavaScript story panels are not all visible: {no_js_opacities}"
            )

            assert not failed_requests, f"browser requests failed: {failed_requests}"
            assert not external_requests, f"unexpected external requests: {external_requests}"
            assert not console_errors, f"browser errors: {console_errors}"

            browser.close()

    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    print(
        json.dumps(
            {
                "status": "PASS",
                "browser_engine": BROWSER_ENGINE,
                "pages": len(PAGES),
                "viewports": [width for width, _ in VIEWPORTS],
                "page_viewport_runs": len(measurements),
                "sticky_story_chapters": 3,
                "checks": [
                    "no horizontal overflow",
                    "HTTP routes and local image loads",
                    "shared navigation order",
                    "mobile menu Escape/focus behavior",
                    "nine supplied drawing groups render in the sticky art collage, with 20 independent transparent character cut-outs from drawings 6–9; original complete sheets remain in Jouer/créer",
                    "all eleven owner-supplied assets/posts photos are distributed to activity and community sections on secondary pages; homepage stays photo-light except for gathering.jpeg",
                    "sticky art and chapter transitions",
                    "reduced-motion content visibility",
                    "no-JavaScript content visibility",
                    "story screenshot captured after all three opacity transitions complete",
                    "desktop and mobile actualites pages captured, including three un-dated community photos",
                    "desktop and mobile qui-sommes-nous pages captured, including eight activity photos",
                    "desktop and mobile closing gathering.jpeg composition screenshots captured and image decode verified",
                    "About audience cards omit decorative numbering; centered Adhérer/legal layouts and bottom-aligned desktop Contact/Adhérer card details",
                    "only Google Fonts requests are permitted externally; no failed requests or console errors",
                ],
                "measurements": measurements,
                "screenshots": [
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/home-story-01-desktop.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/home-story-02-desktop.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/home-story-03-desktop.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/news-desktop.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/news-mobile.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/about-desktop.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/about-mobile.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/home-closing-desktop.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/home-story-01-mobile.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/home-closing-mobile.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/article-26-octobre-desktop.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/article-26-octobre-mobile.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/article-17-octobre-desktop.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/article-17-octobre-mobile.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/article-10-octobre-desktop.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/article-10-octobre-mobile.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/adhesion-desktop.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/adhesion-mobile.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/contact-desktop.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/contact-mobile.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/mentions-legales-desktop.png",
                    "artifacts/loop025-browser-${BROWSER_ENGINE}/mentions-legales-mobile.png",
                ],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
