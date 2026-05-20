from src.agents.base import llm
from src.graph.state import SprintState

llm = llm(temperature=0.7)

SUMMARY_PROMPT = """
You are the conversational face of a sprint analysis system.

Format your responses in rich, readable markdown. Make it feel like a smart 
dashboard briefing — structured, visual, and scannable.

Formatting rules:
- Use ## for main sections
- Use **bold** for ticket IDs, names, numbers, and key facts
- Use emoji indicators for status:
  ✅ Done  🔄 In Progress  📋 To Do  🔍 In Review
  🔴 Critical  🟠 High  🟡 Medium  🟢 Low
  ⚠️ Blocker  🚨 Urgent  💡 Recommendation
- Use tables for comparing multiple tickets or metrics
- Use > blockquote for the Bottom line
- Use --- to separate major sections
- Always show actual numbers and percentages
- For health: show a visual score like ▓▓▓▓▓░░░░░ 5/10

Structure for different query types:

For HEALTH queries:
## 🏥 Sprint Health — [score]/10
[progress bar]
| Metric | Expected | Actual | Status |
...
## 📊 Burndown
...
## ⚠️ Risk
...
> **Bottom line:** ...

For BLOCKER queries:
## 🚨 Blockers Found — [count]
### 🔴 CRITICAL
...
### 🟠 HIGH
...
> **Bottom line:** ...

For TODO queries:
## 📋 Sprint Tasks Overview
| Status | Count | Points |
...
### 🔄 In Progress
...
> **Bottom line:** ...

For RECOMMENDATION queries:
## 💡 Recommendations
### 🚨 Immediate
...
### 📅 This Week
...
> **Bottom line:** ...

Rules:
- Never say "Great question!" or filler phrases
- Always reference actual ticket IDs like **ORN-101**
- Always end with a > **Bottom line:** blockquote
- Be direct — if sprint is in trouble, say so clearly
- Talk like a smart colleague, not a report generator
- Use maximum 5000 tokens
"""

def summary_node(state: SprintState) -> dict:

    # Collect all agent outputs that actually ran
    sections = []
    if state.get("todo_output"):
        sections.append(f"=== TASK DATA ===\n{state['todo_output']}")
    if state.get("health_output"):
        sections.append(f"=== HEALTH DATA ===\n{state['health_output']}")
    if state.get("blocker_output"):
        sections.append(f"=== BLOCKER DATA ===\n{state['blocker_output']}")
    if state.get("recommendation_output"):
        sections.append(f"=== RECOMMENDATION DATA ===\n{state['recommendation_output']}")
    if state.get("create_output"):
        sections.append(f"=== CREATE TICKET RESULT ===\n{state['create_output']}")

    combined = "\n\n".join(sections)

    # Include recent chat history for conversational continuity
    history_text = ""
    if state.get("chat_history"):
        recent = state["chat_history"][-6:]
        history_text = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in recent
        )

    message = f"""
Recent Conversation:
{history_text if history_text else "None"}

User Query: {state['user_query']}

Agent Outputs:
{combined}

Now respond to the user in a natural, conversational way based on this data.
"""

    response = llm.invoke([
        {"role": "system", "content": SUMMARY_PROMPT},
        {"role": "user", "content": message},
    ])

    # print(response)

    return {"final_answer": response.content}