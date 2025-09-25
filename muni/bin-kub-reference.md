# Kubernetes Reference (`bin/kub`)

## Quick Start
| Command | Use Case |
|---------|----------|
| `bin/kub/info` | Show current cluster and namespaces |
| `bin/kub/[env]/setup` | Connect to environment cluster |
| `bin/kub/[env]/login-console` | Access login service pod |

## Environment Setup

### Connect to Environments
```bash
bin/kub/alpha/setup                     # Alpha environment
bin/kub/demo/setup                      # Demo environment  
bin/kub/staging/setup                   # Staging environment
bin/kub/production/setup                # Production environment
bin/kub/zulu/setup                      # Zulu environment
```

### Check Current Status
```bash
bin/kub/info                            # Current cluster info & namespaces
```

## Service Console Access

### Login Service
```bash
bin/kub/alpha/login-console             # Alpha login service
bin/kub/demo/login-console              # Demo login service
bin/kub/staging/login-console           # Staging login service
bin/kub/production/login-console        # Production login service
bin/kub/zulu/login-console              # Zulu login service
```

### Staging-Specific Services
```bash
bin/kub/staging/billing-console         # Legacy billing console
bin/kub/staging/core-console            # Core service console
```

## Common Workflows

### Environment Switching
```bash
# Switch to staging
bin/kub/staging/setup
bin/kub/info                            # Verify connection

# Access services in staging
bin/kub/staging/login-console
bin/kub/staging/billing-console
bin/kub/staging/core-console
```

### Production Debugging
```bash
bin/kub/production/setup                # Connect to production
bin/kub/info                            # Check cluster status
bin/kub/production/login-console        # Access login service
```

### Multi-Environment Check
```bash
bin/kub/alpha/setup && bin/kub/info
bin/kub/staging/setup && bin/kub/info
bin/kub/production/setup && bin/kub/info
```

## How Console Access Works

1. **Setup** connects to the appropriate GKE cluster
2. **Console commands** find the first running pod in the namespace
3. **Execute** drops you into a bash shell inside the pod
4. **Environment** automatically sets APP_ROOT and working directory

## Prerequisites
- Tailscale connection required (`gcp_check_tailscale`)
- Appropriate GCP authentication
- kubectl configured with cluster access
- Environment variables for each cluster (project, host, cluster name)

## Available Environments
- **Alpha** - Development/testing environment
- **Demo** - Demonstration environment
- **Staging** - Pre-production testing
- **Production** - Live production environment
- **Zulu** - Additional environment

## Safety Notes
- Production access should be used carefully
- Console sessions run inside live application pods
- Changes in production console affect live services
- Always verify environment before making changes (`bin/kub/info`)