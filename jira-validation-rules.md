# JIRA Validation Rules for Engineering Portal (EP)
## Automated Quality Checks for TriQ Agent

### Overview
These rules define specific, automatable validation checks that TriQ can perform on Engineering Portal tickets. Each rule includes the validation logic, scoring criteria, and feedback templates.

---

## Rule Categories

### 1. Summary Validation Rules

#### Rule 1.1: Summary Length and Specificity
```bash
# Check: Summary length and content quality
CRITERIA:
- Length: 10-100 characters optimal
- Content: Must contain specific problem indicators
- Forbidden: Generic terms like "help", "issue", "problem" without context

VALIDATION LOGIC:
- IF length < 10 chars: SCORE = 0, FLAG = "too_short"
- IF length > 100 chars: SCORE = 7, FLAG = "too_long"  
- IF contains_only_generic_terms(): SCORE = 1, FLAG = "generic"
- IF contains_specific_problem_words(): SCORE += 3
- IF contains_system_component(): SCORE += 2

GENERIC_TERMS = ["help", "issue", "problem", "error", "bug", "tech"]
SPECIFIC_TERMS = ["login", "authentication", "payment", "unauthorized", "timeout", "crash"]
SYSTEM_COMPONENTS = ["portal", "API", "database", "gateway", "integration"]
```

#### Rule 1.2: Summary Action Clarity
```bash
# Check: Does summary indicate what user is trying to do?
CRITERIA:
- Contains action verb (login, access, submit, process, etc.)
- Indicates desired outcome
- Specifies system component if relevant

VALIDATION LOGIC:
- IF contains_action_verb(): SCORE += 2
- IF indicates_desired_outcome(): SCORE += 2
- IF specifies_component(): SCORE += 1

ACTION_VERBS = ["login", "access", "submit", "upload", "download", "process", "create", "update", "delete"]
```

### 2. Description Validation Rules

#### Rule 2.1: Description Structure
```bash
# Check: Description contains required sections
CRITERIA:
- Has identifiable problem statement
- Contains environment or context information
- Includes error details or symptoms
- Describes impact or urgency

VALIDATION LOGIC:
- IF has_problem_statement(): SCORE += 3
- IF has_environment_details(): SCORE += 2
- IF has_error_details(): SCORE += 3
- IF has_impact_statement(): SCORE += 2

PROBLEM_INDICATORS = ["unable to", "cannot", "error when", "fails to", "not working"]
ENVIRONMENT_KEYWORDS = ["browser", "Chrome", "Safari", "mobile", "desktop", "Windows", "Mac", "iOS"]
ERROR_KEYWORDS = ["error", "message", "code", "exception", "failed", "timeout", "unauthorized"]
IMPACT_KEYWORDS = ["urgent", "blocking", "critical", "users affected", "business impact"]
```

#### Rule 2.2: Description Length and Detail
```bash
# Check: Description provides sufficient detail
CRITERIA:
- Minimum 50 characters for meaningful description
- Contains multiple sentences
- Provides context beyond just "it's broken"

VALIDATION LOGIC:
- IF length < 50: SCORE = 0, FLAG = "insufficient_detail"
- IF length 50-200: SCORE = 3
- IF length 200-500: SCORE = 7
- IF length 500-1000: SCORE = 10
- IF length > 1000: SCORE = 8, FLAG = "too_verbose"
- IF sentence_count < 2: SCORE -= 2
```

### 3. Technical Context Validation Rules

#### Rule 3.1: Environment Information
```bash
# Check: Contains technical environment details
CRITERIA:
- Browser/device information
- Operating system details
- Network context when relevant
- Application version if applicable

VALIDATION LOGIC:
- IF mentions_browser(): SCORE += 2
- IF mentions_os(): SCORE += 2
- IF mentions_device_type(): SCORE += 1
- IF mentions_network(): SCORE += 1
- IF mentions_version(): SCORE += 1

BROWSER_TERMS = ["Chrome", "Firefox", "Safari", "Edge", "Internet Explorer", "browser"]
OS_TERMS = ["Windows", "Mac", "macOS", "iOS", "Android", "Linux"]
DEVICE_TERMS = ["mobile", "tablet", "desktop", "phone", "iPad", "iPhone"]
NETWORK_TERMS = ["WiFi", "cellular", "VPN", "corporate network", "home network"]
```

#### Rule 3.2: Error Message Specificity
```bash
# Check: Contains specific error messages or codes
CRITERIA:
- Exact error text in quotes
- Error codes if applicable
- Screenshots mentioned or attached
- Console messages if technical user

VALIDATION LOGIC:
- IF has_quoted_error_text(): SCORE += 4
- IF has_error_code(): SCORE += 3
- IF mentions_screenshots(): SCORE += 2
- IF has_console_logs(): SCORE += 2

ERROR_CODE_PATTERN = r'\b[A-Z0-9]{3,10}\b'  # Pattern for error codes
QUOTED_TEXT_PATTERN = r'"[^"]{10,}"'  # Quoted strings 10+ chars
SCREENSHOT_TERMS = ["screenshot", "image", "attached", "see attached"]
CONSOLE_TERMS = ["console", "network tab", "developer tools", "F12"]
```

### 4. Business Context Validation Rules

#### Rule 4.1: Impact Assessment
```bash
# Check: Describes business impact and urgency
CRITERIA:
- Number of affected users
- Business process disruption
- Timeline requirements
- Workaround availability

VALIDATION LOGIC:
- IF has_user_count(): SCORE += 3
- IF describes_business_disruption(): SCORE += 2
- IF has_timeline_requirement(): SCORE += 2
- IF mentions_workaround(): SCORE += 1

USER_COUNT_PATTERN = r'\b\d+\s+users?\b'
BUSINESS_TERMS = ["revenue", "customer", "billing", "payment", "service", "production"]
TIMELINE_TERMS = ["urgent", "ASAP", "by EOD", "deadline", "time sensitive"]
WORKAROUND_TERMS = ["workaround", "alternative", "manual process", "bypass"]
```

#### Rule 4.2: Account Context
```bash
# Check: Provides relevant account/system context
CRITERIA:
- System or portal identification
- User role or permissions context
- Company or organization reference
- Account identifier (anonymized)

VALIDATION LOGIC:
- IF identifies_system(): SCORE += 2
- IF mentions_user_role(): SCORE += 2
- IF has_company_context(): SCORE += 1
- IF has_account_reference(): SCORE += 1

SYSTEM_TERMS = ["customer portal", "admin panel", "billing system", "payment gateway"]
ROLE_TERMS = ["admin", "user", "manager", "staff", "customer", "guest"]
COMPANY_INDICATORS = ["company", "organization", "client", "account"]
```

### 5. Metadata Validation Rules

#### Rule 5.1: Priority Assignment (Enhanced with Urgency/Impact Matrix)
```bash
# Check: Priority matches urgency and impact assessment based on MuniBilling framework
CRITERIA:
- Critical (1): High urgency + High impact (15 min response, 2 hour resolution)
- High (2): High urgency + Medium impact OR Medium urgency + High impact (30 min response, 1 day resolution)
- Medium (3): Medium urgency + Medium impact OR Low urgency + High impact (1 hour response, 2 days resolution)
- Low (4): Low urgency + Medium impact OR Medium urgency + Low impact (4 hours response, 5 days resolution)
- Very Low (5): Low urgency + Low impact (1 day response, 10 days resolution)

VALIDATION LOGIC:
- Calculate urgency_score and impact_score
- Determine expected_priority using urgency/impact matrix
- Compare against assigned priority
- IF assigned_priority matches expected_priority: SCORE += 3
- IF assigned_priority differs by 1 level: SCORE += 1, FLAG = "priority_minor_mismatch"
- IF assigned_priority differs by 2+ levels: SCORE -= 2, FLAG = "priority_major_mismatch"

# Urgency Indicators (time sensitivity)
HIGH_URGENCY_TERMS = ["immediate", "ASAP", "urgent", "emergency", "critical", "blocking", "production down", "system unavailable"]
MEDIUM_URGENCY_TERMS = ["soon", "today", "this week", "by EOD", "time sensitive", "deadline"]
LOW_URGENCY_TERMS = ["when possible", "future", "eventually", "enhancement", "nice to have"]

# Impact Indicators (scope and business effect)
HIGH_IMPACT_TERMS = ["all users", "production", "revenue", "billing", "payment", "security breach", "data loss", "system-wide"]
MEDIUM_IMPACT_TERMS = ["multiple users", "department", "workflow", "customer facing", "integration", "reporting"]
LOW_IMPACT_TERMS = ["single user", "cosmetic", "minor", "documentation", "training", "feature request"]

# Business Context Indicators
FINANCIAL_IMPACT = ["revenue", "billing", "payment", "transaction", "financial", "customer invoice"]
COMPLIANCE_IMPACT = ["regulatory", "audit", "compliance", "legal", "violation", "breach"]
OPERATIONAL_IMPACT = ["workflow", "process", "productivity", "efficiency", "automation"]
```

#### Rule 5.2: Response Time Validation
```bash
# Check: Priority aligns with described timeline requirements
CRITERIA:
- Timeline expectations match assigned priority level
- Response time requirements are realistic
- Resolution expectations align with priority SLAs

VALIDATION LOGIC:
- Extract timeline_requirements from description
- Map to expected_priority based on urgency
- Compare against assigned_priority
- IF timeline matches priority SLA: SCORE += 2
- IF timeline is unrealistic for priority: SCORE -= 1, FLAG = "timeline_mismatch"
- IF no timeline but high priority: SCORE -= 1, FLAG = "missing_timeline"

# Response Time Expectations (from MuniBilling framework)
CRITICAL_SLA = {"response": "15 minutes", "resolution": "2 hours"}
HIGH_SLA = {"response": "30 minutes", "resolution": "1 business day"}
MEDIUM_SLA = {"response": "1 hour", "resolution": "2 business days"}
LOW_SLA = {"response": "4 hours", "resolution": "5 business days"}
VERY_LOW_SLA = {"response": "1 business day", "resolution": "10 business days"}

# Timeline Pattern Detection
IMMEDIATE_TIMELINE = ["now", "immediately", "ASAP", "urgent", "within minutes"]
DAILY_TIMELINE = ["today", "by EOD", "end of day", "within hours"]
WEEKLY_TIMELINE = ["this week", "few days", "next week"]
MONTHLY_TIMELINE = ["this month", "few weeks", "when possible"]
```

#### Rule 5.3: Component Assignment
```bash
# Check: Appropriate component/label assignment
CRITERIA:
- Component matches described issue type
- Labels help with categorization
- Team assignment makes sense

VALIDATION LOGIC:
- IF has_component_assigned(): SCORE += 1
- IF component_matches_description(): SCORE += 2
- IF has_useful_labels(): SCORE += 1

COMPONENT_KEYWORDS = {
    "Authentication": ["login", "password", "unauthorized", "authentication"],
    "Payment Processing": ["payment", "billing", "charge", "transaction"],
    "Customer Portal": ["portal", "dashboard", "customer interface"],
    "API Integration": ["API", "integration", "endpoint", "webhook"],
    "Infrastructure": ["server", "database", "network", "performance"]
}
```

---

## Validation Workflow

### 1. Initial Automated Scan
```bash
FOR each new Engineering Portal ticket:
    1. Run all validation rules
    2. Calculate total score
    3. Identify specific gaps
    4. Generate feedback report
    5. Determine routing action
```

### 2. Score Calculation
```bash
TOTAL_SCORE = (
    summary_score +
    description_score +
    technical_context_score +
    business_context_score +
    metadata_score
) / 5  # Average across categories

# Apply category weights if needed
WEIGHTED_SCORE = (
    summary_score * 0.25 +
    description_score * 0.35 +
    technical_context_score * 0.20 +
    business_context_score * 0.15 +
    metadata_score * 0.05
)
```

### 3. Action Triggers
```bash
IF TOTAL_SCORE >= 9: ACTION = "APPROVE"
ELIF TOTAL_SCORE >= 7: ACTION = "APPROVE_WITH_NOTES"
ELIF TOTAL_SCORE >= 5: ACTION = "REQUEST_CLARIFICATION"
ELIF TOTAL_SCORE >= 3: ACTION = "REQUEST_REVISION"
ELSE: ACTION = "ROUTE_ELSEWHERE"
```

### 4. Special Case Handlers
```bash
# Security Issues
IF contains_security_keywords(): FLAG = "SECURITY_REVIEW"
SECURITY_KEYWORDS = ["password", "authentication", "unauthorized", "security", "breach", "hack"]

# Production Issues
IF contains_production_keywords(): PRIORITY_BOOST = True
PRODUCTION_KEYWORDS = ["production down", "system unavailable", "all users affected"]

# Customer-Facing Issues
IF contains_customer_impact(): URGENCY_BOOST = True
CUSTOMER_IMPACT_KEYWORDS = ["customer", "billing", "payment", "invoice", "portal"]
```

---

## Implementation Commands

### ACLI Integration Examples
```bash
# Get ticket details for validation
acli jira workitem view {ticket_key}

# Search for recent tickets to validate
acli jira workitem search --jql "project = EP AND created >= -1d ORDER BY created DESC" --limit 10

# Add comment with validation feedback
acli jira workitem comment {ticket_key} --body "{validation_feedback}"

# Update ticket priority if mismatched
acli jira workitem edit {ticket_key} --priority "{correct_priority}"

# Add labels for categorization
acli jira workitem edit {ticket_key} --labels "{validation_status},{quality_score}"
```

### Monitoring Queries
```bash
# Find tickets needing validation
acli jira workitem search --jql "project = EP AND status IN ('To Do', 'Open') AND labels NOT IN (validated)"

# Track validation metrics
acli jira workitem search --jql "project = EP AND labels IN (quality_score_high)" --count

# Identify problematic patterns
acli jira workitem search --jql "project = EP AND labels IN (needs_revision)" --limit 20
```

---

## Error Handling

### Common Issues
1. **Missing ticket details**: Graceful degradation with partial validation
2. **ACLI connectivity issues**: Retry logic with exponential backoff
3. **Malformed ticket content**: Safe text processing with fallbacks
4. **Permission issues**: Clear error messages for access problems

### Logging Requirements
- Log all validation attempts with timestamps
- Track rule performance and accuracy
- Monitor false positive/negative rates
- Record user feedback on validation quality

### Quality Assurance
- Weekly manual review of validation results
- Calibration against human triage decisions
- Continuous improvement of rule accuracy
- User satisfaction surveys on feedback quality