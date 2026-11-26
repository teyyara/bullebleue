#!/usr/bin/env python3
"""Generate static French (France) MP3 narration with Azure Speech.

The API key is read only from AZURE_SPEECH_KEY. It is never written to an
output file, manifest, log line, or website asset.
"""
from __future__ import annotations

from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
import json
import os
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "speech" / "fr-FR"
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
    "facile-a-lire.html",
    "accessibilite.html",
    "404.html",
)
VOICES = {
    "denise": {
        "label": "Denise · voix féminine",
        "name": "fr-FR-DeniseNeural",
    },
    "henri": {
        "label": "Henri · voix masculine",
        "name": "fr-FR-HenriNeural",
    },
}
SAMPLE_TEXT = (
    "Bonjour et bienvenue à la Bulle Bleue. Ici, on prend le temps de se "
    "retrouver, de s’écouter et de créer ensemble. Chacun vient comme il est."
)
OUTPUT_FORMAT = "audio-24khz-96kbitrate-mono-mp3"
MAX_REQUEST_CHARACTERS = 9000
BLOCK_TAGS = {"h1", "h2", "h3", "p", "li", "figcaption"}
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}
SKIP_TAGS = {"button", "script", "style", "svg", "noscript"}
SKIP_CLASSES = {"listen", "a11y-ui", "sr-only"}


class MainTextExtractor(HTMLParser):
    """Extract the same readable main content the former page reader exposed."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_main = False
        self.skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if not self.in_main:
            if tag == "main" and attributes.get("id") == "contenu":
                self.in_main = True
            return

        if self.skip_depth:
            if tag not in VOID_TAGS:
                self.skip_depth += 1
            return

        classes = set((attributes.get("class") or "").split())
        if (
            tag in SKIP_TAGS
            or classes.intersection(SKIP_CLASSES)
            or attributes.get("aria-hidden") == "true"
            or "hidden" in attributes
        ):
            if tag not in VOID_TAGS:
                self.skip_depth = 1
            return

        if tag == "abbr" and attributes.get("title"):
            self.parts.append(" " + str(attributes["title"]) + " ")
            self.skip_depth = 1
            return

        if tag in BLOCK_TAGS or tag == "br" or classes.intersection({"day", "when"}):
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if not self.in_main:
            return
        if self.skip_depth:
            if tag not in VOID_TAGS:
                self.skip_depth -= 1
            return
        classes = set()
        if tag in BLOCK_TAGS:
            self.parts.append(". ")
        elif tag == "main":
            self.in_main = False

    def handle_data(self, data: str) -> None:
        if self.in_main and not self.skip_depth:
            self.parts.append(data)


def extract_main_text(html: str) -> str:
    parser = MainTextExtractor()
    parser.feed(html)
    parser.close()
    text = re.sub(r"\s+", " ", " ".join(parser.parts)).strip()
    text = re.sub(r"([.!?…:;])\s*\.\s*", r"\1 ", text)
    text = text.strip()
    text = re.sub(r"\s+\.", ".", text)
    if not text:
        raise ValueError("No readable text was found inside main#contenu.")
    return text


def build_ssml(text: str, voice_name: str) -> str:
    allowed = {item["name"] for item in VOICES.values()}
    if voice_name not in allowed:
        raise ValueError("Unsupported voice name.")
    if not text.strip():
        raise ValueError("Cannot synthesize an empty text.")
    if len(text) > MAX_REQUEST_CHARACTERS:
        raise ValueError(
            f"Text has {len(text)} characters; split or shorten it before synthesis."
        )
    from xml.sax.saxutils import escape

    safe_text = escape(text)
    return (
        '<speak version="1.0" '
        'xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="fr-FR">'
        f'<voice name="{voice_name}">{safe_text}</voice>'
        "</speak>"
    )


def synthesize(text: str, voice_name: str, key: str, region: str) -> bytes:
    if not re.fullmatch(r"[a-z0-9]+", region):
        raise ValueError("AZURE_SPEECH_REGION must be the lowercase region slug from Azure.")
    ssml = build_ssml(text, voice_name).encode("utf-8")
    endpoint = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
    request = Request(
        endpoint,
        data=ssml,
        method="POST",
        headers={
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": OUTPUT_FORMAT,
            "User-Agent": "BulleBleue-APAiL-StaticAudioGenerator",
            "Accept": "audio/mpeg",
        },
    )
    try:
        with urlopen(request, timeout=120) as response:
            data = response.read()
    except HTTPError as error:
        details = error.read(1200).decode("utf-8", errors="replace")
        raise RuntimeError(f"Azure Speech returned HTTP {error.code}: {details}") from error
    except URLError as error:
        raise RuntimeError(f"Could not reach the Azure Speech endpoint: {error.reason}") from error

    is_mp3 = data.startswith(b"ID3") or any(
        data[index] == 0xFF and (data[index + 1] & 0xE0) == 0xE0
        for index in range(min(32, max(0, len(data) - 1)))
    )
    if len(data) < 256 or not is_mp3:
        preview = data[:300].decode("utf-8", errors="replace")
        raise RuntimeError(f"Azure returned an empty or non-MP3 response: {preview}")
    return data


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def generate() -> None:
    key = os.environ.get("AZURE_SPEECH_KEY", "").strip()
    region = os.environ.get("AZURE_SPEECH_REGION", "").strip().lower()
    if not key or not region:
        raise SystemExit(
            "Missing AZURE_SPEECH_KEY or AZURE_SPEECH_REGION. "
            "Add them as GitHub Actions repository secrets before running this workflow."
        )

    for page in PAGES:
        if not (ROOT / page).is_file():
            raise SystemExit(f"Required page is missing: {page}")

    manifest = {
        "version": 1,
        "locale": "fr-FR",
        "status": "ready",
        "engine": "Azure Speech Neural",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "voices": {},
    }
    characters = 0

    for key_name, voice in VOICES.items():
        sample_path = OUTPUT / key_name / "sample.mp3"
        sample_data = synthesize(SAMPLE_TEXT, voice["name"], key, region)
        atomic_write(sample_path, sample_data)
        characters += len(SAMPLE_TEXT)
        print(f"Generated audition: {voice['name']} ({len(SAMPLE_TEXT)} characters)")

        page_files: dict[str, str] = {}
        for page in PAGES:
            html = (ROOT / page).read_text(encoding="utf-8")
            text = extract_main_text(html)
            audio_data = synthesize(text, voice["name"], key, region)
            output_name = Path(page).stem + ".mp3"
            audio_path = OUTPUT / key_name / "pages" / output_name
            atomic_write(audio_path, audio_data)
            page_files[page] = f"/assets/speech/fr-FR/{key_name}/pages/{output_name}"
            characters += len(text)
            print(f"Generated {page}: {len(text)} characters · {voice['name']}")

        manifest["voices"][key_name] = {
            "label": voice["label"],
            "voiceName": voice["name"],
            "sample": f"/assets/speech/fr-FR/{key_name}/sample.mp3",
            "pages": page_files,
        }
        time.sleep(0.15)

    manifest_path = OUTPUT / "manifest.json"
    atomic_write(
        manifest_path,
        json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8") + b"\n",
    )
    print(
        f"Generated two French (France) voice sets: {characters:,} billable text "
        f"characters estimated across both voices. Manifest: {manifest_path.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    try:
        generate()
    except Exception as error:
        print(f"Audio generation failed: {error}", file=sys.stderr)
        raise
