#!/usr/bin/env python3
"""Generate static French (France) MP3 narration with the open Piper TTS engine.

Everything runs on a standard public GitHub Actions runner. No API credentials,
paid speech endpoint, or visitor-side inference is involved.
"""
from __future__ import annotations

from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import subprocess
import sys
import wave

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "speech" / "fr-FR"
MODEL_DIR = ROOT / ".cache" / "piper-voices"
VOICE_ID = "fr_FR-siwis-medium"
VOICE_KEY = "siwis"
VOICE_LABEL = "Siwis · voix féminine · français de France"
VOICE_MODEL_URL = "https://huggingface.co/rhasspy/piper-voices"
MODEL_LICENSE = "CC-BY-4.0"
PIPER_VERSION = "1.8.0"
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
SAMPLE_TEXT = (
    "Bonjour et bienvenue à la Bulle Bleue. Ici, on prend le temps de se "
    "retrouver, de s’écouter et de créer ensemble. Chacun vient comme il est."
)


class MainTextExtractor(HTMLParser):
    """Extract readable text inside main#contenu, excluding UI and decoration."""

    VOID_TAGS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr",
    }
    SKIP_TAGS = {"button", "script", "style", "svg", "noscript"}
    SKIP_CLASSES = {"listen", "a11y-ui", "sr-only"}
    BLOCK_TAGS = {"h1", "h2", "h3", "p", "li", "figcaption"}

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
            if tag not in self.VOID_TAGS:
                self.skip_depth += 1
            return
        classes = set((attributes.get("class") or "").split())
        if (
            tag in self.SKIP_TAGS
            or classes.intersection(self.SKIP_CLASSES)
            or attributes.get("aria-hidden") == "true"
            or "hidden" in attributes
        ):
            if tag not in self.VOID_TAGS:
                self.skip_depth = 1
            return
        if tag == "abbr" and attributes.get("title"):
            self.parts.append(" " + str(attributes["title"]) + " ")
            self.skip_depth = 1
            return
        if tag in self.BLOCK_TAGS or tag == "br" or classes.intersection({"day", "when"}):
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if not self.in_main:
            return
        if self.skip_depth:
            if tag not in self.VOID_TAGS:
                self.skip_depth -= 1
            return
        if tag in self.BLOCK_TAGS:
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
    text = re.sub(r"\s+\.", ".", text).strip()
    if not text:
        raise ValueError("No readable text was found inside main#contenu.")
    return text


def model_paths(model_dir: Path) -> tuple[Path, Path]:
    return model_dir / f"{VOICE_ID}.onnx", model_dir / f"{VOICE_ID}.onnx.json"


def download_model(model_dir: Path) -> tuple[Path, Path]:
    model_dir.mkdir(parents=True, exist_ok=True)
    model, config = model_paths(model_dir)
    if model.is_file() and config.is_file():
        return model, config
    command = [
        sys.executable, "-m", "piper.download_voices", VOICE_ID,
        "--data-dir", str(model_dir),
    ]
    subprocess.run(command, check=True, cwd=ROOT)
    if not model.is_file() or not config.is_file():
        raise FileNotFoundError(
            f"Piper did not create the expected model/config: {model.name}"
        )
    return model, config


def mp3_conversion_command(wav_path: Path, mp3_path: Path) -> list[str]:
    return [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(wav_path),
        "-vn", "-ac", "1", "-ar", "22050",
        "-codec:a", "libmp3lame", "-b:a", "96k",
        str(mp3_path),
    ]


def convert_wav_to_mp3(wav_path: Path, mp3_path: Path) -> None:
    mp3_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(mp3_conversion_command(wav_path, mp3_path), check=True)
    if not mp3_path.is_file() or mp3_path.stat().st_size < 256:
        raise RuntimeError(f"MP3 generation failed: {mp3_path}")


def synthesize_mp3(voice, text: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    wav_path = destination.with_suffix(".wav")
    try:
        with wave.open(str(wav_path), "wb") as wav_file:
            voice.synthesize_wav(text, wav_file)
        convert_wav_to_mp3(wav_path, destination)
    finally:
        wav_path.unlink(missing_ok=True)


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def generate() -> None:
    for page in PAGES:
        if not (ROOT / page).is_file():
            raise SystemExit(f"Required page is missing: {page}")
    try:
        from piper import PiperVoice
    except ImportError as error:
        raise SystemExit(
            f"Piper {PIPER_VERSION} is not installed. Install it with pip install piper-tts."
        ) from error

    model_path, _config_path = download_model(MODEL_DIR)
    print(f"Loading {VOICE_ID} once for all page recordings…")
    voice = PiperVoice.load(str(model_path))

    sample_path = OUTPUT / VOICE_KEY / "sample.mp3"
    synthesize_mp3(voice, SAMPLE_TEXT, sample_path)
    page_files: dict[str, str] = {}
    for page in PAGES:
        text = extract_main_text((ROOT / page).read_text(encoding="utf-8"))
        output_name = Path(page).stem + ".mp3"
        audio_path = OUTPUT / VOICE_KEY / "pages" / output_name
        synthesize_mp3(voice, text, audio_path)
        page_files[page] = f"/assets/speech/fr-FR/{VOICE_KEY}/pages/{output_name}"
        print(f"Generated {page}: {len(text):,} characters · {audio_path.stat().st_size:,} bytes")

    manifest = {
        "version": 1,
        "locale": "fr-FR",
        "status": "ready",
        "engine": "Piper TTS",
        "engineVersion": PIPER_VERSION,
        "model": VOICE_ID,
        "modelLicense": MODEL_LICENSE,
        "modelSource": VOICE_MODEL_URL,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "voices": {
            VOICE_KEY: {
                "label": VOICE_LABEL,
                "voiceName": VOICE_ID,
                "sample": f"/assets/speech/fr-FR/{VOICE_KEY}/sample.mp3",
                "pages": page_files,
            }
        },
    }
    atomic_write(
        OUTPUT / "manifest.json",
        json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8") + b"\n",
    )
    print(f"Generated one audition and {len(page_files)} page MP3s with {VOICE_ID}.")
    print("No paid speech service or API key was used.")


if __name__ == "__main__":
    try:
        generate()
    except Exception as error:
        print(f"Piper audio generation failed: {error}", file=sys.stderr)
        raise
