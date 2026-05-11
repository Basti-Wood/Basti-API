import json
from pathlib import Path

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
    # Load the existing data from the JSON file
    try:
        with open(MEDIA_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    if owner not in data:
        data[owner] = {"requests": []}

    data[owner]["requests"].append({
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

