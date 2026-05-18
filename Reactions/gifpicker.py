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
	
	try:
		# Read existing GIFs
		with open(json_file, 'r') as f:
			gifs = json.load(f)
		
		# Ensure gifs is a dictionary
		if not isinstance(gifs, dict):
			gifs = {}
		
		# Update only the specific category
		gifs[category] = gif_url
		
		# Write back the complete dictionary
		with open(json_file, 'w') as f:
			json.dump(gifs, f, indent=4, ensure_ascii=False)
		
		return True
	except Exception as e:
		raise ValueError(f"Failed to set GIF: {str(e)}")