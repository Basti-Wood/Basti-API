import json
import random
import os


def get_gif(json_file, category):
		# Convert to absolute path if relative
		if not os.path.isabs(json_file):
			json_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), json_file)
		
		with open(json_file, 'r') as f:
			gifs = json.load(f)
		
		# Check if category exists
		if category not in gifs:
			raise ValueError(f"Category '{category}' not found in gifs.json")
		
		# Check if category has any gifs
		if not gifs[category]:
			raise ValueError(f"No GIFs available for category '{category}'")
		
		return random.choice(gifs[category])