# Cloud SQL Proxy Reference (`bin/csp`)

## Quick Start
| Command | Use Case |
|---------|----------|
| `source bin/csp/dev/refresh-token` | Get fresh auth token |
| `bin/csp/dev/instance start` | Start dev database |
| `bin/csp/dev/run-from-docker` | Connect to dev DB |
| `bin/csp/dev/instance stop` | Stop dev database (save costs) |

## Daily Development Workflow

### Morning Setup
```bash
source bin/csp/dev/refresh-token        # Fresh 12-hour token
bin/csp/dev/instance status             # Check if running
bin/csp/dev/instance start              # Start if needed
bin/csp/dev/run-from-docker            # Connect proxy
```

### Evening Cleanup
```bash
bin/csp/dev/instance stop               # Stop to save costs
```

## Instance Management

### Status & Info
```bash
bin/csp/dev/instance status             # Running/stopped status
bin/csp/dev/instance ip                 # Get instance IP
bin/csp/dev/show-expiration            # Time until auto-deletion
```

### Lifecycle Operations
```bash
bin/csp/dev/instance start              # Start instance
bin/csp/dev/instance stop               # Stop instance
bin/csp/dev/extend-expiration          # Add 14 days before deletion
```

### Set Custom Expiration
```bash
bin/csp/dev/instance expires 2024-12-31 11:59 PM
```

## Database Connections

### Development Database
```bash
# Via Docker (recommended)
bin/csp/dev/run-from-docker

# Direct on host
bin/csp/dev/run-from-host
```

### Production Read-Only Access
```bash
# Production replica
bin/csp/prod/replica/run-from-docker

# Staging replica  
bin/csp/staging/replica/run-from-host
```

## Common Scenarios

**First time setup:**
```bash
source bin/csp/dev/refresh-token
bin/csp/dev/instance start
bin/csp/dev/run-from-docker
```

**Token expired (12hr limit):**
```bash
source bin/csp/dev/refresh-token
# Restart proxy if needed
```

**Instance about to expire:**
```bash
bin/csp/dev/show-expiration
bin/csp/dev/extend-expiration          # +14 days
```

**Production data analysis:**
```bash
bin/csp/prod/replica/run-from-docker   # Read-only access
```

**Weekend/holiday shutdown:**
```bash
bin/csp/dev/instance stop              # Save on hosting costs
```

## Environment Variables Required
- `BDBDEV_PROJECT` - Google Cloud project
- `BDBDEV_INSTANCE_NAME` - SQL instance name
- `BDBDEV_IAM_ACCOUNT` - Service account
- `BDBDEV_PORT` - Local proxy port
- `BDBPROD_REPLICA_PORT` - Production replica port

## Important Notes
- Tokens expire every 12 hours
- Dev instances auto-delete after expiration date
- Always `source` the refresh-token script
- Production access is read-only via replicas
- Stop dev instances when not in use to save costs