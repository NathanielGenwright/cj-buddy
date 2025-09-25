#!/bin/bash

# Muni MCP Server Status Script
# This script shows the status of the MCP server and related services

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
CYAN='\033[0;36m'
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

info() {
    echo -e "${BLUE}$1${NC}"
}

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Show status of MCP server and related services"
    echo ""
    echo "OPTIONS:"
    echo "  --verbose, -v      Show detailed information"
    echo "  --json             Output status in JSON format"
    echo "  --watch, -w [N]    Watch status with N second intervals (default: 5)"
    echo "  --help, -h         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Show basic status"
    echo "  $0 --verbose      # Show detailed status"
    echo "  $0 --watch        # Watch status (refresh every 5 seconds)"
    echo "  $0 --json         # Output as JSON"
    echo ""
}

is_server_running() {
    if [ -f "$PIDFILE" ]; then
        local pid=$(cat "$PIDFILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            # PID file exists but process is not running
            rm -f "$PIDFILE" 2>/dev/null || true
            return 1
        fi
    fi
    return 1
}

get_server_info() {
    local info_array=()
    
    if is_server_running; then
        local pid=$(cat "$PIDFILE")
        local cmd=$(ps -p "$pid" -o command= 2>/dev/null || echo "Unknown")
        local start_time=$(ps -p "$pid" -o lstart= 2>/dev/null || echo "Unknown")
        local mem_cpu=$(ps -p "$pid" -o %mem,%cpu --no-headers 2>/dev/null || echo "0.0,0.0")
        local mem=$(echo "$mem_cpu" | cut -d',' -f1 | xargs)
        local cpu=$(echo "$mem_cpu" | cut -d',' -f2 | xargs)
        
        # Determine database mode from command line
        local db_mode="development"
        if echo "$cmd" | grep -q -- "--test"; then
            db_mode="test"
        fi
        
        info_array[0]="running"
        info_array[1]="$pid"
        info_array[2]="$start_time"
        info_array[3]="$mem"
        info_array[4]="$cpu"
        info_array[5]="$db_mode"
        info_array[6]="$cmd"
    else
        info_array[0]="stopped"
        info_array[1]=""
        info_array[2]=""
        info_array[3]=""
        info_array[4]=""
        info_array[5]=""
        info_array[6]=""
    fi
    
    printf '%s\n' "${info_array[@]}"
}

check_prerequisites() {
    local issues=0
    
    # Check Node.js
    if command -v node &> /dev/null; then
        local node_version=$(node --version)
        local node_major=$(echo "$node_version" | cut -d'.' -f1 | cut -d'v' -f2)
        if [ "$node_major" -ge 18 ]; then
            echo "node_ok:$node_version"
        else
            echo "node_old:$node_version"
            issues=$((issues + 1))
        fi
    else
        echo "node_missing"
        issues=$((issues + 1))
    fi
    
    # Check MCP server files
    if [ -d "$MCP_SERVER_DIR" ]; then
        if [ -f "$MCP_SERVER_DIR/server.js" ]; then
            echo "server_files_ok"
        else
            echo "server_files_missing"
            issues=$((issues + 1))
        fi
    else
        echo "server_dir_missing"
        issues=$((issues + 1))
    fi
    
    # Check dependencies
    if [ -d "$MCP_SERVER_DIR/node_modules" ]; then
        echo "dependencies_ok"
    else
        echo "dependencies_missing"
        issues=$((issues + 1))
    fi
    
    # Check .env file
    if [ -f "$MCP_SERVER_DIR/.env" ]; then
        echo "env_file_ok"
    else
        echo "env_file_missing"
        issues=$((issues + 1))
    fi
    
    return $issues
}

check_docker_services() {
    local docker_status=""
    local db_dev_status=""
    local db_test_status=""
    
    # Check if docker is available
    if command -v docker-compose &> /dev/null || command -v docker &> /dev/null; then
        docker_status="available"
        
        if [ -f "$PROJECT_ROOT/docker-compose.yml" ]; then
            cd "$PROJECT_ROOT"
            
            # Check development database
            if docker-compose ps bdb-dev 2>/dev/null | grep -q "running"; then
                db_dev_status="running"
            elif docker-compose ps bdb-dev 2>/dev/null | grep -q "Exit"; then
                db_dev_status="stopped"
            else
                db_dev_status="not_configured"
            fi
            
            # Check test database
            if docker-compose ps bdb-test 2>/dev/null | grep -q "running"; then
                db_test_status="running"
            elif docker-compose ps bdb-test 2>/dev/null | grep -q "Exit"; then
                db_test_status="stopped"
            else
                db_test_status="not_configured"
            fi
        else
            docker_status="no_compose_file"
        fi
    else
        docker_status="not_available"
    fi
    
    echo "$docker_status:$db_dev_status:$db_test_status"
}

get_log_info() {
    if [ -f "$LOGFILE" ]; then
        local file_size=$(du -h "$LOGFILE" 2>/dev/null | cut -f1)
        local line_count=$(wc -l < "$LOGFILE" 2>/dev/null || echo "0")
        local last_modified=$(stat -f "%Sm" "$LOGFILE" 2>/dev/null || stat -c "%y" "$LOGFILE" 2>/dev/null || echo "Unknown")
        
        echo "exists:$file_size:$line_count:$last_modified"
    else
        echo "missing:::"
    fi
}

test_database_connections() {
    local dev_status="unknown"
    local test_status="unknown"
    
    if [ -f "$MCP_SERVER_DIR/.env" ]; then
        cd "$MCP_SERVER_DIR"
        
        # Test connections using the test script
        if [ -f "test-connection.js" ]; then
            local test_output=$(node test-connection.js 2>/dev/null || echo "")
            
            if echo "$test_output" | grep -q "Development.*Connection successful"; then
                dev_status="connected"
            else
                dev_status="failed"
            fi
            
            if echo "$test_output" | grep -q "Test.*Connection successful"; then
                test_status="connected"
            else
                test_status="failed"
            fi
        fi
    fi
    
    echo "$dev_status:$test_status"
}

show_basic_status() {
    echo -e "${CYAN}=== Muni MCP Server Status ===${NC}\n"
    
    # Server status
    local server_info=($(get_server_info))
    local status="${server_info[0]}"
    
    if [ "$status" = "running" ]; then
        local pid="${server_info[1]}"
        local db_mode="${server_info[5]}"
        echo -e "🟢 Server Status: ${GREEN}Running${NC} (PID: $pid)"
        echo -e "📊 Database Mode: ${BLUE}$db_mode${NC}"
    else
        echo -e "🔴 Server Status: ${RED}Stopped${NC}"
    fi
    
    # Quick prerequisite check
    local prereq_issues
    check_prerequisites > /dev/null
    prereq_issues=$?
    
    if [ $prereq_issues -eq 0 ]; then
        echo -e "✅ Prerequisites: ${GREEN}All OK${NC}"
    else
        echo -e "⚠️  Prerequisites: ${YELLOW}$prereq_issues issue(s)${NC}"
    fi
    
    # Docker services
    local docker_info=$(check_docker_services)
    local docker_status=$(echo "$docker_info" | cut -d':' -f1)
    local db_dev=$(echo "$docker_info" | cut -d':' -f2)
    local db_test=$(echo "$docker_info" | cut -d':' -f3)
    
    if [ "$docker_status" = "available" ]; then
        if [ "$db_dev" = "running" ] && [ "$db_test" = "running" ]; then
            echo -e "🐳 Docker DBs: ${GREEN}Both Running${NC}"
        elif [ "$db_dev" = "running" ] || [ "$db_test" = "running" ]; then
            echo -e "🐳 Docker DBs: ${YELLOW}Partially Running${NC}"
        else
            echo -e "🐳 Docker DBs: ${RED}Stopped${NC}"
        fi
    else
        echo -e "🐳 Docker: ${YELLOW}Not Available${NC}"
    fi
    
    # Log file
    local log_info=$(get_log_info)
    local log_exists=$(echo "$log_info" | cut -d':' -f1)
    
    if [ "$log_exists" = "exists" ]; then
        local log_size=$(echo "$log_info" | cut -d':' -f2)
        echo -e "📝 Log File: ${GREEN}$log_size${NC}"
    else
        echo -e "📝 Log File: ${YELLOW}Not Found${NC}"
    fi
}

show_verbose_status() {
    echo -e "${CYAN}=== Detailed MCP Server Status ===${NC}\n"
    
    # Server Information
    info "🖥️  Server Information:"
    local server_info=($(get_server_info))
    local status="${server_info[0]}"
    
    if [ "$status" = "running" ]; then
        local pid="${server_info[1]}"
        local start_time="${server_info[2]}"
        local mem="${server_info[3]}"
        local cpu="${server_info[4]}"
        local db_mode="${server_info[5]}"
        local cmd="${server_info[6]}"
        
        echo "   Status: ${GREEN}Running${NC}"
        echo "   PID: $pid"
        echo "   Database Mode: $db_mode"
        echo "   Started: $start_time"
        echo "   Memory Usage: ${mem}%"
        echo "   CPU Usage: ${cpu}%"
        echo "   Command: $cmd"
    else
        echo "   Status: ${RED}Stopped${NC}"
    fi
    echo
    
    # Prerequisites
    info "🔧 Prerequisites:"
    local prereq_output=$(check_prerequisites)
    
    while IFS= read -r line; do
        case "$line" in
            "node_ok:"*)
                local version=$(echo "$line" | cut -d':' -f2)
                echo "   Node.js: ${GREEN}$version${NC}"
                ;;
            "node_old:"*)
                local version=$(echo "$line" | cut -d':' -f2)
                echo "   Node.js: ${YELLOW}$version (upgrade recommended)${NC}"
                ;;
            "node_missing")
                echo "   Node.js: ${RED}Not installed${NC}"
                ;;
            "server_files_ok")
                echo "   Server Files: ${GREEN}OK${NC}"
                ;;
            "server_files_missing")
                echo "   Server Files: ${RED}Missing${NC}"
                ;;
            "server_dir_missing")
                echo "   Server Directory: ${RED}Missing${NC}"
                ;;
            "dependencies_ok")
                echo "   Dependencies: ${GREEN}Installed${NC}"
                ;;
            "dependencies_missing")
                echo "   Dependencies: ${RED}Missing (run 'npm install')${NC}"
                ;;
            "env_file_ok")
                echo "   Environment File: ${GREEN}Present${NC}"
                ;;
            "env_file_missing")
                echo "   Environment File: ${RED}Missing (copy .env.example to .env)${NC}"
                ;;
        esac
    done <<< "$prereq_output"
    echo
    
    # Docker Services
    info "🐳 Docker Services:"
    local docker_info=$(check_docker_services)
    local docker_status=$(echo "$docker_info" | cut -d':' -f1)
    local db_dev=$(echo "$docker_info" | cut -d':' -f2)
    local db_test=$(echo "$docker_info" | cut -d':' -f3)
    
    case "$docker_status" in
        "available")
            echo "   Docker: ${GREEN}Available${NC}"
            ;;
        "no_compose_file")
            echo "   Docker: ${YELLOW}Available (no docker-compose.yml)${NC}"
            ;;
        "not_available")
            echo "   Docker: ${RED}Not available${NC}"
            ;;
    esac
    
    if [ "$docker_status" = "available" ]; then
        case "$db_dev" in
            "running")
                echo "   Dev Database: ${GREEN}Running${NC}"
                ;;
            "stopped")
                echo "   Dev Database: ${RED}Stopped${NC}"
                ;;
            "not_configured")
                echo "   Dev Database: ${YELLOW}Not configured${NC}"
                ;;
        esac
        
        case "$db_test" in
            "running")
                echo "   Test Database: ${GREEN}Running${NC}"
                ;;
            "stopped")
                echo "   Test Database: ${RED}Stopped${NC}"
                ;;
            "not_configured")
                echo "   Test Database: ${YELLOW}Not configured${NC}"
                ;;
        esac
    fi
    echo
    
    # Database Connections
    info "🔌 Database Connections:"
    local db_connections=$(test_database_connections)
    local dev_conn=$(echo "$db_connections" | cut -d':' -f1)
    local test_conn=$(echo "$db_connections" | cut -d':' -f2)
    
    case "$dev_conn" in
        "connected")
            echo "   Development DB: ${GREEN}Connected${NC}"
            ;;
        "failed")
            echo "   Development DB: ${RED}Connection Failed${NC}"
            ;;
        "unknown")
            echo "   Development DB: ${YELLOW}Unknown${NC}"
            ;;
    esac
    
    case "$test_conn" in
        "connected")
            echo "   Test DB: ${GREEN}Connected${NC}"
            ;;
        "failed")
            echo "   Test DB: ${RED}Connection Failed${NC}"
            ;;
        "unknown")
            echo "   Test DB: ${YELLOW}Unknown${NC}"
            ;;
    esac
    echo
    
    # Log Information
    info "📝 Log Information:"
    local log_info=$(get_log_info)
    local log_exists=$(echo "$log_info" | cut -d':' -f1)
    
    if [ "$log_exists" = "exists" ]; then
        local log_size=$(echo "$log_info" | cut -d':' -f2)
        local line_count=$(echo "$log_info" | cut -d':' -f3)
        local last_modified=$(echo "$log_info" | cut -d':' -f4)
        
        echo "   Log File: ${GREEN}$LOGFILE${NC}"
        echo "   Size: $log_size ($line_count lines)"
        echo "   Last Modified: $last_modified"
        
        # Show last few log entries if available
        if [ -s "$LOGFILE" ]; then
            echo "   Recent entries:"
            tail -n 3 "$LOGFILE" 2>/dev/null | sed 's/^/     /' || echo "     (Unable to read recent entries)"
        fi
    else
        echo "   Log File: ${YELLOW}Not found${NC}"
    fi
    echo
    
    # File Locations
    info "📁 File Locations:"
    echo "   Project Root: $PROJECT_ROOT"
    echo "   MCP Server Directory: $MCP_SERVER_DIR"
    echo "   Log File: $LOGFILE"
    echo "   PID File: $PIDFILE"
}

show_json_status() {
    local server_info=($(get_server_info))
    local status="${server_info[0]}"
    local pid="${server_info[1]}"
    local start_time="${server_info[2]}"
    local mem="${server_info[3]}"
    local cpu="${server_info[4]}"
    local db_mode="${server_info[5]}"
    
    local prereq_issues
    check_prerequisites > /dev/null
    prereq_issues=$?
    
    local docker_info=$(check_docker_services)
    local docker_status=$(echo "$docker_info" | cut -d':' -f1)
    local db_dev=$(echo "$docker_info" | cut -d':' -f2)
    local db_test=$(echo "$docker_info" | cut -d':' -f3)
    
    local log_info=$(get_log_info)
    local log_exists=$(echo "$log_info" | cut -d':' -f1)
    local log_size=$(echo "$log_info" | cut -d':' -f2)
    local line_count=$(echo "$log_info" | cut -d':' -f3)
    
    local db_connections=$(test_database_connections)
    local dev_conn=$(echo "$db_connections" | cut -d':' -f1)
    local test_conn=$(echo "$db_connections" | cut -d':' -f2)
    
    cat << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "server": {
    "status": "$status",
    "pid": "$pid",
    "database_mode": "$db_mode",
    "start_time": "$start_time",
    "memory_percent": "$mem",
    "cpu_percent": "$cpu"
  },
  "prerequisites": {
    "issues": $prereq_issues,
    "all_ok": $([ $prereq_issues -eq 0 ] && echo "true" || echo "false")
  },
  "docker": {
    "status": "$docker_status",
    "development_db": "$db_dev",
    "test_db": "$db_test"
  },
  "database_connections": {
    "development": "$dev_conn",
    "test": "$test_conn"
  },
  "logs": {
    "exists": $([ "$log_exists" = "exists" ] && echo "true" || echo "false"),
    "size": "$log_size",
    "line_count": "$line_count"
  },
  "paths": {
    "project_root": "$PROJECT_ROOT",
    "server_directory": "$MCP_SERVER_DIR",
    "log_file": "$LOGFILE",
    "pid_file": "$PIDFILE"
  }
}
EOF
}

watch_status() {
    local interval="${1:-5}"
    
    log "Watching MCP server status (refresh every ${interval}s, Press Ctrl+C to stop)..."
    echo
    
    while true; do
        clear
        show_basic_status
        echo
        echo -e "${YELLOW}Next refresh in ${interval}s...${NC}"
        sleep "$interval"
    done
}

# Parse command line arguments
ACTION="basic"
INTERVAL="5"

while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            ACTION="verbose"
            shift
            ;;
        --json)
            ACTION="json"
            shift
            ;;
        --watch|-w)
            ACTION="watch"
            if [[ $2 =~ ^[0-9]+$ ]]; then
                INTERVAL="$2"
                shift
            fi
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
    case "$ACTION" in
        "basic")
            show_basic_status
            ;;
        "verbose")
            show_verbose_status
            ;;
        "json")
            show_json_status
            ;;
        "watch")
            watch_status "$INTERVAL"
            ;;
        *)
            error "Unknown action: $ACTION"
            exit 1
            ;;
    esac
}

# Handle Ctrl+C gracefully when watching
trap 'echo -e "\n${GREEN}Status monitoring stopped${NC}"; exit 0' SIGINT SIGTERM

# Run main function
main "$@"