"""Demo 3. The same tool calling, in a loop. That's an agent."""
import sys
from google.genai import types
from config import client, MODEL, show
from tools import (GET_CURRENT_TIME, GET_SCHEDULE, MINUTES_BETWEEN,
                   GET_SPEAKER_INFO, REMIND_ME, run_tool, LIST_REMINDERS, run_tool)

MAX_STEPS = 8

question = " ".join(sys.argv[1:]) or (
    "What's the next session in the BUILD track at DevFest Pretoria, "
    "and how many minutes until it starts?"
)

config = types.GenerateContentConfig(
    system_instruction=(
    "You are a helpful assistant at DevFest Pretoria. "
    "Never guess about the time, the schedule, speakers or the user's reminders. "
    "Always use a tool for those. If no tool can answer, say so."
),
    tools=[types.Tool(function_declarations=[
        GET_CURRENT_TIME, GET_SCHEDULE, MINUTES_BETWEEN, GET_SPEAKER_INFO, REMIND_ME, LIST_REMINDERS
    ])],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)

contents = [types.Content(role="user", parts=[types.Part(text=question)])]
show("YOU", question)

for step in range(1, MAX_STEPS + 1):
    response = client.models.generate_content(model=MODEL, contents=contents, config=config)

    if not response.function_calls:
        show(f"DONE AFTER {step - 1} TOOL STEP(S)", response.text)
        break

    contents.append(response.candidates[0].content)
    parts = []
    for call in response.function_calls:
        args = dict(call.args or {})
        show(f"STEP {step}", f"model asks for {call.name}({args})")
        result = run_tool(call.name, args)
        show(f"STEP {step}", f"our code returned {result}")
        parts.append(types.Part.from_function_response(name=call.name, response=result))
    contents.append(types.Content(role="user", parts=parts))
else:
    show("STOPPED", f"Hit MAX_STEPS={MAX_STEPS} without a final answer.")
