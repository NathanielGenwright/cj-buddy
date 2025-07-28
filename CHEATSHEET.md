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
| Command | Description | Example |
|---------|-------------|---------|
| `cj TICKET-ID` | Smart summary | `cj SAAS-1234` |
| `cj-test TICKET-ID` | QA test plan | `cj-test MI-43` |
| `cj-tag TICKET-ID` | Suggest tags | `cj-tag TRI-2114` |
| `cj-task TICKET-ID` | Break into subtasks | `cj-task SAAS-658` |

## What You Need
- **Jira API Token**: https://id.atlassian.com/manage-profile/security/api-tokens
- **Claude API Key**: https://console.anthropic.com/

## Common Use Cases
- **Before Development**: `cj-task` to break down work
- **QA Handoff**: `cj-test` for test scenarios  
- **Sprint Planning**: `cj` for quick understanding
- **Bug Triage**: `cj-tag` for categorization

## Troubleshooting
- **Command not found**: Run `source ~/.zshrc`
- **No comments posted**: Check `.env` credentials
- **Permission denied**: Verify Jira API token

*💡 Tip: All commands automatically post AI analysis as Jira comments*