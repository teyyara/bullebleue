# Generate the French page recordings

The site uses static MP3 recordings generated from the published page copy. Azure is called only during this generation workflow; the public site never receives an Azure key and does not call Azure when a visitor presses Play.

## 1. Create a Speech resource

1. Open the [Azure portal](https://portal.azure.com/).
2. Create an **Azure AI Speech** resource. Choose the **Free F0** pricing tier and a region supported by Speech.
3. After creation, open the resource's **Keys and Endpoint** page.
4. Copy **Key 1** and note the resource's **Location/region** slug.

The generator uses the standard neural French (France) voices `fr-FR-DeniseNeural` and `fr-FR-HenriNeural`. It intentionally does not use HD voices: Microsoft's F0 pricing lists 500,000 neural characters per month, while HD voices are excluded from that free allowance. Check the [current Azure Speech pricing](https://azure.microsoft.com/en-us/pricing/details/speech/) before changing tiers or voices.

## 2. Store credentials as repository secrets

In GitHub, open **teyyara/bullebleue → Settings → Secrets and variables → Actions → New repository secret**.

Create these two secrets:

- `AZURE_SPEECH_KEY`: Key 1 from the Speech resource.
- `AZURE_SPEECH_REGION`: the resource's region slug, in lowercase (for example, `francecentral` if that is the region shown for the resource).

Do not add the key to a source file, a commit, a website environment variable, or a chat message. The generator reads it only inside the protected GitHub Actions job.

## 3. Generate the audio

Open **Actions → Generate French page audio → Run workflow** on `main`. The workflow:

- creates audition MP3s for Denise and Henri using the same short Bulle Bleue introduction;
- creates a complete MP3 for each of the site's twelve pages in both voices;
- writes a small manifest that maps each page to its audio file;
- commits the generated assets to `main`.

The files are served as ordinary static assets under `/assets/speech/fr-FR/`. No Azure call or speech-model download is needed when someone visits the site. Each page's public text is sent to Azure only during the initial generation or a later regeneration.

The two sets of voice files use a modest amount of the F0 monthly character allowance. Regenerating all pages consumes the characters again, so avoid rerunning the workflow unnecessarily.

## 4. Refresh after changing page copy

Whenever the readable text on a page changes, run the workflow again. It regenerates both voice sets and the manifest from the current `main` HTML files.

## References

- [Azure Speech language and voice support](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support)
- [Text-to-speech REST API](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech)
- [Azure Speech pricing](https://azure.microsoft.com/en-us/pricing/details/speech/)
