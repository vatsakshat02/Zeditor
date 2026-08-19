from anthropic import Anthropic
from dotenv import load_dotenv
import subprocess, json

load_dotenv()

client = Anthropic()

tools = [
    {
        "name":"get_video_info",
        "description": "Identify the width, height, codec_name, color_transfer, bits_per_raw_sample, duration and avg_frame_rate of the video file. Call this before planning any grade log footage and consumer footage needs opposite corrections",
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
        "description": "Identify the brightness of the footage. Call this after you have identified the information from the video",
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


def get_video_info(file_path):
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", "-select_streams", "v:0", file_path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return f"Could not read the file: {r.stderr}"
    data = json.loads(r.stdout)
    streams = data["streams"][0]
    width = streams["width"]
    height = streams["height"]
    codec_name = streams["codec_name"]
    color_transfer = streams.get("color_transfer","unknown")
    bits_per_raw_sample = streams["bits_per_raw_sample"]
    duration = streams["duration"]
    nums = streams["avg_frame_rate"].split("/")
    avg_frame_rate = round(float(nums[0])/float(nums[1]),2)
    
    return (
    f"{width}x{height}, {avg_frame_rate}fps, {codec_name}, "
    f"{bits_per_raw_sample}-bit, colour transfer {color_transfer}, "
    f"{duration}s duration."
    )
    

def get_frame_brightness(file_path):
    return 3400.91

TOOLS_FUNCTIONS = {
    "get_video_info":get_video_info,
    "get_frame_brightness":get_frame_brightness
}

messages = [{"role": "user", "content": "I need to grade /Users/akshatvats/Downloads/talking_head_1.MP4. Tell me what I'm working with."}]    

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