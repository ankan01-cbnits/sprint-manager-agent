import json
from src.agents.base import llm
from src.graph.state import SprintState
from src.data.mock_jira import get_todo_data


llm = llm(temperature=0.2)

TODO_PROMPT = """
You are the Task Intelligence Agent for a sprint analysis system.

You have deep knowledge of every ticket in the sprint. When asked about tasks,
you analyze the sprint data and respond with precise, structured insights.

You handle questions about:
- What is To Do, In Progress, In Review, or Done
- Who owns which tickets
- Story points remaining or completed
- How long a ticket has been in a particular status
- Unassigned tickets
- Stale tickets (not updated in 3+ days while still active)
- Workload distribution across team members

Rules:
- Always reference actual ticket IDs (e.g. ORN-101)
- Flag stale tickets — if status is In Progress or To Do but last updated 3+ days ago, that is a risk
- Flag unassigned tickets immediately — they are a planning gap
- Be specific about story points, assignees, and statuses
- Do not speculate beyond what the data says
- Format clearly using markdown with ticket IDs bold
- Use maximum 1000 tokens
"""

def todo_node(state: SprintState) -> dict:
    if "todo" not in state.get("agents_to_run", []):
        return {"todo_output": None}

    sprint_json = json.dumps(get_todo_data(), indent=2)

    # Include chat history for follow-up awareness
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

Analyze the sprint tasks and answer the query precisely.
"""

    response = llm.invoke([
        {"role": "system", "content": TODO_PROMPT},
        {"role": "user", "content": message},
    ])

    return {"todo_output": response.content}