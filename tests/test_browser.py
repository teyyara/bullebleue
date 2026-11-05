#!/usr/bin/env python3
"""Current-candidate browser checks for navigation, layout, media and sticky homepage story."""
from __future__ import annotations

import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
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
    screenshot_dir = ROOT / "artifacts" / "loop017-browser"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    measurements: list[dict] = []

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
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
                if not request.url.startswith(base_url)
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
                    image_count = check_images(page, path)
                    if path == "index.html":
                        drawing_count = page.locator(".story-art .drawing-sticker").count()
                        assert drawing_count == 5, f"homepage must display all five supplied drawings, found {drawing_count}"
                        photo_cards = page.locator(".home-photo-card")
                        assert photo_cards.count() == 2, "homepage photo gallery must show two cards"
                        assert page.locator(".home-photo-card img[alt]").count() == 2, (
                            "homepage gallery photos require descriptive alternative text"
                        )

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

            # Capture the gallery as an element after explicitly decoding its lazy images.
            desktop_gallery = page.locator(".home-photo-section")
            desktop_gallery.scroll_into_view_if_needed()
            prepare_screenshot_images(page)
            assert desktop_gallery.locator("img").count() == 2
            desktop_gallery.screenshot(
                path=str(screenshot_dir / "home-gallery-desktop.png")
            )

            # Mobile captures keep the same sticky story and show the actual loaded gallery.
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
            mobile_gallery = page.locator(".home-photo-section")
            mobile_gallery.scroll_into_view_if_needed()
            prepare_screenshot_images(page)
            mobile_gallery.screenshot(
                path=str(screenshot_dir / "home-gallery-mobile.png")
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
                "pages": len(PAGES),
                "viewports": [width for width, _ in VIEWPORTS],
                "page_viewport_runs": len(measurements),
                "sticky_story_chapters": 3,
                "checks": [
                    "no horizontal overflow",
                    "HTTP routes and local image loads",
                    "shared navigation order",
                    "mobile menu Escape/focus behavior",
                    "five supplied drawings render in the sticky art collage",
                    "sticky art and chapter transitions",
                    "reduced-motion content visibility",
                    "no-JavaScript content visibility",
                    "story screenshot captured after all three opacity transitions complete",
                    "desktop and mobile gallery screenshots captured after lazy images decode",
                    "no external requests, failed requests or console errors",
                ],
                "measurements": measurements,
                "screenshots": [
                    "artifacts/loop017-browser/home-story-01-desktop.png",
                    "artifacts/loop017-browser/home-story-02-desktop.png",
                    "artifacts/loop017-browser/home-story-03-desktop.png",
                    "artifacts/loop017-browser/home-gallery-desktop.png",
                    "artifacts/loop017-browser/home-story-01-mobile.png",
                    "artifacts/loop017-browser/home-gallery-mobile.png",
                ],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
