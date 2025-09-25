# Docker Commands Reference (`bin/dc`)

## Quick Start
| Command | Use Case |
|---------|----------|
| `bin/dc/build` | First-time setup or after code changes |
| `bin/dc/up` | Start full development environment |
| `bin/dc/down` | Stop all services |
| `bin/dc/list` | Check what's running |

## Development Workflows

### Full Stack Development
```bash
bin/dc/build                    # Build all containers
bin/dc/up                       # Start everything (Ctrl+C to stop)
```

### Service-Specific Development
```bash
bin/dc/billing/up               # Legacy billing app only
bin/dc/connect/up               # Connect service only  
bin/dc/login/up                 # Login service only
bin/dc/cuport/up                # Customer portal
bin/dc/paylib/up                # Payment library
```

### Debugging & Console Access
```bash
bin/dc/billing/web/rails-console    # Rails console for billing
bin/dc/billing/web/bash-console     # Shell access to billing
bin/dc/connect/console              # Connect service console
bin/dc/login/rails-console          # Login service Rails console
```

### Testing
```bash
bin/dc/billing/web/spec         # Run billing tests
bin/dc/connect/spec             # Run connect tests
bin/dc/login/spec               # Run login tests
```

### Maintenance
```bash
bin/dc/list                     # See running containers
bin/dc/dfht                     # Clean up + show disk usage
bin/dc/down                     # Stop everything
bin/dc/build --no-cache         # Force clean rebuild
```

## Common Scenarios

**Starting fresh after git pull:**
```bash
bin/dc/down && bin/dc/build && bin/dc/up
```

**Just working on billing:**
```bash
bin/dc/billing/up
# In another terminal: bin/dc/billing/web/rails-console
```

**Debugging payment issues:**
```bash
bin/dc/paylib/up
bin/dc/paylib/console
```

**Running tests:**
```bash
bin/dc/billing/web/spec
```

**System cleanup:**
```bash
bin/dc/dfht    # Clean up Docker resources
```