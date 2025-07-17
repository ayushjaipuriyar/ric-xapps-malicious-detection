#!/bin/bash

# OpenRAN Docker Stop Script
# Stops all OpenRAN services using Docker Compose

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

echo -e "${YELLOW}Stopping OpenRAN Docker Services${NC}"
echo "Project Directory: $PROJECT_DIR"

# Change to project directory
cd "$PROJECT_DIR"

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}Docker is not running. Please start Docker first.${NC}"
        exit 1
    fi
}

# Function to gracefully stop services
stop_services() {
    echo -e "${YELLOW}Checking running services...${NC}"
    
    # Check if any services are running
    if ! docker compose ps -q | grep -q .; then
        echo -e "${YELLOW}No OpenRAN services are currently running.${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}Stopping services gracefully...${NC}"
    
    # Stop services in reverse order for clean shutdown
    echo "Stopping RAN Simulator..."
    docker compose stop ran-simulator 2>/dev/null || true
    
    echo "Stopping xApp..."
    docker compose stop sample-xapp 2>/dev/null || true
    
    echo "Stopping Near-RT RIC components..."
    docker compose stop rtmgr 2>/dev/null || true
    docker compose stop e2mgr 2>/dev/null || true
    docker compose stop e2term 2>/dev/null || true
    
    echo "Stopping monitoring services..."
    docker compose stop grafana prometheus 2>/dev/null || true
    
    echo "Stopping logging services..."
    docker compose stop kibana elasticsearch 2>/dev/null || true
    
    echo "Stopping Redis..."
    docker compose stop redis 2>/dev/null || true
    
    echo -e "${GREEN}All services stopped successfully.${NC}"
}

# Function to remove containers
remove_containers() {
    echo -e "${YELLOW}Removing containers...${NC}"
    docker compose down
    echo -e "${GREEN}Containers removed successfully.${NC}"
}

# Function to remove volumes
remove_volumes() {
    echo -e "${YELLOW}Removing volumes...${NC}"
    docker compose down -v
    echo -e "${GREEN}Volumes removed successfully.${NC}"
}

# Function to remove everything including images
remove_all() {
    echo -e "${YELLOW}Removing everything (containers, volumes, networks, images)...${NC}"
    docker compose down -v --rmi all
    echo -e "${GREEN}Everything removed successfully.${NC}"
}

# Function to show cleanup options
show_cleanup_options() {
    echo ""
    echo -e "${BLUE}Additional cleanup options:${NC}"
    echo "  Remove containers: ./scripts/stop.sh --remove-containers"
    echo "  Remove volumes: ./scripts/stop.sh --remove-volumes"
    echo "  Remove everything: ./scripts/stop.sh --remove-all"
    echo "  Force stop: ./scripts/stop.sh --force"
    echo ""
}

# Function to force stop all containers
force_stop() {
    echo -e "${RED}Force stopping all OpenRAN containers...${NC}"
    
    # Get all OpenRAN container IDs
    containers=$(docker ps -a --filter "name=openran" --format "{{.ID}}" 2>/dev/null || true)
    
    if [ -n "$containers" ]; then
        echo "Force stopping containers..."
        docker stop $containers 2>/dev/null || true
        docker rm $containers 2>/dev/null || true
        echo -e "${GREEN}Force stop completed.${NC}"
    else
        echo -e "${YELLOW}No OpenRAN containers found.${NC}"
    fi
}

# Function to display current status
show_status() {
    echo -e "${BLUE}Current Status:${NC}"
    if docker compose ps -q | grep -q .; then
        docker compose ps
    else
        echo "No services are currently running."
    fi
}

# Main execution
main() {
    check_docker
    stop_services
    show_cleanup_options
}

# Handle script arguments
case "$1" in
    --remove-containers)
        check_docker
        remove_containers
        ;;
    --remove-volumes)
        check_docker
        remove_volumes
        ;;
    --remove-all)
        check_docker
        remove_all
        ;;
    --force)
        check_docker
        force_stop
        ;;
    --status)
        show_status
        ;;
    --help)
        echo "Usage: $0 [--remove-containers|--remove-volumes|--remove-all|--force|--status|--help]"
        echo "  (no args): Stop all services gracefully"
        echo "  --remove-containers: Stop and remove containers"
        echo "  --remove-volumes: Stop and remove containers and volumes"
        echo "  --remove-all: Stop and remove everything including images"
        echo "  --force: Force stop all containers"
        echo "  --status: Show current service status"
        echo "  --help: Show this help message"
        ;;
    *)
        main
        ;;
esac