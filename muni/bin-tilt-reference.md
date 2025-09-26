# Tilt Development Reference (`bin/tilt`)

## Quick Start
| Command | Use Case |
|---------|----------|
| `bin/tilt/up` | Start Tilt development environment |

## Tilt Development Environment

Tilt is a development tool that provides live updates and hot reloading for Kubernetes development. The Muni project uses Tilt as an alternative to Docker Compose for certain development workflows.

### Start Tilt Environment
```bash
bin/tilt/up                             # Start Tilt with live reload
```

### What Happens When You Run `bin/tilt/up`

1. **Stack Preparation**: Prepares the current development stack
2. **Mode Switch**: Switches from Docker Compose to Tilt mode
3. **Fresh Start**: Ensures clean Tilt environment
4. **Tilt Launch**: Runs `tilt up` command

## How Tilt Works

- **Live Reload**: Automatically rebuilds and redeploys on code changes
- **Kubernetes**: Runs services in local Kubernetes instead of Docker Compose
- **Web UI**: Provides web interface for monitoring services and logs
- **Hot Updates**: Fast incremental updates without full rebuilds

## Tilt vs Docker Compose

| Feature | Docker Compose (`bin/dc/up`) | Tilt (`bin/tilt/up`) |
|---------|------------------------------|---------------------|
| **Speed** | Full rebuilds on changes | Incremental hot updates |
| **Environment** | Docker containers | Local Kubernetes |
| **Monitoring** | Command line logs | Web UI dashboard |
| **Complexity** | Simpler setup | More advanced tooling |
| **Use Case** | General development | Kubernetes-focused dev |

## When to Use Tilt

### Ideal for:
- Kubernetes development and testing
- Services that benefit from hot reloading
- Complex microservice architectures
- When you need fast iteration cycles

### Use Docker Compose when:
- Simple service development
- Database-heavy development
- Traditional web application work
- Learning the system basics

## Common Workflows

### Kubernetes Development
```bash
# Switch to Tilt for K8s development
bin/tilt/up

# Monitor services in web UI (usually http://localhost:10350)
# Code changes trigger automatic rebuilds and redeployments
```

### Switch Between Environments
```bash
# From Docker Compose to Tilt
bin/dc/down                             # Stop Docker services
bin/tilt/up                             # Start Tilt environment

# From Tilt back to Docker
# Ctrl+C to stop Tilt
bin/dc/up                               # Start Docker services
```

## Tilt Web Interface

When Tilt is running:
- Access web UI at `http://localhost:10350` (default)
- Monitor service status and logs
- See build progress and errors
- Trigger manual rebuilds if needed

## Stack Integration

Tilt respects the current development stack:
```bash
bin/stacks/set billing                  # Configure for billing work
bin/tilt/up                             # Start Tilt with billing stack
```

## Prerequisites

- Tilt installed on your system
- Local Kubernetes cluster (Docker Desktop, minikube, etc.)
- Current development stack configured
- Tiltfile present in project root

## Important Notes

- Tilt runs in foreground - Ctrl+C to stop
- Web UI provides better monitoring than command line
- Hot reloading speeds up development iteration
- Requires Kubernetes understanding for advanced usage
- Stack configuration affects which services are loaded

## Troubleshooting

### Tilt Won't Start
- Ensure Kubernetes is running
- Check if Tiltfile exists
- Verify current stack is set

### Services Not Updating
- Check Tilt web UI for errors
- Ensure file watching is working
- Verify Tiltfile configuration

### Port Conflicts
- Stop other development environments
- Check for conflicting Docker services
- Review port mappings in Tiltfile