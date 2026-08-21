from anthropic import Anthropic
from dotenv import load_dotenv
import subprocess, json
import os
import math

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
       
    },
    {
        "name":"apply_grade",
        "description": "It grades your footage and writes a new file for that graded footage. The scale of parameters are: Temperature = -100 to +100, exposure is in stops: -2 to +2, tint = -100 to +100, contrast = -100 to +100, saturation = -100 to +100",
        "input_schema":{
            "type":"object",
            "properties": {
                "file_path":{
                    "type":"string",
                    "description": "Tells where the file is located"
                },
                "temperature":{
                    "type":"number",
                    "description": "tells us the temperature of the footage. negative number means cooler and positive means warmer and 0 means unchanged."
                }, 
                "tint":{
                    "type":"number",
                    "description": "Tells us how much tint is in the footage.  0 means unchanged and negative means decreasing the value of the tint(greenish) and positive means increasing the value of the tint(magenta)"
                },
                "exposure":{
                    "type":"number",
                    "description": "tells us how bright the footage is. Measured in stops where 0 is unchanged "
                },
                "contrast":{
                    "type":"number",
                    "description": "tells us about the contrast of the footage. 0 means unchanged and negative means decreasing the value of the contrast and positive means increasing the value of the contrast."
                },
                "saturation":{
                    "type":"number",
                    "description": "tells us about the saturation of the footage. 0 means unchanged and negative means decreasing the value of the saturation and positive means increasing the value of the saturation"
                }
            },
            "required": ["file_path", "temperature", "saturation", "exposure", "contrast", "tint"]
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
    cmd = ["ffmpeg", "-i", file_path, "-vf", r"select='eq(n\,100)',signalstats,metadata=print", "-f", "null", "-" ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return f"could not read the file"
    stats = {}
    parsed_output = ["YAVG", "YMIN", "YMAX" ,"SATAVG"]

    for line in r.stderr.splitlines():
        if "signalstats" in line:
            for field in parsed_output:
                if field in line:
                    stats[field] = float(line.split("=")[1])

    return (
    f"Measured from frame 100 only, not the whole clip. "
    f"Average luma {stats['YAVG']} on a 0-255 scale (128 = mid-grey). "
    f"Range {stats['YMIN']} to {stats['YMAX']}. "
    f"Average saturation {stats['SATAVG']} on a 0-255 scale."
)
                
def build_filter(temperature, tint, exposure, contrast, saturation):
    new_contrast = 1 + (contrast/100)
    new_gamma =  2 ** (exposure / 2)
    new_saturation = 1 + (saturation/100)
    rm = temperature/1000
    bm = -temperature/1000
    gm = -tint/1000


    return f"colorbalance=gm={gm}:rm={rm}:bm={bm},eq=gamma={new_gamma}:contrast={new_contrast}:saturation={new_saturation}"





def apply_grade(file_path, temperature, tint, exposure, contrast, saturation):
    vf = build_filter(temperature, tint, exposure, contrast, saturation)
    base,ext = os.path.splitext(file_path)
    output_path = f"{base}_graded{ext}"
    cmd = ["ffmpeg","-y", "-i", file_path, "-vf", vf, "-c:a", "copy", output_path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return f"Something went wrong {r.stderr}"
    return f"your file is in {output_path}, and here are the changes that were made: {vf}"



TOOLS_FUNCTIONS = {
    "get_video_info":get_video_info,
    "get_frame_brightness":get_frame_brightness,
    "apply_grade": apply_grade
}

messages = [{"role": "user", "content": " grade /Users/akshatvats/Downloads/talking_head_1.MP4 and do all the color correction"}]    

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