# TriQ Workflows for JIRA Triage Validation
## Operational Procedures for Engineering Portal Quality Assurance

### Overview
These workflows define the operational procedures TriQ should follow when performing ticket validation on Engineering Portal (EP) tickets. Each workflow includes specific commands, decision trees, and automation steps.

---

## Core Workflows

### Workflow 1: Single Ticket Validation

#### Workflow W1.1: Manual Ticket Assessment with Automatic Routing
```bash
PURPOSE: Validate a specific ticket requested by user
TRIGGER: User requests "Please validate ticket EP-XXX"
INPUTS: Ticket key (e.g., EP-4)

STEPS:
1. Get ticket details
   acli jira workitem view {ticket_key}

2. Extract validation data:
   - Summary text and length
   - Description structure and content  
   - Priority level
   - Assignee status
   - Labels/components
   - Created date and reporter

3. Apply validation rules (reference: jira-validation-rules.md)
   - Rule 1.1: Summary validation
   - Rule 2.1-2.2: Description validation
   - Rule 3.1-3.2: Technical context validation
   - Rule 4.1-4.2: Business context validation
   - Rule 5.1-5.2: Metadata validation

4. Calculate weighted score
   TOTAL_SCORE = (summary*0.25 + description*0.35 + technical*0.20 + business*0.15 + metadata*0.05)

5. Determine action and routing based on score:
   - Score > 5.0: Route to "Eng Queue" status + "engq" label
   - Score ≤ 5.0: Route to "Parking Lot" status for re-evaluation
   
   Validation Status:
   - 9-10: APPROVE → Eng Queue
   - 7-8: APPROVE_WITH_NOTES → Eng Queue
   - 5.1-6.9: NEEDS_CLARIFICATION → Eng Queue
   - ≤5.0: PARKING_LOT → Parking Lot

6. Generate feedback using appropriate template (reference: jira-feedback-templates.md)

7. Apply automatic routing:
   acli jira workitem edit {ticket_key} --status "{target_status}"
   acli jira workitem edit {ticket_key} --labels "triq_validated,quality_score_{score},{routing_label}"

8. Post feedback as comment:
   acli jira workitem comment {ticket_key} --body "{feedback_text}"

OUTPUT: Ticket routed to appropriate queue with feedback provided
```

#### Workflow W1.2: Continuous Monitoring & Re-evaluation
```bash
PURPOSE: Monitor tickets in Initial Review and Parking Lot statuses with escalation tracking
TRIGGER: Automated monitoring script (every 3 minutes)
INPUTS: Tickets in "Initial Review" OR "Parking Lot" status

STEPS:
1. Search for tickets requiring processing:
   acli jira workitem search --jql "project = EP AND status IN ('Initial Review', 'Parking Lot')"

2. For each ticket:
   - Increment evaluation counter
   - Run full validation process (W1.1)
   - Check evaluation count against threshold (5)

3. Apply routing logic:
   - Score > 5.0: Move to "Eng Queue" + "engq" label + reset counter
   - Score ≤ 5.0: Keep in current status or move to "Parking Lot"

4. Admin escalation check:
   - If evaluation count >= 5: Add "admin_review_needed" label
   - Generate admin notification with intervention recommendations
   - Log escalation for project admin review

5. Generate appropriate feedback based on evaluation count:
   - First evaluation: Standard validation feedback
   - Multiple evaluations: Include coaching and improvement guidance
   - Escalated tickets: Note admin review process initiated

OUTPUT: Continuous ticket processing with automatic escalation for stuck tickets
```

#### Workflow W1.3: Admin Escalation Process
```bash
PURPOSE: Handle tickets requiring admin intervention after multiple evaluations
TRIGGER: Ticket reaches 5+ evaluation cycles in Initial Review or Parking Lot
INPUTS: Ticket key with evaluation count >= 5

STEPS:
1. Add admin_review_needed label:
   acli jira workitem edit {ticket_key} --labels "admin_review_needed"

2. Generate admin notification with context:
   - Ticket details and evaluation history
   - Quality scores from previous evaluations
   - Recommended intervention actions
   - Submitter engagement history

3. Notify project admin via:
   - JIRA comment to admin
   - Email notification (if configured)
   - Admin dashboard alert

4. Possible admin actions:
   - Override triage decision and route to engineering
   - Close ticket as invalid/duplicate
   - Provide submitter training
   - Adjust quality threshold for special cases
   - Reassign to different project/team

OUTPUT: Escalated ticket flagged for manual admin review
```

#### Workflow W1.4: Quick Quality Check
```bash
PURPOSE: Fast quality assessment without posting feedback
TRIGGER: User requests "Quick check on EP-XXX"
INPUTS: Ticket key

STEPS:
1. Get ticket summary info:
   acli jira workitem search --jql "key = {ticket_key}"

2. Apply basic validation rules (subset of full validation):
   - Summary specificity check
   - Description length check
   - Basic error message presence
   - Priority reasonableness

3. Generate quality score (0-10)

4. Provide assessment without posting to JIRA

OUTPUT: Quality score and brief improvement suggestions
```

### Workflow 2: Batch Validation

#### Workflow W2.1: Recent Tickets Scan
```bash
PURPOSE: Validate all tickets created in last 24 hours
TRIGGER: Daily automated run or user request "Check recent EP tickets"
INPUTS: Time range (default: 24 hours)

STEPS:
1. Search for recent tickets:
   acli jira workitem search --jql "project = EP AND created >= -{hours}h ORDER BY created DESC" --limit 50

2. FOR EACH ticket found:
   - Skip if already has "validated" label
   - Run W1.1 validation workflow
   - Log results to validation tracking

3. Generate batch summary:
   - Total tickets processed
   - Average quality score
   - Distribution by action taken
   - Common improvement areas

4. Report findings to monitoring channel

OUTPUT: Batch validation summary with metrics and patterns
```

#### Workflow W2.2: Backlog Quality Audit
```bash
PURPOSE: Review existing backlog for quality issues
TRIGGER: Weekly audit or user request "Audit EP backlog"
INPUTS: Status filter (default: "To Do")

STEPS:
1. Search backlog tickets:
   acli jira workitem search --jql "project = EP AND status IN ('To Do', 'Open') AND labels NOT IN (validated)" --limit 100

2. Prioritize review order:
   - High priority tickets first
   - Older tickets next
   - Recently modified tickets last

3. Apply validation rules with relaxed standards for older tickets

4. Generate audit report:
   - Tickets needing immediate attention
   - Tickets needing clarification
   - Tickets ready for engineering
   - Quality trend analysis

OUTPUT: Backlog audit report with actionable recommendations
```

### Workflow 3: Proactive Monitoring

#### Workflow W3.1: New Ticket Alert Processing
```bash
PURPOSE: Immediate validation of newly created tickets
TRIGGER: JIRA webhook or periodic check every 15 minutes
INPUTS: None (searches for new tickets)

STEPS:
1. Find unprocessed tickets:
   acli jira workitem search --jql "project = EP AND created >= -15m AND labels NOT IN (validated)"

2. FOR EACH new ticket:
   - Apply expedited validation (focus on critical issues)
   - Check for emergency indicators
   - Determine if immediate escalation needed

3. Take action based on findings:
   - Emergency: Immediate escalation + validation
   - Standard: Normal validation process
   - Routing needed: Transfer to appropriate project

4. Log monitoring activity

OUTPUT: Real-time validation results and any escalations triggered
```

#### Workflow W3.2: Quality Trend Monitoring
```bash
PURPOSE: Track validation metrics over time
TRIGGER: Daily report generation
INPUTS: Date range for analysis

STEPS:
1. Gather validation metrics:
   - Total tickets validated
   - Average quality scores
   - Most common validation failures
   - Improvement over time

2. Query for trend data:
   acli jira workitem search --jql "project = EP AND created >= -{days}d" --count
   acli jira workitem search --jql "project = EP AND labels IN (quality_score_high)" --count
   acli jira workitem search --jql "project = EP AND labels IN (needs_revision)" --count

3. Calculate KPIs:
   - Validation success rate (score >= 7)
   - Revision request rate (score < 5)
   - Time to resolution after feedback
   - Re-submission success rate

4. Generate trend report

OUTPUT: Quality metrics dashboard with trends and recommendations
```

### Workflow 4: Special Case Handling

#### Workflow W4.1: Security Issue Processing
```bash
PURPOSE: Special handling for authentication/security issues
TRIGGER: Keywords detected: "login", "password", "unauthorized", "security", "authentication"
INPUTS: Ticket with security indicators

STEPS:
1. Apply standard validation rules

2. Add security-specific checks:
   - Verify no credentials exposed in description
   - Check for PII (personally identifiable information)
   - Assess security impact level

3. Determine security routing:
   - Low impact: Standard engineering queue
   - Medium impact: Security team notification
   - High impact: Immediate security escalation

4. Apply special feedback template (R3)

5. Add security labels:
   acli jira workitem edit {ticket_key} --labels "security_review,{impact_level}"

OUTPUT: Security-validated ticket with appropriate routing and security team notification
```

#### Workflow W4.2: Emergency Escalation
```bash
PURPOSE: Handle production-down or critical issues
TRIGGER: Keywords detected: "production down", "system unavailable", "all users affected", "critical"
INPUTS: Ticket with emergency indicators

STEPS:
1. Bypass normal validation requirements

2. Immediate actions:
   - Add "emergency" label
   - Set priority to "High" if not already
   - Post emergency template (S1)
   - Trigger notification to on-call team

3. Gather emergency context:
   - Scope of impact
   - Business disruption level
   - Available contact information

4. Create emergency summary for on-call team

5. Monitor for updates and coordinate response

OUTPUT: Emergency escalation with immediate team notification and tracking
```

---

## Automation Commands

### Daily Automation Script
```bash
#!/bin/bash
# Daily TriQ automation for Engineering Portal

# Morning health check
echo "Starting daily TriQ validation run..."

# Process recent tickets
echo "Validating tickets from last 24 hours..."
acli jira workitem search --jql "project = EP AND created >= -24h ORDER BY created DESC" --limit 20

# Check for unvalidated backlog items  
echo "Checking for unvalidated backlog tickets..."
acli jira workitem search --jql "project = EP AND status IN ('To Do', 'Open') AND labels NOT IN (validated)" --limit 10

# Generate daily metrics
echo "Calculating daily metrics..."
TOTAL_TICKETS=$(acli jira workitem search --jql "project = EP AND created >= -1d" --count)
HIGH_QUALITY=$(acli jira workitem search --jql "project = EP AND created >= -1d AND labels IN (quality_score_high)" --count)
NEEDS_WORK=$(acli jira workitem search --jql "project = EP AND created >= -1d AND labels IN (needs_revision)" --count)

echo "Daily Summary:"
echo "- Total tickets: $TOTAL_TICKETS"
echo "- High quality: $HIGH_QUALITY"
echo "- Needs revision: $NEEDS_WORK"
echo "- Success rate: $(($HIGH_QUALITY * 100 / $TOTAL_TICKETS))%"

echo "Daily TriQ run completed."
```

### Monitoring Queries
```bash
# Find tickets needing validation
UNVALIDATED="project = EP AND status IN ('To Do', 'Open', 'In Progress') AND labels NOT IN (validated)"

# Track quality metrics
HIGH_QUALITY="project = EP AND labels IN (quality_score_high) AND created >= -7d"
NEEDS_REVISION="project = EP AND labels IN (needs_revision) AND created >= -7d"
SECURITY_REVIEW="project = EP AND labels IN (security_review) AND status NOT IN (Resolved, Closed)"

# Emergency monitoring
EMERGENCY_TICKETS="project = EP AND labels IN (emergency) AND status NOT IN (Resolved, Closed)"
HIGH_PRIORITY_OLD="project = EP AND priority = High AND created <= -2d AND status IN ('To Do', 'Open')"
```

### Integration Commands
```bash
# Add validation comment
acli jira workitem comment EP-XXX --body "$(cat validation_feedback.txt)"

# Update ticket labels
acli jira workitem edit EP-XXX --labels "validated,quality_score_7,needs_clarification"

# Set priority based on validation
acli jira workitem edit EP-XXX --priority "High"

# Assign to appropriate team
acli jira workitem assign EP-XXX --assignee "team-lead@company.com"

# Transfer to different project (if routing needed)
# Note: This may require project-specific commands or manual intervention
```

---

## Error Handling and Recovery

### Common Error Scenarios
1. **ACLI Connection Issues**
   - Retry with exponential backoff
   - Log connectivity problems
   - Fall back to cached ticket data if available

2. **Malformed Ticket Content**
   - Apply partial validation rules
   - Flag for manual review
   - Provide generic improvement guidance

3. **Permission Issues**
   - Log access denials
   - Notify administrator
   - Skip problematic tickets with alert

4. **Rate Limiting**
   - Implement request throttling
   - Queue validation requests
   - Process in batches during off-peak hours

### Recovery Procedures
```bash
# Restart validation for failed tickets
acli jira workitem search --jql "project = EP AND labels IN (validation_failed)" --limit 50

# Clean up incomplete validations
acli jira workitem search --jql "project = EP AND labels IN (validation_in_progress) AND updated <= -2h"

# Retry batch operations
for ticket in $(cat failed_validations.txt); do
    echo "Retrying validation for $ticket"
    # Run W1.1 workflow
done
```

### Quality Assurance
- **Manual Review**: Weekly spot-checks of automated validations
- **Feedback Loop**: Track user responses to validation feedback
- **Calibration**: Compare automated scores to human assessments
- **Continuous Improvement**: Update rules based on validation accuracy

### Reporting and Analytics
- **Daily Reports**: Validation summary with key metrics
- **Weekly Trends**: Quality improvement patterns and problem areas  
- **Monthly Analysis**: Rule effectiveness and user satisfaction
- **Quarterly Review**: Process optimization and rule updates