import accelerate
print(accelerate.__version__)
import bitsandbytes as bnb
print(bnb.__version__)
import torch

print(torch.cuda.is_available())
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "google/gemma-2b-it"

# Load the model with the quantization_config
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto"
)

tokenizer = AutoTokenizer.from_pretrained(model_name)


prompt = "Hier ist dein Prompt-Text"
inputs = tokenizer(prompt, return_tensors="pt").to('mps')
outputs = model.generate(**inputs)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
