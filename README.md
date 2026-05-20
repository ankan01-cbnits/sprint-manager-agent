# Sprinter - Sprint Analyzer AI

Sprinter is a FastAPI + LangGraph application that analyzes an active Jira sprint through a small multi-agent workflow. The UI is a single-page chat dashboard where a user can ask questions like "What are the blockers?", "How healthy is the sprint?", "Who is overloaded?", or "Give me recommendations". The backend routes each question to specialized agents, gathers sprint data, and returns a synthesized markdown answer.

This README is written as project context for another coding agent. If Claude is going to write code in this repo, start with the "Claude handoff" and "Suggested work items" sections near the bottom.

## Current Stack

- Python 3.12+
- FastAPI for the API server
- Uvicorn for local development
- LangGraph for the agent workflow
- LangChain OpenAI client configured against Groq's OpenAI-compatible API
- Jira Cloud REST API for live sprint data
- `python-dotenv` for local environment variables
- Static HTML/CSS/JS UI mounted from `ui/`
- `uv` for dependency management

## Project Layout

```text
.
|-- main.py                      # Minimal uv-created entrypoint, not the FastAPI app
|-- pyproject.toml               # Project metadata and dependencies
|-- test_jira.py                 # Manual script for validating Jira loading
|-- ui/
|   |-- __init__.py
|   `-- index.html               # Static chat dashboard
`-- src/
    |-- main.py                  # FastAPI app and HTTP endpoints
    |-- agents/
    |   |-- base.py              # LLM factory using Groq API via ChatOpenAI
    |   |-- orchestrator.py      # Selects specialized agents for each query
    |   |-- todo_agent.py        # Task/status/ownership analysis
    |   |-- health_agent.py      # Sprint health, burndown, velocity analysis
    |   |-- blocker_agent.py     # Blocker and risk detection
    |   |-- recommendation_agent.py
    |   `-- summary_agent.py     # Final answer synthesis
    |-- data/
    |   |-- jira_client.py       # Jira Cloud API integration
    |   `-- mock_jira.py         # Data shaping helpers and fallback wrapper
    `-- graph/
        |-- state.py             # Shared LangGraph state shape
        `-- workflow.py          # Graph construction and routing
```

## How The App Works

1. The frontend sends a user query to `POST /analyze`.
2. `src/main.py` adds the query to an in-memory `chat_history`.
3. A LangGraph state object is created with the query, chat history, empty sprint data, empty agent outputs, and an empty final answer.
4. `load_data_node` calls `get_sprint_data()` to fetch the active sprint.
5. The orchestrator LLM decides which agents are needed.
6. LangGraph routes to selected specialized agents:
   - `todo`
   - `health`
   - `blocker`
   - `recommendation`
7. The selected agents analyze shaped subsets of the sprint data.
8. The summary agent combines agent outputs into a final markdown answer.
9. The API returns the answer, selected agents, and sprint name.
10. The frontend renders markdown using `marked` and highlights the agents used.

## API Surface

### `POST /analyze`

Request:

```json
{
  "query": "What are the blockers?"
}
```

Response:

```json
{
  "answer": "markdown answer",
  "agents_used": ["blocker"],
  "sprint_name": "Sprint name from Jira"
}
```

### `GET /sprint-meta`

Returns the current sprint `meta` object. The UI uses this to populate the top bar, completion progress, velocity numbers, and team label.

### `POST /reset`

Clears the in-memory chat history.

### Static UI

The UI is mounted at:

```text
/ui/index.html
```

When the server is running, open:

```text
http://127.0.0.1:8000/ui/index.html
```

## Local Setup

Install dependencies:

```bash
uv sync
```

Create a `.env` file in the project root. The code currently expects these variables:

```bash
GROQ_API_KEY_2=your_groq_key
JIRA_DOMAIN=https://your-domain.atlassian.net
JIRA_EMAIL=your_email@example.com
JIRA_API_TOKEN=your_jira_api_token
JIRA_PROJECT_KEY=ORN
```

Run the FastAPI app:

```bash
uv run uvicorn src.main:app --reload
```

Open the UI:

```text
http://127.0.0.1:8000/ui/index.html
```

Manually test Jira loading:

```bash
uv run python test_jira.py
```

## Data Contract

The agents expect `get_sprint_data()` to return:

```python
{
    "meta": {
        "sprint_id": str,
        "sprint_name": str,
        "team": str,
        "start_date": str,
        "end_date": str,
        "total_story_points": int,
        "completed_story_points": int,
        "days_elapsed": int,
        "days_remaining": int,
        "velocity_last_sprint": int,
        "velocity_avg_3_sprints": int,
    },
    "issues": [
        {
            "id": str,
            "summary": str,
            "type": str,
            "status": str,
            "assignee": str,
            "priority": str,
            "story_points": int,
            "labels": list[str],
            "updated": str,
            "created": str,
            "blockers": list[str],
            "comments": list[dict],
        }
    ]
}
```

The specialized data helper functions in `src/data/mock_jira.py` intentionally narrow this full object before passing it to each agent:

- `get_todo_data()` passes issue status, assignee, points, updated date, and blockers.
- `get_health_data()` passes meta, status counts, points by status, and assignee point totals.
- `get_blocker_data()` passes at-risk issues only.
- `get_recommendation_data()` passes incomplete high-priority items and workload data.

## Agent Responsibilities

### Orchestrator

File: `src/agents/orchestrator.py`

Reads the current query plus recent chat history and returns JSON:

```json
{
  "agents_to_run": ["todo", "health"],
  "reasoning": "one sentence"
}
```

Only `agents_to_run` is used by the graph.

### Todo Agent

File: `src/agents/todo_agent.py`

Handles statuses, owners, story points, stale tickets, unassigned tickets, and workload distribution.

### Health Agent

File: `src/agents/health_agent.py`

Handles burndown, sprint health score, velocity comparison, completion risk, bug/story mix, and work distribution.

### Blocker Agent

File: `src/agents/blocker_agent.py`

Looks for explicit blockers, cascade blockers, silent stalls, unassigned critical/high-priority work, dependencies, and review bottlenecks.

### Recommendation Agent

File: `src/agents/recommendation_agent.py`

Produces prioritized action items. It can use outputs from todo, health, and blocker agents if those ran earlier in the same graph state.

### Summary Agent

File: `src/agents/summary_agent.py`

Combines available agent outputs into the final user-facing markdown response.

## LangGraph Details

The graph is built in `src/graph/workflow.py`:

```text
load_data -> orchestrator -> selected agents -> summary -> END
```

Important detail: `route_agents()` maps logical agent names to node names:

```python
{
    "todo": "todo_agent",
    "health": "health_agent",
    "blocker": "blocker_agent",
    "recommendation": "recommendation_agent",
}
```

The graph currently adds edges from each specialized agent to `summary`. If more routing paths are added, make sure every path still reaches `summary`.

## Jira Integration

File: `src/data/jira_client.py`

Current Jira behavior:

- Finds the first board for `JIRA_PROJECT_KEY`.
- Finds the first active sprint on that board.
- Fetches up to 100 issues for that sprint.
- Extracts common fields:
  - summary
  - status
  - assignee
  - priority
  - issue type
  - story points from `customfield_10016`
  - labels
  - last 3 comments
  - issue links as blocker strings
  - created/updated dates
- Builds sprint metadata from live issue data.

Potential Jira customization points:

- `customfield_10016` may not be the Story Points field in every Jira instance.
- Board selection currently uses the first board returned for the project.
- Velocity history is currently hardcoded to `0`.
- Pagination is not implemented beyond `maxResults: 100`.

## Frontend Details

File: `ui/index.html`

The frontend is plain HTML/CSS/JS. It:

- Loads sprint metadata from `/sprint-meta`.
- Sends chat messages to `/analyze`.
- Renders markdown answers with `marked`.
- Uses Lucide icons from CDN.
- Supports light/dark theme via `localStorage`.
- Displays selected agents and a simple run activity panel.
- Shows fallback mock-like UI metrics only if `/sprint-meta` cannot be reached.

No frontend build tool is currently used.

## Current Limitations And Sharp Edges

These are useful starting points for Claude if you want improvements written:

- `README.md` was empty before this handoff.
- `src/main.py` imports `load_dotenv` but does not call it. Other modules call it, so the app still works through `base.py` and `jira_client.py`.
- `main.py` at the repo root is a default placeholder and is not the real app entrypoint.
- `src/data/mock_jira.py` is named like a mock data file, but it actually wraps live Jira loading and contains data-shaping helpers. There is no real mock dataset in the current file.
- If Jira loading fails, `get_sprint_data()` returns `{"meta": {}, "issues": [], "error": "Jira data not found"}`. Many helper functions then assume keys like `meta["sprint_name"]`, which can crash.
- The API response assumes `result["sprint_data"]["meta"]["sprint_name"]` exists.
- Orchestrator JSON parsing has minimal error handling. If the model returns invalid JSON, the request fails.
- Some files contain mojibake characters in comments/prompts because emoji/symbol text appears with broken encoding in the terminal output.
- `requests.get()` has no timeout.
- Jira pagination is not implemented.
- Chat history is global process memory, shared across users and cleared on restart.
- There are stray files named `src/__init__py` and `src/__init__pycls` that do not appear to be used.
- No automated tests currently cover routing, Jira data shaping, endpoint responses, or graph error paths.

## Suggested Work Items For Claude

Good first coding tasks:

1. Add robust fallback mock data so the app works without Jira credentials.
2. Add graceful error handling for Jira failures and empty sprint data.
3. Harden orchestrator parsing with a default agent route when JSON parsing fails.
4. Add request timeouts and pagination in `jira_client.py`.
5. Move Story Points field ID into an environment variable, for example `JIRA_STORY_POINTS_FIELD`.
6. Add tests for data shaping helpers and API endpoints.
7. Replace global chat history with per-session storage or a client-provided conversation ID.
8. Clean up unused files and the placeholder root `main.py`.

## Claude Handoff

When asking Claude to write code in this repo, give it this orientation:

```text
You are working on Sprinter, a FastAPI + LangGraph sprint analysis app.

The real app entrypoint is src/main.py, not the root main.py.
The frontend is static HTML in ui/index.html and talks to:
- POST /analyze
- GET /sprint-meta
- POST /reset

The backend workflow is:
load_data -> orchestrator -> selected specialized agents -> summary.

Shared state is defined in src/graph/state.py.
Graph construction is in src/graph/workflow.py.
Agents live in src/agents/.
Jira loading and data shaping live in src/data/.

Use existing patterns:
- Agent nodes accept SprintState and return a partial dict update.
- Data helpers should return plain dictionaries/lists that are JSON serializable.
- Keep UI changes in plain HTML/CSS/JS unless a build system is intentionally added.
- Keep environment-driven configuration in .env and os.getenv.

Be careful with:
- Empty Jira data causing KeyError.
- Orchestrator LLM returning invalid JSON.
- Global chat_history being shared process-wide.
- Jira customfield_10016 being instance-specific.
- The root main.py being only a placeholder.
```

## Development Notes

Run the app:

```bash
uv run uvicorn src.main:app --reload
```

Run the Jira smoke test:

```bash
uv run python test_jira.py
```

The project currently has no formal test command configured in `pyproject.toml`.
