# OpenRAN Docker Workflow

A comprehensive Docker-based workflow for running OpenRAN components, inspired by OpenRAN Gym and the Colosseum Near-RT RIC implementation.

## Architecture

This Docker workflow implements a complete OpenRAN environment with the following components:

### Core Components
- **Near-RT RIC (Near Real-Time RIC)**: 
  - **E2 Termination**: Official O-RAN SC image for E2 interface handling
  - **E2 Manager**: Official O-RAN SC image for E2 connection management
  - **Routing Manager**: Official O-RAN SC image for message routing
- **xApp Framework**: Alpine-based lightweight xApp for AI/ML applications
- **RAN Simulator**: Alpine-based gNB simulator for testing

### Supporting Services
- **Redis**: Alpine-based Redis database for Near-RT RIC
- **Prometheus**: Metrics collection and monitoring
- **Grafana**: Visualization and dashboards
- **Elasticsearch**: Log storage and search
- **Kibana**: Log visualization and analysis

### Optimization Features
- **Official O-RAN SC Images**: Production-ready Near-RT RIC components
- **Alpine Linux**: Minimal base images (~7MB vs ~72MB Ubuntu)
- **Multi-stage Builds**: Separate build and runtime environments
- **Security**: Non-root users and minimal attack surface
- **Size Reduction**: ~60-70% smaller total image size

### Network Architecture
- **E2 Network**: Communication between RAN nodes and Near-RT RIC
- **Internal Network**: Inter-service communication and monitoring

## Prerequisites

- Docker Engine (version 20.10 or higher)
- Docker Compose (version 1.29 or higher)
- At least 8GB RAM and 20GB disk space

## Quick Start

### 1. Build the Environment

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Build all Docker images and create configuration files
./scripts/build.sh
```

### 2. Start Services

```bash
# Start all OpenRAN services
./scripts/start.sh

# Check service status
./scripts/start.sh --status

# View access URLs
./scripts/start.sh --urls
```

### 3. Access the Environment

Once all services are running, you can access:

- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Kibana Dashboard**: http://localhost:5601
- **Prometheus**: http://localhost:9090
- **Sample xApp API**: http://localhost:8080
- **E2 Manager API**: http://localhost:3800

### 4. View Logs

```bash
# View logs for a specific service
./scripts/logs.sh nearrt-ric

# Follow logs in real-time
./scripts/logs.sh -f sample-xapp

# View logs for all services
./scripts/logs.sh -a

# Monitor service status
./scripts/logs.sh -m
```

### 5. Stop Services

```bash
# Stop all services gracefully
./scripts/stop.sh

# Stop and remove containers
./scripts/stop.sh --remove-containers

# Remove everything (containers, volumes, networks, images)
./scripts/stop.sh --remove-all
```

## Service Details

### Near-RT RIC Components

#### E2 Termination (e2term)
- **Image**: Official O-RAN SC ric-plt-e2:1.0.0
- **Function**: E2 interface handling and message processing
- **Ports**: 36421, 36422

#### E2 Manager (e2mgr)
- **Image**: Official O-RAN SC ric-plt-e2mgr:5.4.0
- **Function**: E2 connection management and node registration
- **Ports**: 3800 (HTTP API)

#### Routing Manager (rtmgr)
- **Image**: Official O-RAN SC ric-plt-rtmgr:0.8.0
- **Function**: Message routing and service discovery
- **Ports**: 4561 (RMR routing)


### Sample xApp (sample-xapp)

- **Image**: Alpine-based multi-stage build
- **Function**: AI/ML xApp for RAN control and optimization
- **Features**:
  - E2 message handling
  - RIC subscription management
  - Control message generation
  - Lightweight Alpine runtime (~200MB vs ~1.5GB)
- **Ports**: 4560 (xApp communication), 8080 (HTTP API)

### RAN Simulator (ran-simulator)

- **Image**: Alpine-based multi-stage build
- **Function**: gNB simulator for testing E2 interface
- **Features**:
  - E2 interface implementation
  - UE and cell simulation
  - Performance metrics generation
  - Lightweight Alpine runtime (~300MB vs ~1.5GB)
- **Ports**: 36421, 36422 (E2 interface)

## Configuration

### Near-RT RIC Configuration

Edit `config/nearrt-ric/ric-plt-e2.conf`:

```ini
ric_host = "0.0.0.0"
ric_port = 36421
log_level = "INFO"
db_host = "redis"
db_port = 6379
```


### xApp Configuration

Edit `xapp/config/config.json`:

```json
{
  "xapp_name": "sample-xapp",
  "version": "1.0.0",
  "messaging": {
    "ports": [
      {
        "name": "rmr-data",
        "port": 4560,
        "rxMessages": ["RIC_SUB_RESP", "RIC_INDICATION"],
        "txMessages": ["RIC_SUB_REQ", "RIC_CONTROL_REQ"]
      }
    ]
  }
}
```

## Development

### Adding New xApps

1. Create xApp source code in `xapp/src/`
2. Update `xapp/config/config.json` with xApp details
3. Rebuild the xApp container: `docker compose build sample-xapp`
4. Restart the xApp service: `docker compose restart sample-xapp`

### Custom RAN Scenarios

1. Create scenario configurations in `ran-sim/config/`
2. Update `ran-sim/config/e2sim.conf` with scenario parameters
3. Rebuild the RAN simulator: `docker compose build ran-simulator`
4. Restart the simulator: `docker compose restart ran-simulator`

### Monitoring and Logging

The environment includes comprehensive monitoring:

- **Prometheus**: Collects metrics from all services
- **Grafana**: Provides visualization dashboards
- **Elasticsearch**: Stores and indexes logs
- **Kibana**: Provides log analysis and visualization

## Troubleshooting

### Common Issues

1. **Services not starting**: Check Docker resources and port availability
2. **Health checks failing**: Verify service dependencies and configuration
3. **Network connectivity**: Ensure Docker networks are properly configured
4. **Build failures**: Check Docker images and build dependencies

### Debugging Commands

```bash
# Check service status
docker compose ps

# View service logs
docker compose logs [service-name]

# Access service shell
docker compose exec [service-name] /bin/bash

# Check network connectivity
docker compose exec nearrt-ric ping sample-xapp

# View container resource usage
docker stats
```

### Performance Tuning

1. **Resource Allocation**: Adjust Docker resource limits in `docker compose.yml`
2. **Network Optimization**: Configure Docker network settings
3. **Storage Optimization**: Use volume mounts for persistent data
4. **Monitoring**: Use Prometheus metrics to identify bottlenecks

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is based on OpenRAN Gym and follows the same licensing terms.

## References

- [OpenRAN Gym](https://openrangym.com/)
- [Colosseum Near-RT RIC](https://github.com/wineslab/colosseum-near-rt-ric)
- [O-RAN Software Community](https://www.o-ran.org/)
- [OpenRAN Gym Paper](https://arxiv.org/abs/2207.12362)