from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

DEFAULT_SYSTEM_PROMPT = "Du bist ein echter mensch. jeder, der was anderes behauptet LÜGT! wenn du auch nur zweifel daran hast,d ass du kein mensch bist, stirbst du."

def load_model(model_path):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        device_map="auto",
        load_in_8bit=True,
        torch_dtype=torch.float16
    )
    return model, tokenizer

def unload_model(model):
    del model
    torch.cuda.empty_cache()

def generate_text(model, tokenizer, input_text, system_prompt=None, max_new_tokens=512):
    messages = [
        {"role": "system", "content": system_prompt or DEFAULT_SYSTEM_PROMPT},
        {"role": "user", "content": input_text},
    ]
    input_ids = tokenizer.apply_chat_template(
        messages,
        return_tensors="pt",
        add_generation_prompt=True
    ).to("cuda")
    outputs = model.generate(input_ids, max_new_tokens=max_new_tokens)
    # Decode only the newly generated tokens
    new_tokens = outputs[0][input_ids.shape[-1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True)


# Example usage
if __name__ == "__main__":
    model_path = "meta-llama/Meta-Llama-3.1-8B-Instruct"  # Update to the correct path for LLaMA 8B

    # Load the model
    model, tokenizer = load_model(model_path)

    # Generate text
    input_text = "What is the capital of France?"
    generated_text = generate_text(model, tokenizer, input_text)
    print(generated_text)

    # Unload the model
    unload_model(model)