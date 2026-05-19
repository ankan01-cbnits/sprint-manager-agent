from langgraph.graph import StateGraph, END
from src.graph.state import SprintState
from src.agents.orchestrator import orchestrator_node
from src.agents.todo_agent import todo_node
from src.agents.health_agent import health_node
from src.agents.blocker_agent import blocker_node
from src.agents.recommendation_agent import recommendation_node
from src.agents.summary_agent import summary_node
from src.data.mock_jira import get_sprint_data


def load_data_node(state: SprintState) -> dict:
    """First node — loads sprint data into shared state once."""
    data = get_sprint_data()
    return {"sprint_data":data}


def route_agents(state: SprintState) -> list[str]:
    """
    Dynamic router — called by LangGraph after orchestrator runs.
    Returns list of agent node names to execute.
    LangGraph fans out to ALL of them in parallel.
    """
    agent_map = {
        "todo": "todo_agent",
        "health": "health_agent",
        "blocker": "blocker_agent",
        "recommendation": "recommendation_agent",
    }
    return [agent_map[a] for a in state["agents_to_run"] if a in agent_map]


def build_graph() -> StateGraph:
    graph = StateGraph(SprintState)

    # Register every node
    graph.add_node("load_data", load_data_node)
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("todo_agent", todo_node)
    graph.add_node("health_agent", health_node)
    graph.add_node("blocker_agent", blocker_node)
    graph.add_node("recommendation_agent", recommendation_node)
    graph.add_node("summary", summary_node)

    # Entry point
    graph.set_entry_point("load_data")

    # load_data → orchestrator (always)
    graph.add_edge("load_data", "orchestrator")

    # orchestrator → dynamic fan-out to selected agents only
    graph.add_conditional_edges(
        "orchestrator",
        route_agents,
        {
            "todo_agent": "todo_agent",
            "health_agent": "health_agent",
            "blocker_agent": "blocker_agent",
            "recommendation_agent": "recommendation_agent",
        }
    )

    # All agents converge into summary
    graph.add_edge("todo_agent", "summary")
    graph.add_edge("health_agent", "summary")
    graph.add_edge("blocker_agent", "summary")
    graph.add_edge("recommendation_agent", "summary")

    # summary → END
    graph.add_edge("summary", END)

    return graph.compile()


# Compiled graph — imported by main.py
sprint_graph = build_graph()