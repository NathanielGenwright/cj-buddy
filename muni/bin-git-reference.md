# Git Multi-Repo Reference (`bin/git`)

## Quick Start
| Command | Use Case |
|---------|----------|
| `bin/git/show-branches` | See current branch in all repos |
| `bin/git/pull-all` | Pull latest changes in all repos |
| `bin/git/reset-all` | ⚠️ Reset all repos to pristine state |
| `bin/git/overwrite-branch` | ⚠️ Overwrite one branch with another |

## Multi-Repository Management

### Status & Information
```bash
bin/git/show-branches                   # Current branch in each repo
```

### Safe Operations
```bash
bin/git/pull-all                        # Pull all repositories
```

### Destructive Operations (⚠️ Use with caution)
```bash
bin/git/reset-all                       # Reset ALL repos to match remote
                                        # ⚠️ Loses ALL local changes

bin/git/overwrite-branch [repo] [target] [source]
# Example: bin/git/overwrite-branch muni-billing/legacy staging main
```

## Common Workflows

### Daily Sync
```bash
bin/git/show-branches                   # Check current state
bin/git/pull-all                        # Get latest changes
```

### Fresh Start (Emergency Reset)
```bash
bin/git/reset-all                       # ⚠️ Nuclear option
# Confirms before proceeding
# Resets ALL repos to pristine remote state
```

### Branch Management
```bash
# Overwrite staging with main in billing repo
bin/git/overwrite-branch muni-billing/legacy staging main

# What this does:
# 1. Confirms with user (shows warnings about data loss)
# 2. Switches to trunk branch
# 3. Deletes local copies of source/target branches
# 4. Fetches latest remote changes
# 5. Creates fresh target branch from source
# 6. Force pushes to remote
# 7. Adds earmark commit for CI branches
```

## Safety Features

### User Confirmations
- `reset-all` requires explicit confirmation
- `overwrite-branch` shows multiple warnings about data loss
- Both operations clearly state what will be lost

### Automatic Cleanup
- Aborts ongoing merges/rebases before reset
- Cleans untracked files
- Handles CI branch earmarking to keep PRs open

## Use Cases

**Morning sync across all projects:**
```bash
bin/git/show-branches && bin/git/pull-all
```

**Deploy staging from main:**
```bash
bin/git/overwrite-branch muni-billing/legacy staging main
```

**Complete environment reset:**
```bash
bin/git/reset-all  # ⚠️ Loses all local work
```

**Check what branches you're on:**
```bash
bin/git/show-branches
```

## ⚠️ Important Warnings
- `reset-all` destroys ALL local changes across ALL repositories
- `overwrite-branch` permanently overwrites target branch content
- Both operations cannot be undone
- Always commit/stash important work before using these tools
- Production-level operations - confirm you understand the consequences