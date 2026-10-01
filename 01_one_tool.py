"""Demo 1. One tool, one round trip, every step printed."""
import sys
from google.genai import types
from config import client, MODEL, show
from tools import GET_CURRENT_TIME, run_tool

question = " ".join(sys.argv[1:]) or "What time is it in Pretoria right now?"

config = types.GenerateContentConfig(
    tools=[types.Tool(function_declarations=[GET_CURRENT_TIME])],
    # Turn off the SDK's automatic mode so we can see each step ourselves.
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)

contents = [types.Content(role="user", parts=[types.Part(text=question)])]
show("YOU", question)

# Call 1: the model sees the question and the tool list.
response = client.models.generate_content(model=MODEL, contents=contents, config=config)

if not response.function_calls:
    show("MODEL (no tool needed)", response.text)
    sys.exit()

call = response.function_calls[0]
show("MODEL ASKS FOR A TOOL", f"{call.name}({dict(call.args or {})})")

# We run the function. Not the model.
result = run_tool(call.name, dict(call.args or {}))
show("OUR CODE RAN IT", result)

# Call 2: send back the model's request and our result.
contents.append(response.candidates[0].content)
contents.append(types.Content(
    role="user",
    parts=[types.Part.from_function_response(name=call.name, response=result)],
))

response = client.models.generate_content(model=MODEL, contents=contents, config=config)
show("MODEL ANSWERS", response.text)
