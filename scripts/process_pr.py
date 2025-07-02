import os
import json
import requests
from datetime import datetime, timedelta

# Load PR metadata from event payload
with open(os.getenv("GITHUB_EVENT_PATH")) as f:
    event = json.load(f)

pr_number = event["pull_request"]["number"]
repo_full = os.getenv("GITHUB_REPOSITORY")  # e.g., "owner/repo"
token = os.getenv("GITHUB_TOKEN")

# headers = {
#     "Authorization": f"token {token}",
#     "Accept": "application/vnd.github.v3+json"
# }

# Fetch PR details
api_url = f"https://api.github.com/repos/{repo_full}/pulls/{pr_number}"
# response = requests.get(api_url, headers=headers)
response = requests.get(api_url)
data = response.json()

print("PR Title:", data.get("title"))
print("PR Description:", data.get("body"))

# Fetch changed files
files_url = f"{api_url}/files"
# files_response = requests.get(files_url, headers=headers)
files_response = requests.get(files_url)
files = files_response.json()

print("\nChanged Files and Diffs:")
for file in files:
    print(f"\n--- {file['filename']} ---")
    print(file.get("patch", "[No diff shown]"))

def create_cmr_mapping_file(cmr_id: str, pr_number: str):
    """
    Create a JSON file mapping PR ID to CMR ID.
    """
    mapping_data = {
        "pr_id": pr_number,
        "cmr_id": cmr_id,
        "created_at": datetime.now().isoformat(),
        "pr_title": fetchPR.title
    }
    
    # Create the mapping file
    mapping_file = "cmr_mapping.json"
    with open(mapping_file, 'w') as f:
        json.dump(mapping_data, f, indent=2)
    
    print(f"✅ Created mapping file: {mapping_file}")
    print(f"📋 PR #{pr_number} -> CMR {cmr_id}")
    return mapping_file
create_cmr_mapping_file("456", "111")
