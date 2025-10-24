#!/bin/bash
#
# TriQ Dashboard Quick Start Script
#
# Usage:
#   ./start.sh          # Parse logs and start dashboard
#   ./start.sh parse    # Just parse logs
#   ./start.sh serve    # Just start dashboard (no parsing)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "${1:-}" in
    parse)
        echo "📊 Parsing TriQ logs..."
        python3 triq_db.py
        ;;
    serve)
        echo "🚀 Starting dashboard..."
        python3 dashboard.py
        ;;
    *)
        echo "============================================================"
        echo "TriQ Dashboard - Quick Start"
        echo "============================================================"
        echo ""
        echo "Step 1: Parsing logs into database..."
        python3 triq_db.py
        echo ""
        echo "Step 2: Starting dashboard server..."
        echo ""
        python3 dashboard.py
        ;;
esac
