import torch
from llama_cpp import Llama
import os

# Recommended model for GTX 1060 (6GB VRAM):
# Meta-Llama-3.2-3B-Instruct-Q4_K_M.gguf (~2GB VRAM)
# Download from: https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF
DEFAULT_MODEL_PATH = "models/Llama-3.2-3B-Instruct-Q4_K_M.gguf"

# n_gpu_layers=-1 offloads all layers to GPU. Lower this value (e.g. 20) if you run out of VRAM.
def load_model(model_path: str = DEFAULT_MODEL_PATH, n_gpu_layers: int = -1, context_length: int = 4096) -> Llama:
	model = Llama(
		model_path=model_path,
		n_gpu_layers=n_gpu_layers,
		n_ctx=context_length,
		verbose=False,
	)
	return model

def generate_response(model: Llama, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
	output = model.create_chat_completion(
		messages=[{"role": "user", "content": prompt}],
		max_tokens=max_tokens,
		temperature=temperature,
	)
	return output["choices"][0]["message"]["content"]

def load_llama_model(model_path):
    """Load the LLaMA model using llama.cpp."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")

    # Load the model
    print("Loading LLaMA model...")
    llama = Llama(model_path=model_path)
    print("Model loaded successfully.")
    return llama

def generate_response(llama, prompt):
    """Generate a response from the LLaMA model."""
    output = llama(prompt, max_tokens=100, stop=["\n"])
    return output["choices"][0]["text"].strip()

if __name__ == "__main__":
    # Path to the quantized LLaMA model (e.g., ggml-model-q4_0.bin)
    model_path = "path/to/your/quantized/model/ggml-model-q4_0.bin"

    try:
        llama = load_llama_model(model_path)
        prompt = "What is the capital of France?"
        response = generate_response(llama, prompt)
        print("Response:", response)
    except Exception as e:
        print(f"An error occurred: {e}")
