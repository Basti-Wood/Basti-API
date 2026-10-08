# Basti API
Eine API, die ich mit allem möglichen fülle

# Setup

## Docker (empfohlen)

Die gesamte App läuft - inklusive FreeLLMAPI - mit Docker Compose:

1. `.env` aus der Vorlage anlegen: `Copy-Item .env.example .env`
2. Werte in `.env` eintragen (siehe Tabelle unten), insbesondere
   `FREELLMAPI_ENCRYPTION_KEY` (einmalig erzeugen, siehe `.env.example`).
3. Starten: `docker compose up -d --build`
4. FreeLLMAPI-Dashboard öffnen: http://localhost:3001
   - Erstes Setup abschließen und auf der **Keys**-Seite deine Provider-Keys hinzufügen.
   - Den **unified API key** (`freellmapi-...`) aus dem Kopfbereich der Keys-Seite kopieren.
5. `FREELLMAPI_API_KEY=<key>` in `.env` eintragen.
6. API neu starten: `docker compose up -d`

Die Basti-API ist danach unter http://localhost:8000 erreichbar.

### Variablen (`.env`)

| Variable | Bedeutung |
| --- | --- |
| `API_KEYS` | Komma-getrennte gültige API-Keys (Header `x-api-key`). Ersetzt `envs/API.env`. |
| `YTAPI` | YouTube Data API Key für Media_share. Ersetzt `envs/media.env`. |
| `FREELLMAPI_API_KEY` | Unified API Key aus dem FreeLLMAPI-Dashboard. |
| `FREELLMAPI_MODEL` | Zu verwendendes Modell (z. B. `auto`, `auto:fast`, `gemini-2.5-flash`). |
| `FREELLMAPI_ENCRYPTION_KEY` | Verschlüsselungskey für FreeLLMAPI (einmalig erzeugen, stabil halten). |

## Lokal (ohne Docker)

	pip install -r requirements.txt

Anschließend einen Einstiegspunkt `main.py` anlegen:

	from Entrypoint import app
	import uvicorn

	if __name__ == "__main__":
		uvicorn.run(app, host="0.0.0.0", port=8000)

Dabei die Host-IP und den Port nach Wunsch anpassen. Die Konfiguration erfolgt
wie oben über Umgebungsvariablen (oder weiterhin über die `envs/*.env`-Dateien).

# Content

## Basic

- ``IP/Heath`` zeigt den aktuellen stand der API

- ``/`` ist der basic einstiegspunkt

# Reactions

- ``/reactions/{chategory}`` gibt ein Gif wieder, basierend auf der Chategory.

	- hug
	- pat
	- slap
	- cuddle
	- cheer
	- poke
	- *Mehr die hnzugefügt werden können*

# Mediashare

- ``/getmedia/{owner}`` nimmt sich den ersten eintrag aus der liste eines Users, gibt diesen wieder und löscht diesen aus der liste.

- ``/setmedia/{owner}/{user}/{Media}`` Setzt Media für einen besitzer der liste von einem Benutzer.

- ``/setmediatop/{owner}/{user}/{Media}`` Wie ``/setmedia``, fügt das Media aber an den ANFANG der liste (index 0) ein. Wird von der Mediashare-Seite für eigene Songs benutzt. Der ``user`` trägt die Markierung ``US<channel>`` und der eintrag bekommt ``owner_song: true``.

- ``/getallmedia/{owener}`` Bekommt alle Medien, die ein besitzer hat, ohne diese zu löschen.

## WebSocket Push Updates

The route ``/ws/getallmedia/{owner}`` is now subscription-based:

- On connect, clients immediately receive the current media list for ``owner``.
- On every successful ``/setmedia`` and ``/removemedia`` for that ``owner``, all subscribed websocket clients receive an updated ``{"owner": owner, "media": [...]}`` payload automatically.
- Clients can still send any text message to request a manual refresh.

# LLM (FreeLLMAPI)

Die KI läuft über [FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi) -
einen OpenAI-kompatiblen Router über kostenlose LLM-Provider. Ein lokales
Modell muss nicht mehr geladen oder entladen werden, die KI ist immer verfügbar.

- ``/generatetext?input_text=...`` generiert Text. Optional: ``system_prompt`` und ``user``.

- ``/clearmemory`` löscht den Chat-Verlauf (für einen ``user`` oder alle).
