# Development Stacks Reference (`bin/stacks`)

## Quick Start
| Command | Use Case |
|---------|----------|
| `bin/stacks/list` | Show available development stacks |
| `bin/stacks/set billing` | Switch to billing stack |
| `bin/stacks/show` | Display current active stack |
| `bin/stacks/clear` | Clear current stack selection |

## Stack Management

Development stacks are predefined configurations that set up different combinations of services for specific development scenarios.

### Available Commands
```bash
bin/stacks/list                         # List all available stacks
bin/stacks/set <stack_name>             # Activate a specific stack
bin/stacks/show                         # Show currently active stack
bin/stacks/clear                        # Deactivate current stack
```

## Common Workflows

### Switch Development Focus
```bash
# See what stacks are available
bin/stacks/list

# Switch to billing development
bin/stacks/set billing

# Verify the switch
bin/stacks/show

# Build and start the stack
bin/dc/build
bin/dc/up
```

### Stack Configuration
```bash
# Set a stack (defaults to 'billing' if no name provided)
bin/stacks/set                          # Sets 'billing' stack
bin/stacks/set payment                  # Sets 'payment' stack  
bin/stacks/set portal                   # Sets 'portal' stack
```

### Clear Active Stack
```bash
bin/stacks/clear                        # Remove current stack selection
# or
bin/stacks/set                          # Setting without parameter also clears
```

## How Stacks Work

1. **Stack Definition**: Each stack is defined in `./dev-meta/stacks/<stack_name>/`
2. **Docker Compose**: Each stack has its own `docker-compose.yml` file
3. **Setup Script**: Optional `setup` script for stack-specific configuration
4. **Activation**: `set` command copies docker-compose.yml to project root
5. **Services**: Each stack defines which services to run

## Stack Structure

```
dev-meta/stacks/
├── billing/
│   ├── docker-compose.yml      # Service definitions
│   └── setup                   # Optional setup script
├── payment/
│   ├── docker-compose.yml
│   └── setup
└── portal/
    ├── docker-compose.yml
    └── setup
```

## What `set` Does

1. **Validates** the stack name exists
2. **Copies** the stack's docker-compose.yml to project root
3. **Executes** the stack's setup script (if present)
4. **Saves** the current stack selection
5. **Displays** next steps (build and up)

## Development Scenarios

### Billing Development
```bash
bin/stacks/set billing
bin/dc/build
bin/dc/up
# Focus on legacy billing, payments, background jobs
```

### Payment Integration Work
```bash
bin/stacks/set payment
bin/dc/build
bin/dc/up
# Focus on payment processing, gateways, convenience fees
```

### Customer Portal Features
```bash
bin/stacks/set portal
bin/dc/build  
bin/dc/up
# Focus on customer-facing features, UI/UX
```

### Switch Between Stacks
```bash
bin/stacks/clear                        # Stop current work
bin/stacks/set portal                   # Switch focus
bin/dc/down                             # Stop old services
bin/dc/build                            # Build new configuration
bin/dc/up                               # Start new stack
```

## Stack Announcement

All stack commands show the current status:
- Which stack is active (if any)
- Location of active docker-compose.yml
- Next steps for building/starting services

## Integration with Docker Commands

Stacks work seamlessly with `bin/dc` commands:
```bash
bin/stacks/set billing                  # Configure stack
bin/dc/build                            # Build stack services
bin/dc/up                               # Start stack services
bin/dc/down                             # Stop stack services
```

## Best Practices

- Always check current stack: `bin/stacks/show`
- Clear before switching: `bin/stacks/clear`
- Build after switching: `bin/dc/build`
- Use stacks to focus development effort on specific areas