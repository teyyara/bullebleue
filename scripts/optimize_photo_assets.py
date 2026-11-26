#!/usr/bin/env python3
"""Create measured WebP derivatives for raster assets used by public pages."""
from __future__ import annotations
import json
import re
from pathlib import Path
from urllib.parse import quote
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
IMAGE_PATHS = [
    "assets/logo final.png", "assets/gathering.jpeg",
    "mockup-v3/img/mural.jpg", "mockup-v3/img/c10.jpg", "mockup-v3/img/c8.jpg",
    "mockup-v3/img/p1.jpg", "mockup-v3/img/p3.jpg", "mockup-v3/img/p5.jpg",
    "mockup-v3/img/p6.jpg", "mockup-v3/img/p7.jpg", "mockup-v3/img/p8.jpg",
    "mockup-v3/img/p9.jpg", "mockup-v3/img/p10.jpg", "mockup-v3/img/p11.jpg",
    "mockup-v3/img/p12.jpg", "mockup-v3/img/p13.jpg", "mockup-v3/img/p14.jpg",
]
REPORT = ROOT / "evidence/visual/webp-optimization-report.json"
REGISTER = ROOT / "evidence/visual/asset-register.json"
TODO = ROOT / "TODO.md"
README = ROOT / "README.md"
VALIDATOR = ROOT / "tests/validate_site.py"

def encode_webp(source: Path, destination: Path, lossless: bool) -> tuple[int, int]:
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened)
        icc = opened.info.get("icc_profile")
        alpha = "A" in image.getbands() or "transparency" in opened.info
        image = image.convert("RGBA" if alpha else "RGB")
        if lossless:
            # Header/footer render at 36–48 px; 256 px keeps >5x source detail.
            image.thumbnail((256, 256), Image.Resampling.LANCZOS)
            image.save(destination, "WEBP", lossless=True, method=6, exact=True, icc_profile=icc)
        else:
            image.save(destination, "WEBP", quality=84, method=6, exact=True, icc_profile=icc)
            if destination.stat().st_size >= source.stat().st_size:
                destination.unlink()
                image.save(destination, "WEBP", quality=78, method=6, exact=True, icc_profile=icc)
        if destination.stat().st_size >= source.stat().st_size:
            destination.unlink(missing_ok=True)
            raise RuntimeError(f"WebP is not smaller than original: {source.relative_to(ROOT)}")
        return image.width, image.height

def rewrite_text(path: Path, replacements: dict[str, str]) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    def replace_attr(match: re.Match[str]) -> str:
        prefix, q, value = match.group(1), match.group(2), match.group(3)
        for old, new in replacements.items():
            value = value.replace(quote(old, safe="/"), quote(new, safe="/")).replace(old, new)
        return f"{prefix}{q}{value}{q}"
    text = re.sub(r'((?:src|poster|data-src)\s*=\s*)(["\'])(.*?)\2', replace_attr, text, flags=re.I | re.S)
    def replace_url(match: re.Match[str]) -> str:
        q, value = match.group(1), match.group(2)
        for old, new in replacements.items():
            value = value.replace(quote(old, safe="/"), quote(new, safe="/")).replace(old, new)
        return f"url({q}{value}{q})"
    text = re.sub(r'url\(\s*(["\']?)(.*?)\1\s*\)', replace_url, text, flags=re.I | re.S)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False

def main() -> None:
    if not Image.registered_extensions().get(".webp"):
        raise RuntimeError("Pillow WebP support is unavailable")
    rows = []
    replacements = {}
    for rel in IMAGE_PATHS:
        source = ROOT / rel
        if not source.is_file():
            raise FileNotFoundError(source)
        destination = source.with_suffix(".webp")
        with Image.open(source) as original:
            original_width, original_height = original.size
        width, height = encode_webp(source, destination, lossless=source.suffix.lower() == ".png")
        before, after = source.stat().st_size, destination.stat().st_size
        replacements[source.relative_to(ROOT).as_posix()] = destination.relative_to(ROOT).as_posix()
        rows.append({
            "source": source.relative_to(ROOT).as_posix(),
            "webp": destination.relative_to(ROOT).as_posix(),
            "source_width": original_width, "source_height": original_height,
            "width": width, "height": height,
            "source_bytes": before, "webp_bytes": after,
            "saved_bytes": before-after,
            "saved_percent": round((1-after/before)*100, 1),
            "encoding": "lossless at 256 px max" if source.suffix.lower() == ".png" else "quality 84 (fallback 78)",
        })

    changed = []
    text_files = [*ROOT.glob("*.html"), *ROOT.rglob("*.css")]
    for path in text_files:
        if rewrite_text(path, replacements):
            changed.append(path.relative_to(ROOT).as_posix())

    before = sum(int(row["source_bytes"]) for row in rows)
    after = sum(int(row["webp_bytes"]) for row in rows)
    saved = before-after
    percent = round((1-after/before)*100, 1)
    report = {
        "version": 1,
        "policy": "Original uploads are retained. HTML/CSS use WebP derivatives; Open Graph continues to use JPEG.",
        "summary": {
            "images_converted": len(rows), "original_total_bytes": before,
            "webp_total_bytes": after, "bytes_saved": saved,
            "reduction_percent": percent,
        },
        "images": rows,
        "updated_source_files": changed,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    register["webp_derivatives"] = rows
    previous_optimization = re.sub(
        r"\\s*WebP derivatives are used for \\d+ rendered raster assets; originals remain unchanged\\. Combined transfer-size reduction: [\\d,.]+% \\([\\d,]+ to [\\d,]+ bytes\\)\\.",
        "",
        str(register.get("optimization", "")),
    ).strip()
    register["optimization"] = (
        previous_optimization
        + f" WebP derivatives are used for {len(rows)} rendered raster assets; originals remain unchanged. "
        + f"Combined transfer-size reduction: {percent}% ({before:,} to {after:,} bytes)."
    ).strip()
    REGISTER.write_text(json.dumps(register, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    todo = TODO.read_text(encoding="utf-8")
    old = "- [ ] Convert photographic assets to WebP and verify the actual transfer-size reduction; binary processing is not available in this repository-edit session."
    new = f"- [x] Create WebP derivatives for {len(rows)} rendered raster assets and measure the result: {before:,} bytes to {after:,} bytes ({percent}% smaller); original uploads retained."
    if old in todo:
        todo = todo.replace(old, new)
    else:
        todo, count = re.subn(
            r"^- \\[x\\] Create WebP derivatives for .*; original uploads retained\\.$",
            new,
            todo,
            count=1,
            flags=re.MULTILINE,
        )
        if count != 1:
            raise RuntimeError("WebP TODO entry not found")
    TODO.write_text(todo, encoding="utf-8")

    readme = README.read_text(encoding="utf-8")
    note = (
        "\n\n## Image delivery\n\n"
        f"The {len(rows)} raster assets rendered by the public pages now have WebP variants "
        f"({before:,} bytes combined before, {after:,} bytes after; {percent}% smaller). "
        "Original supplied images remain available in the repository. The Open Graph sharing "
        "image deliberately remains JPEG for compatibility. Per-image measurements are in "
        "evidence/visual/webp-optimization-report.json.\n"
    )
    if "## Image delivery" in readme:
        readme = readme[:readme.index("## Image delivery")].rstrip() + note
    else:
        readme += note
    README.write_text(readme, encoding="utf-8")

    validator = VALIDATOR.read_text(encoding="utf-8").replace("mockup-v3/img/mural.jpg", "mockup-v3/img/mural.webp").replace('src="/assets/gathering.jpeg"', 'src="/assets/gathering.webp"').replace('src="/assets/logo%20final.png"', 'src="/assets/logo%20final.webp"').replace("/assets/logo%20final.png", "/assets/logo%20final.webp")
    marker = '    assert "verbally authorized" in todo, "owner-provided photo permission record must be retained"'
    addition = marker + '\n' + (
        '    webp_report = json.loads((ROOT / "evidence/visual/webp-optimization-report.json").read_text(encoding="utf-8"))\n'
        '    assert webp_report["summary"]["reduction_percent"] > 0, "WebP must reduce transfer size"\n'
        '    assert webp_report["summary"]["images_converted"] >= 10, "rendered photos and logo should use WebP"\n'
        '    for image in webp_report["images"]:\n'
        '        webp_path = image["webp"]\n'
        '        assert (ROOT / webp_path).is_file(), f"missing WebP derivative: {webp_path}"\n'
    )
    if marker in validator and "webp_report =" not in validator:
        validator = validator.replace(marker, addition)
    if "mockup-v3/img/mural.webp" not in validator:
        raise RuntimeError("Mural WebP validator path was not updated")
    VALIDATOR.write_text(validator, encoding="utf-8")

    browser_test = ROOT / "tests/test_browser.py"
    browser_text = browser_test.read_text(encoding="utf-8")
    browser_text = browser_text.replace(
        'get_attribute("src")=="/assets/gathering.jpeg"',
        'get_attribute("src")=="/assets/gathering.webp"',
    )
    browser_test.write_text(browser_text, encoding="utf-8")

    print(json.dumps({"status":"PASS", "images":len(rows), "original_bytes":before,
        "webp_bytes":after, "saved_bytes":saved, "reduction_percent":percent,
        "updated_sources":changed}, ensure_ascii=False))

if __name__ == "__main__":
    main()
