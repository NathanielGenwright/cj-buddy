#!/bin/bash

# Muni MCP Server Logs Script
# This script displays and manages MCP server logs

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MCP_SERVER_DIR="$PROJECT_ROOT/mcp-servers/mysql-readonly"
LOGFILE="$MCP_SERVER_DIR/logs/mcp-server.log"
PIDFILE="$MCP_SERVER_DIR/mcp-server.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Display and manage MCP server logs"
    echo ""
    echo "OPTIONS:"
    echo "  --tail, -t [N]     Show last N lines and follow (default: 50)"
    echo "  --follow, -f       Follow log file (like tail -f)"
    echo "  --head, -h [N]     Show first N lines (default: 20)"
    echo "  --lines, -n N      Show last N lines without following"
    echo "  --clear            Clear the log file"
    echo "  --rotate           Rotate the log file"
    echo "  --size             Show log file size"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Show last 50 lines and follow"
    echo "  $0 --tail 100     # Show last 100 lines and follow"
    echo "  $0 --lines 20     # Show last 20 lines without following"
    echo "  $0 --clear        # Clear the log file"
    echo "  $0 --size         # Show log file size"
    echo ""
}

is_server_running() {
    if [ -f "$PIDFILE" ]; then
        local pid=$(cat "$PIDFILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

show_server_info() {
    echo -e "${BLUE}=== MCP Server Information ===${NC}"
    echo "Log file: $LOGFILE"
    echo "Server directory: $MCP_SERVER_DIR"
    
    if is_server_running; then
        local pid=$(cat "$PIDFILE")
        echo -e "${GREEN}Status: Running (PID: $pid)${NC}"
    else
        echo -e "${YELLOW}Status: Not running${NC}"
    fi
    
    if [ -f "$LOGFILE" ]; then
        local file_size=$(du -h "$LOGFILE" 2>/dev/null | cut -f1)
        local line_count=$(wc -l < "$LOGFILE" 2>/dev/null || echo "0")
        echo "Log size: $file_size ($line_count lines)"
        
        if [ -s "$LOGFILE" ]; then
            local last_modified=$(stat -f "%Sm" "$LOGFILE" 2>/dev/null || stat -c "%y" "$LOGFILE" 2>/dev/null || echo "Unknown")
            echo "Last modified: $last_modified"
        fi
    else
        echo -e "${YELLOW}Log file does not exist${NC}"
    fi
    echo ""
}

show_logs() {
    local mode="$1"
    local lines="${2:-50}"
    
    # Ensure logs directory exists
    mkdir -p "$MCP_SERVER_DIR/logs"
    
    if [ ! -f "$LOGFILE" ]; then
        warn "Log file does not exist: $LOGFILE"
        return 1
    fi
    
    if [ ! -s "$LOGFILE" ]; then
        warn "Log file is empty"
        return 1
    fi
    
    case "$mode" in
        "tail")
            log "Showing last $lines lines and following log file..."
            log "Press Ctrl+C to stop following"
            echo ""
            tail -n "$lines" -f "$LOGFILE"
            ;;
        "follow")
            log "Following log file (Press Ctrl+C to stop)..."
            echo ""
            tail -f "$LOGFILE"
            ;;
        "head")
            log "Showing first $lines lines..."
            echo ""
            head -n "$lines" "$LOGFILE"
            ;;
        "lines")
            log "Showing last $lines lines..."
            echo ""
            tail -n "$lines" "$LOGFILE"
            ;;
        *)
            error "Unknown mode: $mode"
            return 1
            ;;
    esac
}

clear_logs() {
    if [ -f "$LOGFILE" ]; then
        local file_size=$(du -h "$LOGFILE" 2>/dev/null | cut -f1)
        read -p "Clear log file ($file_size)? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            > "$LOGFILE"
            log "Log file cleared"
        else
            log "Operation cancelled"
        fi
    else
        warn "Log file does not exist"
    fi
}

rotate_logs() {
    if [ -f "$LOGFILE" ]; then
        local timestamp=$(date +"%Y%m%d_%H%M%S")
        local backup_file="${LOGFILE}.${timestamp}"
        
        local file_size=$(du -h "$LOGFILE" 2>/dev/null | cut -f1)
        log "Rotating log file ($file_size) to backup..."
        
        if mv "$LOGFILE" "$backup_file"; then
            log "Log file rotated to: $backup_file"
            
            # Create new empty log file
            touch "$LOGFILE"
            log "Created new log file: $LOGFILE"
            
            # Clean up old rotated logs (keep last 5)
            local old_logs=$(ls -1t "${LOGFILE}".* 2>/dev/null | tail -n +6 || true)
            if [ -n "$old_logs" ]; then
                log "Cleaning up old log files..."
                echo "$old_logs" | while read -r old_log; do
                    rm -f "$old_log"
                    log "Removed: $old_log"
                done
            fi
        else
            error "Failed to rotate log file"
            return 1
        fi
    else
        warn "Log file does not exist"
    fi
}

show_log_size() {
    if [ -f "$LOGFILE" ]; then
        local file_size=$(du -h "$LOGFILE" 2>/dev/null | cut -f1)
        local line_count=$(wc -l < "$LOGFILE" 2>/dev/null || echo "0")
        local byte_size=$(stat -f "%z" "$LOGFILE" 2>/dev/null || stat -c "%s" "$LOGFILE" 2>/dev/null || echo "0")
        
        log "Log file statistics:"
        echo "  File: $LOGFILE"
        echo "  Size: $file_size ($byte_size bytes)"
        echo "  Lines: $line_count"
        
        if [ -s "$LOGFILE" ]; then
            local first_line=$(head -n 1 "$LOGFILE" 2>/dev/null || echo "")
            local last_line=$(tail -n 1 "$LOGFILE" 2>/dev/null || echo "")
            
            if [ -n "$first_line" ]; then
                echo "  First entry: $first_line"
            fi
            if [ -n "$last_line" ]; then
                echo "  Last entry: $last_line"
            fi
        fi
        
        # Show recent activity (last 5 lines)
        if [ -s "$LOGFILE" ]; then
            echo ""
            echo "Recent activity:"
            tail -n 5 "$LOGFILE" | sed 's/^/  /'
        fi
    else
        warn "Log file does not exist: $LOGFILE"
    fi
}

# Default action
ACTION="tail"
LINES=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --tail|-t)
            ACTION="tail"
            if [[ $2 =~ ^[0-9]+$ ]]; then
                LINES="$2"
                shift
            fi
            shift
            ;;
        --follow|-f)
            ACTION="follow"
            shift
            ;;
        --head)
            ACTION="head"
            if [[ $2 =~ ^[0-9]+$ ]]; then
                LINES="$2"
                shift
            fi
            shift
            ;;
        --lines|-n)
            ACTION="lines"
            if [[ $2 =~ ^[0-9]+$ ]]; then
                LINES="$2"
                shift
            else
                error "Option --lines requires a number"
                exit 1
            fi
            shift
            ;;
        --clear)
            ACTION="clear"
            shift
            ;;
        --rotate)
            ACTION="rotate"
            shift
            ;;
        --size)
            ACTION="size"
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Set default line counts
case "$ACTION" in
    "tail")
        LINES="${LINES:-50}"
        ;;
    "head")
        LINES="${LINES:-20}"
        ;;
    "lines")
        LINES="${LINES:-20}"
        ;;
esac

# Main execution
main() {
    show_server_info
    
    case "$ACTION" in
        "tail"|"follow"|"head"|"lines")
            show_logs "$ACTION" "$LINES"
            ;;
        "clear")
            clear_logs
            ;;
        "rotate")
            rotate_logs
            ;;
        "size")
            show_log_size
            ;;
        *)
            error "Unknown action: $ACTION"
            exit 1
            ;;
    esac
}

# Handle Ctrl+C gracefully when following logs
trap 'echo -e "\n${GREEN}Log viewing stopped${NC}"; exit 0' SIGINT SIGTERM

# Run main function
main "$@"