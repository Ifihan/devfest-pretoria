"""Demo 4. The same agent, but we keep the messages between questions. That's memory."""
import importlib
from google.genai import types
from config import show

# Module names can't start with a digit, so import Demo 3's loop this way.
run_agent = importlib.import_module("03_agent_loop").run_agent

contents = []
print("Ask about DevFest Pretoria. Press Enter on an empty line to stop.")

while True:
    question = input("\nYOU: ").strip()
    if not question:
        break
    contents.append(types.Content(role="user", parts=[types.Part(text=question)]))
    run_agent(contents)
    show("MEMORY", f"{len(contents)} messages in the conversation so far")