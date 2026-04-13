import json
import os
from typing import Optional

MEMORY_DIR = "memory/profiles"

def save_profile(user_id: str, data: dict):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    path = f"{MEMORY_DIR}/{user_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_profile(user_id: str) -> Optional[dict]:
    path = f"{MEMORY_DIR}/{user_id}.json"
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def profile_exists(user_id: str) -> bool:
    return os.path.exists(f"{MEMORY_DIR}/{user_id}.json")

def update_profile(user_id: str, data: dict):
    profile = load_profile(user_id) or {}
    profile.update(data)
    save_profile(user_id, profile)

def update_profile(user_id: str, updates: dict):
    existing = load_profile(user_id) or {}
    existing.update(updates)
    save_profile(user_id, existing)

def save_to_history(user_id: str, result: dict):
    from datetime import datetime
    history = load_history(user_id)
    entry = {
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "profile": result.get("profile", {}),
        "nutrition": result.get("nutrition", {}),
        "training": result.get("training", {}),
        "validation": result.get("validation", {})
    }
    history.append(entry)
    os.makedirs(MEMORY_DIR, exist_ok=True)
    path = f"{MEMORY_DIR}/{user_id}_history.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_history(user_id: str) -> list:
    path = f"{MEMORY_DIR}/{user_id}_history.json"
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_checkin(user_id: str, checkin: dict):
    from datetime import datetime
    checkins = load_checkins(user_id)
    checkin["date"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    checkins.append(checkin)
    os.makedirs(MEMORY_DIR, exist_ok=True)
    path = f"{MEMORY_DIR}/{user_id}_checkins.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(checkins, f, ensure_ascii=False, indent=2)

def load_checkins(user_id: str) -> list:
    path = f"{MEMORY_DIR}/{user_id}_checkins.json"
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)