import os
import json
from config import PREFERENCES_FILE, MEMORY_FILE, file_lock

def load_preferences():
    with file_lock:
        if os.path.exists(PREFERENCES_FILE):
            try:
                with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "favorite_apps": [],
            "work_hours": {"start": "09:00", "end": "18:00"},
            "music_preferences": [],
            "low_battery_alert": 20,
            "username": os.getlogin() if hasattr(os, "getlogin") else "Sir",
        }

def save_preferences(prefs):
    with file_lock:
        try:
            with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
                json.dump(prefs, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")

def load_memory():
    with file_lock:
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"conversations": [], "facts": {}}

def save_memory(memory_data):
    with file_lock:
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(memory_data, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")

def add_conversation_memory(user_cmd, assistant_response):
    mem = load_memory()
    mem["conversations"].append(f"User: {user_cmd} | Jay: {assistant_response[:100]}")
    if len(mem["conversations"]) > 50:
        mem["conversations"] = mem["conversations"][-50:]
    save_memory(mem)
