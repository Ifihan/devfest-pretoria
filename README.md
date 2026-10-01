# Giving Your Model Hands Then Setting It Loose

Demo code for DevFest Pretoria 2026.

## Setup

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here          # get one at aistudio.google.com
export GEMINI_MODEL=gemini-3.7-flash         # optional, this is the default
export DEMO_TIME=10:20                       # optional, freezes "now" so the demo is predictable
```

Needs Python 3.9 or newer.

## Run

| File | What it shows |
|---|---|
| `00_just_talk.py` | No tools. The model guesses. |
| `01_one_tool.py` | One tool, one round trip, every step printed. |
| `02_two_tools.py` | Two tools, the model picks. Add `--vague` to see bad descriptions. |
| `03_agent_loop.py` | Tool calling in a loop. That's an agent. |

Every script takes an optional question. Good ones for `03_agent_loop.py`:

```
python 03_agent_loop.py "Who's giving the next BUILD talk, and what have they worked on?"
python 03_agent_loop.py "What's next in SCALE? Remind me about it."
python 03_agent_loop.py "When is lunch?"
```

`get_speaker_info` searches the web through Gemini's Google Search grounding. If the network
is slow it gives up after 15 seconds and falls back to the bios in `SPEAKER_BIOS`.
Set `OFFLINE=1` to skip the web entirely.

`remind_me` writes to `reminders.txt`, and the script asks you to approve it before it runs.

Other examples:

```
python 03_agent_loop.py "When is lunch, and what's on in SCALE right after it?"
```

## Files

`tools.py` holds the functions, the descriptions the model sees, and `run_tool`.
`config.py` holds the client and model name.

All tools are local except `get_speaker_info`, which searches the web.
