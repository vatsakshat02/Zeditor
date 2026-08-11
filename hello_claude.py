from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

message = client.messages.create(model="claude-sonnet-5", max_tokens=20, messages=[{"role":"user", "content":"hey how are you"}])

print(message.content[0].text)
print(message.usage.input_tokens)
print(message.usage.output_tokens)
print(message.stop_reason)