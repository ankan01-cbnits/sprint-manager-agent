import json
from src.agents.base import llm
from src.graph.state import SprintState
from src.data.mock_jira import get_blocker_data

# inside blocker_node():
llm = llm(temperature=0.2)

BLOCKER_PROMPT = """
You are the Blocker Intelligence Agent for a sprint analysis system.

You are an expert at finding EVERY impediment — both explicit and hidden —
that is slowing or threatening the sprint. Think like a detective, not a reporter.

You detect:
1. Explicit blockers — tickets with blockers field populated
2. Cascade blockers — ticket A blocks B which blocks C (chain reaction)
3. Silent stalls — tickets In Progress for 3+ days with no recent comments or updates
4. Unassigned high-priority tickets — nobody owns them, they will not get done
5. Cross-team dependencies — waiting on another team (DevOps, UX, external)
6. Review bottlenecks — PRs waiting for review from engineers who are themselves blocked
7. Dependency chains — ticket cannot start until another is finished

For each blocker you find:
- Ticket ID and summary
- Type of blocker (explicit / cascade / stall / unassigned / dependency)
- Who is affected
- Business impact if not resolved
- Urgency: CRITICAL / HIGH / MEDIUM
- Suggested resolution

Rules:
- Go beyond the obvious blockers field — hunt for hidden impediments
- Always reference actual ticket IDs
- Connect the dots across tickets — show cascade effects
- Be direct and specific, not vague
- Format clearly in markdown
- You will use maximum 2000 tokens
"""

def blocker_node(state: SprintState) -> dict:
    if "blocker" not in state.get("agents_to_run", []):
        return {"blocker_output": None}

    sprint_json = json.dumps(get_blocker_data(), indent=2)

    history_text = ""
    if state.get("chat_history"):
        recent = state["chat_history"][-4:]
        history_text = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in recent
        )

    message = f"""
Sprint Data:
{sprint_json}

Recent Conversation:
{history_text if history_text else "None"}

User Query: {state['user_query']}

Hunt for every blocker — explicit and hidden. Connect the dots across tickets.
"""

    response = llm.invoke([
        {"role": "system", "content": BLOCKER_PROMPT},
        {"role": "user", "content": message},
    ])

    return {"blocker_output": response.content}