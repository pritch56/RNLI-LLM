
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import login

# Option 1: Set your Hugging Face token here (recommended for scripts)
HF_TOKEN = "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"  # <-- Put your token between the quotes
if HF_TOKEN:
    login(HF_TOKEN)

model_name = "google/gemma-3n-e4b"
tokenizer = AutoTokenizer.from_pretrained(model_name, token=HF_TOKEN if HF_TOKEN else None)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto", token=HF_TOKEN if HF_TOKEN else None)