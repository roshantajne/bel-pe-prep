import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "bel_pe_questions.json")

os.makedirs(DATA_DIR, exist_ok=True)



SCOPES = ["https://www.googleapis.com/auth/documents"]

def append_to_google_doc(text: str):
    creds_dict = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))

    credentials = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES
    )

    service = build("docs", "v1", credentials=credentials)

    doc_id = os.getenv("GOOGLE_DOC_ID")

    requests = [
        {
            "insertText": {
                "location": {"index": 1},
                "text": text + "\n\n"
            }
        }
    ]

    service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": requests}
    ).execute()


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
