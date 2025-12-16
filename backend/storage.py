import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "bel_pe_questions.json")

os.makedirs(DATA_DIR, exist_ok=True)


def save_question(entry: dict):
    data = []

    # Safely load existing data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
        except Exception as e:
            print("⚠️ JSON load failed, recreating file:", e)
            data = []

    # Append new entry
    data.append(entry)

    # Safely write back
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_all_questions():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                return json.loads(content)
    except Exception as e:
        print("⚠️ JSON load failed:", e)

    return []
