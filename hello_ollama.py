import os
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

response = client.chat.completions.create(model="llama3.1:8b", messages=[{"role":"user","content": "hey how are you"}])

print(response.choices[0].message.content)
print(response.usage.prompt_tokens)
print(response.usage.completion_tokens)
print(response.choices[0].finish_reason)

