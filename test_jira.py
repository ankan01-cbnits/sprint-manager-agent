from src.data.jira_client import create_issue, add_issue_to_sprint, get_active_sprint
from dotenv import load_dotenv

load_dotenv()

# Step 1 — test create issue
print("Creating issue...")
result = create_issue(
    summary      = "Test ticket from API",
    issue_type   = "Bug",
    priority     = "High",
    story_points = 3,
    labels       = ["test"],
)
print("Create result:", result)

# Step 2 — test add to sprint
issue_key = result.get("key")
print(f"\nAdding {issue_key} to sprint...")
sprint = get_active_sprint()
print("Sprint:", sprint["sprint_name"], "ID:", sprint["sprint_id"])
added = add_issue_to_sprint(issue_key, sprint["sprint_id"])
print("Added to sprint:", added)