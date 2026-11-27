# Générer gratuitement la lecture audio française

Le lecteur du site utilise des fichiers MP3 préparés à l’avance avec **Piper**, un moteur de synthèse vocale libre et local. Le modèle choisi est `fr_FR-siwis-medium`, une voix féminine française (France) distribuée sous licence **CC BY 4.0**.

Aucune carte bancaire, aucun compte Azure, aucune clé API et aucun service de synthèse payant ne sont nécessaires.

## Générer les enregistrements

Le dépôt est public. Les runners GitHub Actions standards sont gratuits pour les dépôts publics ; le workflow utilise uniquement un runner Ubuntu standard, pas un runner « larger » payant.

1. Ouvrir [Actions → Generate free French page audio](https://github.com/teyyara/bullebleue/actions/workflows/generate-french-audio.yml).
2. Choisir **Run workflow** sur la branche `main`.
3. Le workflow installe Piper, télécharge le modèle français SIWIS, génère l’exemple et une piste complète pour chaque page, puis convertit les WAV en MP3.
4. Les MP3 et le manifeste sont commités sur `main`. Le site peut alors les servir comme des fichiers statiques ordinaires.

Le modèle est téléchargé pendant la génération seulement. Les visiteurs ne téléchargent ni Piper, ni ONNX, ni modèle vocal. Leur navigateur lit simplement le MP3 correspondant à la page.

## Voix et licences

- Moteur : [Piper TTS](https://github.com/OHF-Voice/piper1-gpl), licence GPL-3.0-or-later.
- Modèle : [fr_FR-siwis-medium](https://huggingface.co/rhasspy/piper-voices), français (France), voix féminine, environ 63 Mo, licence CC BY 4.0.
- Données vocales : SIWIS French Speech Synthesis Database — Junichi Yamagishi, Pierre-Edouard Honnet, Philip N. Garner et Alexandros Lazaridis, University of Edinburgh / CSTR, 2017.

Attribution à afficher avec les contenus audio : « Voix SIWIS — SIWIS French Speech Synthesis Database, J. Yamagishi, P.-E. Honnet, P. N. Garner et A. Lazaridis, University of Edinburgh / CSTR, licence CC BY 4.0. Modèle Piper fr_FR-siwis-medium. »

## Après une modification du texte

Relancer le même workflow manuel. Il relit le contenu de `main` et remplace les pistes avec les versions à jour. La génération ne passe par aucun fournisseur vocal externe ; seul le téléchargement public du modèle et l’exécution du moteur Piper sont nécessaires.

