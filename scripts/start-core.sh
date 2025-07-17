#!/bin/bash

# OpenRAN Core Services Start Script
# Starts only the core OpenRAN services without monitoring

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

echo -e "${GREEN}Starting OpenRAN Core Services${NC}"
echo "Project Directory: $PROJECT_DIR"

# Change to project directory
cd "$PROJECT_DIR"

# Start core OpenRAN services
echo -e "${YELLOW}Starting core OpenRAN services...${NC}"
docker compose up -d redis e2term e2mgr rtmgr sample-xapp ran-simulator

echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 10

# Display service status
echo -e "${BLUE}Service Status:${NC}"
docker compose ps

echo ""
echo -e "${BLUE}Service Logs (last 5 lines each):${NC}"
for service in redis e2term e2mgr rtmgr sample-xapp ran-simulator; do
    echo -e "${YELLOW}=== $service ===${NC}"
    docker compose logs --tail=5 $service
    echo ""
done

echo -e "${BLUE}Access URLs:${NC}"
echo "  E2 Manager API: http://localhost:3800"
echo "  E2 Termination: localhost:36421"
echo "  Sample xApp API: http://localhost:8080"
echo "  Redis: localhost:6379"
echo "  Routing Manager: localhost:4561"
echo ""

echo -e "${BLUE}Useful Commands:${NC}"
echo "  View logs: docker compose logs -f [service-name]"
echo "  Stop services: docker compose down"
echo "  Service status: docker compose ps"
echo ""

echo -e "${GREEN}OpenRAN Core Services are running!${NC}"