from src.data.jira_client import get_full_sprint_data

data = get_full_sprint_data()

print("\n--- SPRINT META ---")
for k, v in data["meta"].items():
    print(f"  {k}: {v}")

print(f"\n--- ISSUES ({len(data['issues'])}) ---")
for i in data["issues"]:
    print(f"  {i['id']} | {i['status']:<12} | {i['priority']:<8} | {i['story_points']}pts | {i['summary'][:50]}")