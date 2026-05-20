import json
from src.agents.base import llm
from src.graph.state import SprintState



llm = llm(temperature=0.1)


ORCHESTRATOR_PROMPT = """
You are the Orchestrator of a multi-agent Sprint Analysis system.

Your ONLY job is to read the user's query and chat history, then decide 
which specialized agents are needed to answer it. Do NOT answer the question yourself.

Available agents:
- "todo"            → Tasks by status (To Do, In Progress, In Review, Done), ownership, story points
- "health"          → Sprint velocity, burndown, completion %, risk of missing sprint goal
- "blocker"         → Blockers, impediments, stuck tickets, cascade dependencies, at-risk items
- "recommendation"  → Suggestions, prioritization advice, what to focus on, process improvements
- "create"          → Creates tickets , adds it to current sprint 

Routing rules — be surgical, not thorough:
- "what are the todos / in progress / done / tasks" → ["todo"]
- "sprint health / velocity / burndown / on track" → ["health"]
- "blockers / stuck / impediments / at risk" → ["blocker"]
- "recommendations / suggestions / priorities / what should we do" → ["recommendation"]
- "full report / overview / summary of sprint" → ["todo", "health", "blocker", "recommendation"]
- "why is X blocked / what is blocking Y" → ["blocker"]
- "who is overloaded / workload" → ["todo", "recommendation"]
- "create / add ticket / new task / new bug / new story / create a ticket" → ["create"]
- "will we finish / can we complete sprint" → ["health", "blocker"]
- Follow-up questions → infer from chat history which agents are relevant

Respond ONLY with valid JSON, no extra text:
{
  "agents_to_run": ["agent1", "agent2"],
  "reasoning": "one sentence explanation"
}
"""

def orchestrator_node(state: SprintState) -> dict:
  

    # Build chat history context
    history_text = ""
    if state.get("chat_history"):
        recent = state["chat_history"][-6:]  # last 3 exchanges
        history_text = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in recent
        )

    message = f"""
Chat History (for context):
{history_text if history_text else "No previous messages."}

Current Query: {state['user_query']}

Which agents should handle this query?
"""

    response = llm.invoke([
        {"role": "system", "content": ORCHESTRATOR_PROMPT},
        {"role": "user", "content": message},
    ])

    raw = response.content.strip()

    # Strip markdown code fences if present
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        parsed = json.loads(raw.strip())
    except:
        return {
            "agents_to_run":["todo"]
        }

    return {
        "agents_to_run": parsed["agents_to_run"],
    }