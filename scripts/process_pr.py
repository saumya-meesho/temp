import requests
import os
import json

from dotenv import load_dotenv
import re

def extract_table_details(patch):
    """Extract detailed table changes from SQL patch content."""
    table_changes = {}
    current_table = None
    
    # Process each line in the patch
    for line in patch.split('\n'):
        original_line = line
        content = line.strip()
        
        if content:
            # Check what type of line this is
            line_type = "context"
            if line.startswith('@@'):
                line_type = "header"
            elif line.startswith('+'):
                line_type = "added"
                content = line[1:].strip()
            elif line.startswith('-'):
                line_type = "removed"
                content = line[1:].strip()
            elif line.startswith(' '):
                line_type = "context"
                content = line[1:].strip()
            
            # Check for CREATE TABLE statements to identify current table
            create_table_match = re.search(r'CREATE TABLE\s+[`"]?([a-zA-Z_][a-zA-Z0-9_]*)[`"]?', content, re.IGNORECASE)
            if create_table_match:
                current_table = create_table_match.group(1)
                if current_table not in table_changes:
                    table_changes[current_table] = {
                        'operation': 'CREATE/MODIFY',
                        'all_columns': [],
                        'changes': []
                    }
            
            # Check for DROP TABLE statements
            drop_table_match = re.search(r'DROP TABLE\s+(?:IF EXISTS\s+)?[`"]?([a-zA-Z_][a-zA-Z0-9_]*)[`"]?', content, re.IGNORECASE)
            if drop_table_match:
                table_name = drop_table_match.group(1)
                table_changes[table_name] = {
                    'operation': 'DROP',
                    'all_columns': [],
                    'changes': [{'type': 'drop_table', 'line': original_line}]
                }
            
            # If we're inside a table definition, look for ALL column definitions (including context)
            if current_table and line_type in ['added', 'removed', 'context']:
                # Check for column definitions
                column_match = re.search(r'[`"]?([a-zA-Z_][a-zA-Z0-9_]*)[`"]?\s+([a-zA-Z]+(?:\([^)]+\))?)', content)
                if column_match and not content.upper().startswith(('PRIMARY', 'UNIQUE', 'KEY', 'INDEX', 'CONSTRAINT', 'ENGINE', ')')):
                    column_name = column_match.group(1)
                    
                    # Extract full column definition
                    full_def_match = re.search(r'[`"]?' + re.escape(column_name) + r'[`"]?\s+(.+?)(?:,\s*$|$)', content)
                    full_definition = full_def_match.group(1) if full_def_match else column_match.group(2)
                    
                    # Parse data type
                    data_type_match = re.search(r'([a-zA-Z]+(?:\([^)]+\))?)', full_definition)
                    data_type = data_type_match.group(1) if data_type_match else "unknown"
                    
                    # Check for constraints
                    constraints = []
                    if 'NOT NULL' in full_definition.upper():
                        constraints.append('NOT NULL')
                    if 'AUTO_INCREMENT' in full_definition.upper():
                        constraints.append('AUTO_INCREMENT')
                    if 'DEFAULT' in full_definition.upper():
                        default_match = re.search(r'DEFAULT\s+([^,\s]+(?:\s+[^,]*)?)', full_definition, re.IGNORECASE)
                        if default_match:
                            default_value = default_match.group(1)
                            # Handle complex default values
                            if 'ON UPDATE' in full_definition.upper():
                                on_update_match = re.search(r'ON UPDATE\s+([^,\s]+)', full_definition, re.IGNORECASE)
                                if on_update_match:
                                    default_value += f' ON UPDATE {on_update_match.group(1)}'
                            constraints.append(f'DEFAULT {default_value}')
                    if 'COMMENT' in full_definition.upper():
                        comment_match = re.search(r'COMMENT\s+[\'"]([^\'\"]*)[\'"]', full_definition, re.IGNORECASE)
                        if comment_match:
                            constraints.append(f'COMMENT: {comment_match.group(1)[:50]}{"..." if len(comment_match.group(1)) > 50 else ""}')
                    
                    column_info = {
                        'column': column_name,
                        'data_type': data_type,
                        'constraints': constraints,
                        'full_definition': full_definition.strip().rstrip(','),
                        'line_type': line_type,
                        'original_line': original_line
                    }
                    
                    # Add to all columns list
                    table_changes[current_table]['all_columns'].append(column_info)
                    
                    # If it's a changed line, also add to changes
                    if line_type in ['added', 'removed']:
                        change_detail = {
                            'type': 'column_change',
                            'action': line_type,
                            'column': column_name,
                            'data_type': data_type,
                            'full_line': content,
                            'original_line': original_line
                        }
                        table_changes[current_table]['changes'].append(change_detail)
    
    return table_changes

def extract_complete_table_definition(file_content, table_name):
    """Extract the complete CREATE TABLE statement for a specific table from file content."""
    lines = file_content.split('\n')
    table_def_lines = []
    in_table = False
    found_closing = False
    
    for i, line in enumerate(lines):
        # Look for CREATE TABLE statement
        if re.search(rf'CREATE TABLE\s+[`"]?{re.escape(table_name)}[`"]?', line, re.IGNORECASE):
            in_table = True
            table_def_lines.append(line)
            
            # If the line has opening parenthesis, we're starting column definitions
            if '(' in line:
                continue
        
        if in_table:
            table_def_lines.append(line)
            
            # Look for the end pattern: ) followed by optional ENGINE, CHARSET, etc.
            stripped_line = line.strip()
            if (stripped_line.startswith(')') and 
                ('ENGINE=' in stripped_line or 'DEFAULT CHARSET=' in stripped_line or 
                 stripped_line == ')' or stripped_line.endswith(';'))):
                found_closing = True
                
                # Continue to capture ENGINE and other table options
                if not (stripped_line == ')' or stripped_line.endswith(';')):
                    # Look ahead for more table options on next lines
                    for j in range(i + 1, min(i + 5, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith('--'):
                            if (';' in next_line or 
                                next_line.startswith('CREATE') or 
                                next_line.startswith('DROP') or
                                next_line.startswith('INSERT')):
                                if ';' in next_line:
                                    table_def_lines.append(lines[j])
                                break
                            else:
                                table_def_lines.append(lines[j])
                break
                
            # Also break if we hit another CREATE or significant SQL statement
            if (stripped_line.startswith('CREATE TABLE') and 
                not re.search(rf'CREATE TABLE\s+[`"]?{re.escape(table_name)}[`"]?', line, re.IGNORECASE)):
                table_def_lines.pop()  # Remove this line as it's for another table
                break
    
    if table_def_lines and found_closing:
        return '\n'.join(table_def_lines)
    else:
        return None

def apply_patch_to_table_definition(table_definition, patch_content):
    """Apply patch changes to the table definition to show the updated state."""
    if not table_definition or not patch_content:
        return table_definition
    
    # Split table definition into lines
    lines = table_definition.split('\n')
    
    # Process patch to identify changes
    patch_lines = patch_content.split('\n')
    
    # Find lines that are being removed (-) and added (+)
    lines_to_remove = []
    lines_to_add = []
    
    for patch_line in patch_lines:
        if patch_line.startswith('-') and not patch_line.startswith('---'):
            # Line being removed
            removed_content = patch_line[1:].strip()
            lines_to_remove.append(removed_content)
        elif patch_line.startswith('+') and not patch_line.startswith('+++'):
            # Line being added
            added_content = patch_line[1:].strip()
            lines_to_add.append(added_content)
    
    # Apply changes to table definition
    updated_lines = []
    for line in lines:
        line_content = line.strip()
        line_modified = False
        
        # Check if this line needs to be replaced
        for i, removed_line in enumerate(lines_to_remove):
            if removed_line and removed_line in line_content:
                # Find corresponding added line
                if i < len(lines_to_add):
                    added_line = lines_to_add[i]
                    # Replace the content
                    updated_line = line.replace(removed_line, added_line)
                    updated_lines.append(updated_line)
                    line_modified = True
                    break
        
        if not line_modified:
            updated_lines.append(line)
    
    return '\n'.join(updated_lines)

# Load PR metadata from event payload
try:
    # Check if running in GitHub Actions environment
    github_actions = os.getenv("GITHUB_ACTIONS")
    if github_actions == "true":
        print("🔄 Running in GitHub Actions environment")
        # Continue with GitHub Actions specific logic
        event_path = os.getenv("GITHUB_EVENT_PATH")
        if not event_path or not os.path.exists(event_path):
            print("❌ GITHUB_EVENT_PATH not found or file doesn't exist!")
            print("This script is designed to run in GitHub Actions environment.")
            exit(1)
        
        with open(event_path) as f:
            event = json.load(f)
            pr_number = event["pull_request"]["number"]
    else:
        print("🔄 Running in local environment")
        # Load from config.env for local development
        load_dotenv('config.env')
        
        # Set default values for local development
        pr_number = os.getenv("GITHUB_PR_NUMBER")
        
    

    repo_full = os.getenv("GITHUB_REPOSITORY")  # e.g., "owner/repo"
    token = os.getenv("GITHUB_TOKEN")
    
    print(f"Repository: {repo_full}")
    print(f"PR Number: {pr_number}")
        
except Exception as e:
    print(f"❌ Error reading GitHub event payload: {e}")
    print("This script is designed to run in GitHub Actions environment.")
    exit(1)

if not repo_full:
    print("❌ GITHUB_REPOSITORY environment variable not found!")
    exit(1)

if not token:
    print("❌ GITHUB_TOKEN environment variable not found!")
    exit(1)

# Headers for authentication
headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {token}"
}

# # Fetch PR details
# api_url = f"https://api.github.com/repos/{repo_full}/pulls/{pr_number}"
# print(f"Fetching: {api_url}")

# pr_response = requests.get(api_url, headers=headers)
# print(f"Status Code: {pr_response.status_code}")

# if pr_response.status_code != 200:
#     print(f"Error: {pr_response.status_code}")
#     print(f"Response: {pr_response.text}")
#     if pr_response.status_code == 401:
#         print("❌ Authentication failed - check your token!")
#     elif pr_response.status_code == 404:
#         print("❌ Repository or PR not found!")
#     exit(1)

# pr_data = pr_response.json()
# title = pr_data.get("title")
# description = pr_data.get("body")

# print(f"Title: {title}\n")
# print(f"Description:\n{description}\n")

# Fetch files changed in the PR
files_url = f"https://api.github.com/repos/{repo_full}/pulls/{pr_number}/files"
print(f"Fetching changed files...")

files_response = requests.get(files_url, headers=headers)

if files_response.status_code == 200:
    files_data = files_response.json()

    if files_data:
        # Filter files that have "seed" as prefix
        seed_files = []
        for file_info in files_data:
            filename = file_info.get("filename", "")
            # Check if filename (or just the basename) starts with "seed"
            basename = filename.split('/')[-1]  # Get just the filename part
            if basename.lower().startswith('seed'):
                seed_files.append(file_info)
        
        print(f"\n📁 All Changed Files: {len(files_data)}")
        print(f"📁 Seed Files Found: {len(seed_files)}")
        print("-" * 50)
        
        if seed_files:
            for file_info in seed_files:
                filename = file_info.get("filename")
                status = file_info.get("status")
                additions = file_info.get("additions", 0)
                deletions = file_info.get("deletions", 0)
                patch = file_info.get("patch", "")
                
                print(f"• {filename} ({status})")
                print(f"  +{additions} -{deletions}")
                
                # Show the actual code changes
                if patch:
                    print(f"\n  📝 Code Changes:")
                    print("  " + "=" * 60)
                    for line in patch.split('\n'):
                        if line.startswith('@@'):
                            print(f"  🔍 {line}")
                        elif line.startswith('+'):
                            print(f"  ✅ {line}")
                        elif line.startswith('-'):
                            print(f"  ❌ {line}")
                        elif line.startswith(' '):
                            print(f"     {line}")
                    print("  " + "=" * 60)
                    
                    # Extract detailed table changes if it's a SQL file
                    if filename.lower().endswith('.sql'):
                        # First, get table names from the patch
                        table_changes = extract_table_details(patch)
                        
                        if table_changes:
                            # Fetch the complete file content to get full table definitions
                            file_content_url = f"https://api.github.com/repos/{repo_full}/contents/{filename}"
                            file_response = requests.get(file_content_url, headers=headers)
                            
                            if file_response.status_code == 200:
                                import base64
                                file_data = file_response.json()
                                file_content = base64.b64decode(file_data['content']).decode('utf-8')
                                
                                print(f"\n  🗂️  Complete Table Definitions:")
                                
                                # Extract complete table definitions from the full file
                                for table_name in table_changes.keys():
                                    complete_table_def = extract_complete_table_definition(file_content, table_name)
                                    
                                    if complete_table_def:
                                        # Apply patch changes to show the updated state
                                        updated_table_def = apply_patch_to_table_definition(complete_table_def, patch)
                                        
                                        print(f"\n    📋 Table: {table_name}")
                                        print(f"    🔧 Complete Definition from File:")
                                        print()
                                        
                                        # Print the updated table definition with proper indentation
                                        for line in updated_table_def.split('\n'):
                                            if line.strip():
                                                print(f"    {line}")
                                        
                                        # Show what changed in this table
                                        if table_changes[table_name]['changes']:
                                            print(f"\n    📝 Changes in this PR:")
                                            for change in table_changes[table_name]['changes']:
                                                if change['type'] == 'column_change':
                                                    action = "Modified" if change['action'] == 'added' else "Removed"
                                                    print(f"      • {action}: `{change['column']}` ({change['data_type']})")
                                        print()
                                    else:
                                        print(f"\n    ❌ Could not find complete definition for table: {table_name}")
                            else:
                                print(f"\n  ❌ Could not fetch complete file content (Status: {file_response.status_code})")
                                # Fallback to patch-based analysis
                                print(f"\n  🗂️  Table Definitions (from patch only):")
                                for table_name, details in table_changes.items():
                                    print(f"\n    📋 Table: {table_name} (partial view)")
                        else:
                            print(f"\n  ℹ️  No specific table operations detected")
                else:
                    print(f"  ℹ️  No patch data available (binary file or large change)")
                
                print()
        else:
            print("🔍 No files with 'seed' prefix found in this PR.")
    else:
        print("No files changed in this PR.")
else:
    print(f"Error fetching files: {files_response.status_code}")

