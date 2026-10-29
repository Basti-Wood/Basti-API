import json
from pathlib import Path
import os
from dotenv import load_dotenv
import requests
from urllib.parse import unquote, urlsplit

env_path = os.path.join('envs', 'media.env')
load_dotenv(dotenv_path=env_path)


def _youtube_api_key() -> str:
    key = os.getenv("YTAPI")
    if not key:
        raise ValueError("YouTube API key is missing. Set YTAPI in envs/media.env or in the environment.")
    return key


MEDIA_FILE = Path(__file__).resolve().parent / "media.json"


def get_media(owner):
    try:
        with open(MEDIA_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        return None

    requests = data.get(owner, {}).get("requests", [])
    if requests:
        ret = requests[0]
        with open(MEDIA_FILE, "w") as f:
            data.setdefault(owner, {})["requests"] = requests
            json.dump(data, f, indent=4)
        return ret
    else:
        return None 

def _media_metadata(media, song_name=None, platform=None):
    media_path = urlsplit(media).path
    detected = "local" if media_path.startswith("/api/local-media/") else (
        "youtube" if "yout" in media else "spotify" if "spot" in media else "unknown"
    )
    platform = platform if platform in {"local", "youtube", "spotify", "other", "unknown"} else detected
    name = (song_name or "").strip()
    if not name and platform == "local":
        name = unquote(media_path.rsplit("/", 1)[-1])
    if not name and platform == "youtube":
        video_id = media.split("v=")[-1].split("&")[0] if "v=" in media else media.rstrip("/").split("/")[-1]
        api_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={_youtube_api_key()}"
        response = requests.get(api_url)
        name = "Unknown YouTube Video"
        if response.status_code == 200:
            items = response.json().get("items", [])
            if items:
                name = items[0]["snippet"]["title"]
    return platform, name or "Unknown"


def _store_media(owner, user, media, song_name=None, platform=None, at_top=False):
    try:
        with open(MEDIA_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    data.setdefault(owner, {"requests": []})
    resolved_platform, name = _media_metadata(media, song_name, platform)
    entry = {"Platform": resolved_platform, "song_name": name, "username": user, "media": media}
    if at_top:
        entry["owner_song"] = True
        data[owner]["requests"].insert(0, entry)
    else:
        data[owner]["requests"].append(entry)
    with open(MEDIA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def set_media(owner, user, media, song_name=None, platform=None):
    _store_media(owner, user, media, song_name, platform)


def set_media_top(owner, user, media, song_name=None, platform=None):
    # Existing three-argument callers remain supported. Metadata from the site
    # is saved before the route broadcasts the updated queue to bot clients.
    _store_media(owner, user, media, song_name, platform, at_top=True)


def get_all_media(owner):
    try:
        with open(MEDIA_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        return []
    return data.get(owner, {}).get("requests", [])


def remove_media(owner, index):
	try:
		with open(MEDIA_FILE, "r") as f:
			data = json.load(f)
	except FileNotFoundError:
		return False

	requests = data.get(owner, {}).get("requests", [])
	if 0 <= index < len(requests):
		requests.pop(index)
		with open(MEDIA_FILE, "w") as f:
			data.setdefault(owner, {})["requests"] = requests
			json.dump(data, f, indent=4)
		return True
	else:
		return False

