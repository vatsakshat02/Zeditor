from anthropic import Anthropic
from dotenv import load_dotenv
import json

load_dotenv()

SYSTEM_COLOR =""" you are a color grading planner. The output should be JSON only no markdown code fences, no prose before and after and the parameters are temperature from the range -100 to +100 where negative number means cooler and positive means warmer and 0 means unchanged.
 exposure from the range -2 to +2, measured in stops where 0 is unchanged .
 contrast from the range -100 to +100 in which 0 means unchanged and negative means decreasing the value of the contrast and positive means increasing the value of the contrast.
 saturation  from the range -100 to +100 in which 0 means unchanged and negative means decreasing the value of the saturation and positive means increasing the value of the saturation
 tint from the range -100 to +100 in which 0 means unchanged and negative means decreasing the value of the tint(greenish) and positive means increasing the value of the tint(magenta)

 shape of json should look like this: 
 {
 "adjustments":[
 {"parameter": "temperature","value":-8,"reason":"footage too warm"}
 ]
 }

 parameters must be exactly of temperature, exposure, contrast, saturation, tint only these parameters should be there nothing other than them.Only include parameters that need to change. Omit any parameter that should stay at 0.

 tHe reason is also mandatory
 """

TEST_INPUT = """Frame analysed. Average skin tone RGB: 210, 150, 120.
Overall image brightness: 0.34. Shot on S-Log3, not yet converted.
Grade this for natural skin tones."""

client = Anthropic()

def get_color_plan():
    
    message = client.messages.create(model="claude-sonnet-5", max_tokens=3000, system=SYSTEM_COLOR,messages=[{"role":"user","content":TEST_INPUT}])

    raw_text = None

    for block in message.content:
        if block.type == "text":
            raw_text = block.text

    if raw_text is None:
        raise ValueError('No text block in the response')

    plan = json.loads(raw_text)
    
    return plan

failures = 0
for i in range(10):
    try:
        plan = get_color_plan()
        print(f"{i+1}: ok")
    except Exception as e:
        failures += 1
        print(f"{i+1}: FAILED - {type(e).__name__}: {e}")
print(f"{10 - failures}/10 parsed")
