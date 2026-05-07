import json


def get_media(owner):
    with open("Requests.json", "r") as f:
        data = json.load(f)
    requests = data.get(owner, {}).get("requests", [])
    if requests:
        ret = requests.pop(0)
        with open("Requests.json", "w") as f:
            data["requests"] = requests
            json.dump(data, f, indent=4)
        return ret
    else:
        return None 

def set_media(owner, user, media):
    # Load the existing data from the JSON file
    try:
        with open("media.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    if owner not in data:
        data[owner] = {"requests": []}

    data[owner]["requests"].append({
        "username": user,
        "media": media
    })
    with open("media.json", "w") as f:
        json.dump(data, f, indent=4)


def get_all_media(owner):
	with open("media.json", "r") as f:
		data = json.load(f)
	return data.get(owner, {}).get("requests", [])

