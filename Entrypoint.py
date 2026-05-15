import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Header, WebSocket, WebSocketDisconnect
from Reactions.gifpicker import get_gif
from Media_share.mediashare import (
	get_media as fetch_media,
	set_media as store_media,
	get_all_media as fetch_all_media,
	remove_media as remove_media
)
from dotenv import load_dotenv, dotenv_values
try:
	from LLM.LLM import load_model, generate_text, unload_model, clear_memory, DEFAULT_SYSTEM_PROMPT
except ImportError:
	print("LLM module not found. LLM-related routes will not work.")
from typing import Optional

# Load env files — API.env for access keys, AI.env for external API keys
VALID_API_KEYS = set(dotenv_values(os.path.join('envs', 'API.env')).values())
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'envs', 'AI.env'))

# Dependency to validate API key
def validate_api_key(x_api_key: str = Header(...)):
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# Global model state — loaded/unloaded manually via routes
_model = None
_tokenizer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Runs on shutdown — unload model if still loaded
    if _model is not None:
        unload_model(_model, _tokenizer)

app = FastAPI(dependencies=[Depends(validate_api_key)], lifespan=lifespan)

# Basic routes
@app.get("/", dependencies=[Depends(validate_api_key)])
async def read_root():
    return {"message": "Welcome to your custom FastAPI!"}

@app.get("/health", dependencies=[Depends(validate_api_key)])
async def health():
    return {"status": "ok"}


# Reaction routes
@app.get("/reaction/{category}")
async def get_reaction(category: str):
	gif_url = get_gif('Reactions/gifs.json', category)
	return {"gif_url": gif_url}


# Media sharing routes

@app.get("/getmedia/{owner}")
async def get_media_route(owner: str):
	response = fetch_media(owner)
	if response:
		return {"media": response}
	else:
		return {"message": "No media found for this owner."}
      
@app.post("/setmedia/{owner}/{user}/{media:path}")
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
	
@app.post("/removemedia/{owner}/{index}")
async def remove_media_route(owner: str, index: int):
	success = remove_media(owner, index)
	if success:
		return {"message": "Media removed successfully."}
	else:
		return {"message": "Failed to remove media. Check the owner and index."}

# WebSocket route for getallmedia
@app.websocket("/ws/getallmedia/{owner}")
async def websocket_get_all_media(websocket: WebSocket, owner: str):
    await websocket.accept()
    try:
        while True:
            # Wait for a message from the client (optional, can be removed if not needed)
            await websocket.receive_text()

            # Fetch all media for the owner
            response = fetch_all_media(owner)
            if response:
                await websocket.send_json({"media": response})
            else:
                await websocket.send_json({"message": "No media found for this owner."})
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for owner: {owner}")

#LLM integration
@app.post("/loadmodel")
async def load_model_route():
	global _model, _tokenizer
	if _model is not None:
		return {"message": "Model is already loaded."}
	model_path = "bartowski/Llama-3.2-3B-Instruct-GGUF"
	_model, _tokenizer = load_model(model_path)
	return {"message": "Model loaded successfully."}

@app.get("/generatetext")
async def generate_text_route(input_text: str, user: str = "default", system_prompt: Optional[str] = None):
	if _model is None:
		raise HTTPException(status_code=503, detail="Model is not loaded. Call /loadmodel first.")
	generated_text = generate_text(_model, _tokenizer, input_text, system_prompt=system_prompt, user=user)
	return {"generated_text": generated_text}

@app.post("/clearmemory")
async def clear_memory_route(user: Optional[str] = None):
	clear_memory(user)
	if user:
		return {"message": f"Memory cleared for user '{user}'."}
	return {"message": "All memory cleared."}

@app.post("/unloadmodel")
async def unload_model_route():
	global _model, _tokenizer
	if _model is None:
		return {"message": "Model is not loaded."}
	unload_model(_model, _tokenizer)
	_model = None
	_tokenizer = None
	return {"message": "Model unloaded successfully."}
