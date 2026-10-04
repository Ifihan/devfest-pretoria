"""Demo 0. No tools. The model can only talk."""
import sys
from config import client, MODEL, show

question = " ".join(sys.argv[1:]) or (
    "What's the next session in Track 1 at DevFest Pretoria, "
    "and how many minutes until it starts?"
)

show("YOU", question)
response = client.models.generate_content(model=MODEL, contents=question)
show("MODEL", response.text)
