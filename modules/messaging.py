"""
Simple file-based messaging between investors and entrepreneurs.
Each conversation thread is stored at data/messages/{id1}__{id2}.json
where the two IDs are always sorted alphabetically so both sides see the same file.
"""
import json
from datetime import datetime
from pathlib import Path

from config.settings import MESSAGES_DIR


# ── Internal helpers ──────────────────────────────────────────────────────────

def _thread_path(user_a: str, user_b: str) -> Path:
    ids = sorted([user_a, user_b])
    return MESSAGES_DIR / f"{'__'.join(ids)}.json"


def _read_thread(path: Path) -> list[dict]:
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []


def _write_thread(path: Path, messages: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)


# ── Public API ────────────────────────────────────────────────────────────────

def send_message(sender_id: str, recipient_id: str, text: str):
    text = text.strip()
    if not text:
        return
    path = _thread_path(sender_id, recipient_id)
    messages = _read_thread(path)
    messages.append({
        "sender_id": sender_id,
        "text": text,
        "timestamp": datetime.now().isoformat(),
        "read": False,
    })
    _write_thread(path, messages)


def get_conversation(user_a: str, user_b: str) -> list[dict]:
    return _read_thread(_thread_path(user_a, user_b))


def mark_read(viewer_id: str, other_id: str):
    path = _thread_path(viewer_id, other_id)
    messages = _read_thread(path)
    for m in messages:
        if m["sender_id"] != viewer_id:
            m["read"] = True
    _write_thread(path, messages)


def get_all_conversations(user_id: str) -> list[dict]:
    """
    Returns all conversation threads involving user_id, newest first.
    Each entry has: other_id, last_message, last_timestamp, unread_count, messages.
    """
    if not MESSAGES_DIR.exists():
        return []

    threads = []
    for path in MESSAGES_DIR.glob("*.json"):
        ids = path.stem.split("__")
        if user_id not in ids:
            continue
        other_id = next(i for i in ids if i != user_id)
        messages = _read_thread(path)
        if not messages:
            continue
        unread = sum(1 for m in messages if m["sender_id"] != user_id and not m["read"])
        threads.append({
            "other_id": other_id,
            "last_message": messages[-1]["text"],
            "last_timestamp": messages[-1]["timestamp"],
            "unread_count": unread,
            "messages": messages,
        })

    threads.sort(key=lambda x: x["last_timestamp"], reverse=True)
    return threads


def get_unread_count(user_id: str) -> int:
    return sum(t["unread_count"] for t in get_all_conversations(user_id))
