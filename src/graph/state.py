from typing import TypedDict, Optional, List

class SprintState(TypedDict):
    # Original user query
    user_query: str

    # Full conversation history for memory
    chat_history: List[dict]

    # Sprint data loaded once, shared across all agents
    sprint_data: dict

    # Orchestrator decision
    agents_to_run: List[str]

    # Individual agent outputs
    todo_output: Optional[str]
    health_output: Optional[str]
    blocker_output: Optional[str]
    recommendation_output: Optional[str]

    #create ticket
    create_output: Optional[str]

    # Final synthesized answer
    final_answer: str