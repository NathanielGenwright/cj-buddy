# Claude Project Context

## Release Notes & Documentation Best Practices

### MBSaas Release Management
- **Primary Project**: MBSaas (project key for JIRA searches)
- **Standard Release Naming**: Use format like "7.10.0" for fix versions
- **Release Notes Tool**: `./cj-release TICKET-ID` generates professional release notes
- **Batch Processing**: Can process multiple tickets efficiently, but watch for timeouts on large batches

### Release Notes Strategy
1. **Group Related Tickets**: Identify relationships between tickets (aim for 75%+ confidence)
2. **Positive Framing**: Present fixes as improvements and enhancements rather than just bug fixes
3. **Business Value Focus**: Emphasize customer experience and system reliability benefits
4. **Technical Context**: Include architectural changes and new tools for stakeholders

### Common MBSaas Release Categories
- **Payment Processing**: Core focus area with Paya/Heartland gateway integrations
- **Customer Portal**: Multi-version support (v1, v2, v3) with version management
- **Convenience Fees**: Complex split-transaction processing (base amount + fees)
- **Admin Tools**: DevOps utilities like "Charge Explorer" for troubleshooting
- **Infrastructure**: Authentication, monitoring, deployment improvements

## JIRA Query Best Practices

When running ACLI JIRA queries that may return large result sets:

1. **Always verify counts first**: Use `--count` flag to get the exact number of results before fetching detailed data
2. **Handle truncation**: JSON responses may be truncated due to length limits. If you expect more results than shown, increase the `--limit` parameter
3. **Measure twice, cut once**: When results seem incomplete or truncated (look for `... [X lines truncated] ...`), run the count command to verify total results and adjust limit accordingly

### Example workflow:
```bash
# First get the count
acli jira workitem search --jql "your query here" --count

# Then fetch with appropriate limit
acli jira workitem search --jql "your query here" --limit 20 --json

# For release-specific searches
acli jira workitem search --jql "project = MBSaas AND fixVersion = 7.10.0" --count
```

### Useful JQL Patterns
```bash
# Payment-related issues
"project = MBSaas AND (summary ~ 'payment' OR summary ~ 'convenience fee' OR summary ~ 'Paya' OR summary ~ 'Heartland')"

# Customer Portal issues  
"project = MBSaas AND summary ~ 'Customer Portal'"

# Issues by status
"project = MBSaas AND fixVersion = X.X.X AND status in ('Ready for Acceptance', 'QA In Progress')"
```

This prevents reporting incorrect numbers due to truncated responses.

## JIRA Environment
- Base URL: https://jiramb.atlassian.net
- Email: nathaniel@Munibilling.com
- ACLI is configured and authenticated
- MCP JIRA integration available for direct API access

## MBSaas 7.10.0 Release Context

### Major Release Themes
**Payment Processing Modernization**: 
- Core architecture overhaul with new "Purchasers" framework (SAAS-1354)
- Enhanced split transaction handling for convenience fees
- Paya gateway health monitoring (complementing existing Heartland)
- Proactive error handling and user-friendly messaging

**Customer Portal Evolution**:
- Smart version redirect system (SAAS-536) 
- Complete portal disable option (SAAS-1193)
- Enhanced self-service capabilities (PDF bills, guest payments, service requests)
- Multi-account switching and improved payment history

### Key Technical Improvements
- **Charge Explorer**: New admin diagnostic tool for payment troubleshooting
- **Gateway Health Checks**: Real-time status for both Paya and Heartland
- **Performance Optimizations**: 90-day Remote Charges, 18-month payment history
- **International Support**: Enhanced billing address handling

### Ticket Relationship Patterns Identified
1. **Core Payment Issues**: SAAS-1354 → SAAS-1768, 1706, 1725 (direct dependencies)
2. **Convenience Fee Cluster**: SAAS-1354, 1768, 1858, 2165 (related processing)
3. **Portal Display Issues**: SAAS-1705, 1751, 1951, 1952 (UI/history fixes)
4. **Customer Portal Features**: SAAS-1888, 1889, 1890, 1891, 1892 (new capabilities)

### Release Notes Lessons Learned
- Always deep-dive into ticket comments to understand relationships
- Group tickets by business impact rather than just technical similarity  
- Present improvements positively (enhanced reliability vs. fixed bugs)
- Include business value and customer experience benefits
- Document new admin tools and their intended usage

## Jobs System Documentation

### Overview
The Muni Billing system uses a multi-layered job processing architecture for background tasks. Full documentation is available at: `docs/jobs_system_guide.md`

### Key Job Interfaces
- **Main Jobs Dashboard**: `/jobs` - Unified view of all background processing systems
- **Sidekiq Web Interface**: `/jobs/sidekiq` - Redis-based job monitoring with Pro features
- **Active Jobs Monitor**: `/jobs/sidekiq/busy` - Real-time view of currently executing jobs

### Job Processing Systems
- **Delayed::Job** - Legacy Rails background job system
- **Sidekiq v5.2.10** - Modern Redis-based job processor
- **Sidekiq Pro v4.0.5** - Enhanced features (batches, metrics, morgue)
- **BillingJob** - Custom billing system job management (29 job types)
- **Jasper Reports** - Report generation server

### Critical Scheduled Jobs (20+ automated jobs)
**Payment Processing:**
- Recurring payments (daily 8 PM)
- Heartland IVR processing (multiple daily)
- Auto payment reconciliation (daily 12:45 AM)

**Customer Communications:**
- Late notice generation (daily 12 PM)
- Payment reminders (daily 2 PM) 
- Leak detection alerts (daily 1 PM)

**Data Management:**
- Meter reading imports (every 2 hours)
- Customer aging updates (daily 1:57 AM)
- Reporting table generation (hourly)

**Water Smart Integration:**
- Autopay exports (daily 11:40 PM)
- Nightly data exports (daily 11:45 PM)

### Queue Management
**Default Queue**: `default_rails5` (primary Sidekiq queue)
**Queue Operations:**
- Clear stuck/failed jobs via `/jobs` interface
- Monitor queue depth and latency
- Pause/unpause processing as needed

### Monitoring Best Practices
1. **Morning Health Check**: Verify overnight scheduled jobs completed
2. **Queue Monitoring**: Watch for failed jobs and high latency
3. **Performance Tracking**: Monitor job processing rates and worker utilization
4. **Error Analysis**: Review failed job patterns and retry queues

### Performance Indicators
- **Green (Normal)**: 0-30 seconds for quick operations
- **Yellow (Watch)**: 5-15 minutes for large operations
- **Red (Concern)**: 15+ minutes or stuck jobs

### Access Requirements
- Admin authentication required (`AdminRequestAuthenticator`)
- Custom Sidekiq layout with inlined assets for production load balancers
- SSL Redis connections in production environments

### Configuration Files
- `config/schedule.yml` - Scheduled job definitions
- `config/initializers/sidekiq.rb` - Sidekiq configuration
- `app/models/billing_job_type.rb` - Job type constants (29 types)
- `app/controllers/jobs_controller.rb` - Main jobs interface

## MBSaas Release Management Tools & Context

### cj-release Tool Usage
- **Standard Command**: `./cj-release TICKET-ID`
- **Batch Processing**: Use loops but watch for 2-minute timeouts
- **Auto-approval**: Tool auto-approves in non-interactive environments
- **Output Location**: Saves to JIRA "Instructions/Operational Notes" field

### Common Release Workflows
1. **Identify Release Scope**: `acli jira workitem search --jql "project = MBSaas AND fixVersion = X.X.X" --count`
2. **Analyze Relationships**: Deep-dive into ticket descriptions and comments
3. **Generate Individual Notes**: Use cj-release for each ticket
4. **Compile Comprehensive**: Create executive summary with business value
5. **Update Documentation**: Add lessons learned to CLAUDE.md

### Payment System Context
- **Paya/Heartland**: Primary payment gateways with health monitoring
- **Convenience Fees**: Complex split-transaction processing (base + fee)
- **Charge Explorer**: Admin tool for payment troubleshooting
- **Gateway Health**: Hourly status updates with intelligent UI responses

### Customer Portal Versions
- **Portal v1, v2, v3**: Multiple versions with smart redirect capabilities
- **Version Management**: Companies can disable portal entirely or redirect users
- **Self-Service Features**: PDF bills, guest payments, service requests, account switching