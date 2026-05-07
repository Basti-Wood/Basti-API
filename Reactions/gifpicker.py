import json
import random


def get_gif(json_file, category):
		with open(json_file, 'r') as f:
			gifs = json.load(f)
		return random.choice(gifs[category])