# Database Access Reference (`bin/bdb`)

## Quick Start
| Command | Use Case |
|---------|----------|
| `bin/bdb/dev/console` | MySQL console for dev database |
| `bin/bdb/dev/show-tables` | List all tables in dev DB |
| `bin/bdb/dev/status` | Check dev database status |

## Database Environments

### Development Database
```bash
bin/bdb/dev/console                     # Interactive MySQL console
bin/bdb/dev/show-tables                 # List all tables
bin/bdb/dev/status                      # Database server status
```

### Test Database
```bash
bin/bdb/test/console                    # Test DB console
bin/bdb/test/show-tables               # Test DB tables
bin/bdb/test/status                    # Test DB status
```

### Production Read-Only Access
```bash
bin/bdb/prod/replica/console           # Production replica console
bin/bdb/prod/replica/show-tables       # Production tables
bin/bdb/prod/replica/status            # Production status
```

### Staging Read-Only Access  
```bash
bin/bdb/staging/replica/console        # Staging replica console
bin/bdb/staging/replica/show-tables    # Staging tables
bin/bdb/staging/replica/status         # Staging status
```

## Common Workflows

### Development Database Work
```bash
# Quick table check
bin/bdb/dev/show-tables

# Interactive queries
bin/bdb/dev/console
> SELECT * FROM customers LIMIT 10;
> DESCRIBE billing_accounts;
> EXIT;
```

### Production Data Analysis
```bash
# Read-only production access
bin/bdb/prod/replica/console
> SELECT COUNT(*) FROM payments WHERE created_at > '2024-01-01';
> EXIT;
```

### Database Health Check
```bash
bin/bdb/dev/status                     # Dev environment
bin/bdb/prod/replica/status            # Production health
```

### Cross-Environment Comparison
```bash
# Compare table counts
bin/bdb/dev/show-tables | wc -l
bin/bdb/staging/replica/show-tables | wc -l
bin/bdb/prod/replica/show-tables | wc -l
```

## Prerequisites
- Cloud SQL Proxy must be running (`bin/csp/*/run-from-*`)
- Valid CSP token (`source bin/csp/dev/refresh-token`)
- Environment variables set (BDBDEV_HOST, BDBDEV_PORT, etc.)

## Safety Notes
- Production and staging access is **read-only** via replicas
- Development database is full read/write access
- Test database is isolated for testing purposes
- Always verify environment before running destructive queries

## Environment Variables Required
- `BDBDEV_HOST`, `BDBDEV_PORT`, `BDBDEV_USER`, `BDBDEV_PASS`, `BDBDEV_NAME`
- Similar variables for test, staging, and production environments