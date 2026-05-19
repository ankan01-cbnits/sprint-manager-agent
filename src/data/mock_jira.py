
DONE_STATUSES = {"done", "closed", "resolved", "complete", "completed"}


def _is_done(status: str) -> bool:
    return (status or "").strip().lower() in DONE_STATUSES




def get_sprint_data() -> dict:
    """
    Uses real Jira if credentials exist.
    Falls back to mock data if Jira is unavailable.
    """
    try:
            from src.data.jira_client import get_full_sprint_data
            return get_full_sprint_data()
    except Exception as e:
            print(f"[Jira] Failed: {e}")
            print("[Jira] Falling back to mock data")
    return {"meta": {}, "issues": [], "error": "Jira data not found"}



def _get_data(data: dict | None = None) -> dict:
    if data and data.get("meta") and "issues" in data:
        return data
    return get_sprint_data()



def get_todo_data(data: dict | None = None) -> dict:
    """Only incomplete tasks — for todo agent."""
    data = _get_data(data)
    filtered_issues = [
        {
            "id": i["id"],
            "summary": i["summary"],
            "status": i["status"],
            "assignee": i["assignee"],
            "priority": i["priority"],
            "story_points": i["story_points"],
            "updated": i["updated"],
            "blockers": i["blockers"],
        }
        for i in data["issues"]
    ]
    return {
        "meta": {
            "sprint_name": data["meta"]["sprint_name"],
            "days_remaining": data["meta"]["days_remaining"],
            "total_story_points": data["meta"]["total_story_points"],
            "completed_story_points": data["meta"]["completed_story_points"],
        },
        "issues": filtered_issues
    }


def get_health_data(data: dict | None = None) -> dict:
    """Only meta + status summary — for health agent."""
    data = _get_data(data)
    status_summary = {}
    points_by_status = {}
    for issue in data["issues"]:
        s = issue["status"]
        status_summary[s] = status_summary.get(s, 0) + 1
        points_by_status[s] = points_by_status.get(s, 0) + issue["story_points"]

    return {
        "meta": data["meta"],
        "status_summary": status_summary,
        "points_by_status": points_by_status,
        "assignee_points": _get_assignee_points(data["issues"]),
    }


def get_blocker_data(data: dict | None = None) -> dict:
    """Only blocked or at-risk tickets — for blocker agent."""
    data = _get_data(data)
    risky = [
        {
            "id": i["id"],
            "summary": i["summary"],
            "status": i["status"],
            "assignee": i["assignee"],
            "priority": i["priority"],
            "story_points": i["story_points"],
            "updated": i["updated"],
            "blockers": i["blockers"],
            "comments": i["comments"],
        }
        for i in data["issues"]
        if i["blockers"]
        or i["assignee"] == "Unassigned"
        or i["priority"] == "Critical"
        or i["status"] in ["In Progress", "To Do"]
    ]
    return {
        "meta": {
            "sprint_name": data["meta"]["sprint_name"],
            "days_remaining": data["meta"]["days_remaining"],
        },
        "at_risk_issues": risky
    }


def get_recommendation_data(data: dict | None = None) -> dict:
    """Meta + unfinished high priority tickets — for recommendation agent."""
    data = _get_data(data)
    important = [
        {
            "id": i["id"],
            "summary": i["summary"],
            "status": i["status"],
            "assignee": i["assignee"],
            "priority": i["priority"],
            "story_points": i["story_points"],
            "blockers": i["blockers"],
        }
        for i in data["issues"]
        if not _is_done(i["status"])
        and i["priority"] in ["Critical", "High"]
    ]
    return {
        "meta": data["meta"],
        "high_priority_incomplete": important,
        "assignee_points": _get_assignee_points(data["issues"]),
    }


def _get_assignee_points(issues: list) -> dict:
    """Helper — total story points per assignee."""
    result = {}
    for i in issues:
        if not _is_done(i["status"]):
            a = i["assignee"]
            result[a] = result.get(a, 0) + i["story_points"]
    return result
