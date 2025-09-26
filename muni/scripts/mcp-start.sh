#!/bin/bash

# Muni MCP Server Start Script
# This script starts the MCP MySQL server for database access

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
    echo "Start the Muni MCP MySQL server"
    echo ""
    echo "OPTIONS:"
    echo "  --dev, --development    Start with development database (default)"
    echo "  --test                  Start with test database" 
    echo "  --daemon, -d            Run as daemon (background process)"
    echo "  --help, -h              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                      # Start with development database"
    echo "  $0 --test              # Start with test database"
    echo "  $0 --daemon            # Start as background daemon"
    echo "  $0 --test --daemon     # Start test database as daemon"
    echo ""
}

check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        error "Node.js is not installed. Please install Node.js (version 18 or higher)."
        exit 1
    fi
    
    local node_version=$(node --version | cut -d 'v' -f 2 | cut -d '.' -f 1)
    if [ "$node_version" -lt 18 ]; then
        error "Node.js version 18 or higher is required. Current version: $(node --version)"
        exit 1
    fi
    
    # Check if MCP server directory exists
    if [ ! -d "$MCP_SERVER_DIR" ]; then
        error "MCP server directory not found: $MCP_SERVER_DIR"
        error "Please run the setup first: cd $MCP_SERVER_DIR && npm install"
        exit 1
    fi
    
    # Check if dependencies are installed
    if [ ! -d "$MCP_SERVER_DIR/node_modules" ]; then
        error "Node modules not found. Installing dependencies..."
        cd "$MCP_SERVER_DIR" && npm install
    fi
    
    # Check if .env file exists
    if [ ! -f "$MCP_SERVER_DIR/.env" ]; then
        warn ".env file not found. Please copy .env.example to .env and configure it."
        if [ -f "$MCP_SERVER_DIR/.env.example" ]; then
            log "You can copy the example file: cp $MCP_SERVER_DIR/.env.example $MCP_SERVER_DIR/.env"
        fi
        exit 1
    fi
    
    log "Prerequisites check passed ✓"
}

check_docker_services() {
    log "Checking Docker services..."
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
        warn "Docker not found. Make sure Docker services are running if you need database access."
        return 1
    fi
    
    # Check if docker-compose.yml exists
    if [ -f "$PROJECT_ROOT/docker-compose.yml" ]; then
        cd "$PROJECT_ROOT"
        
        # Check if database services are running
        local db_services=$(docker-compose ps --services | grep -E '^bdb-(dev|test)$' || true)
        if [ -n "$db_services" ]; then
            local running_services=$(docker-compose ps --filter "status=running" --services | grep -E '^bdb-(dev|test)$' || true)
            
            if [ -z "$running_services" ]; then
                warn "Database services are not running. Starting them now..."
                docker-compose up -d bdb-dev bdb-test
                sleep 5 # Give services time to start
            else
                log "Database services are running ✓"
            fi
        else
            warn "Database services not found in docker-compose.yml"
        fi
    else
        warn "docker-compose.yml not found in project root"
    fi
}

test_database_connection() {
    log "Testing database connection..."
    
    cd "$MCP_SERVER_DIR"
    if npm run test > /dev/null 2>&1; then
        log "Database connection test passed ✓"
    else
        error "Database connection test failed. Please check your .env configuration and ensure Docker services are running."
        error "Run 'npm run test' in $MCP_SERVER_DIR for detailed error information."
        exit 1
    fi
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

start_server() {
    local database_mode="$1"
    local daemon_mode="$2"
    
    # Check if server is already running
    if is_server_running; then
        local pid=$(cat "$PIDFILE")
        error "MCP server is already running (PID: $pid)"
        error "Use 'scripts/mcp-stop.sh' to stop it first, or 'scripts/mcp-restart.sh' to restart"
        exit 1
    fi
    
    # Create logs directory
    mkdir -p "$MCP_SERVER_DIR/logs"
    
    # Prepare command arguments
    local args=()
    if [ "$database_mode" = "test" ]; then
        args+=("--test")
    else
        args+=("--dev")
    fi
    
    log "Starting MCP server in $database_mode mode..."
    
    cd "$MCP_SERVER_DIR"
    
    if [ "$daemon_mode" = "true" ]; then
        # Start as daemon
        log "Starting as background daemon..."
        nohup node server.js "${args[@]}" > "$LOGFILE" 2>&1 &
        local pid=$!
        echo $pid > "$PIDFILE"
        
        # Give it a moment to start
        sleep 2
        
        if ps -p "$pid" > /dev/null 2>&1; then
            log "MCP server started successfully as daemon"
            log "PID: $pid"
            log "Log file: $LOGFILE"
            log "Use 'scripts/mcp-logs.sh' to view logs"
            log "Use 'scripts/mcp-stop.sh' to stop the server"
        else
            error "Failed to start MCP server as daemon"
            rm -f "$PIDFILE"
            exit 1
        fi
    else
        # Start in foreground
        log "Starting in foreground mode (Press Ctrl+C to stop)..."
        log "Database mode: $database_mode"
        log "Server directory: $MCP_SERVER_DIR"
        
        # Handle cleanup on exit
        trap 'log "Shutting down MCP server..."; exit 0' SIGINT SIGTERM
        
        exec node server.js "${args[@]}"
    fi
}

# Parse command line arguments
DATABASE_MODE="development"
DAEMON_MODE="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        --dev|--development)
            DATABASE_MODE="development"
            shift
            ;;
        --test)
            DATABASE_MODE="test"
            shift
            ;;
        --daemon|-d)
            DAEMON_MODE="true"
            shift
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
    log "Starting Muni MCP Server..."
    log "Project root: $PROJECT_ROOT"
    log "MCP server directory: $MCP_SERVER_DIR"
    
    check_prerequisites
    check_docker_services
    test_database_connection
    start_server "$DATABASE_MODE" "$DAEMON_MODE"
}

# Run main function
main "$@"