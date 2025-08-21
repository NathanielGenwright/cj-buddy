# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based JIRA ticket triage automation tool that automatically reviews tickets in "Triage" status and alerts reporters when required fields are missing. The tool integrates with JIRA REST API v3 to fetch issues, validate required fields, and post comments.

## Key Commands

### Running the Application
```bash
python triage_tix.py
# or
./triage_tix
```

### Development Setup
```bash
# Install required dependencies
pip install requests python-dotenv

# Copy and configure environment variables
cp .env.example .env  # (create .env file with required variables)
```

## Environment Configuration

Required environment variables in `.env`:
- `JIRA_BASE_URL`: Your JIRA instance URL
- `JIRA_EMAIL`: Email for JIRA authentication  
- `JIRA_API_TOKEN`: JIRA API token for authentication
- `ANTHROPIC_API_KEY`: Anthropic API key (for potential AI features)

## Code Architecture

### Main Components

**triage_tix.py**: Core automation script with four main functions:
- `fetch_issues()`: Queries JIRA using JQL for tickets in "Triage" status
- `check_fields()`: Validates required fields (summary, description, components, priority, environment)
- `alert_reporter()`: Posts automated comments to tickets with missing fields
- `run()`: Main execution loop that processes all triage tickets

### Business Logic
- Targets tickets with `project = MYPROJECT AND status = "Triage"`
- Only alerts when 2+ required fields are missing (prevents spam)
- Uses JIRA REST API v3 endpoints for issue retrieval and commenting
- Authenticates using email + API token combination

### File Structure
- `triage_tix.py`: Main script source code
- `triage_tix`: Executable copy (identical to .py file)
- `.env`: Environment configuration (not tracked in git)

## Development Notes

- No formal testing framework currently implemented
- No dependency management file (requirements.txt) exists
- Error handling is minimal - consider adding robust exception handling
- The codebase uses direct API calls without a JIRA SDK wrapper
- Both executable files contain identical code - maintain consistency when editing