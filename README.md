# Giving Your Model Hands Then Setting It Loose

Demo code for DevFest Pretoria 2026.

## Setup

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here          # get one at aistudio.google.com
export GEMINI_MODEL=gemini-3.7-flash         # optional, this is the default
```

Needs Python 3.9 or newer.

## Run

| File | What it shows |
|---|---|
| `00_just_talk.py` | No tools. The model guesses. |
| `01_one_tool.py` | One tool, one round trip, every step printed. |
| `02_two_tools.py` | Two tools, the model picks. Add `--vague` to see bad descriptions. |
| `03_agent_loop.py` | Tool calling in a loop. That's an agent. Prints the model's reasoning and what each step costs. |
| `04_agent_chat.py` | The same agent as a chat that keeps the conversation. That's memory. |

Scripts 00 to 03 take an optional question. Good ones for `03_agent_loop.py`:

```
python 03_agent_loop.py "What's next in the main hall, and how many minutes until it starts?"
python 03_agent_loop.py "Who's speaking in Track 2 right now, and what have they worked on?"
python 03_agent_loop.py "When's the fireside chat? Remind me about it."
python 03_agent_loop.py "What's on in the Workshop track?"
python 03_agent_loop.py "When is lunch?"
```

There's no Workshop track, so `get_schedule` returns an error listing the real tracks.
The model reads it like any other result and recovers.

`04_agent_chat.py` asks for questions until you press Enter on an empty line. Follow-ups work
because the whole conversation goes back to the model each time:

```
YOU: What's the next talk in Track 1?
YOU: Tell me more about that talk, and give me three questions I could ask the speaker.
YOU: Remind me about it.
```

`get_speaker_info` and `research_talk` search the web through Gemini's Google Search grounding.
If the network is slow they give up after 15 seconds; `get_speaker_info` then falls back to the
bios in `SPEAKER_BIOS`. Set `OFFLINE=1` to skip the web entirely.

`remind_me` writes to `reminders.txt`, and the script asks you to approve it before it runs.

Other examples:

```
python 03_agent_loop.py "When is lunch, and what's on in Track 2 right after it?"
```

## Files

`tools.py` holds the functions, the descriptions the model sees, and `run_tool`.
`config.py` holds the client and model name.

All tools are local except `get_speaker_info` and `research_talk`, which search the web.
