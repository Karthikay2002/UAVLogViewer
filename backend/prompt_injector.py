# backend/utils/prompt_injector.py
import json
import os
from utils.memory_store import MemoryStore

# Paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
LOGDOCS_PATH = os.path.join(BACKEND_DIR, "logdocs_dict.json")
LOGCODES_PATH = os.path.join(BACKEND_DIR, "logcodes_dict.json")

# Load both knowledge bases
try:
    with open(LOGDOCS_PATH, "r") as f:
        FIELD_DOCS = json.load(f)
except Exception as e:
    FIELD_DOCS = {}
    print(f"[!] Could not load logdocs_dict.json: {e}")

try:
    with open(LOGCODES_PATH, "r") as f:
        CODE_DOCS = json.load(f)
except Exception as e:
    CODE_DOCS = {}
    print(f"[!] Could not load logcodes_dict.json: {e}")

memory = MemoryStore()

def inject_field_explanations(user_question: str) -> str:
    """Injects context from telemetry fields and error codes into LLM prompt."""
    context = []
    lower_q = user_question.lower()

    # Inject telemetry fields (AccX, SampleUS...)
    for field, meta in FIELD_DOCS.items():
        if field.lower() in lower_q:
            explanation = f"\n• **{field}** ({meta.get('unit', '')}): {meta.get('description', '')}"
            context.append(explanation)

    # Inject log error codes (FAILSAFE, GPSGLITCH...)
    for code, desc in CODE_DOCS.items():
        if code.lower() in lower_q:
            explanation = f"\n• **{code}**: {desc}"
            context.append(explanation)

    if context:
        return "\n\n📌 **Context from MAVLink Log Reference:**" + "".join(context)
    else:
        return ""

# Example usage (test)
if __name__ == "__main__":
    q = "What does AccX and SampleUS represent in this log?"
    print(inject_field_explanations(q))
