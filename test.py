import openai
import os

openai.api_key = os.environ["OPENAI_API_KEY"]

gpt_prompt = "Write a hilarious joke about a cat with a hat."

response = openai.Completion.create(
  engine="text-davinci-002",
  prompt=gpt_prompt,
  temperature=1.0,
  max_tokens=256,
  top_p=1.0,
  frequency_penalty=0.0,
  presence_penalty=0.0
)

print(response['choices'][0]['text'])
