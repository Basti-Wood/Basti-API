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
	
	# Check if gif URL is empty
	if not gifs[category]:
		raise ValueError(f"No GIF available for category '{category}'")
	
	return gifs[category]

def set_gif(json_file, category, gif_url):
	# Convert to absolute path if relative
	if not os.path.isabs(json_file):
		json_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), json_file)
	
	with open(json_file, 'r') as f:
		gifs = json.load(f)
	
	# Set the GIF URL for this category
	gifs[category] = gif_url
	
	with open(json_file, 'w') as f:
		json.dump(gifs, f, indent=4)