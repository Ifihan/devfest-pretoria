"""Demo 3. The same tool calling, in a loop. That's an agent."""
import re
import sys
import time
from google.genai import types
from config import client, MODEL, show
from tools import (GET_CURRENT_TIME, GET_SCHEDULE, MINUTES_BETWEEN, GET_SPEAKER_INFO,
                   RESEARCH_TALK, REMIND_ME, LIST_REMINDERS, run_tool)

MAX_STEPS = 8

config = types.GenerateContentConfig(
    system_instruction=(
        "You are a helpful assistant at DevFest Pretoria. "
        "Never guess about the time, the schedule, speakers, talks or the user's reminders. "
        "Always use a tool for those. If no tool can answer, say so."
    ),
    tools=[types.Tool(function_declarations=[
        GET_CURRENT_TIME, GET_SCHEDULE, MINUTES_BETWEEN, GET_SPEAKER_INFO,
        RESEARCH_TALK, REMIND_ME, LIST_REMINDERS,
    ])],
    thinking_config=types.ThinkingConfig(include_thoughts=True),
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)


def headline(thought):
    """Gemini's thought summaries are long. Show just the first bold heading."""
    heading = re.search(r"\*\*(.+?)\*\*", thought)
    text = heading.group(1) if heading else thought.strip()
    return text if len(text) <= 100 else text[:100] + "…"


def run_agent(contents):
    """Call the model until it stops asking for tools, then return its answer."""
    total = {"in": 0, "out": 0, "thinking": 0, "seconds": 0.0}

    for step in range(1, MAX_STEPS + 1):
        started = time.perf_counter()
        response = client.models.generate_content(model=MODEL, contents=contents, config=config)
        usage = response.usage_metadata
        cost = {"in": usage.prompt_token_count or 0, "out": usage.candidates_token_count or 0,
                "thinking": usage.thoughts_token_count or 0,
                "seconds": time.perf_counter() - started}
        total = {k: total[k] + cost[k] for k in total}

        message = response.candidates[0].content
        contents.append(message)
        for part in message.parts:
            if part.thought and part.text:
                show(f"STEP {step} THINKING", headline(part.text))
        show(f"STEP {step} COST", "{in:,} tokens in · {out:,} out · {thinking:,} thinking · {seconds:.1f}s".format(**cost))

        if not response.function_calls:
            answer = "".join(p.text for p in message.parts if p.text and not p.thought)
            show(f"ANSWER AFTER {step - 1} TOOL STEP(S)", answer)
            show("TOTAL", "{in:,} tokens in · {out:,} out · {thinking:,} thinking · {seconds:.1f}s".format(**total))
            return answer

        parts = []
        for call in response.function_calls:
            args = dict(call.args or {})
            show(f"STEP {step}", f"model asks for {call.name}({args})")
            result = run_tool(call.name, args)
            show(f"STEP {step}", f"our code returned {result}")
            parts.append(types.Part.from_function_response(name=call.name, response=result))
        contents.append(types.Content(role="user", parts=parts))

    show("STOPPED", f"Hit MAX_STEPS={MAX_STEPS} without a final answer.")


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or (
        "What's next in the main hall at DevFest Pretoria, "
        "and how many minutes until it starts?"
    )
    show("YOU", question)
    run_agent([types.Content(role="user", parts=[types.Part(text=question)])])
