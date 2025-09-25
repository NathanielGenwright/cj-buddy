# Miscellaneous Tools Reference (`bin/misc`)

## Quick Start
| Command | Use Case |
|---------|----------|
| `bin/misc/self_service create_database 48` | Create personal dev DB (48hr TTL) |
| `bin/misc/self_service refresh_database` | Refresh dev DB with production data |
| `bin/misc/self_service extend_database_ttl 48` | Extend DB TTL by 48 hours |

## Self-Service Database Management

The `self_service` tool mimics self-service actions from Port (getport.io) IDP for database lifecycle management.

### Personal Developer Database
```bash
# Create new database with TTL
bin/misc/self_service create_database 48       # 48 hour TTL

# Refresh with production backup
bin/misc/self_service refresh_database

# Extend expiration time
bin/misc/self_service extend_database_ttl 48   # Add 48 hours

# Delete database
bin/misc/self_service delete_database
```

### Shared Developer Database
```bash
# Create shared database
bin/misc/self_service create_shared_database 48

# Refresh shared database
bin/misc/self_service refresh_shared_database

# Extend shared database TTL
bin/misc/self_service extend_shared_database_ttl 48

# Delete shared database
bin/misc/self_service delete_shared_database
```

## Common Workflows

### Start New Development Work
```bash
# Create personal dev database for 48 hours
bin/misc/self_service create_database 48
```

### Working on Team Features
```bash
# Use shared database for team collaboration
bin/misc/self_service create_shared_database 72    # 3 days
```

### Refresh with Latest Production Data
```bash
# Personal database
bin/misc/self_service refresh_database

# Shared database  
bin/misc/self_service refresh_shared_database
```

### Extend Work Session
```bash
# Need more time? Extend TTL
bin/misc/self_service extend_database_ttl 24       # Add 1 day
bin/misc/self_service extend_shared_database_ttl 48 # Add 2 days
```

### Clean Up
```bash
# Done with development work
bin/misc/self_service delete_database
bin/misc/self_service delete_shared_database
```

## How It Works

1. **Authentication**: Uses `gcloud auth print-identity-token` for identity
2. **Webhook**: Calls Port.io webhook at `https://us-central1-common-infra-401220.cloudfunctions.net/common-webhook`
3. **Security**: Signs requests with HMAC SHA256 using `SELF_SERVICE_WEBHOOK_SECRET`
4. **Actions**: Maps CLI commands to Port.io blueprint actions

## Prerequisites

- `SELF_SERVICE_WEBHOOK_SECRET` environment variable must be set
- Valid Google Cloud authentication (`gcloud auth`)
- Ruby with required gems: `jwt`, `json`, `net/https`, `openssl`

## Available Actions

| CLI Command | Port.io Action | Description |
|-------------|----------------|-------------|
| `create_database` | `create_developer_database` | Create personal dev DB |
| `create_shared_database` | `create_developer_database_shared` | Create shared dev DB |
| `delete_database` | `destroy_developer_database` | Delete personal dev DB |
| `delete_shared_database` | `destroy_developer_database` | Delete shared dev DB |
| `refresh_database` | `refresh_developer_database` | Refresh personal DB |
| `refresh_shared_database` | `refresh_developer_database` | Refresh shared DB |
| `extend_database_ttl` | `extend_ttl_of_developer_database` | Extend personal TTL |
| `extend_shared_database_ttl` | `extend_ttl_of_developer_database` | Extend shared TTL |

## Notes

- Default TTL is 2 hours if not specified
- Shared databases are for team collaboration
- Personal databases are individual developer instances
- All operations are logged and tracked through Port.io
- Database refreshes use production backups