# CJ-Buddy User Manual 📚

## Table of Contents
1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Configuration](#configuration)
4. [Core Features](#core-features)
5. [Use Cases & Examples](#use-cases--examples)
6. [Advanced Usage](#advanced-usage)
7. [Troubleshooting](#troubleshooting)
8. [API Reference](#api-reference)

## Overview

CJ-Buddy is an AI-powered CLI tool that transforms how you interact with Jira tickets. It leverages Claude AI to provide intelligent analysis, summaries, and actionable insights directly within your Jira workflow.

### Key Benefits
- **Save Time**: Instant ticket analysis instead of manual reading
- **Improve Quality**: AI-generated test plans and subtasks
- **Enhance Collaboration**: Automated comments with structured insights
- **Streamline Workflow**: Quick command shortcuts for common tasks

### What It Does
- Analyzes Jira tickets using Claude AI
- Generates structured summaries and breakdowns
- Posts AI insights as Jira comments automatically
- **Applies smart labels directly to tickets** (tag mode)
- Provides multiple analysis modes for different use cases
- **Beautiful terminal interface** with progress indicators and visual feedback

## Installation & Setup

### Prerequisites
- Python 3.9 or higher
- Git
- Active Jira account with API access
- Claude API account

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/NathanielGenwright/cj-buddy.git
   cd cj-buddy
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Environment Variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your credentials:
   ```bash
   JIRA_BASE_URL=https://yourcompany.atlassian.net
   JIRA_EMAIL=your.email@company.com
   JIRA_TOKEN=your_jira_api_token
   CLAUDE_API_KEY=your_claude_api_key
   ```

4. **Install Command Shortcuts**
   ```bash
   ./install.sh
   source ~/.zshrc  # or ~/.bashrc
   ```

5. **Verify Installation**
   ```bash
   cj --help
   ```

## Configuration

### Getting Your API Keys

#### Jira API Token
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "CJ-Buddy")
4. Copy the generated token to your `.env` file

#### Claude API Key
1. Visit https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy to your `.env` file

### Environment Variables Explained

| Variable | Description | Example |
|----------|-------------|---------|
| `JIRA_BASE_URL` | Your Jira instance URL | `https://company.atlassian.net` |
| `JIRA_EMAIL` | Your Jira account email | `user@company.com` |
| `JIRA_TOKEN` | Jira API token | `ATATTxxx...` |
| `CLAUDE_API_KEY` | Claude API key | `sk-ant-xxx...` |

## Enhanced Terminal Experience

CJ-Buddy provides a beautiful, intuitive terminal interface with:

### Visual Progress Indicators
- **Mode-specific icons**: 📋 Analysis, 🏷️ Tagging, 📝 Task Breakdown, 🧪 QA Testing
- **Step-by-step progress**: Real-time status updates with checkmarks
- **Clean separators**: Unicode lines for clear visual sections

### Smart Error Handling
- **Graceful failures**: Clear error messages without technical jargon
- **Progressive updates**: See exactly where issues occur
- **Recovery guidance**: Helpful troubleshooting hints

### Real-time Feedback
```bash
🔍 Fetching ticket data... ✓
🤖 Analyzing with Claude AI... ✓
💬 Posting to Jira... ✓
🔖 Adding labels... ✓
```

## Core Features

### 1. Summarize Mode (`cj` or `cj-sum`)
**Purpose**: Creates a structured technical analysis of the ticket

**Output Format**:
- **Summary**: One-sentence overview
- **Key Components**: Technical elements involved
- **Acceptance Criteria**: What defines "done"
- **Technical Considerations**: Implementation notes
- **Potential Risks**: Things to watch out for

**Example**:
```bash
cj SAAS-1234
```

### 2. Test Notes Mode (`cj-test`)
**Purpose**: Generates comprehensive QA test plans

**Output Format**:
- **Test Scenarios**: Different conditions to test
- **Edge Cases**: Boundary conditions and error states
- **Regression Tests**: Areas that might be affected
- **User Acceptance Tests**: End-user focused testing

**Example**:
```bash
cj-test MI-43
```

### 3. Smart Tagging Mode (`cj-tag`)
**Purpose**: Applies relevant labels directly to Jira tickets

**Enhanced Terminal Experience**:
```bash
🏷️ TAGGING: TRI-2114
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Fetching ticket data... ✓
🤖 Analyzing with Claude AI... ✓
🏷️  Parsing and applying tags... ✓
📌 Applying 5 tags:
   • documentation ✓
   • configuration ✓
   • api-integration ✓
   • backend ✓
   • data-migration ✓
🔖 Adding audit label... ✓

🎯 Applied tags: documentation, configuration, api-integration, backend, data-migration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ TAGGING complete!
```

**Features**:
- **Direct Application**: Labels are applied to tickets, not posted as comments
- **Smart Parsing**: AI response converted to clean, searchable labels
- **Audit Trail**: Automatic `ai-tagged` label for tracking
- **Real-time Feedback**: See each label being applied with confirmation

**Example**:
```bash
cj-tag TRI-2114
```

### 4. Subtasks Mode (`cj-task`)
**Purpose**: Breaks down work into actionable development tasks

**Output Format**:
- **Development Tasks**: Code changes needed
- **Testing Tasks**: QA activities required
- **Documentation Tasks**: Updates needed
- **Deployment Tasks**: Release considerations

**Example**:
```bash
cj-task SAAS-658
```

## Use Cases & Examples

### Use Case 1: Sprint Planning
**Scenario**: Product manager needs to estimate story points for upcoming sprint

```bash
# Get quick understanding of multiple tickets
cj PROJ-101
cj PROJ-102
cj PROJ-103

# Break down complex stories
cj-task PROJ-104
```

**Benefit**: Fast comprehension of ticket scope and complexity for accurate estimation.

### Use Case 2: Development Handoff
**Scenario**: Senior developer assigns ticket to junior developer

```bash
# Provide structured breakdown
cj-task DEV-456

# Generate comprehensive context
cj DEV-456
```

**Benefit**: Junior developer gets AI-generated guidance and clear task breakdown.

### Use Case 3: QA Preparation
**Scenario**: QA engineer receives ticket for testing

```bash
# Generate test plan
cj-test QA-789

# Understand technical context
cj QA-789
```

**Benefit**: Complete test scenarios generated automatically, ensuring thorough coverage.

### Use Case 4: Bug Triage
**Scenario**: Support team needs to categorize and prioritize bugs

```bash
# Quick categorization
cj-tag BUG-321

# Understand severity and impact
cj BUG-321
```

**Benefit**: Consistent categorization and priority assessment across team.

### Use Case 5: Code Review Preparation
**Scenario**: Reviewer needs context before reviewing pull request

```bash
# Understand original requirements
cj STORY-567

# See breakdown of what should be implemented
cj-task STORY-567
```

**Benefit**: Reviewer has comprehensive context for more effective code review.

## Advanced Usage

### Direct Python Usage
```bash
python main.py TICKET-ID --mode MODE
```

### Modes Available
- `summarize`: Structured analysis (default)
- `tag`: Tag suggestions
- `subtasks`: Task breakdown
- `test-notes`: QA test plan

### Customizing Prompts
Edit `main.py` to modify AI prompts:

```python
def generate_prompt(mode, summary, description):
    prompts = {
        "summarize": f"""Your custom template here...""",
        # Modify other modes as needed
    }
```

### Batch Processing
Process multiple tickets:

```bash
for ticket in PROJ-101 PROJ-102 PROJ-103; do
    cj $ticket
done
```

## Troubleshooting

### Common Issues

#### "Command not found" Error
**Symptoms**: `cj: command not found`

**Solutions**:
1. Run `source ~/.zshrc` or `source ~/.bashrc`
2. Verify `~/bin` is in your PATH: `echo $PATH`
3. Re-run installation: `./install.sh`
4. Check file permissions: `ls -la ~/bin/cj*`

#### Comments Not Appearing in Jira
**Symptoms**: Tool runs but no comments posted

**Solutions**:
1. Verify Jira credentials in `.env`
2. Check API token is valid
3. Ensure you have comment permissions on the ticket
4. Test Jira connection: `curl -u email:token https://company.atlassian.net/rest/api/3/myself`

#### Claude API Errors
**Symptoms**: "API key invalid" or rate limit errors

**Solutions**:
1. Verify Claude API key in `.env`
2. Check API usage limits in Claude console
3. Ensure proper formatting (key should start with `sk-ant-`)

#### Complex Ticket Descriptions Causing Errors
**Symptoms**: KeyError or parsing failures

**Solutions**:
1. Ensure you're using latest version
2. The tool handles Atlassian Document Format (ADF)
3. Check for special characters in ticket descriptions

### Debug Mode
Enable verbose logging:

```bash
export DEBUG=1
cj TICKET-ID
```

### Testing Your Setup
Use the test script to verify everything works:

```bash
python test_cj.py
```

## API Reference

### Core Functions

#### `fetch_jira_ticket(ticket_id)`
Retrieves ticket data from Jira API.

**Parameters**:
- `ticket_id` (str): Jira ticket identifier

**Returns**: Ticket data including summary and description

#### `post_comment_to_jira(ticket_id, comment)`
Posts AI analysis as comment to Jira ticket.

**Parameters**:
- `ticket_id` (str): Jira ticket identifier
- `comment` (str): Comment text to post

#### `get_claude_analysis(prompt)`
Sends prompt to Claude AI and returns analysis.

**Parameters**:
- `prompt` (str): Formatted prompt for AI analysis

**Returns**: AI-generated analysis text

### Prompt Templates

The tool uses structured prompts for consistent output:

```python
SUMMARIZE_TEMPLATE = """
Analyze this Jira ticket and provide a structured summary:

**Summary**: [One sentence overview]
**Key Components**: [Technical elements]
**Acceptance Criteria**: [Definition of done]
**Technical Considerations**: [Implementation notes]
**Potential Risks**: [Things to watch]

Ticket: {summary}
Description: {description}
"""
```

### Configuration Options

Customize behavior by modifying these variables in `main.py`:

- `CLAUDE_MODEL`: AI model to use (default: claude-3-5-sonnet-20241022)
- `MAX_TOKENS`: Maximum response length
- `TEMPERATURE`: AI creativity level (0.0-1.0)

## Best Practices

### For Teams
1. **Standardize Usage**: Train team on consistent command usage
2. **Review AI Output**: Always validate AI suggestions before acting
3. **Customize Prompts**: Adapt prompts to your domain and terminology
4. **Regular Updates**: Keep the tool updated for latest features

### For Security
1. **Protect API Keys**: Never commit `.env` files to version control
2. **Use Strong Tokens**: Generate dedicated API tokens for the tool
3. **Regular Rotation**: Periodically rotate API keys
4. **Access Control**: Limit Jira permissions to necessary projects only

### For Efficiency
1. **Use Shortcuts**: Learn the command shortcuts for speed
2. **Batch Operations**: Process multiple tickets in sequence
3. **Combine Modes**: Use different modes for comprehensive analysis
4. **Automate Workflows**: Integrate into CI/CD or automation scripts

---

## Support & Contributing

### Getting Help
- Check this manual first
- Review troubleshooting section
- Open GitHub issue with detailed error information

### Contributing
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

### License
MIT License - free to use and modify for your needs.

---

*Created with ❤️ by the development team and Claude AI*