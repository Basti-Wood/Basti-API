# Basti API
Eine API, die ich mit allem möglichen fülle

# Setup

Um die app zu starten installiere alle requirements mit

	pip install -r requirements.txt

um einen Entry punkt zu haben zur app erstelle eine ```main.py``` datei und füge folgendes hinzu

	from Entrypoint import app
	import uvicorn

	if __name__ == "__main__":
		uvicorn.run(app, host="0.0.0.0", port=8000)

Dabei verändere die Host IP und den Port zu dem gewünschten wert.

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

# LLM

- ``/loadmodel`` Läd das LLama model "meta-llama/Meta-Llama-3.1-8B-Instruct"

- ``/generatetext/{InputText}/{Systemprompt}`` generiert einen text mit dem input text und OPTIONAL mit dem kontext des systemprompts.

- ``/unloadmodel`` schließt die LLM wieder (WICHTIG für Recourcen management)
