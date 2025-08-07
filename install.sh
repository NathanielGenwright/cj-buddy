#!/bin/bash
# Install CJ-Buddy shortcuts to user's local bin

# Create local bin directory if it doesn't exist
mkdir -p ~/bin

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Create symbolic links in ~/bin
echo "Installing CJ-Buddy shortcuts..."
ln -sf "$SCRIPT_DIR/cj" ~/bin/cj
ln -sf "$SCRIPT_DIR/cj-sum" ~/bin/cj-sum
ln -sf "$SCRIPT_DIR/cj-tag" ~/bin/cj-tag
ln -sf "$SCRIPT_DIR/cj-task" ~/bin/cj-task
ln -sf "$SCRIPT_DIR/cj-test" ~/bin/cj-test
ln -sf "$SCRIPT_DIR/cj-rca" ~/bin/cj-rca
ln -sf "$SCRIPT_DIR/agentj" ~/bin/agentj

# Check if ~/bin is in PATH
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
    echo ""
    echo "Adding ~/bin to PATH in .zshrc..."
    echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
    echo ""
    echo "✅ Installation complete!"
    echo "Please run: source ~/.zshrc"
    echo "Or restart your terminal for the changes to take effect."
else
    echo "✅ Installation complete!"
fi

echo ""
echo "Available commands:"
echo "  cj <ticket>      - Summarize a ticket (default)"
echo "  cj-sum <ticket>  - Summarize a ticket"
echo "  cj-tag <ticket>  - Suggest tags for a ticket"
echo "  cj-task <ticket> - Break down into subtasks"
echo "  cj-test <ticket> - Generate test notes"
echo "  cj-rca <ticket>  - Generate Root Cause Analysis"
echo ""
echo "AgentJ - Ticket Monitoring:"
echo "  agentj monitor   - Start monitoring ticket queue"
echo "  agentj validate <ticket> - Validate specific ticket"
echo "  agentj status    - Show monitoring statistics"
echo ""
echo "Example: cj SAAS-1234"
echo "Example: agentj monitor --dry-run"