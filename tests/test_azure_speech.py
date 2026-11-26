#!/usr/bin/env python3
"""Offline tests for the Azure static speech generator."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import generate_azure_speech as speech


class SpeechGeneratorTests(TestCase):
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

    def test_ssml_uses_france_locale_and_escapes_text(self):
        result = speech.build_ssml("L’association APAiL & ses adhérents.", "fr-FR-DeniseNeural")
        self.assertIn('xml:lang="fr-FR"', result)
        self.assertIn('voice name="fr-FR-DeniseNeural"', result)
        self.assertIn("APAiL &amp; ses adhérents", result)

    def test_rejects_unapproved_voice_and_oversized_text(self):
        with self.assertRaises(ValueError):
            speech.build_ssml("Bonjour.", "fr-CA-SylvieNeural")
        with self.assertRaises(ValueError):
            speech.build_ssml("x" * 9001, "fr-FR-HenriNeural")

    @patch("generate_azure_speech.urlopen")
    def test_synthesis_requests_mp3_and_never_exposes_the_key(self, urlopen):
        fake_mp3 = b"ID3" + (b"\x00" * 500)
        urlopen.return_value = BytesIO(fake_mp3)
        result = speech.synthesize("Bonjour.", "fr-FR-HenriNeural", "private-test-key", "francecentral")
        request = urlopen.call_args.args[0]
        self.assertEqual(result, fake_mp3)
        self.assertEqual(request.full_url, "https://francecentral.tts.speech.microsoft.com/cognitiveservices/v1")
        self.assertEqual(request.get_header("X-microsoft-outputformat"), speech.OUTPUT_FORMAT)
        self.assertEqual(request.get_header("Ocp-apim-subscription-key"), "private-test-key")
        self.assertNotIn("private-test-key", speech.build_ssml("Bonjour.", "fr-FR-HenriNeural"))


if __name__ == "__main__":
    main()
