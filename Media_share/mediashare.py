import json
from pathlib import Path
import os
from dotenv import load_dotenv
import requests

env_path = os.path.join('envs', 'media.env')
load_dotenv(dotenv_path=env_path)

YOUTUBE_API_KEY = os.getenv("YTAPI")
if not YOUTUBE_API_KEY:
    raise ValueError("YouTube API key is missing. Please check your 'media.env' file.")

MEDIA_FILE = Path(__file__).resolve().parent / "media.json"


def get_media(owner):
    try:
        with open(MEDIA_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        return None

    requests = data.get(owner, {}).get("requests", [])
    if requests:
        ret = requests.pop(0)
        with open(MEDIA_FILE, "w") as f:
            data.setdefault(owner, {})["requests"] = requests
            json.dump(data, f, indent=4)
        return ret
    else:
        return None 

def set_media(owner, user, media):
	try:
		with open(MEDIA_FILE, "r") as f:
			data = json.load(f)
	except FileNotFoundError:
		data = {}

	if owner not in data:
		data[owner] = {"requests": []}#
        
	
	platform = "unknown"
	name = "Unknown"
	if(media.find("yout") != -1):
		platform = "youtube"
	elif(media.find("spot") != -1):
		platform = "spotify"
    
	if(platform == "youtube"):
		video_id = media.split("v=")[-1].split("&")[0] if "v=" in media else media.split("/")[-1] if "/" in media else media
		api_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={YOUTUBE_API_KEY}"
		response = requests.get(api_url)
		if response.status_code == 200:
			data_json = response.json()
			if data_json["items"]:
				name = data_json["items"][0]["snippet"]["title"]
			else:
				name = "Unknown YouTube Video"
		else:
			name = "Unknown YouTube Video"

	data[owner]["requests"].append({
		"Platform": platform,
        "song_name": name,
		"username": user,
		"media": media
	})
	with open(MEDIA_FILE, "w") as f:
		json.dump(data, f, indent=4)


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
