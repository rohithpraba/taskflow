"""TaskFlow API.

A small Flask REST backend with in-memory storage and deterministic keyword-based
priority scoring. Data resets whenever the process restarts.
"""

from __future__ import annotations

from datetime import datetime, timezone
from itertools import count
import os
from typing import Any

from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, template_folder="templates")
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

tasks: list[dict[str, Any]] = []
_id_counter = count(1)

HIGH_PRIORITY_WORDS = {
    "urgent",
    "asap",
    "today",
    "immediately",
    "critical",
    "deadline",
    "now",
}
MEDIUM_PRIORITY_WORDS = {
    "soon",
    "tomorrow",
    "this week",
    "important",
    "priority",
}


def detect_priority(title: str) -> str:
    """Return a deterministic priority label from title keywords."""
    text = title.lower()
    if any(word in text for word in HIGH_PRIORITY_WORDS):
        return "high"
    if any(word in text for word in MEDIUM_PRIORITY_WORDS):
        return "medium"
    return "low"


def find_task(task_id: int) -> dict[str, Any] | None:
    return next((task for task in tasks if task["id"] == task_id), None)


def serialize_stats() -> dict[str, int | float]:
    total = len(tasks)
    completed = sum(1 for task in tasks if task["completed"])
    percentage = round((completed / total) * 100, 1) if total else 0.0
    return {"total": total, "completed": completed, "percentage": percentage}


def _json_object() -> tuple[dict[str, Any] | None, tuple[Any, int] | None]:
    payload = request.get_json(silent=True)
    if payload is None:
        return None, (jsonify({"error": "Request body must be a JSON object."}), 400)
    if not isinstance(payload, dict):
        return None, (jsonify({"error": "Request body must be a JSON object."}), 400)
    return payload, None


@app.get("/")
def index():
    return send_from_directory(TEMPLATES_DIR, "index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "storage": "in-memory"})


@app.get("/api/tasks")
def list_tasks():
    ordered = sorted(tasks, key=lambda task: task["id"], reverse=True)
    return jsonify({"tasks": ordered, "stats": serialize_stats()})


@app.post("/api/tasks")
def add_task():
    payload, error = _json_object()
    if error is not None:
        return error
    assert payload is not None

    raw_title = payload.get("title")
    if not isinstance(raw_title, str):
        return jsonify({"error": "Task title must be a string."}), 400

    title = raw_title.strip()
    if not title:
        return jsonify({"error": "Task title cannot be empty."}), 400
    if len(title) > 200:
        return jsonify({"error": "Task title is too long (max 200 chars)."}), 400

    task = {
        "id": next(_id_counter),
        "title": title,
        "completed": False,
        "priority": detect_priority(title),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    tasks.append(task)
    return jsonify({"task": task, "stats": serialize_stats()}), 201


@app.patch("/api/tasks/<int:task_id>")
def update_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        return jsonify({"error": "Task not found."}), 404

    if request.data:
        payload, error = _json_object()
        if error is not None:
            return error
        assert payload is not None
    else:
        payload = {}

    if "completed" in payload:
        completed = payload["completed"]
        if not isinstance(completed, bool):
            return jsonify({"error": "completed must be a JSON boolean."}), 400
        task["completed"] = completed
    else:
        task["completed"] = not task["completed"]

    return jsonify({"task": task, "stats": serialize_stats()})


@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        return jsonify({"error": "Task not found."}), 404

    tasks.remove(task)
    return jsonify({"deleted": task_id, "stats": serialize_stats()})


@app.get("/api/stats")
def stats():
    return jsonify(serialize_stats())


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8080")),
        debug=_env_bool("FLASK_DEBUG", False),
    )
