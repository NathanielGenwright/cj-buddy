# CJ-Buddy 🤖

CLI tool to summarize and enhance Jira tickets using Claude AI.

## Features

- **AI-Powered Analysis**: Get intelligent summaries of Jira tickets
- **Multiple Modes**:
  - `summarize`: Structured technical analysis
  - `tag`: Apply relevant labels directly to tickets
  - `subtasks`: Break down into development tasks
  - `test-notes`: Generate QA test plans
  - `rca`: Generate comprehensive Root Cause Analysis documents
  - `release-notes`: Generate and append release notes to Instructions/Operational Notes field
- **AgentJ Monitoring**: Automated ticket quality validation with approval tagging
- **Enhanced Terminal Experience**: Beautiful, progressive output with icons and status updates
- **Quick Access**: Simple command shortcuts
- **Rich Text Support**: Handles complex Jira descriptions
- **Smart Error Handling**: Clear error messages and graceful recovery
- **Dry-Run Mode**: Preview all changes without making modifications to Jira

## Quick Start

```bash
# Summarize a ticket
cj SAAS-1234

# Generate test notes
cj-test SAAS-1234

# Apply tags directly to ticket
cj-tag SAAS-1234

# Break into subtasks
cj-task SAAS-1234

# Generate Root Cause Analysis
cj-rca SAAS-1234

# Generate release notes
cj-release SAAS-1234

# Monitor ticket queue for quality
agentj monitor --dry-run

# Use dry-run mode to preview without making changes
cj SAAS-1234 --dry-run
cj-tag SAAS-1234 --dry-run
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/NathanielGenwright/cj-buddy.git
cd cj-buddy
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
# Create shared .env file in parent directory (recommended for multi-project setup)
cp .env.example ../.env
# OR create local .env file
cp .env.example .env

# Edit .env with your credentials:
# - JIRA_BASE_URL
# - JIRA_EMAIL  
# - JIRA_API_TOKEN (or JIRA_TOKEN for compatibility)
# - ANTHROPIC_API_KEY (or CLAUDE_API_KEY for compatibility)
```

4. Install shortcuts:
```bash
./install.sh
source ~/.zshrc
```

## Configuration

### Environment Variables
CJ-Buddy now supports shared configuration for multi-project setups. The tool automatically looks for `.env` files in this order:
1. Parent directory (recommended for shared setup with AgentJ)
2. Current project directory (traditional setup)

### Jira Setup
1. Get your Jira API token from: https://id.atlassian.com/manage-profile/security/api-tokens
2. Add to `.env` file as `JIRA_API_TOKEN`

### Claude Setup
1. Get your Claude API key from: https://console.anthropic.com/
2. Add to `.env` file as `ANTHROPIC_API_KEY`

### Shared Configuration (Recommended)
If you're using both CJ-Buddy and AgentJ, create a single `.env` file in the parent directory:
```bash
# In parent directory containing both cj-buddy/ and agentJ/
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
ANTHROPIC_API_KEY=your-claude-api-key
```

This eliminates duplicate credentials and simplifies maintenance.

## Usage

### Basic Usage
```bash
python main.py TICKET-ID --mode MODE
```

### With Shortcuts
```bash
cj TICKET-ID          # Summarize (default)
cj-sum TICKET-ID      # Summarize
cj-tag TICKET-ID      # Apply tags directly
cj-task TICKET-ID     # Break into subtasks
cj-test TICKET-ID     # Generate test notes
cj-rca TICKET-ID      # Generate Root Cause Analysis
cj-release TICKET-ID  # Generate release notes

# Dry-run mode (preview without making changes)
cj TICKET-ID --dry-run
cj-sum TICKET-ID --dry-run
cj-tag TICKET-ID --dry-run
cj-task TICKET-ID --dry-run
cj-test TICKET-ID --dry-run
cj-rca TICKET-ID --dry-run
cj-release TICKET-ID --dry-run

# AgentJ monitoring
agentj monitor        # Start monitoring ticket queue
agentj validate TICKET-ID # Validate specific ticket
agentj status         # Show monitoring statistics
```

### Examples
```bash
# Get a structured analysis
cj SAAS-658
# Output: 📋 ANALYSIS with preview and progress indicators

# Preview analysis without posting to Jira
cj SAAS-658 --dry-run
# Output: 📋 ANALYSIS [DRY RUN] with full output preview

# Generate QA test cases  
cj-test MI-43
# Output: 🧪 QA TEST PLAN with structured test scenarios

# Preview test notes without posting
cj-test MI-43 --dry-run
# Output: 🧪 QA TEST PLAN [DRY RUN] with full test plan

# Get development subtasks
cj-task TRI-2114
# Output: 📝 TASK BREAKDOWN with actionable development tasks

# Apply smart labels
cj-tag SAAS-658
# Output: 🏷️ TAGGING with real-time label application

# Preview tags without applying them
cj-tag SAAS-658 --dry-run
# Output: 🏷️ TAGGING [DRY RUN] showing suggested tags

# Generate Root Cause Analysis
cj-rca SAAS-1761
# Output: 🔍 ROOT CAUSE ANALYSIS saved as Markdown file with optional Jira posting

# Generate release notes
cj-release SAAS-1234
# Output: 📝 RELEASE NOTES with interactive questions and draft review
```

## Dry-Run Mode

The `--dry-run` flag allows you to preview what any command would do without making actual changes to Jira. This is perfect for:

- **Testing configurations** before applying changes
- **Reviewing AI suggestions** before posting comments
- **Previewing tag suggestions** before applying labels
- **Validating output format** during development

### Dry-Run Features:
- ✅ **No Jira Changes**: Comments, labels, and field updates are skipped
- ✅ **Full Preview**: Shows complete AI-generated output
- ✅ **Clear Indicators**: `[DRY RUN]` markers throughout the output  
- ✅ **Same Analysis**: Uses identical AI prompts and processing
- ✅ **Safe Testing**: Perfect for experimentation and validation

### Dry-Run Examples:
```bash
# Preview ticket analysis
cj-sum TRI-2279 --dry-run
# Shows: 📋 ANALYSIS: TRI-2279 [DRY RUN]
#        🚨 DRY RUN MODE - No changes will be made to Jira
#        📝 FULL OUTPUT: [complete analysis text]

# Preview tag suggestions  
cj-tag SAAS-1234 --dry-run
# Shows: 🏷️ TAGGING: SAAS-1234 [DRY RUN]
#        📌 Suggested tags (X): tag1 (would apply), tag2 (would apply)
#        🎯 [DRY RUN] Would apply tags: tag1, tag2, tag3

# Preview RCA generation
cj-rca SAAS-1761 --dry-run
# Shows: 🔍 ROOT CAUSE ANALYSIS: SAAS-1761 [DRY RUN]  
#        📝 [DRY RUN] Would save RCA to file
#        💬 [DRY RUN] Would skip posting to Jira
```

## Root Cause Analysis (RCA) Feature

The RCA mode generates comprehensive Root Cause Analysis documents that include:

- **Incident Summary**: What happened, impact, and timeline
- **Immediate Cause**: Direct trigger of the incident
- **Root Causes**: Underlying causes and contributing factors
- **Resolution**: Actions taken and time to resolve
- **Lessons Learned**: What went wrong and what went well
- **Preventive Measures**: Short and long-term improvements
- **Action Items**: Specific tasks to prevent recurrence

RCA documents are:
- Saved as Markdown files in `rca_reports/` directory
- Named with format: `RCA_TICKET-ID_YYYYMMDD_HHMMSS.md`
- Optionally posted to Jira as a comment
- Tagged with `rca-completed` label when posted

## Release Notes Feature

The Release Notes mode generates user-facing release notes and appends them to the "Instructions / Operational Notes" field (customfield_10424):

### Interactive Process:
1. **Issue Analysis**: Extracts key information from the Jira ticket
2. **Clarifying Questions**: Asks about user impact, business value, and limitations
3. **AI Generation**: Creates draft release notes using Claude AI
4. **Review & Edit**: Allows review, manual editing, or regeneration with feedback
5. **Field Update**: Appends final notes to the Instructions/Operational Notes field

### Release Note Formats:
- **✨ New**: For new features and capabilities
- **🐛 Fixed**: For bug fixes and corrections
- **⚡ Improved**: For enhancements and optimizations
- **⚠️ Breaking**: For breaking changes requiring attention

### Features:
- **User-Centric Language**: Focuses on business value and user impact
- **Interactive Workflow**: Asks clarifying questions for better quality
- **Draft Review System**: Multiple rounds of review and editing
- **Automatic Timestamping**: Tracks when release notes were added
- **Field Preservation**: Appends to existing content rather than overwriting

Usage:
```bash
# Generate release notes for a ticket
cj-release SAAS-571

# Or use the full command
cj SAAS-571 --mode release-notes
```

## AgentJ - Ticket Monitoring Agent

AgentJ automatically monitors Jira ticket queues and validates ticket quality:

### Core Features:
- **Automated Validation**: Checks required fields, field rules, and severity-specific requirements
- **Approval Tagging**: Tickets passing all validations get `AJ-approved` label
- **Smart Re-evaluation**: Only re-checks tickets without approval labels
- **Reporter Alerts**: Posts helpful comments with improvement suggestions
- **Configurable Rules**: JSON-based validation configuration

### Monitoring Process:
1. **Queue Monitoring**: Continuously watches specified JQL filter
2. **Validation**: Checks each ticket against configured rules
3. **Approval**: Adds `AJ-approved` label if all validations pass
4. **Feedback**: Posts comment with improvement suggestions if issues found
5. **Re-evaluation**: Rechecks tickets in next cycle until approved

### Commands:
```bash
# Start continuous monitoring
agentj monitor

# Run once in dry-run mode (no changes)
agentj monitor --once --dry-run

# Validate specific ticket
agentj validate SAAS-1234

# Force revalidation (removes approval first)
agentj revalidate SAAS-1234

# Show monitoring statistics
agentj status

# Create default config file
agentj init-config
```

### Configuration:
Edit `agentj_config.json` to customize:
- **JQL Filter**: Which tickets to monitor
- **Required Fields**: Fields that must be present
- **Field Rules**: Minimum length, patterns, allowed values
- **Severity Fields**: Additional requirements for Critical/High priority
- **Alert Methods**: Comment and/or label alerts

## Customization

### Modify Analysis Template
Edit the prompts in `main.py`:

```python
def generate_prompt(mode, summary, description):
    prompts = {
        "summarize": f"""Your custom template here...""",
        # ... other modes
    }
```

## Technical Details

- **Python 3.9+** required
- Uses **Jira REST API v3**
- Claude model: **claude-3-5-sonnet-20241022**
- Handles Atlassian Document Format (ADF)
- **Enhanced Terminal UI** with Unicode icons and progress indicators
- **Smart Label Management** with direct Jira integration

## Troubleshooting

### Comments not appearing in Jira?
- Check your Jira API token is valid
- Ensure you have comment permissions
- Verify `.env` credentials

### Complex ticket descriptions causing errors?
- Latest version handles ADF format
- Pull latest changes from repo

### Command not found?
- Run `source ~/.zshrc`
- Ensure `~/bin` is in PATH
- Re-run `./install.sh`

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use and modify!

## Author

Created with ❤️ by Nathaniel Genwright and Claude