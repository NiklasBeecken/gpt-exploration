import openai
import os

openai.api_key = os.environ["OPENAI_API_KEY"]

gpt_prompt = "Correct this to standard English:\n\nShe no went to the market."

response = openai.Completion.create(
  engine="text-davinci-002",
  prompt=gpt_prompt,
  temperature=0.5,
  max_tokens=256,
  top_p=1.0,
  frequency_penalty=0.0,
  presence_penalty=0.0
)

print(response['choices'][0]['text'])
