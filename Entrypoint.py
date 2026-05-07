from fastapi import FastAPI
from Reactions.gifpicker import get_gif
from LLM.BastiLLM import load_model, generate_response

app = FastAPI()
llm = load_model()

@app.get("/")
async def read_root():
    return {"message": "Welcome to your custom FastAPI!"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/reaction/{category}")
async def get_reaction(category: str):
	gif_url = get_gif('Reactions/gifs.json', category)
	return {"gif_url": gif_url}

@app.post("/chat")
async def chat(prompt: str):
	response = generate_response(llm, prompt)
	return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)