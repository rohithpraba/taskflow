# TaskFlow

A minimal full-stack task manager: Flask REST API + a single-page React
frontend (no build step — React and Tailwind are loaded via CDN and JSX is
transpiled in-browser by Babel).

## Run locally / on Replit

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:8080 (or the Replit preview URL — the app already
binds to `0.0.0.0:8080` so it works there out of the box).

## API

| Method | Route                  | Description                          |
|--------|-------------------------|--------------------------------------|
| GET    | `/api/tasks`            | List all tasks + progress stats      |
| POST   | `/api/tasks`             | Create a task (`{ "title": str }`)  |
| PATCH  | `/api/tasks/<id>`        | Toggle or set completion status      |
| DELETE | `/api/tasks/<id>`        | Remove a task                        |
| GET    | `/api/stats`             | Progress stats only                  |

Storage is an in-memory Python list — data resets on server restart, as
allowed by the spec.

## Creative feature: Smart Priority Detection

Instead of a manual priority dropdown, `detect_priority()` in `app.py`
scans each task title for urgency keywords ("urgent", "asap", "today",
"deadline", etc. → **High**; "soon", "this week", "important" → **Medium**;
otherwise **Low**) and tags the task automatically. It's a simple,
transparent heuristic rather than a real ML model — chosen deliberately
so it's honest about what it is, fast to build, and easy to extend later
(e.g. swapping in a small classifier trained on real task data).

## Structure

```
taskboard/
├── app.py                # Flask backend + API routes
├── requirements.txt
└── templates/
    └── index.html         # React frontend (CDN React/Babel/Tailwind)
```

## Design notes

- The frontend is served as a static file (`send_from_directory`) rather
  than through Jinja's `render_template`, since the page contains
  in-browser JSX using `{}`/`{{}}` syntax that Jinja would otherwise try
  to parse as its own template syntax.
- Validation lives server-side (empty/overlong titles are rejected with
  a 400), so the API is safe to call from any client, not just this UI.
