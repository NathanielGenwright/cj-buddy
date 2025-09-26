#!/bin/bash

# Muni MCP Server Stop Script
# This script stops the MCP MySQL server

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MCP_SERVER_DIR="$PROJECT_ROOT/mcp-servers/mysql-readonly"
PIDFILE="$MCP_SERVER_DIR/mcp-server.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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
    echo "Stop the Muni MCP MySQL server"
    echo ""
    echo "OPTIONS:"
    echo "  --force, -f    Force kill the server process"
    echo "  --help, -h     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0             # Stop the server gracefully"
    echo "  $0 --force     # Force kill the server"
    echo ""
}

is_server_running() {
    if [ -f "$PIDFILE" ]; then
        local pid=$(cat "$PIDFILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            # PID file exists but process is not running
            rm -f "$PIDFILE"
            return 1
        fi
    fi
    return 1
}

stop_server() {
    local force_kill="$1"
    
    if ! is_server_running; then
        warn "MCP server is not running"
        return 0
    fi
    
    local pid=$(cat "$PIDFILE")
    log "Stopping MCP server (PID: $pid)..."
    
    if [ "$force_kill" = "true" ]; then
        # Force kill
        log "Force killing server process..."
        if kill -9 "$pid" 2>/dev/null; then
            log "Server process killed forcefully"
        else
            warn "Could not kill process $pid (it may have already stopped)"
        fi
    else
        # Graceful shutdown
        log "Sending graceful shutdown signal..."
        if kill -TERM "$pid" 2>/dev/null; then
            # Wait up to 10 seconds for graceful shutdown
            local count=0
            while [ $count -lt 10 ] && ps -p "$pid" > /dev/null 2>&1; do
                sleep 1
                count=$((count + 1))
            done
            
            if ps -p "$pid" > /dev/null 2>&1; then
                warn "Graceful shutdown timeout. Force killing..."
                kill -9 "$pid" 2>/dev/null || true
            fi
        else
            warn "Could not send shutdown signal to process $pid (it may have already stopped)"
        fi
    fi
    
    # Clean up PID file
    if [ -f "$PIDFILE" ]; then
        rm -f "$PIDFILE"
        log "Cleaned up PID file"
    fi
    
    # Verify process is stopped
    if ps -p "$pid" > /dev/null 2>&1; then
        error "Failed to stop server process $pid"
        return 1
    else
        log "MCP server stopped successfully"
        return 0
    fi
}

find_and_stop_orphaned_processes() {
    log "Checking for orphaned MCP server processes..."
    
    # Look for node processes running our server script
    local server_script="$MCP_SERVER_DIR/server.js"
    local pids=$(pgrep -f "$server_script" || true)
    
    if [ -n "$pids" ]; then
        warn "Found orphaned MCP server processes:"
        echo "$pids" | while read -r pid; do
            if [ -n "$pid" ]; then
                warn "  PID $pid: $(ps -p $pid -o command= 2>/dev/null || echo 'Process info unavailable')"
                log "Stopping orphaned process $pid..."
                kill -TERM "$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null || true
            fi
        done
        
        # Wait a moment and check again
        sleep 2
        local remaining_pids=$(pgrep -f "$server_script" || true)
        if [ -n "$remaining_pids" ]; then
            warn "Some processes may still be running. You may need to manually kill them."
        else
            log "All orphaned processes have been stopped"
        fi
    else
        log "No orphaned MCP server processes found"
    fi
}

show_server_status() {
    log "Checking MCP server status..."
    
    if is_server_running; then
        local pid=$(cat "$PIDFILE")
        log "MCP server is running:"
        log "  PID: $pid"
        log "  Command: $(ps -p $pid -o command= 2>/dev/null || echo 'Command unavailable')"
        log "  Started: $(ps -p $pid -o lstart= 2>/dev/null || echo 'Start time unavailable')"
        
        # Show memory and CPU usage if available
        local mem_cpu=$(ps -p $pid -o %mem,%cpu 2>/dev/null || true)
        if [ -n "$mem_cpu" ]; then
            log "  Memory/CPU: $mem_cpu"
        fi
    else
        log "MCP server is not running"
        
        # Check for orphaned processes
        find_and_stop_orphaned_processes
    fi
}

# Parse command line arguments
FORCE_KILL="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        --force|-f)
            FORCE_KILL="true"
            shift
            ;;
        --status|-s)
            show_server_status
            exit 0
            ;;
        --help|-h)
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

# Main execution
main() {
    log "Stopping Muni MCP Server..."
    log "MCP server directory: $MCP_SERVER_DIR"
    
    stop_server "$FORCE_KILL"
    
    # Also clean up any orphaned processes
    find_and_stop_orphaned_processes
    
    log "Stop operation completed"
}

# Run main function
main "$@"