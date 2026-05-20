import json
from src.agents.base import llm
from src.graph.state import SprintState
from src.data.jira_client import create_issue, add_issue_to_sprint, get_active_sprint
import os

DOMAIN = os.getenv("JIRA_DOMAIN")

CREATE_PROMPT = """
You are the Ticket Creation Agent for a sprint management system.

The user wants to create a Jira ticket. Extract ALL details from their message.

Return ONLY valid JSON, no extra text:
{
  "summary": "clear ticket title",
  "issue_type": "Story" or "Task" or "Bug",
  "priority": "Critical" or "High" or "Medium" or "Low",
  "story_points": number,
  "labels": ["label1", "label2"]
}

Rules:
- summary: clean, professional ticket title
- issue_type: if fix/crash/error → "Bug", if feature/user story → "Story", if technical work → "Task"
- priority: if not mentioned → "Medium"
- story_points: pick closest from [1, 2, 3, 5, 8, 13], default 3
- labels: lowercase single words extracted from context
- If user mentions a label explicitly, always include it
"""


def create_agent_node(state: SprintState) -> dict:
    if "create" not in state.get("agents_to_run", []):
        return {"create_output": None}

    llm_instance = llm(temperature=0.1)

    response = llm_instance.invoke([
        {"role": "system", "content": CREATE_PROMPT},
        {"role": "user", "content": state["user_query"]},
    ])

    raw = response.content.strip()

    # Strip markdown fences if present
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        ticket = json.loads(raw.strip())
    except json.JSONDecodeError:
        return {
            "create_output": (
                "I could not parse the ticket details from your message. "
                "Try something like: 'Create a bug - Login crashes on iOS, "
                "priority High, labels mobile frontend'"
            )
        }

    try:
        # Step 1 — Create the issue in Jira
        result    = create_issue(
            summary      = ticket["summary"],
            issue_type   = ticket.get("issue_type", "Task"),
            priority     = ticket.get("priority", "Medium"),
            story_points = ticket.get("story_points", 3),
            labels       = ticket.get("labels", []),
        )
        issue_key = result["key"]

        # Step 2 — Add to active sprint
        sprint = get_active_sprint()
        added  = add_issue_to_sprint(issue_key, sprint["sprint_id"])

        sprint_status = (
            f"Added to **{sprint['sprint_name']}**"
            if added else
            "⚠️ Created but could not add to sprint automatically"
        )

        return {
            "create_output": (
                f"✅ **{issue_key}** created successfully!\n\n"
                f"| Field | Value |\n"
                f"|-------|-------|\n"
                f"| Summary | {ticket['summary']} |\n"
                f"| Type | {ticket.get('issue_type', 'Task')} |\n"
                f"| Priority | {ticket.get('priority', 'Medium')} |\n"
                f"| Story Points | {ticket.get('story_points', 3)} |\n"
                f"| Labels | {', '.join(ticket.get('labels', [])) or 'None'} |\n"
                f"| Sprint | {sprint_status} |\n\n"
                f"🔗 [View in Jira]({DOMAIN}/browse/{issue_key})"
            )
        }

    except Exception as e:
        return {
            "create_output": f"❌ Failed to create ticket: {str(e)}"
        }