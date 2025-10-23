# Claude Project Context

## Release Notes & Documentation Best Practices

### MBSaas Release Management
- **Primary Project**: MBSaas (project key for JIRA searches)
- **Standard Release Naming**: Use format like "7.10.0" for fix versions
- **Release Notes Tool**: `./cj-release TICKET-ID` generates professional release notes
- **Batch Processing**: Use `./batch-cj-release.sh` for multiple tickets efficiently
  - Usage: `./batch-cj-release.sh TICKET-1 TICKET-2 TICKET-3` (custom tickets)
  - Usage: `./batch-cj-release.sh` (uses default MBSaas 7.11.0 tickets)
  - Includes error handling, progress tracking, and summary reporting

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

## TriQ (JIRA Triage Validator) System

### TriQ Agent Overview
TriQ is a comprehensive JIRA triage validation system implemented as a specialized Claude agent located at:
**`/Users/munin8/_myprojects/.claude/agents/jira-triage-validator.md`**

TriQ operates as a friendly, approachable service agent that helps internal teams self-serve their JIRA ticket quality needs. The agent maintains high validation standards while using clear, jargon-free communication and empowering users to create better tickets independently.

### Core Capabilities
- **5-Category Validation Framework**: Summary (25%), Description (35%), Technical Context (20%), Business Context (15%), Metadata (5%)
- **Enhanced Quality Scoring**: 1-10 scale with half-step increments (7.0-9.5) for granular assessment
- **MuniBilling Priority Integration**: Urgency/Impact matrix with 5-level priority system (Critical → Very Low)
- **SLA-Aware Validation**: Response time validation against business SLAs (15 min → 1 day)
- **Smart Routing**: Automatic detection of security, emergency, and feature request tickets
- **Template-Based Feedback**: Standardized responses for APPROVE, APPROVE_WITH_NOTES, NEEDS_CLARIFICATION, REQUEST_REVISION, and ROUTE_ELSEWHERE
- **Workflow Analysis**: Comprehensive assessment of ticket patterns, bottlenecks, and quality trends

### Active Projects Supported
- **Engineering Portal (EP)**: Primary validation for engineering tickets
- **TRI Project**: Triage board analysis and workflow optimization
- **MBSaas**: Release management and quality assurance integration

### Supporting Documentation
- **Agent Definition**: `/Users/munin8/_myprojects/.claude/agents/jira-triage-validator.md` (updated with MuniBilling integration)
- **Quality Rubric**: `/Users/munin8/_myprojects/jira-triage-quality-rubric.md` (enhanced with half-step scoring)
- **Validation Rules**: `/Users/munin8/_myprojects/jira-validation-rules.md` (updated with priority matrix and SLA validation)
- **Feedback Templates**: `/Users/munin8/_myprojects/jira-feedback-templates.md`
- **Operational Workflows**: `/Users/munin8/_myprojects/triq-workflows.md`
- **Monitoring Script**: `/Users/munin8/_myprojects/triq-monitor.sh`
- **Deployment Guide**: `/Users/munin8/_myprojects/triq-deployment-guide.md`
- **MuniBilling Integration Source**: `/Users/munin8/Library/CloudStorage/OneDrive-MuniBilling/_downloads/triq/Issue Classifications.docx`
- **Ideal Ticket Template**: Generated on-demand for 9+ quality scores

### Recent Analysis Reports
- **TRI Workflow Analysis**: `/Users/munin8/_myprojects/TRI_Workflow_Analysis_Report.md` (30-day comprehensive assessment)
- **Triage Board Assessment**: `/Users/munin8/_myprojects/triage-board-assessment-2025-10-02.md` (99 active tickets analyzed)

### Quick Usage Examples
- **Single Ticket Validation**: "TriQ, please validate ticket EP-XXX"
- **Priority Assessment**: "TriQ, analyze the priority classification for EP-XXX using the MuniBilling matrix"
- **Batch Validation**: "TriQ, check all new Engineering Portal tickets from today"
- **SLA Validation**: "TriQ, check for any priority/timeline mismatches in recent tickets"
- **Quality Assessment**: "TriQ, what's the quality trend for EP tickets this week?"
- **Workflow Analysis**: "TriQ, analyze TRI project tickets from the last month"
- **Triage Board Review**: "TriQ, assess tickets in TRI project where status is not in (Closed, Resolved, Send to Engineering, Pending)"
- **Backlog Validation**: "TriQ, check unvalidated tickets in 'To Do' or 'Open' status"

### Communication Style
TriQ uses a friendly, empowering approach that:
- Challenges vague requests respectfully
- Collects details systematically to avoid overwhelming users
- Uses active, direct instructions with clear examples
- Celebrates success with light humor for high-quality tickets
- Teaches users how to write better tickets independently

The TriQ agent automatically applies the comprehensive validation framework with weighted scoring and provides standardized feedback templates for consistent quality improvement across all supported JIRA projects.

### MuniBilling Issue Classifications Integration (2025-10-06)

TriQ now incorporates the proven MuniBilling framework for structured priority assessment and SLA management:

#### Priority Matrix System
- **Critical (1)**: High urgency + High impact → 15 min response, 2 hour resolution
- **High (2)**: High urgency + Medium impact OR Medium urgency + High impact → 30 min response, 1 day resolution  
- **Medium (3)**: Medium urgency + Medium impact OR Low urgency + High impact → 1 hour response, 2 days resolution
- **Low (4)**: Low urgency + Medium impact OR Medium urgency + Low impact → 4 hours response, 5 days resolution
- **Very Low (5)**: Low urgency + Low impact → 1 day response, 10 days resolution

#### Enhanced Impact Assessment
- **User Count**: Specific numbers of affected users
- **Workflow Criticality**: Impact on billing, payment, customer service processes
- **Financial Impact**: Revenue loss, transaction disruption, billing delays
- **Compliance Risk**: Regulatory, audit, legal implications
- **Operational Disruption**: System availability, process dependencies

#### Integration Benefits
- **Structured Priority Validation**: Replaces subjective assessment with proven methodology
- **SLA Awareness**: Validates timeline expectations against business requirements
- **Operational Alignment**: Integrates existing MuniBilling practices into technical validation
- **Enhanced Business Context**: More comprehensive assessment of business disruption

## TRI Project Custom Field Analysis (2025-10-13)

### CONFIRMED Custom Field Mappings
- **cf[10413]**: Company field (1,205 tickets have data)
- **cf[10450]**: Urgency field (1,244 tickets have data)
  - **Critical**: 77 tickets
  - **High**: 493 tickets  
  - **Medium**: 485 tickets
  - **Low**: 189 tickets
- **cf[10451]**: Impact field (148 tickets have data)
- **component**: Standard JIRA component field (127 tickets have data)

### Reference Ticket: TRI-1858
- **Summary**: CID 1769: Durango West Metro District: Unpost Meter Reading with end date 03/31/25
- **Confirmed Urgency**: High (cf[10450])
- **Company**: Linked to CID 1769 pattern (cf[10413])

### Analysis Assets Available
- **Enhanced Dataset**: `tri_enhanced_with_custom_fields.csv` (500 tickets with full custom field analysis)
- **Executive Report**: `TRI_Enhanced_Analysis_Report.md` (comprehensive business insights)
- **Pivot-Ready Dataset**: `tri_comprehensive_pivot_ready.csv` (1,000 tickets with business-friendly fields)
- **Field Reference**: `tri_pivot_guide.md` (complete field mapping documentation)

### Key Business Insights (Latest Analysis)
- **Dominant Category**: Payment/Billing (47.0% of tickets)
- **Top Client**: CID 1780 (11 tickets)
- **Urgency Distribution**: 493 High + 77 Critical = 570 priority tickets (45.8%)
- **Custom Field Coverage**: Company field has strongest data population

### Analysis Methodology
- **Actual Custom Field Extraction**: Successfully extracted real urgency values using ACLI
- **CID Pattern Matching**: Correlated company field with summary CID extraction
- **Business Categorization**: Payment/Billing, Meter Management, Customer Portal, Data Management
- **Priority Analysis**: Derived urgency + impact assessment for workflow optimization

### Scripts for Reanalysis
- **`create_enhanced_tri_analysis.py`**: Complete custom field analysis with actual value extraction
- **`create_lightweight_tri_export.py`**: Optimized export for pivot table analysis
- **`create_comprehensive_raw_dataset.py`**: Full field coverage analysis (comprehensive but may timeout)

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

## Project Repository Status (Updated 2025-10-22)

### Last Repository Submission
- **Most Recent Commit**: `cf46875` - September 25, 2025 
- **Commit Message**: "Add --dry-run functionality to all CJ tools"
- **Author**: Nathaniel Genwright
- **Gap Since Last Commit**: ~27 days (as of 2025-10-22)

### Current Repository State  
- **Branch**: `feature/dry-run-mode`
- **Modified Files**: 113 files with changes
- **Major Uncommitted Work**:
  - Enhanced TriQ system with business operations priority matrix
  - Comprehensive verbose logging implementation
  - Priority validation using urgency/impact custom fields (cf[10450], cf[10451])
  - SLA validation and admin escalation features
  - Updated agent definitions and monitoring scripts

### Recent Development Focus
- **TriQ System Enhancements**: Implemented business operations priority matrix (2025-10-22)
- **Priority Validation**: Added urgency/impact extraction and validation logic
- **Workflow Automation**: Enhanced monitoring with evaluation tracking and admin escalation
- **Documentation Updates**: Comprehensive updates to agent definitions and operational procedures

### Recommendation
Consider committing recent TriQ enhancements as they represent significant functional improvements to the triage validation system with proper business operations alignment.