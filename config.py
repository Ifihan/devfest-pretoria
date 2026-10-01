"""Shared setup: the Gemini client, the model name, and a small printer."""
import os
from google import genai

# gemini-2.5-flash shuts down 16 Oct 2026, so default to a current 3.x Flash model.
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.7-flash")

# Reads GEMINI_API_KEY from your environment.
client = genai.Client()


def show(label, text=""):
    print(f"\n\033[1m[{label}]\033[0m {text}")
