"""
TaskFlow API
------------
A small Flask REST backend for a task management app.

Storage: in-memory (runtime persistence only), as required.

Creative feature: Smart Priority Detection.
When a task is created, its title is scanned for urgency signals
(e.g. "urgent", "asap", "today", "deadline") and automatically
tagged High / Medium / Low priority. This removes a manual step
for the user and gives the board a lightweight "smart" feel
without pretending to be a full ML model.
"""

from flask import Flask, jsonify, request, send_from_directory
from datetime import datetime, timezone
from itertools import count
import os

app = Flask(__name__, template_folder="templates")
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------
tasks: list[dict] = []
_id_counter = count(1)

# ---------------------------------------------------------------------------
# Smart Priority Detection (creative feature)
# ---------------------------------------------------------------------------
HIGH_PRIORITY_WORDS = {
    "urgent", "asap", "today", "immediately", "critical", "deadline", "now",
}
MEDIUM_PRIORITY_WORDS = {
    "soon", "tomorrow", "this week", "important", "priority",
}


def detect_priority(title: str) -> str:
    """Infer a priority level from keywords in the task title."""
    text = title.lower()

    if any(word in text for word in HIGH_PRIORITY_WORDS):
        return "high"
    if any(word in text for word in MEDIUM_PRIORITY_WORDS):
        return "medium"
    return "low"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def find_task(task_id: int) -> dict | None:
    return next((t for t in tasks if t["id"] == task_id), None)


def serialize_stats() -> dict:
    total = len(tasks)
    completed = sum(1 for t in tasks if t["completed"])
    percentage = round((completed / total) * 100, 1) if total else 0.0
    return {"total": total, "completed": completed, "percentage": percentage}


# ---------------------------------------------------------------------------
# Routes: frontend
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    # Served as a raw static file (not through Jinja) because the page
    # contains in-browser JSX with {{ }}-style syntax that Jinja would
    # otherwise try (and fail) to parse.
    return send_from_directory(TEMPLATES_DIR, "index.html")


# ---------------------------------------------------------------------------
# Routes: API
# ---------------------------------------------------------------------------
@app.get("/api/tasks")
def list_tasks():
    """Return all tasks, newest first."""
    ordered = sorted(tasks, key=lambda t: t["id"], reverse=True)
    return jsonify({"tasks": ordered, "stats": serialize_stats()})


@app.post("/api/tasks")
def add_task():
    """Create a new task. Body: { "title": str }"""
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()

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
def update_task(task_id):
    """Toggle or set completion status. Body: { "completed": bool } (optional)."""
    task = find_task(task_id)
    if task is None:
        return jsonify({"error": "Task not found."}), 404

    payload = request.get_json(silent=True) or {}
    if "completed" in payload:
        task["completed"] = bool(payload["completed"])
    else:
        task["completed"] = not task["completed"]

    return jsonify({"task": task, "stats": serialize_stats()})


@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    global tasks
    task = find_task(task_id)
    if task is None:
        return jsonify({"error": "Task not found."}), 404

    tasks = [t for t in tasks if t["id"] != task_id]
    return jsonify({"deleted": task_id, "stats": serialize_stats()})


@app.get("/api/stats")
def stats():
    return jsonify(serialize_stats())


if __name__ == "__main__":
    # host=0.0.0.0 is required for the Replit preview link to work
    app.run(host="0.0.0.0", port=8080, debug=True)
