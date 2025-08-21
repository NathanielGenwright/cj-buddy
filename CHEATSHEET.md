# CJ-Buddy Quick Reference 🚀

## Setup (One-time)
```bash
git clone https://github.com/NathanielGenwright/cj-buddy.git
cd cj-buddy
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
./install.sh && source ~/.zshrc
```

## Commands
| Command | Description | Visual Output | Example |
|---------|-------------|---------------|---------|
| `cj TICKET-ID` | Smart summary | 📋 ANALYSIS | `cj SAAS-1234` |
| `cj-test TICKET-ID` | QA test plan | 🧪 QA TEST PLAN | `cj-test MI-43` |
| `cj-tag TICKET-ID` | Apply tags directly | 🏷️ TAGGING | `cj-tag TRI-2114` |
| `cj-task TICKET-ID` | Break into subtasks | 📝 TASK BREAKDOWN | `cj-task SAAS-658` |

## What You Need
- **Jira API Token**: https://id.atlassian.com/manage-profile/security/api-tokens
- **Claude API Key**: https://console.anthropic.com/

## Common Use Cases
- **Before Development**: `cj-task` to break down work into actionable tasks
- **QA Handoff**: `cj-test` for comprehensive test scenarios  
- **Sprint Planning**: `cj` for quick technical understanding
- **Bug Triage**: `cj-tag` to apply smart labels instantly
- **Code Review Prep**: `cj` to understand requirements context

## Troubleshooting
- **Command not found**: Run `source ~/.zshrc`
- **No comments posted**: Check `.env` credentials
- **Permission denied**: Verify Jira API token

*💡 Tip: Enhanced terminal UI shows real-time progress with beautiful icons and status updates*
*🏷️ Tag mode applies labels directly to tickets instead of comments*