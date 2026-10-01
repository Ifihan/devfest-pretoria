"""Demo 2. Two tools. The model picks which one.

python 02_two_tools.py "What's on in the SCALE track today?"
python 02_two_tools.py "What time is it?"
python 02_two_tools.py --vague "What's on in the SCALE track today?"   # bad descriptions
"""
import sys
from google.genai import types
from config import client, MODEL, show
from tools import (GET_CURRENT_TIME, GET_SCHEDULE,
                   VAGUE_GET_CURRENT_TIME, VAGUE_GET_SCHEDULE, run_tool)

args = sys.argv[1:]
vague = "--vague" in args
args = [a for a in args if a != "--vague"]
question = " ".join(args) or "What's on in the SCALE track today?"

declarations = ([VAGUE_GET_CURRENT_TIME, VAGUE_GET_SCHEDULE] if vague
                else [GET_CURRENT_TIME, GET_SCHEDULE])

config = types.GenerateContentConfig(
    tools=[types.Tool(function_declarations=declarations)],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)

contents = [types.Content(role="user", parts=[types.Part(text=question)])]
show("YOU", question + ("   (vague descriptions)" if vague else ""))

response = client.models.generate_content(model=MODEL, contents=contents, config=config)

if not response.function_calls:
    show("MODEL (no tool used)", response.text)
    sys.exit()

contents.append(response.candidates[0].content)
parts = []
for call in response.function_calls:
    show("MODEL PICKED", f"{call.name}({dict(call.args or {})})")
    result = run_tool(call.name, dict(call.args or {}))
    show("OUR CODE RAN IT", result)
    parts.append(types.Part.from_function_response(name=call.name, response=result))
contents.append(types.Content(role="user", parts=parts))

response = client.models.generate_content(model=MODEL, contents=contents, config=config)
show("MODEL ANSWERS", response.text)
