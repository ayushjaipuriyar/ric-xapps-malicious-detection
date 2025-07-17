#!/bin/bash

# OpenRAN Docker Logs Script
# View logs from OpenRAN services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Available services
SERVICES=(
    "redis"
    "e2term"
    "e2mgr"
    "rtmgr"
    "sample-xapp"
    "ran-simulator"
    "prometheus"
    "grafana"
    "elasticsearch"
    "kibana"
)

# Change to project directory
cd "$PROJECT_DIR"

# Function to show available services
show_services() {
    echo -e "${BLUE}Available services:${NC}"
    for service in "${SERVICES[@]}"; do
        echo "  $service"
    done
    echo ""
}

# Function to show logs for a specific service
show_service_logs() {
    local service=$1
    local follow=$2
    local lines=$3
    
    if [ -z "$service" ]; then
        echo -e "${RED}Error: No service specified${NC}"
        show_usage
        exit 1
    fi
    
    # Check if service exists
    if ! printf '%s\n' "${SERVICES[@]}" | grep -q "^$service$"; then
        echo -e "${RED}Error: Service '$service' not found${NC}"
        show_services
        exit 1
    fi
    
    # Check if service is running
    if ! docker compose ps "$service" | grep -q "Up"; then
        echo -e "${YELLOW}Warning: Service '$service' is not running${NC}"
    fi
    
    echo -e "${GREEN}Showing logs for service: $service${NC}"
    
    # Build docker compose logs command
    local cmd="docker compose logs"
    
    if [ "$follow" = true ]; then
        cmd="$cmd -f"
    fi
    
    if [ -n "$lines" ]; then
        cmd="$cmd --tail=$lines"
    fi
    
    cmd="$cmd $service"
    
    # Execute command
    eval "$cmd"
}

# Function to show logs for all services
show_all_logs() {
    local follow=$1
    local lines=$2
    
    echo -e "${GREEN}Showing logs for all services${NC}"
    
    # Build docker compose logs command
    local cmd="docker compose logs"
    
    if [ "$follow" = true ]; then
        cmd="$cmd -f"
    fi
    
    if [ -n "$lines" ]; then
        cmd="$cmd --tail=$lines"
    fi
    
    # Execute command
    eval "$cmd"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [SERVICE]"
    echo ""
    echo "Options:"
    echo "  -f, --follow     Follow log output (like tail -f)"
    echo "  -n, --lines NUM  Number of lines to show from the end of the logs"
    echo "  -a, --all        Show logs for all services"
    echo "  -l, --list       List available services"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 nearrt-ric                    # Show logs for Near-RT RIC"
    echo "  $0 -f nearrt-ric                # Follow logs for Near-RT RIC"
    echo "  $0 -n 100 sample-xapp           # Show last 100 lines for xApp"
    echo "  $0 -f -n 50 ran-simulator       # Follow last 50 lines for RAN simulator"
    echo "  $0 -a                           # Show logs for all services"
    echo "  $0 -f -a                        # Follow logs for all services"
    echo ""
}

# Function to monitor all services status
monitor_services() {
    echo -e "${GREEN}Monitoring OpenRAN services (Press Ctrl+C to exit)${NC}"
    echo ""
    
    while true; do
        clear
        echo -e "${BLUE}OpenRAN Services Status - $(date)${NC}"
        echo "=========================================="
        
        for service in "${SERVICES[@]}"; do
            local status=$(docker compose ps "$service" 2>/dev/null | grep "$service" | awk '{print $4}' || echo "Not running")
            local health=$(docker inspect --format='{{.State.Health.Status}}' "openran-$service" 2>/dev/null || echo "no-health-check")
            
            if [ "$status" = "Up" ]; then
                if [ "$health" = "healthy" ]; then
                    echo -e "  $service: ${GREEN}$status ($health)${NC}"
                elif [ "$health" = "unhealthy" ]; then
                    echo -e "  $service: ${RED}$status ($health)${NC}"
                else
                    echo -e "  $service: ${YELLOW}$status ($health)${NC}"
                fi
            else
                echo -e "  $service: ${RED}$status${NC}"
            fi
        done
        
        echo ""
        echo "Press Ctrl+C to exit..."
        sleep 5
    done
}

# Parse command line arguments
FOLLOW=false
LINES=""
ALL=false
SERVICE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        -n|--lines)
            LINES="$2"
            shift 2
            ;;
        -a|--all)
            ALL=true
            shift
            ;;
        -l|--list)
            show_services
            exit 0
            ;;
        -m|--monitor)
            monitor_services
            exit 0
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        -*)
            echo -e "${RED}Error: Unknown option $1${NC}"
            show_usage
            exit 1
            ;;
        *)
            if [ -z "$SERVICE" ]; then
                SERVICE="$1"
            else
                echo -e "${RED}Error: Multiple services specified${NC}"
                show_usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Main execution
if [ "$ALL" = true ]; then
    show_all_logs "$FOLLOW" "$LINES"
elif [ -n "$SERVICE" ]; then
    show_service_logs "$SERVICE" "$FOLLOW" "$LINES"
else
    echo -e "${RED}Error: No service specified${NC}"
    show_usage
    exit 1
fi