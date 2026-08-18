from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

tools = [
    {
        "name":"get_camera_info",
        "description": "Identify the source camera and color profile of the video file. Call this before planning any grade log footage and consumer footage needs opposite corrections",
        "input_schema": {
                "type":"object",
                "properties": {
                    "file_path":{
                        "type": "string",
                        "description": "Path to the video file to analyse."
                    }
                },
                "required": ["file_path"]
        }
    }
]

def get_camera_info(file_path):
    return "Iphone 15 pro Camera"

message = client.messages.create(model="claude-sonnet-5", max_tokens=3000, tools=tools, messages=[{"role":"user","content":"I need to grade clip.mp4. What am I working with?"}])    


for block in message.content:
    if block.type == "tool_use":
        plan = get_camera_info(block.input["file_path"])
        response = client.messages.create(model="claude-sonnet-5",max_tokens=3000,tools=tools, messages=[{"role":"user","content": "I need to grade clip.mp4. What am I working with?"},{"role":"assistant","content": message.content},{"role":"user","content": [{"type":"tool_result","tool_use_id":block.id,"content":plan}]}])

print(response.stop_reason)
for b in response.content:
    if b.type == "text":
        print(b.text)

