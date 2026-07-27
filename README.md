# TaskFlow

> **Status:** Demonstration project. Tasks are stored in memory and reset when the server restarts.

TaskFlow is a minimal task manager with a Flask REST API and a single-page React frontend. It assigns a transparent priority label from title keywords; the priority rule is deterministic and is not presented as a trained Machine Learning model.

## Features

- Create, list, update, and delete tasks through REST endpoints
- Track completion statistics
- Assign High, Medium, or Low priority from documented keywords
- Validate JSON payloads and boolean completion values
- Serve a lightweight browser interface without a frontend build step

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:8080`.

Environment variables:

```text
HOST=127.0.0.1
PORT=8080
FLASK_DEBUG=false
```

## API

| Method | Route | Description |
|---|---|---|
| GET | `/health` | Basic process and storage status |
| GET | `/api/tasks` | List tasks and completion statistics |
| POST | `/api/tasks` | Create a task from `{ "title": "..." }` |
| PATCH | `/api/tasks/<id>` | Toggle completion or set `{ "completed": true/false }` |
| DELETE | `/api/tasks/<id>` | Delete a task |
| GET | `/api/stats` | Return completion statistics |

## Test

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
```

## Limitations

- No persistent database
- No authentication or multi-user isolation
- Intended for local demonstration, not production operation
- React, Babel, and the styling library are loaded by the existing frontend from public CDNs
