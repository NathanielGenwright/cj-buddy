# CJ-Buddy 🤖

CLI tool to summarize and enhance Jira tickets using Claude AI.

## Features

- **AI-Powered Analysis**: Get intelligent summaries of Jira tickets
- **Multiple Modes**:
  - `summarize`: Structured technical analysis
  - `tag`: Suggest relevant tags
  - `subtasks`: Break down into development tasks
  - `test-notes`: Generate QA test plans
- **Quick Access**: Simple command shortcuts
- **Rich Text Support**: Handles complex Jira descriptions

## Quick Start

```bash
# Summarize a ticket
cj SAAS-1234

# Generate test notes
cj-test SAAS-1234

# Suggest tags
cj-tag SAAS-1234

# Break into subtasks
cj-task SAAS-1234
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
cp .env.example .env
# Edit .env with your credentials:
# - JIRA_BASE_URL
# - JIRA_EMAIL  
# - JIRA_TOKEN
# - CLAUDE_API_KEY
```

4. Install shortcuts:
```bash
./install.sh
source ~/.zshrc
```

## Configuration

### Jira Setup
1. Get your Jira API token from: https://id.atlassian.com/manage-profile/security/api-tokens
2. Add to `.env` file

### Claude Setup
1. Get your Claude API key from: https://console.anthropic.com/
2. Add to `.env` file

## Usage

### Basic Usage
```bash
python main.py TICKET-ID --mode MODE
```

### With Shortcuts
```bash
cj TICKET-ID          # Summarize (default)
cj-sum TICKET-ID      # Summarize
cj-tag TICKET-ID      # Suggest tags
cj-task TICKET-ID     # Break into subtasks
cj-test TICKET-ID     # Generate test notes
```

### Examples
```bash
# Get a structured analysis
cj SAAS-658

# Generate QA test cases
cj-test MI-43

# Get development subtasks
cj-task TRI-2114
```

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