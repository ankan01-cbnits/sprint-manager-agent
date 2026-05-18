from datetime import datetime, timedelta

TODAY = datetime.now()
SPRINT_START = TODAY - timedelta(days=7)
SPRINT_END = TODAY + timedelta(days=7)

SPRINT_META = {
    "sprint_id": "SPR-42",
    "sprint_name": "Sprint 42 — Nova Release",
    "team": "Team Orion",
    "start_date": SPRINT_START.strftime("%Y-%m-%d"),
    "end_date": SPRINT_END.strftime("%Y-%m-%d"),
    "total_story_points": 84,
    "completed_story_points": 31,
    "days_elapsed": 7,
    "days_remaining": 7,
    "velocity_last_sprint": 72,
    "velocity_avg_3_sprints": 68,
}

ISSUES = [
    {
        "id": "ORN-101",
        "summary": "Implement OAuth2 login with Google SSO",
        "type": "Story",
        "status": "In Progress",
        "assignee": "Priya Sharma",
        "priority": "High",
        "story_points": 8,
        "labels": ["auth", "backend"],
        "updated": (TODAY - timedelta(days=4)).strftime("%Y-%m-%d"),
        "blockers": ["Waiting for GCP credentials from DevOps — ticket ORN-119 unresolved"],
        "comments": [
            {"author": "Priya Sharma", "body": "Blocked on DevOps. Escalated to Rahul."},
        ],
    },
    {
        "id": "ORN-102",
        "summary": "Migrate legacy REST endpoints to GraphQL",
        "type": "Story",
        "status": "In Progress",
        "assignee": "Arjun Mehta",
        "priority": "High",
        "story_points": 13,
        "labels": ["api", "backend"],
        "updated": TODAY.strftime("%Y-%m-%d"),
        "blockers": [],
        "comments": [
            {"author": "Arjun Mehta", "body": "Schema done. Working on resolvers now."},
        ],
    },
    {
        "id": "ORN-103",
        "summary": "Dashboard: real-time metrics via WebSocket",
        "type": "Story",
        "status": "To Do",
        "assignee": "Sara Lim",
        "priority": "Medium",
        "story_points": 8,
        "labels": ["frontend", "websocket"],
        "updated": SPRINT_START.strftime("%Y-%m-%d"),
        "blockers": ["Depends on ORN-102 GraphQL endpoints being ready"],
        "comments": [],
    },
    {
        "id": "ORN-104",
        "summary": "Write E2E tests for checkout flow",
        "type": "Task",
        "status": "Done",
        "assignee": "Ravi Kumar",
        "priority": "High",
        "story_points": 5,
        "labels": ["qa", "testing"],
        "updated": (TODAY - timedelta(days=2)).strftime("%Y-%m-%d"),
        "blockers": [],
        "comments": [
            {"author": "Ravi Kumar", "body": "All 47 E2E tests passing. PR merged."},
        ],
    },
    {
        "id": "ORN-105",
        "summary": "Fix memory leak in notification service",
        "type": "Bug",
        "status": "In Progress",
        "assignee": "Priya Sharma",
        "priority": "Critical",
        "story_points": 3,
        "labels": ["bug", "backend", "performance"],
        "updated": TODAY.strftime("%Y-%m-%d"),
        "blockers": [],
        "comments": [
            {"author": "Priya Sharma", "body": "Root cause found — event listener not unsubscribed. Fix in progress."},
            {"author": "TechLead", "body": "This is hitting production. P0 priority."},
        ],
    },
    {
        "id": "ORN-106",
        "summary": "User onboarding flow redesign",
        "type": "Story",
        "status": "To Do",
        "assignee": "Neha Joshi",
        "priority": "Medium",
        "story_points": 13,
        "labels": ["frontend", "ux"],
        "updated": SPRINT_START.strftime("%Y-%m-%d"),
        "blockers": ["Design mockups not finalized by UX team"],
        "comments": [
            {"author": "Neha Joshi", "body": "Waiting on Figma link from Anya."},
        ],
    },
    {
        "id": "ORN-107",
        "summary": "Set up Prometheus + Grafana monitoring",
        "type": "Task",
        "status": "Done",
        "assignee": "Rahul Singh",
        "priority": "High",
        "story_points": 8,
        "labels": ["devops", "infra"],
        "updated": (TODAY - timedelta(days=4)).strftime("%Y-%m-%d"),
        "blockers": [],
        "comments": [
            {"author": "Rahul Singh", "body": "Dashboards live. Alerts configured for CPU > 80%."},
        ],
    },
    {
        "id": "ORN-108",
        "summary": "Database query optimization — reports module",
        "type": "Task",
        "status": "In Review",
        "assignee": "Arjun Mehta",
        "priority": "Medium",
        "story_points": 5,
        "labels": ["backend", "performance"],
        "updated": (TODAY - timedelta(days=1)).strftime("%Y-%m-%d"),
        "blockers": ["PR review pending — reviewer Priya is blocked on ORN-101"],
        "comments": [
            {"author": "Arjun Mehta", "body": "Reduced p99 query time from 4.2s to 340ms. Ready for review."},
        ],
    },
    {
        "id": "ORN-109",
        "summary": "Implement rate limiting on public API",
        "type": "Story",
        "status": "To Do",
        "assignee": "Unassigned",
        "priority": "High",
        "story_points": 8,
        "labels": ["api", "security"],
        "updated": SPRINT_START.strftime("%Y-%m-%d"),
        "blockers": ["No owner assigned — sprint planning oversight"],
        "comments": [],
    },
    {
        "id": "ORN-110",
        "summary": "Mobile: push notification deep linking",
        "type": "Story",
        "status": "To Do",
        "assignee": "Sara Lim",
        "priority": "Low",
        "story_points": 5,
        "labels": ["mobile", "frontend"],
        "updated": SPRINT_START.strftime("%Y-%m-%d"),
        "blockers": [],
        "comments": [],
    },
    {
        "id": "ORN-111",
        "summary": "Refactor AuthMiddleware for multi-tenant support",
        "type": "Task",
        "status": "Done",
        "assignee": "Rahul Singh",
        "priority": "High",
        "story_points": 8,
        "labels": ["backend", "auth"],
        "updated": (TODAY - timedelta(days=3)).strftime("%Y-%m-%d"),
        "blockers": [],
        "comments": [
            {"author": "Rahul Singh", "body": "Refactor complete. All tenant isolation tests pass."},
        ],
    },
    {
        "id": "ORN-112",
        "summary": "Fix: incorrect tax calculation for EU users",
        "type": "Bug",
        "status": "Done",
        "assignee": "Ravi Kumar",
        "priority": "Critical",
        "story_points": 5,
        "labels": ["bug", "billing"],
        "updated": (TODAY - timedelta(days=2)).strftime("%Y-%m-%d"),
        "blockers": [],
        "comments": [
            {"author": "Ravi Kumar", "body": "VAT logic was applying US tax table. Patched and deployed."},
        ],
    },
    {
        "id": "ORN-119",
        "summary": "[DevOps] Provision GCP service account for OAuth",
        "type": "Task",
        "status": "To Do",
        "assignee": "Rahul Singh",
        "priority": "High",
        "story_points": 2,
        "labels": ["devops", "blocker"],
        "updated": (TODAY - timedelta(days=3)).strftime("%Y-%m-%d"),
        "blockers": [],
        "comments": [],
    },
]

def get_sprint_data() -> dict:
    return {
        "meta": SPRINT_META,
        "issues": ISSUES,
    }



def get_todo_data() -> dict:
    """Only incomplete tasks — for todo agent."""
    data = get_sprint_data()
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
        if i["status"] != "Done"
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


def get_health_data() -> dict:
    """Only meta + status summary — for health agent."""
    data = get_sprint_data()
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


def get_blocker_data() -> dict:
    """Only blocked or at-risk tickets — for blocker agent."""
    data = get_sprint_data()
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


def get_recommendation_data() -> dict:
    """Meta + unfinished high priority tickets — for recommendation agent."""
    data = get_sprint_data()
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
        if i["status"] != "Done"
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
        if i["status"] != "Done":
            a = i["assignee"]
            result[a] = result.get(a, 0) + i["story_points"]
    return result