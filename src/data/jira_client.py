import os
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DOMAIN  = os.getenv("JIRA_DOMAIN")
EMAIL   = os.getenv("JIRA_EMAIL")
TOKEN   = os.getenv("JIRA_API_TOKEN")
PROJECT = os.getenv("JIRA_PROJECT_KEY")

AUTH    = HTTPBasicAuth(EMAIL, TOKEN)
HEADERS = {"Accept": "application/json"}


def _get(url: str, params: dict = {}) -> dict:
    res = requests.get(url, headers=HEADERS, auth=AUTH, params=params)
    res.raise_for_status()
    return res.json()


def _extract_text(adf) -> str:
    """
    Extracts plain text from Jira Cloud Atlassian Document Format (ADF).
    Jira API v3 returns rich text as nested JSON instead of plain string.
    """
    if not adf:
        return ""
    if isinstance(adf, str):
        return adf[:150]

    texts = []
    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "text":
                texts.append(node.get("text", ""))
            for child in node.get("content", []):
                walk(child)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(adf)
    return " ".join(texts)[:150]


def get_active_sprint() -> dict:
    """Find the currently active sprint for the project."""
    url  = f"{DOMAIN}/rest/agile/1.0/board"
    data = _get(url, {"projectKeyOrId": PROJECT})

    if not data.get("values"):
        raise Exception(f"No board found for project: {PROJECT}")

    board_id = data["values"][0]["id"]

    url  = f"{DOMAIN}/rest/agile/1.0/board/{board_id}/sprint"
    data = _get(url, {"state": "active"})

    if not data.get("values"):
        raise Exception("No active sprint found. Start a sprint in Jira first.")

    sprint = data["values"][0]
    return {
        "sprint_id":   str(sprint["id"]),
        "sprint_name": sprint["name"],
        "start_date":  sprint.get("startDate", "")[:10],
        "end_date":    sprint.get("endDate", "")[:10],
        "board_id":    board_id,
    }


def get_sprint_issues(sprint_id: str) -> list:
    """Fetch all issues in the sprint with full details."""
    url    = f"{DOMAIN}/rest/agile/1.0/sprint/{sprint_id}/issue"
    params = {
        "maxResults": 100,
        "fields": ",".join([
            "summary",
            "status",
            "assignee",
            "priority",
            "issuetype",
            "customfield_10016",  # story points
            "labels",
            "comment",
            "issuelinks",
            "updated",
            "created",
        ])
    }

    data   = _get(url, params)
    issues = []

    for item in data.get("issues", []):
        f = item["fields"]

        # --- ASSIGNEE ---
        assignee = "Unassigned"
        if f.get("assignee"):
            assignee = f["assignee"].get("displayName", "Unassigned")

        # --- PRIORITY ---
        priority = "Medium"
        if f.get("priority"):
            priority = f["priority"].get("name", "Medium")

        # --- STORY POINTS ---
        # Jira Cloud uses customfield_10016 as float e.g. 8.0
        raw_points = f.get("customfield_10016")
        story_points = int(float(raw_points)) if raw_points is not None else 0

        # --- STATUS ---
        status = f.get("status", {}).get("name", "To Do")

        # --- LABELS ---
        labels = f.get("labels", [])

        # --- COMMENTS (last 3, plain text extracted from ADF) ---
        comments = []
        raw_comments = f.get("comment", {}).get("comments", [])
        for c in raw_comments[-3:]:
            body = _extract_text(c.get("body", ""))
            comments.append({
                "author":  c["author"].get("displayName", "Unknown"),
                "body":    body,
                "created": c.get("created", "")[:10],
            })

        # --- BLOCKERS from issue links ---
        blockers = []
        for link in f.get("issuelinks", []):
            link_type = link.get("type", {}).get("name", "")
            outward   = link.get("outwardIssue")
            inward    = link.get("inwardIssue")
            linked    = outward or inward
            if linked:
                linked_summary = linked.get("fields", {}).get("summary", "")
                linked_status  = linked.get("fields", {}).get("status", {}).get("name", "")
                blockers.append(
                    f"{link_type}: {linked['key']} ({linked_status}) — {linked_summary}"
                )

        issues.append({
            "id":           item["key"],
            "summary":      f.get("summary", ""),
            "type":         f.get("issuetype", {}).get("name", "Task"),
            "status":       status,
            "assignee":     assignee,
            "priority":     priority,
            "story_points": story_points,
            "labels":       labels,
            "updated":      f.get("updated", "")[:10],
            "created":      f.get("created", "")[:10],
            "blockers":     blockers,
            "comments":     comments,
        })

    return issues


def get_sprint_meta(sprint: dict, issues: list) -> dict:
    """Build sprint meta stats from live issue data."""
    total_points = sum(i["story_points"] for i in issues)

    done_statuses = {"done", "closed", "resolved", "complete", "completed"}
    done_points   = sum(
        i["story_points"] for i in issues
        if i["status"].lower() in done_statuses
    )

    today = datetime.now()
    try:
        start          = datetime.strptime(sprint["start_date"], "%Y-%m-%d")
        end            = datetime.strptime(sprint["end_date"],   "%Y-%m-%d")
        total_days     = max((end - start).days, 1)
        days_elapsed   = min(max((today - start).days, 0), total_days)
        days_remaining = max((end - today).days, 0)
    except Exception:
        total_days     = 14
        days_elapsed   = 0
        days_remaining = 14

    return {
        "sprint_id":              sprint["sprint_id"],
        "sprint_name":            sprint["sprint_name"],
        "team":                   PROJECT + " Team",
        "start_date":             sprint["start_date"],
        "end_date":               sprint["end_date"],
        "total_story_points":     total_points,
        "completed_story_points": done_points,
        "days_elapsed":           days_elapsed,
        "days_remaining":         days_remaining,
        "velocity_last_sprint":   0,
        "velocity_avg_3_sprints": 0,
    }


def get_full_sprint_data() -> dict:
    """
    Main entry point.
    Returns same structure as mock_jira.py so all agents work unchanged.
    """
    sprint = get_active_sprint()
    issues = get_sprint_issues(sprint["sprint_id"])
    meta   = get_sprint_meta(sprint, issues)

    print(f"[Jira] Loaded: {meta['sprint_name']} — {len(issues)} issues "
          f"({meta['completed_story_points']}/{meta['total_story_points']} pts done)")

    return {
        "meta":   meta,
        "issues": issues,
    }