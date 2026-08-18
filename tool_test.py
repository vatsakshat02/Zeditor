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
    },
    {
        "name":"get_frame_brightness",
        "description": "Identify the brightness of the footage. Call this after you have identified the source camera",
        "input_schema": {
            "type":"object",
            "properties": {
                    "file_path":{
                        "type":"string",
                        "description":"How much is the brightness of the footage"
                    }
            },
             "required":["file_path"]
        }
       
    }
]


def get_camera_info(file_path):
    return "Iphone 15 pro Camera"

def get_frame_brightness(file_path):
    return 3400.91

TOOLS_FUNCTIONS = {
    "get_camera_info":get_camera_info,
    "get_frame_brightness":get_frame_brightness
}

messages = [{"role": "user", "content": "I need to grade clip.mp4. Tell me what I'm working with."}]    

for _ in range(10):
    response = client.messages.create(model="claude-sonnet-5", max_tokens=3000, tools=tools, messages=messages)

    if response.stop_reason != "tool_use":
        break

    messages.append({"role":"assistant","content":response.content})

    result = []
    for block in response.content:
        if block.type == "tool_use":
            print("calling:", block.name, block.input)
            output = TOOLS_FUNCTIONS[block.name](**block.input)
            result.append({
                "type":"tool_result",
                "tool_use_id": block.id,
                "content":str(output)
            })
    messages.append({"role":"user","content":result})

for b in response.content:
     if b.type =="text":
       print(b.text)