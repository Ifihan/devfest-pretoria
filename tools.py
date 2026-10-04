"""The tools. Plain Python functions plus the descriptions the model sees.

Everything is local except get_speaker_info, which searches the web.
"""
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from google import genai
from google.genai import types
from config import MODEL

# ---------------------------------------------------------------------------
# The data: the DevFest Pretoria 2026 programme
# ---------------------------------------------------------------------------
SCHEDULE = {
    "MAIN": [
        {"start": "08:30", "end": "09:00", "title": "Registration, Networking and Welcome", "speaker": ""},
        {"start": "09:00", "end": "09:20", "title": "Opening and Welcome to DevFest", "speaker": ""},
        {"start": "09:20", "end": "09:50", "title": "Opening Keynote: When Intelligence Is No Longer Scarce. Why Adaptability Will Define the Agentic Era", "speaker": "Shiksha Ramgovind (Absa)"},
        {"start": "11:10", "end": "11:20", "title": "Short Break", "speaker": ""},
        {"start": "12:15", "end": "12:25", "title": "Group Photo", "speaker": ""},
        {"start": "12:25", "end": "13:15", "title": "Lunch and Networking", "speaker": ""},
        {"start": "15:05", "end": "15:15", "title": "Transition back to the main hall", "speaker": ""},
        {"start": "15:15", "end": "15:35", "title": "Fireside Chat: Build, Secure, Scale: Developers and Builders in the Agentic Era", "speaker": ""},
        {"start": "15:35", "end": "15:50", "title": "Vote of Thanks and Closing", "speaker": ""},
    ],
    "TRACK 1": [
        {"start": "10:00", "end": "10:35", "title": "Under the Hood: Flutter Fundamentals for New App Developers", "speaker": "Sylvia Dieckmann"},
        {"start": "10:35", "end": "11:10", "title": "Building an Offline Agentic Assistant for Android", "speaker": "Johan van Rooyen"},
        {"start": "11:20", "end": "11:55", "title": "The Cost of AI FOMO: How Hype is Burning Businesses", "speaker": "Thabang Ledwaba"},
        {"start": "11:55", "end": "12:15", "title": "Trust, Tracking, and Trust Boundaries: A Guide to Thinking Like an Attacker", "speaker": "Refiloe Mokopakgosi"},
        {"start": "13:15", "end": "14:30", "title": "Orchestrating Parallel Agents with Antigravity 2.0 and Gemini 3.7 Flash", "speaker": "Gabriel Agbobli"},
        {"start": "14:30", "end": "15:05", "title": "Giving Your Model Hands Then Setting It Loose", "speaker": "Ifihanagbara Olusheye"},
    ],
    "TRACK 2": [
        {"start": "10:00", "end": "10:35", "title": "AI in Production: Sampling, Labeling and Detecting Drift Before Your Customers Do", "speaker": "Akshata Mohanty"},
        {"start": "10:35", "end": "11:10", "title": "Evaluating Generative AI with the Gemini Enterprise Agent Platform", "speaker": "Thamu Mnyulwa"},
        {"start": "11:20", "end": "11:55", "title": "The Blueprint Before The Build", "speaker": "Symphorose Tshibombi"},
        {"start": "11:55", "end": "12:15", "title": "Entrepreneurship Talk", "speaker": "CodeVault"},
        {"start": "13:15", "end": "14:30", "title": "AI on Android: Tap into On-Device Generative AI with AICore", "speaker": "Tashinga Pemhiwa"},
        {"start": "14:30", "end": "15:05", "title": "Reification of Application Intent as an Executable Intermediate Representation for Agentic Systems", "speaker": "Gugulethu Nyoni"},
    ],
    "FORGE": [
        {"start": "13:15", "end": "15:05", "title": "Buildathon", "speaker": "Kananelo and the Forge Team"},
    ],
}


# ---------------------------------------------------------------------------
# The functions: this is the code that actually runs
# ---------------------------------------------------------------------------
def get_current_time() -> dict:
    """Current time in Pretoria. Set DEMO_TIME=10:20 to freeze it for a demo."""
    frozen = os.environ.get("DEMO_TIME")
    if frozen:
        return {"time": frozen, "timezone": "Africa/Johannesburg"}
    now = datetime.now(ZoneInfo("Africa/Johannesburg"))
    return {"time": now.strftime("%H:%M"), "timezone": "Africa/Johannesburg"}


def get_schedule(track: str) -> dict:
    """All sessions in one track."""
    for name, sessions in SCHEDULE.items():
        if name.lower() == track.strip().lower():
            return {"track": name, "sessions": sessions}
    return {"error": f"No track called '{track}'. Try one of {list(SCHEDULE)}."}


def minutes_between(start: str, end: str) -> dict:
    """Minutes from start to end, both as HH:MM."""
    fmt = "%H:%M"
    diff = datetime.strptime(end, fmt) - datetime.strptime(start, fmt)
    return {"minutes": int(diff.total_seconds() // 60)}

def list_reminders() -> dict:
    """Read the saved reminders. Read only, so no approval needed."""
    if not os.path.exists("reminders.txt"):
        return {"reminders": []}
    with open("reminders.txt") as f:
        return {"reminders": [line.strip() for line in f if line.strip()]}

LIST_REMINDERS = {
    "name": "list_reminders",
    "description": "List all of the user's saved reminders for DevFest sessions.",
    "parameters_json_schema": {"type": "object", "properties": {}},
}


# Short bios from the programme. Used on their own when there's no internet,
# and alongside the web search when there is.
SPEAKER_BIOS = {
    "Ifihanagbara Olusheye": (
        "AI/ML engineer and Google Developer Expert in AI. MSc student in AI at "
        "Wits, and founder of ML Lagos."
    ),
}

# A separate client with a short timeout, so a slow venue network can't hang the demo.
_search_client = genai.Client(http_options=types.HttpOptions(timeout=15_000))


def get_speaker_info(name: str) -> dict:
    """Look a speaker up on the web. A tool can be anything, even another model call."""
    result = {"name": name, "bio_from_programme": SPEAKER_BIOS.get(name)}
    if os.environ.get("OFFLINE"):
        return result
    try:
        response = _search_client.models.generate_content(
            model=MODEL,
            contents=(
                f"{name} is speaking at DevFest Pretoria 2026. In two or three sentences, "
                "summarise their professional background: role, organisation, and the "
                "technical work they are known for. Only use sources that clearly refer "
                "to this person. If you can't find anything reliable, say so."
            ),
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            ),
        )
        result["from_the_web"] = response.text
        meta = response.candidates[0].grounding_metadata
        chunks = (meta.grounding_chunks or []) if meta else []
        result["sources"] = [c.web.title for c in chunks[:3] if c.web]
    except Exception as e:
        result["web_error"] = f"Search failed ({type(e).__name__}), using the programme bio only."
    return result


def remind_me(title: str, start: str) -> dict:
    """Save a reminder to reminders.txt. This one changes something, so it needs approval."""
    with open("reminders.txt", "a") as f:
        f.write(f"{start}  {title}\n")
    return {"saved": True, "reminder": f"{start} {title}"}


# ---------------------------------------------------------------------------
# The descriptions: this is all the model ever sees
# ---------------------------------------------------------------------------
GET_CURRENT_TIME = {
    "name": "get_current_time",
    "description": "Get the current local time in Pretoria, South Africa, as HH:MM.",
    "parameters_json_schema": {"type": "object", "properties": {}},
}

GET_SCHEDULE = {
    "name": "get_schedule",
    "description": (
        "Get the DevFest Pretoria 2026 sessions in one track, with each session's "
        "start and end time (HH:MM), title and speaker. MAIN holds everything "
        "for all attendees: registration, opening, keynote, breaks, lunch and closing. "
        "TRACK 1 and TRACK 2 run in parallel. FORGE is the buildathon."
    ),
    "parameters_json_schema": {
        "type": "object",
        "properties": {
            "track": {
                "type": "string",
                "enum": ["MAIN", "TRACK 1", "TRACK 2", "FORGE"],
                "description": "Which track to look up.",
            }
        },
        "required": ["track"],
    },
}

MINUTES_BETWEEN = {
    "name": "minutes_between",
    "description": "Calculate how many minutes there are between two times given as HH:MM.",
    "parameters_json_schema": {
        "type": "object",
        "properties": {
            "start": {"type": "string", "description": "Earlier time, HH:MM."},
            "end": {"type": "string", "description": "Later time, HH:MM."},
        },
        "required": ["start", "end"],
    },
}

GET_SPEAKER_INFO = {
    "name": "get_speaker_info",
    "description": (
        "Search the web for a DevFest Pretoria 2026 speaker's professional background. "
        "Use the speaker's full name exactly as it appears in the schedule."
    ),
    "parameters_json_schema": {
        "type": "object",
        "properties": {"name": {"type": "string", "description": "Speaker's full name."}},
        "required": ["name"],
    },
}

REMIND_ME = {
    "name": "remind_me",
    "description": "Save a reminder for a session so the user doesn't miss it.",
    "parameters_json_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Session title."},
            "start": {"type": "string", "description": "Session start time, HH:MM."},
        },
        "required": ["title", "start"],
    },
}

# Deliberately bad descriptions, for the "description is the interface" slide.
VAGUE_GET_CURRENT_TIME = {
    "name": "get_current_time",
    "description": "Gets data.",
    "parameters_json_schema": {"type": "object", "properties": {}},
}
VAGUE_GET_SCHEDULE = {
    "name": "get_schedule",
    "description": "Gets data.",
    "parameters_json_schema": {
        "type": "object",
        "properties": {"track": {"type": "string"}},
        "required": ["track"],
    },
}

# Name -> function, so we can run whatever the model asks for.
REGISTRY = {
    "get_current_time": get_current_time,
    "get_schedule": get_schedule,
    "minutes_between": minutes_between,
    "get_speaker_info": get_speaker_info,
    "remind_me": remind_me,
    "list_reminders": list_reminders,
}

# Tools that change something in the world. A human says yes before these run.
NEEDS_APPROVAL = {"remind_me"}


def run_tool(name: str, args: dict) -> dict:
    """The model never runs anything. We do, right here."""
    if name not in REGISTRY:
        return {"error": f"Unknown tool '{name}'."}
    if name in NEEDS_APPROVAL:
        answer = input(f"\n  The model wants to run {name}({args}). Allow? [y/N] ")
        if answer.strip().lower() != "y":
            return {"error": "The user declined this action. Do not retry it."}
    try:
        return REGISTRY[name](**args)
    except Exception as e:  # bad arguments go back to the model as an error
        return {"error": str(e)}
