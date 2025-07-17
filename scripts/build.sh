#!/bin/bash

# OpenRAN Docker Build Script
# Builds all OpenRAN components using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}Starting OpenRAN Docker Build Process${NC}"
echo "Project Directory: $PROJECT_DIR"

# Change to project directory
cd "$PROJECT_DIR"

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p monitoring/{grafana/dashboards,grafana/datasources}

# Create monitoring configuration files
echo -e "${YELLOW}Creating monitoring configuration files...${NC}"

# Prometheus configuration
cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'openran-nearrt-ric'
    static_configs:
      - targets: ['nearrt-ric:9090']
  
  
  - job_name: 'openran-xapp'
    static_configs:
      - targets: ['sample-xapp:9090']
EOF

# Grafana datasource configuration
cat > monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF


# Build Docker images
echo -e "${YELLOW}Building Docker images...${NC}"

# Build images in parallel for faster build time
docker compose build --parallel

# Verify images were built successfully
echo -e "${YELLOW}Verifying built images...${NC}"
docker images | grep -E "(openran|dissertation-openran)"

echo -e "${GREEN}OpenRAN Docker build completed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Run './scripts/start.sh' to start all services"
echo "2. Run './scripts/stop.sh' to stop all services"
echo "3. Check logs with 'docker compose logs -f [service-name]'"
echo "4. Access Grafana at http://localhost:3000 (admin/admin)"
echo "5. Access Kibana at http://localhost:5601"