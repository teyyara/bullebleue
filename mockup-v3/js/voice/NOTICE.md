# Voix naturelle — crédits et licences

- **Pocket TTS de Kyutai** : licence CC BY 4.0. Le modèle de navigateur est une conversion ONNX communautaire issue du modèle Kyutai.
- **Graphes ONNX de KevinAHM** : licence CC BY 4.0.
- **État de voix français** : Stuart Bell, à partir d'un enregistrement LibriVox répertorié dans Voice-Zero, CC0. Le texte de chaque page est synthétisé ; aucun enregistrement préexistant de ce texte n'est utilisé.
- **Paquet 8 bits pour navigateur** : `jean-is/pocket-tts-q8-ONNX`, révision épinglée `b94b57dd6e20af2a8d79779fef5a8e60dbe9fc51`, CC BY 4.0. Les poids ont été quantifiés en 8 bits par canal et regroupés avec le décodeur et le tokenizer. L'état de voix français est celui de Stuart Bell plutôt que l'état Estelle du modèle amont.
- **Code de préparation et d'inférence adapté** : `jean-is/jean`, licence MIT. Les changements locaux couvrent le lecteur français, son worker et le téléchargement/cache pour Bulle Bleue.
- **ONNX Runtime Web 1.31.1** : licence MIT, chargé depuis jsDelivr avec une version épinglée.

Pocket TTS est l'unique moteur de lecture intégré au site. Aucun texte de page ni audio généré n'est envoyé à un service de synthèse vocale. Le modèle et ONNX Runtime Web sont téléchargés depuis Hugging Face et jsDelivr ; l'inférence et la lecture sont ensuite exécutées dans le navigateur.
