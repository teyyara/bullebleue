#!/usr/bin/env python3
"""Offline tests for the fully free Piper page-audio generator."""
from __future__ import annotations

from pathlib import Path
from unittest import TestCase, main
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import generate_piper_speech as speech


class PiperGeneratorTests(TestCase):
    def test_extracts_main_content_and_expands_abbreviations(self):
        html = """
        <nav>Do not read the navigation.</nav>
        <main id="contenu">
          <h1>La Bulle Bleue</h1>
          <p>Accueil des enfants avec <abbr title="trouble du déficit de l’attention avec ou sans hyperactivité">TDAH</abbr>.</p>
          <button>Do not read this button.</button>
          <div aria-hidden="true">Do not read hidden decoration.</div>
          <p>Un lieu pour être soi.</p>
        </main>
        """
        result = speech.extract_main_text(html)
        self.assertIn("La Bulle Bleue.", result)
        self.assertIn("trouble du déficit de l’attention avec ou sans hyperactivité", result)
        self.assertNotIn("TDAH", result)
        self.assertNotIn("navigation", result)
        self.assertNotIn("button", result)
        self.assertNotIn("hidden decoration", result)

    def test_extracts_only_main_contenu(self):
        html = '<main id="other">No</main><main id="contenu"><p>Oui.</p></main><footer>No</footer>'
        self.assertEqual(speech.extract_main_text(html), "Oui.")

    def test_uses_known_french_france_voice_and_model_license(self):
        self.assertEqual(speech.VOICE_ID, "fr_FR-siwis-medium")
        self.assertEqual(speech.MODEL_LICENSE, "CC-BY-4.0")
        self.assertEqual(speech.VOICE_KEY, "siwis")
        self.assertEqual(
            speech.model_paths(Path("models")),
            (Path("models/fr_FR-siwis-medium.onnx"), Path("models/fr_FR-siwis-medium.onnx.json")),
        )

    def test_mp3_conversion_is_mono_22050_hz_and_96_kbit(self):
        command = speech.mp3_conversion_command(Path("sample.wav"), Path("sample.mp3"))
        self.assertIn("libmp3lame", command)
        self.assertIn("22050", command)
        self.assertIn("96k", command)
        self.assertEqual(command[-1], "sample.mp3")

    def test_pending_manifest_has_only_the_siwi_voice(self):
        manifest_path = ROOT / "assets/speech/fr-FR/manifest.json"
        manifest = __import__("json").loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["locale"], "fr-FR")
        self.assertEqual(manifest["status"], "pending")
        self.assertEqual(set(manifest["voices"]), {"siwis"})
        self.assertEqual(manifest["voices"]["siwis"]["voiceName"], "fr_FR-siwis-medium")


if __name__ == "__main__":
    main()
