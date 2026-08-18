from pydantic import BaseModel
from typing import Literal
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

SYSTEM_COLOR =""" you are a color grading planner. The parameters are temperature from the range -100 to +100 where negative number means cooler and positive means warmer and 0 means unchanged.
 exposure from the range -2 to +2, measured in stops where 0 is unchanged .
 contrast from the range -100 to +100 in which 0 means unchanged and negative means decreasing the value of the contrast and positive means increasing the value of the contrast.
 saturation  from the range -100 to +100 in which 0 means unchanged and negative means decreasing the value of the saturation and positive means increasing the value of the saturation
 tint from the range -100 to +100 in which 0 means unchanged and negative means decreasing the value of the tint(greenish) and positive means increasing the value of the tint(magenta)


 Only include parameters that need to change. Omit any parameter that should stay at 0.

 """

TEST_INPUT = """Frame analysed. Average skin tone RGB: 210, 150, 120.
Overall image brightness: 0.34. Shot on S-Log3, not yet converted.
Grade this for natural skin tones."""


class Adjustment(BaseModel):
    parameter: Literal["temperature", "contrast", "saturation", "tint", "exposure"]
    value:float
    reason: str

class ColorPlan(BaseModel):
    adjustments: list[Adjustment]

client = Anthropic()

def get_color_plan()-> ColorPlan:

    message = client.messages.parse(max_tokens=3000, model='claude-sonnet-5', system=SYSTEM_COLOR, messages=[{"role":"user", "content":TEST_INPUT}],output_format=ColorPlan)

    plan = None

    for block in message.content:
        if block.type == "text":
            plan = block.parsed_output  

    if plan is None:
        raise ValueError("no text block in the response")


    return plan

variance = {}
failures=0
for i in range(10):
    try:
        plan = get_color_plan()
        print(f"{i+1}: ok")
        for adj in plan.adjustments:
            if adj.parameter not in variance:
                variance[adj.parameter] = []
            variance[adj.parameter].append(adj.value)
    except Exception as e:
        failures += 1
        print(f"{i+1}: FAILED - {type(e).__name__}: {e} ")
print(f"{10 - failures}/10 parsed")

print("parameter min max count")

for parameter, values in variance.items():
    print(parameter, min(values), max(values), len(values))
