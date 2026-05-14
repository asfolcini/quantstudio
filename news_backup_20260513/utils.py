import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from dateutil import parser

def load_config() -> dict:
    with open(Path(__file__).parent.parent / "config" / "config.json", "r") as f:
        return json.load(f)

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    return text

def is_recent(entry_date: str, hours: int = 48) -> bool:
    try:
        published_at = parser.parse(entry_date)
        now = datetime.now(timezone.utc)
        return (now - published_at) <= timedelta(hours=hours)
    except (ValueError, TypeError):
        return False

def to_iso_utc(date_str: str) -> str:
    try:
        dt = parser.parse(date_str)
        return dt.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    except (ValueError, TypeError):
        return None
