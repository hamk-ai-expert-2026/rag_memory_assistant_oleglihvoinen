from pathlib import Path

MEMORY_FILE = Path("memory.md")
DEFAULTS = {
    "preferred_name": "",
    "answer_language": "English",
    "answer_detail": "Medium",
}


def load_preferences():
    preferences = DEFAULTS.copy()
    if not MEMORY_FILE.exists():
        save_preferences(preferences)
        return preferences

    for line in MEMORY_FILE.read_text(encoding="utf-8").splitlines():
        if ":" not in line or line.startswith("#"):
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key in preferences:
            preferences[key] = value
    return preferences


def save_preferences(preferences):
    safe = DEFAULTS.copy()
    for key in safe:
        value = str(preferences.get(key, safe[key])).strip()
        safe[key] = value

    content = (
        "# MemoryRAG user preferences\n\n"
        "preferred_name: " + safe["preferred_name"] + "\n"
        "answer_language: " + safe["answer_language"] + "\n"
        "answer_detail: " + safe["answer_detail"] + "\n"
    )
    MEMORY_FILE.write_text(content, encoding="utf-8")
