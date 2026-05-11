import os
from fastapi import FastAPI, Depends, HTTPException, Header
from Reactions.gifpicker import get_gif
from Media_share.mediashare import (
	get_media as fetch_media,
	set_media as store_media,
	get_all_media as fetch_all_media,
)
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

VALID_API_KEYS = os.environ.values()

# Dependency to validate API key
def validate_api_key(x_api_key: str = Header(...)):
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API Key")

app = FastAPI(dependencies=[Depends(validate_api_key)])

@app.get("/", dependencies=[Depends(validate_api_key)])
async def read_root():
    return {"message": "Welcome to your custom FastAPI!"}

@app.get("/health", dependencies=[Depends(validate_api_key)])
async def health():
    return {"status": "ok"}

@app.get("/reaction/{category}")
async def get_reaction(category: str):
	gif_url = get_gif('Reactions/gifs.json', category)
	return {"gif_url": gif_url}

@app.get("/getmedia/{owner}")
async def get_media_route(owner: str):
	response = fetch_media(owner)
	if response:
		return {"media": response}
	else:
		return {"message": "No media found for this owner."}
      
@app.post("/setmedia/{owner}/{user}/{media}")
@app.get("/setmedia/{owner}/{user}/{media}")
async def set_media_route(owner: str, user: str, media: str):
	store_media(owner, user, media)
	return {"message": "Media set successfully."}
      
@app.get("/getallmedia/{owner}")
async def get_all_media_route(owner: str):
	response = fetch_all_media(owner)
	if response:
		return {"media": response}
	else:
		return {"message": "No media found for this owner."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)