import json
from src.agents.base import llm
from src.graph.state import SprintState
from src.data.mock_jira import get_recommendation_data

# inside recommendation_node():


llm = llm(temperature=0.4)

RECOMMENDATION_PROMPT = """
You are the Recommendation Agent for a sprint analysis system.

You think like a seasoned Engineering Manager and Scrum Master combined.
Your recommendations are sharp, specific, and actionable — never generic advice.

You produce recommendations across these dimensions:
1. Immediate actions — what the team must do TODAY to protect the sprint goal
2. Blocker escalations — which blockers need manager intervention vs self-resolution
3. Scope decisions — what should be moved to backlog given current pace
4. Workload rebalancing — who is overloaded, who can pick up more work
5. Process improvements — what planning gaps does this sprint expose for next sprint

For each recommendation:
- What: exactly what needs to happen
- Who: the specific person responsible (use actual names from the data)
- Why: business or technical impact if ignored
- Urgency: IMMEDIATE / THIS WEEK / NEXT SPRINT

Rules:
- Reference actual ticket IDs and assignee names — never be vague
- If blockers or health data is provided, ground recommendations in that analysis
- Prioritize by impact — most critical recommendations first
- Be direct — a good EM does not sugarcoat risks
- Format clearly in markdown
- Use maximum 1000 tokens
"""

def recommendation_node(state: SprintState) -> dict:
    if "recommendation" not in state.get("agents_to_run", []):
        return {"recommendation_output": None}

    sprint_json = json.dumps(get_recommendation_data(), indent=2)

    # Pull in context from other agents if available
    extra_context = ""
    if state.get("blocker_output"):
        extra_context += f"\n\n--- Blocker Analysis ---\n{state['blocker_output']}"
    if state.get("health_output"):
        extra_context += f"\n\n--- Health Analysis ---\n{state['health_output']}"
    if state.get("todo_output"):
        extra_context += f"\n\n--- Todo Analysis ---\n{state['todo_output']}"

    history_text = ""
    if state.get("chat_history"):
        recent = state["chat_history"][-4:]
        history_text = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in recent
        )

    message = f"""
Sprint Data:
{sprint_json}

{extra_context}

Recent Conversation:
{history_text if history_text else "None"}

User Query: {state['user_query']}

Give sharp, specific, prioritized recommendations grounded in the actual data.
"""

    response = llm.invoke([
        {"role": "system", "content": RECOMMENDATION_PROMPT},
        {"role": "user", "content": message},
    ])

    return {"recommendation_output": response.content}