#!/bin/bash

# OpenRAN Docker Start Script
# Starts all OpenRAN services using Docker Compose

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

echo -e "${GREEN}Starting OpenRAN Docker Services${NC}"
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

# Function to check if docker compose is available
check_docker_compose() {
    if ! docker compose version &> /dev/null; then
        echo -e "${RED}docker compose is not available. Please install Docker Compose v2.${NC}"
        exit 1
    fi
}

# Function to start services in order
start_services() {
    echo -e "${YELLOW}Starting core infrastructure services...${NC}"
    
    # Start Redis first
    docker compose up -d redis
    echo "Waiting for Redis to be ready..."
    sleep 5
    
    # Start Near-RT RIC components
    echo -e "${YELLOW}Starting E2 Termination...${NC}"
    docker compose up -d e2term
    echo "Waiting for E2 Termination to be ready..."
    sleep 10
    
    echo -e "${YELLOW}Starting E2 Manager...${NC}"
    docker compose up -d e2mgr
    echo "Waiting for E2 Manager to be ready..."
    sleep 10
    
    echo -e "${YELLOW}Starting Routing Manager...${NC}"
    docker compose up -d rtmgr
    echo "Waiting for Routing Manager to be ready..."
    sleep 5
    
    
    # Start xApp
    echo -e "${YELLOW}Starting Sample xApp...${NC}"
    docker compose up -d sample-xapp
    echo "Waiting for xApp to be ready..."
    sleep 5
    
    # Start RAN Simulator
    echo -e "${YELLOW}Starting RAN Simulator...${NC}"
    docker compose up -d ran-simulator
    echo "Waiting for RAN Simulator to be ready..."
    sleep 5
    
    # Start monitoring services
    echo -e "${YELLOW}Starting monitoring services...${NC}"
    docker compose up -d prometheus grafana
    echo "Waiting for monitoring services to be ready..."
    sleep 10
    
    # Start logging services
    echo -e "${YELLOW}Starting logging services...${NC}"
    docker compose up -d elasticsearch kibana
    echo "Waiting for logging services to be ready..."
    sleep 15
}

# Function to display service status
show_status() {
    echo -e "${BLUE}Service Status:${NC}"
    docker compose ps
    echo ""
    
    echo -e "${BLUE}Health Check Status:${NC}"
    docker compose ps --services | while read service; do
        health=$(docker inspect --format='{{.State.Health.Status}}' "openran-$service" 2>/dev/null || echo "no-health-check")
        if [ "$health" = "healthy" ]; then
            echo -e "  $service: ${GREEN}$health${NC}"
        elif [ "$health" = "unhealthy" ]; then
            echo -e "  $service: ${RED}$health${NC}"
        else
            echo -e "  $service: ${YELLOW}$health${NC}"
        fi
    done
}

# Function to display access URLs
show_urls() {
    echo ""
    echo -e "${BLUE}Access URLs:${NC}"
    echo "  Grafana Dashboard: http://localhost:3000 (admin/admin)"
    echo "  Kibana Dashboard: http://localhost:5601"
    echo "  Prometheus: http://localhost:9090"
    echo "  Sample xApp API: http://localhost:8080"
    echo "  E2 Manager API: http://localhost:3800"
    echo ""
}

# Function to display useful commands
show_commands() {
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  View logs: docker compose logs -f [service-name]"
    echo "  Stop all services: ./scripts/stop.sh"
    echo "  Restart service: docker compose restart [service-name]"
    echo "  View service status: docker compose ps"
    echo "  Access container shell: docker compose exec [service-name] /bin/bash"
    echo ""
}

# Main execution
main() {
    check_docker
    check_docker_compose
    
    echo -e "${YELLOW}Checking for existing services...${NC}"
    if docker compose ps -q | grep -q .; then
        echo -e "${YELLOW}Some services are already running. Stopping them first...${NC}"
        docker compose down
        sleep 5
    fi
    
    start_services
    
    echo -e "${GREEN}All OpenRAN services started successfully!${NC}"
    echo ""
    
    show_status
    show_urls
    show_commands
    
    echo -e "${GREEN}OpenRAN environment is ready for use!${NC}"
}

# Handle script arguments
case "$1" in
    --status)
        show_status
        ;;
    --urls)
        show_urls
        ;;
    --help)
        echo "Usage: $0 [--status|--urls|--help]"
        echo "  --status: Show service status"
        echo "  --urls: Show access URLs"
        echo "  --help: Show this help message"
        ;;
    *)
        main
        ;;
esac