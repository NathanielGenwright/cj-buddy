import os
import sys
import requests
import logging
import argparse
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

# Load .env from parent directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")

JQL = 'project = TRIAGE AND status = "Waiting For Support"'  # Customize

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

AUTH = (JIRA_EMAIL, JIRA_TOKEN)

# Setup logging
def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Generate log filename with timestamp
    log_filename = log_dir / f"triage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configure logging to write to both file and console
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Store log filename for reference
    logging.info(f"Log file: {log_filename}")
    return log_filename

def log(message, level="INFO"):
    level_map = {
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "SUCCESS": logging.INFO,
        "DEBUG": logging.DEBUG
    }
    
    log_level = level_map.get(level, logging.INFO)
    
    # Add special formatting for SUCCESS messages
    if level == "SUCCESS":
        message = f"✓ {message}"
    
    logging.log(log_level, message)

def fetch_issues():
    log("Fetching issues from JIRA...")
    log(f"Using JQL: {JQL}")
    
    url = f"{JIRA_BASE_URL}/rest/api/3/search"
    params = {
        "jql": JQL,
        "fields": "summary,description,priority,reporter",
        "expand": "names"
    }
    
    try:
        response = requests.get(url, headers=HEADERS, auth=AUTH, params=params)
        response.raise_for_status()
        issues = response.json().get("issues", [])
        log(f"Successfully fetched {len(issues)} issue(s)")
        return issues
    except requests.exceptions.RequestException as e:
        log(f"Error fetching issues: {e}", "ERROR")
        return []

def check_fields(issue):
    missing = []
    fields = issue["fields"]
    if not fields.get("summary"): missing.append("Summary")
    if not fields.get("description"): missing.append("Description")
    #if not fields.get("components"): missing.append("Component")
    if not fields.get("priority"): missing.append("Priority")
    #if not fields.get("environment"): missing.append("Environment")
    return missing

def alert_reporter(issue, missing_fields, dry_run=False):
    issue_key = issue["key"]
    reporter_name = issue["fields"]["reporter"]["displayName"]
    reporter_account_id = issue["fields"]["reporter"]["accountId"]
    
    if dry_run:
        log(f"[DRY RUN] Would comment on {issue_key} (Reporter: {reporter_name})")
        return True
    
    log(f"Posting comment to {issue_key} (Reporter: {reporter_name})")
    
    comment_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/comment"
    payload = { "body": { "type": "doc", "version": 1, "content": [
        {
            "type": "paragraph",
            "content": [
                { "type": "text", "text": "Hi " },
                { "type": "mention", "attrs": { "id": reporter_account_id } },
                { "type": "text", "text": f", please update the following fields: {', '.join(missing_fields)}" }
            ]
        }
    ]}}
    
    try:
        response = requests.post(comment_url, headers=HEADERS, auth=AUTH, json=payload)
        response.raise_for_status()
        log(f"✓ Successfully commented on {issue_key}", "SUCCESS")
        return True
    except requests.exceptions.RequestException as e:
        log(f"✗ Failed to comment on {issue_key}: {e}", "ERROR")
        return False

def display_summary(issues_to_alert):
    print("\n" + "="*60)
    print("TRIAGE SUMMARY")
    print("="*60)
    
    if not issues_to_alert:
        print("No issues require alerts (all have complete required fields)")
        return
    
    print(f"Found {len(issues_to_alert)} issue(s) requiring alerts:\n")
    
    for issue, missing in issues_to_alert:
        issue_key = issue["key"]
        reporter_name = issue["fields"]["reporter"]["displayName"]
        summary = issue["fields"].get("summary", "No summary")[:50]
        
        print(f"  • {issue_key}: {summary}...")
        print(f"    Reporter: {reporter_name}")
        print(f"    Missing: {', '.join(missing)}")
        print()

def prompt_user(skip_prompt=False, default_action=None):
    if skip_prompt and default_action:
        return default_action
    
    print("="*60)
    response = input("Do you want to proceed with posting comments? (yes/no/dry-run): ").strip().lower()
    
    if response in ['yes', 'y']:
        return 'execute'
    elif response in ['dry-run', 'dry', 'd']:
        return 'dry-run'
    else:
        return 'cancel'

def run(args=None):
    # Setup logging first
    log_file = setup_logging()
    
    log("Starting JIRA Triage Automation")
    log(f"JIRA Base URL: {JIRA_BASE_URL}")
    
    # Log command-line mode if applicable
    if args and args.dry_run:
        log("Running in DRY-RUN mode (command-line flag)")
    elif args and args.execute:
        log("Running in EXECUTE mode (command-line flag)")
    
    # Fetch issues
    issues = fetch_issues()
    if not issues:
        log("No issues found or error occurred")
        return
    
    # Check for missing fields
    issues_to_alert = []
    log("Checking for missing required fields...")
    
    for issue in issues:
        missing = check_fields(issue)
        if len(missing) >= 1:
            issues_to_alert.append((issue, missing))
            log(f"  {issue['key']}: Missing {len(missing)} field(s)")
    
    # Display summary
    display_summary(issues_to_alert)
    
    if not issues_to_alert:
        log("No actions required")
        return
    
    # Prompt for action (or use command-line argument)
    skip_prompt = False
    default_action = None
    
    if args:
        if args.dry_run:
            skip_prompt = True
            default_action = 'dry-run'
        elif args.execute:
            skip_prompt = True
            default_action = 'execute'
    
    action = prompt_user(skip_prompt, default_action)
    
    if action == 'cancel':
        log("Operation cancelled by user")
        return
    
    # Process alerts
    dry_run = (action == 'dry-run')
    mode_text = "[DRY RUN MODE] " if dry_run else ""
    
    print("\n" + "="*60)
    log(f"{mode_text}Processing alerts...")
    print("="*60)
    
    success_count = 0
    for issue, missing_fields in issues_to_alert:
        if alert_reporter(issue, missing_fields, dry_run):
            success_count += 1
    
    # Final summary
    print("\n" + "="*60)
    log(f"{mode_text}Completed: {success_count}/{len(issues_to_alert)} alerts processed successfully")
    
    if dry_run:
        log("This was a dry run - no actual comments were posted")
    
    log(f"Session complete. Logs saved to: {logging.root.handlers[0].baseFilename}")

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="JIRA Triage Automation - Alerts reporters about missing required fields",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                  # Interactive mode (prompts for action)
  %(prog)s --dry-run        # Dry-run mode (no comments posted)
  %(prog)s --execute        # Execute mode (posts comments without prompting)
  %(prog)s -d               # Short form of --dry-run
  %(prog)s -e               # Short form of --execute

Required environment variables (in .env file):
  JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN
        """
    )
    
    # Create mutually exclusive group for modes
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '-d', '--dry-run', '--dry_run',
        action='store_true',
        help='Run in dry-run mode (show what would happen without posting comments)'
    )
    mode_group.add_argument(
        '-e', '--execute',
        action='store_true',
        help='Execute immediately without prompting for confirmation'
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    try:
        args = parse_arguments()
        run(args)
    except KeyboardInterrupt:
        log("\nOperation interrupted by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        log(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)