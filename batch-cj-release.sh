#!/bin/bash

# Batch CJ-Release Generator
# Generates release notes for multiple JIRA tickets using cj-release tool
# Usage: ./batch-cj-release.sh [ticket1] [ticket2] [ticket3] ...
# If no tickets provided, uses the default MBSaas 7.11.0 tickets list

# Set environment variables (reads from .env if available)
if [ -f "$(dirname "$0")/.env" ]; then
    export $(grep -v '^#' "$(dirname "$0")/.env" | xargs)
else
    # Fallback to direct environment variables
    # Fallback environment variables - set these in your environment
    export JIRA_BASE_URL=${JIRA_BASE_URL:-"https://jiramb.atlassian.net"}
    export JIRA_EMAIL=${JIRA_EMAIL:-"nathaniel@Munibilling.com"}
    
    # Check for required environment variables
    if [ -z "$JIRA_TOKEN" ] || [ -z "$ANTHROPIC_API_KEY" ]; then
        echo "Error: JIRA_TOKEN and ANTHROPIC_API_KEY must be set in environment or .env file"
        echo "Please set these environment variables before running this script"
        exit 1
    fi
fi

# Use command line arguments or default to MBSaas 7.11.0 tickets
if [ $# -gt 0 ]; then
    TICKETS=("$@")
else
    # Default MBSaas 7.11.0 tickets
    TICKETS=(
        "SAAS-2227"
        "SAAS-1901"
        "SAAS-1892"
        "SAAS-1891" 
        "SAAS-1890"
        "SAAS-1889"
        "SAAS-1888"
        "SAAS-1842"
        "SAAS-1840"
        "SAAS-1839"
        "SAAS-536"
        "SAAS-1193"
        "SAAS-2026"
        "SAAS-2030"
        "SAAS-2052"
        "SAAS-2054"
    )
fi

# Get script directory and change to parent directory where cj-release is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting batch release notes generation for ${#TICKETS[@]} tickets..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Loop through tickets and generate release notes
SUCCESS_COUNT=0
FAILURE_COUNT=0
FAILED_TICKETS=()

for ticket in "${TICKETS[@]}"; do
    echo "📝 Processing $ticket..."
    if ./cj-release "$ticket"; then
        echo "✅ Completed $ticket"
        ((SUCCESS_COUNT++))
    else
        echo "❌ Failed to process $ticket"
        ((FAILURE_COUNT++))
        FAILED_TICKETS+=("$ticket")
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
done

echo ""
echo "📊 BATCH SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Successful: $SUCCESS_COUNT"
echo "❌ Failed: $FAILURE_COUNT"

if [ ${#FAILED_TICKETS[@]} -gt 0 ]; then
    echo "Failed tickets: ${FAILED_TICKETS[*]}"
fi

echo "🎉 Batch release notes generation completed!"