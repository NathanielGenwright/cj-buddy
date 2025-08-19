# Changelog

## [Unreleased] - Environment Configuration Consolidation

### Added
- Shared environment configuration support for multi-project setups
- Automatic .env file detection from parent directory
- Support for both JIRA_API_TOKEN and JIRA_TOKEN for compatibility
- Support for both ANTHROPIC_API_KEY and CLAUDE_API_KEY for compatibility

### Changed
- Updated all Python modules to load .env from parent directory when available
- Fixed path issues in shell scripts (cj, cj-sum, cj-tag, cj-task, cj-test)
- Updated README.md with new configuration instructions
- Removed duplicate .env files to prevent credential duplication

### Fixed
- Corrected hardcoded paths in shell script executables
- Resolved missing rca_generator module import (temporarily disabled)

### Benefits
- Single source of truth for credentials across projects
- Easier maintenance and credential management
- Eliminates duplicate configuration files
- Supports both standalone and multi-project setups

### Migration Notes
If upgrading from a previous version:
1. Move your existing .env file to the parent directory (optional but recommended)
2. Remove duplicate .env files from project subdirectories
3. Both projects (cj-buddy and agentJ) will automatically use the shared configuration

### Technical Details
- Environment loading uses `os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')`
- Maintains backward compatibility with local .env files
- No breaking changes to existing functionality