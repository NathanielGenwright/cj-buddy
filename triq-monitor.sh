#!/bin/bash

# TriQ Engineering Portal Monitoring Script
# Proactive JIRA ticket validation and quality monitoring

set -e  # Exit on any error

# Configuration
PROJECT="EP"
LOG_FILE="/tmp/triq-monitor.log"
REPORT_FILE="/tmp/triq-daily-report.txt"
VALIDATION_LABEL="triq_validated"
EVALUATION_COUNTER_FILE="/tmp/triq-evaluation-counts.txt"
ADMIN_REVIEW_THRESHOLD=5

# Verbose logging configuration
VERBOSE_VALIDATION_LOGGING=true
LOG_FEEDBACK_CONTENT=true
VALIDATION_LOG_LEVEL="DEBUG"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Verbose validation logging functions
log_validation_header() {
    local ticket_key="$1"
    local evaluation_count="$2"
    local priority="$3"
    local issue_type="$4"
    
    if [ "$VERBOSE_VALIDATION_LOGGING" = true ]; then
        log "[$ticket_key] [VALIDATION] [INFO] === Starting Validation (Evaluation #$evaluation_count) ==="
        log "[$ticket_key] [METADATA] [INFO] Priority: $priority, Type: $issue_type"
    fi
}

log_category_score() {
    local ticket_key="$1"
    local category="$2"
    local score="$3"
    local max_score="$4"
    local weight="$5"
    local reasoning="$6"
    
    if [ "$VERBOSE_VALIDATION_LOGGING" = true ]; then
        local weighted_score=$(echo "scale=2; $score * $weight / 100" | bc -l 2>/dev/null || echo "0")
        local max_weighted=$(echo "scale=2; $max_score * $weight / 100" | bc -l 2>/dev/null || echo "0")
        log "[$ticket_key] [$category] [INFO] Category Score: $score/$max_score (Weighted: $weighted_score/$max_weighted) - $reasoning"
    fi
}

log_category_detail() {
    local ticket_key="$1"
    local category="$2"
    local check_name="$3"
    local result="$4"
    local score="$5"
    local reasoning="$6"
    
    if [ "$VERBOSE_VALIDATION_LOGGING" = true ] && [ "$VALIDATION_LOG_LEVEL" = "DEBUG" ]; then
        log "[$ticket_key] [$category] [DEBUG] $check_name: $result (Score: $score/10) - $reasoning"
    fi
}

log_validation_summary() {
    local ticket_key="$1"
    local total_score="$2"
    local max_score="$3"
    local validation_result="$4"
    local routing_decision="$5"
    
    if [ "$VERBOSE_VALIDATION_LOGGING" = true ]; then
        log "[$ticket_key] [VALIDATION] [INFO] === Final Score: $total_score/$max_score ($validation_result) ==="
        log "[$ticket_key] [ROUTING] [INFO] Decision: $routing_decision (Score threshold: 5.0)"
    fi
}

log_feedback_content() {
    local ticket_key="$1"
    local template="$2"
    local feedback_content="$3"
    
    if [ "$LOG_FEEDBACK_CONTENT" = true ]; then
        log "[$ticket_key] [FEEDBACK] [INFO] Template: $template"
        if [ "$VALIDATION_LOG_LEVEL" = "DEBUG" ]; then
            log "[$ticket_key] [FEEDBACK] [DEBUG] Content:"
            echo "$feedback_content" | while IFS= read -r line; do
                log "[$ticket_key] [FEEDBACK] [DEBUG] > $line"
            done
        fi
    fi
}

# Initialize monitoring session
log "=== TriQ Monitoring Session Started ==="

# Check ACLI connectivity
log "Testing JIRA connectivity..."
if ! acli jira project list --limit 1 >/dev/null 2>&1; then
    log "ERROR: Cannot connect to JIRA. Check ACLI configuration."
    exit 1
fi
log "✓ JIRA connectivity confirmed"

# Function: Check for new tickets
check_new_tickets() {
    log "Checking for new Engineering Portal tickets..."

    # Find ALL tickets that need validation in Initial Review AND Parking Lot statuses
    # EXCLUDE tickets with triq_manual_eval label (need manual intervention)
    NEW_TICKETS=$(acli jira workitem search --jql "project = $PROJECT AND status IN ('Initial Review', 'Parking Lot') AND labels NOT IN (triq_manual_eval)" 2>/dev/null || echo "")
    
    if [ -n "$NEW_TICKETS" ]; then
        log "Found new tickets requiring validation:"
        echo "$NEW_TICKETS" | tee -a "$LOG_FILE"
        
        # Extract ticket keys for processing (improved parsing)
        TICKET_KEYS=$(echo "$NEW_TICKETS" | grep -E "EP-[0-9]+" -o | sort -u || echo "")
        
        for ticket in $TICKET_KEYS; do
            if [ -n "$ticket" ]; then
                log "Processing ticket: $ticket"
                validate_ticket "$ticket"
            fi
        done
    else
        log "No tickets found in Initial Review or Parking Lot statuses"
    fi
}

# Function: Calculate priority based on business operations matrix
calculate_priority_from_urgency_impact() {
    local urgency="$1"
    local impact="$2"
    
    # Convert to lowercase for consistent matching
    urgency=$(echo "$urgency" | tr '[:upper:]' '[:lower:]')
    impact=$(echo "$impact" | tr '[:upper:]' '[:lower:]')
    
    # Business Operations Priority Matrix
    # Urgency\Impact  High  Medium  Low
    # High            1     2       3
    # Medium          2     3       4
    # Low             3     4       5
    
    case "$urgency" in
        "high")
            case "$impact" in
                "high") echo "1" ;;
                "medium") echo "2" ;;
                "low") echo "3" ;;
                *) echo "unknown" ;;
            esac
            ;;
        "medium")
            case "$impact" in
                "high") echo "2" ;;
                "medium") echo "3" ;;
                "low") echo "4" ;;
                *) echo "unknown" ;;
            esac
            ;;
        "low")
            case "$impact" in
                "high") echo "3" ;;
                "medium") echo "4" ;;
                "low") echo "5" ;;
                *) echo "unknown" ;;
            esac
            ;;
        *) 
            echo "unknown" ;;
    esac
}

# Function: Get SLA expectations based on priority
get_sla_expectations() {
    local priority_num="$1"
    
    case "$priority_num" in
        "1") echo "15 minutes|2 hours" ;;
        "2") echo "30 minutes|1 business day" ;;
        "3") echo "1 hour|2 business days" ;;
        "4") echo "4 hours|5 business days" ;;
        "5") echo "1 business day|10 business days" ;;
        *) echo "unknown|unknown" ;;
    esac
}

# Function: Validate SLA compliance for priority
validate_sla_compliance() {
    local ticket_key="$1"
    local priority_num="$2"
    local created_date="$3"
    
    local sla_info=$(get_sla_expectations "$priority_num")
    local response_sla=$(echo "$sla_info" | cut -d'|' -f1)
    local resolution_sla=$(echo "$sla_info" | cut -d'|' -f2)
    
    if [ "$VERBOSE_VALIDATION_LOGGING" = true ]; then
        log "[$ticket_key] [SLA] [INFO] Priority $priority_num SLA: Response within $response_sla, Resolution within $resolution_sla"
        
        # Special handling for Critical Priority
        if [ "$priority_num" = "1" ]; then
            local current_hour=$(date +%H)
            local current_day=$(date +%u)  # 1=Monday, 7=Sunday
            
            if [ "$current_hour" -ge 17 ] || [ "$current_day" -eq 6 ] || [ "$current_day" -eq 7 ]; then
                log "[$ticket_key] [SLA] [WARN] Critical Priority workflow stoppage items should only be addressed after hours (after 5 PM EST or weekends/holidays)"
            fi
        fi
    fi
    
    echo "$response_sla|$resolution_sla"
}

# Function: Extract urgency and impact from custom fields
extract_urgency_impact() {
    local ticket_key="$1"
    
    # Extract custom field values using ACLI
    local urgency_raw=$(acli jira workitem view "$ticket_key" --field "cf[10450]" 2>/dev/null | grep -v "^$" | head -1 || echo "")
    local impact_raw=$(acli jira workitem view "$ticket_key" --field "cf[10451]" 2>/dev/null | grep -v "^$" | head -1 || echo "")
    
    # Clean and normalize the values
    local urgency_clean=$(echo "$urgency_raw" | sed 's/.*: //' | tr -d '\n\r' | xargs)
    local impact_clean=$(echo "$impact_raw" | sed 's/.*: //' | tr -d '\n\r' | xargs)
    
    # Set defaults if fields are empty
    if [ -z "$urgency_clean" ]; then
        urgency_clean="Medium"
    fi
    if [ -z "$impact_clean" ]; then
        impact_clean="Medium"
    fi
    
    echo "$urgency_clean|$impact_clean"
}

# Function: Validate individual ticket
validate_ticket() {
    local ticket_key="$1"
    log "Validating ticket: $ticket_key"
    
    # Track evaluation count
    track_evaluation_count "$ticket_key"
    local evaluation_count=$(grep "^$ticket_key:" "$EVALUATION_COUNTER_FILE" | cut -d: -f2 || echo "1")
    
    # Get ticket details
    TICKET_DETAILS=$(acli jira workitem view "$ticket_key" 2>/dev/null || echo "ERROR: Could not retrieve ticket")
    
    if [[ "$TICKET_DETAILS" == *"ERROR"* ]]; then
        log "ERROR: Could not retrieve details for $ticket_key"
        return 1
    fi
    
    # Extract ticket information
    SUMMARY=$(echo "$TICKET_DETAILS" | grep "Summary:" | sed 's/Summary: //' || echo "No summary")
    DESCRIPTION=$(echo "$TICKET_DETAILS" | grep "Description:" | sed 's/Description: //' || echo "No description")
    PRIORITY=$(echo "$TICKET_DETAILS" | grep "Priority:" | sed 's/Priority: //' || echo "Normal")
    ISSUE_TYPE=$(echo "$TICKET_DETAILS" | grep "Type:" | sed 's/Type: //' || echo "Unknown")
    CREATED_DATE=$(echo "$TICKET_DETAILS" | grep "Created:" | sed 's/Created: //' || echo "Unknown")
    
    # Extract urgency and impact from custom fields
    URGENCY_IMPACT=$(extract_urgency_impact "$ticket_key")
    URGENCY=$(echo "$URGENCY_IMPACT" | cut -d'|' -f1)
    IMPACT=$(echo "$URGENCY_IMPACT" | cut -d'|' -f2)
    
    # Calculate expected priority based on business operations matrix
    CALCULATED_PRIORITY=$(calculate_priority_from_urgency_impact "$URGENCY" "$IMPACT")
    
    # Map priority names to numbers for comparison
    case "$PRIORITY" in
        "Critical") ASSIGNED_PRIORITY_NUM="1" ;;
        "High") ASSIGNED_PRIORITY_NUM="2" ;;
        "Medium") ASSIGNED_PRIORITY_NUM="3" ;;
        "Low") ASSIGNED_PRIORITY_NUM="4" ;;
        "Very Low") ASSIGNED_PRIORITY_NUM="5" ;;
        *) ASSIGNED_PRIORITY_NUM="3" ;;  # Default to Medium if unclear
    esac
    
    # Start verbose validation logging
    log_validation_header "$ticket_key" "$evaluation_count" "$PRIORITY" "$ISSUE_TYPE"
    
    # Log priority validation details
    if [ "$VERBOSE_VALIDATION_LOGGING" = true ]; then
        log "[$ticket_key] [PRIORITY] [INFO] Urgency: $URGENCY, Impact: $IMPACT"
        log "[$ticket_key] [PRIORITY] [INFO] Calculated Priority: $CALCULATED_PRIORITY, Assigned Priority: $ASSIGNED_PRIORITY_NUM"
        if [ "$CALCULATED_PRIORITY" != "unknown" ] && [ "$CALCULATED_PRIORITY" != "$ASSIGNED_PRIORITY_NUM" ]; then
            log "[$ticket_key] [PRIORITY] [WARN] Priority mismatch detected!"
        fi
    fi
    
    # Validate SLA expectations
    validate_sla_compliance "$ticket_key" "$ASSIGNED_PRIORITY_NUM" "$CREATED_DATE" >/dev/null
    
    # Initialize scoring variables
    SUMMARY_SCORE=0
    DESCRIPTION_SCORE=0  
    TECHNICAL_SCORE=0
    BUSINESS_SCORE=0
    METADATA_SCORE=0
    ISSUES=()
    
    # 1. SUMMARY VALIDATION (25% weight)
    log_category_detail "$ticket_key" "SUMMARY" "Text Analysis" "\"$SUMMARY\"" "0" "Length: ${#SUMMARY} characters"
    
    # Length check (10-100 characters optimal)
    if [ ${#SUMMARY} -lt 10 ]; then
        SUMMARY_SCORE=$((SUMMARY_SCORE + 1))
        ISSUES+=("Summary too short (${#SUMMARY} chars)")
        log_category_detail "$ticket_key" "SUMMARY" "Length Check" "FAIL" "1" "Too short (${#SUMMARY} chars)"
    elif [ ${#SUMMARY} -gt 100 ]; then
        SUMMARY_SCORE=$((SUMMARY_SCORE + 6))
        ISSUES+=("Summary too long (${#SUMMARY} chars)")
        log_category_detail "$ticket_key" "SUMMARY" "Length Check" "PARTIAL" "6" "Too long (${#SUMMARY} chars)"
    else
        SUMMARY_SCORE=$((SUMMARY_SCORE + 8))
        log_category_detail "$ticket_key" "SUMMARY" "Length Check" "PASS" "8" "Good length (${#SUMMARY} chars)"
    fi
    
    # Specificity check (generic terms detection)
    if echo "$SUMMARY" | grep -qi -E "\b(help|issue|problem|error)\b" && ! echo "$SUMMARY" | grep -qi -E "\b(login|payment|unauthorized|timeout)\b"; then
        SUMMARY_SCORE=$((SUMMARY_SCORE + 0))
        ISSUES+=("Summary too generic")
        log_category_detail "$ticket_key" "SUMMARY" "Specificity Check" "FAIL" "0" "Contains generic terms"
    else
        SUMMARY_SCORE=$((SUMMARY_SCORE + 2))
        log_category_detail "$ticket_key" "SUMMARY" "Specificity Check" "PASS" "2" "Specific problem indication"
    fi
    
    log_category_score "$ticket_key" "SUMMARY" "$SUMMARY_SCORE" "10" "25" "Length and specificity assessment"
    
    # 2. DESCRIPTION VALIDATION (35% weight) 
    log_category_detail "$ticket_key" "DESCRIPTION" "Text Analysis" "\"$DESCRIPTION\"" "0" "Length: ${#DESCRIPTION} characters"
    
    # Structure and length check
    if [ ${#DESCRIPTION} -lt 50 ]; then
        DESCRIPTION_SCORE=$((DESCRIPTION_SCORE + 1))
        ISSUES+=("Description too short (${#DESCRIPTION} chars)")
        log_category_detail "$ticket_key" "DESCRIPTION" "Length Check" "FAIL" "1" "Too short (${#DESCRIPTION} chars)"
    elif [ ${#DESCRIPTION} -gt 200 ]; then
        DESCRIPTION_SCORE=$((DESCRIPTION_SCORE + 8))
        log_category_detail "$ticket_key" "DESCRIPTION" "Length Check" "PASS" "8" "Good length (${#DESCRIPTION} chars)"
    else
        DESCRIPTION_SCORE=$((DESCRIPTION_SCORE + 6))
        log_category_detail "$ticket_key" "DESCRIPTION" "Length Check" "PARTIAL" "6" "Adequate length (${#DESCRIPTION} chars)"
    fi
    
    # Content quality check
    if echo "$DESCRIPTION" | grep -qi -E "\b(error|message|code|exception|failed)\b"; then
        DESCRIPTION_SCORE=$((DESCRIPTION_SCORE + 2))
        log_category_detail "$ticket_key" "DESCRIPTION" "Error Details" "PASS" "2" "Contains error information"
    else
        ISSUES+=("No error details mentioned")
        log_category_detail "$ticket_key" "DESCRIPTION" "Error Details" "FAIL" "0" "No error details provided"
    fi
    
    log_category_score "$ticket_key" "DESCRIPTION" "$DESCRIPTION_SCORE" "10" "35" "Structure and content quality"
    
    # 3. TECHNICAL CONTEXT VALIDATION (20% weight)
    # Environment details check
    if echo "$DESCRIPTION" | grep -qi -E "\b(browser|chrome|safari|firefox|windows|mac|linux|mobile|desktop|android|ios)\b"; then
        TECHNICAL_SCORE=$((TECHNICAL_SCORE + 3))
        log_category_detail "$ticket_key" "TECHNICAL" "Environment Check" "PASS" "3" "Environment details provided"
    else
        ISSUES+=("No environment details")
        log_category_detail "$ticket_key" "TECHNICAL" "Environment Check" "FAIL" "0" "No environment details"
    fi
    
    # Reproduction steps check
    if echo "$DESCRIPTION" | grep -qi -E "\b(steps|reproduce|step|click|navigate|open)\b"; then
        TECHNICAL_SCORE=$((TECHNICAL_SCORE + 2))
        log_category_detail "$ticket_key" "TECHNICAL" "Reproduction Steps" "PASS" "2" "Reproduction information provided"
    else
        TECHNICAL_SCORE=$((TECHNICAL_SCORE + 0))
        log_category_detail "$ticket_key" "TECHNICAL" "Reproduction Steps" "FAIL" "0" "No reproduction steps"
    fi
    
    log_category_score "$ticket_key" "TECHNICAL" "$TECHNICAL_SCORE" "10" "20" "Environment and reproduction details"
    
    # 4. BUSINESS CONTEXT VALIDATION (15% weight)
    # Impact assessment
    if echo "$SUMMARY $DESCRIPTION" | grep -qi -E "\b(all|users|customers|everyone|critical|urgent|production)\b"; then
        BUSINESS_SCORE=$((BUSINESS_SCORE + 3))
        log_category_detail "$ticket_key" "BUSINESS" "Impact Assessment" "PASS" "3" "Business impact indicated"
    else
        BUSINESS_SCORE=$((BUSINESS_SCORE + 1))
        log_category_detail "$ticket_key" "BUSINESS" "Impact Assessment" "PARTIAL" "1" "Limited impact information"
    fi
    
    log_category_score "$ticket_key" "BUSINESS" "$BUSINESS_SCORE" "10" "15" "Business impact assessment"
    
    # 5. METADATA VALIDATION (5% weight)
    # Priority validation using business operations matrix
    if [ "$CALCULATED_PRIORITY" != "unknown" ]; then
        if [ "$CALCULATED_PRIORITY" = "$ASSIGNED_PRIORITY_NUM" ]; then
            METADATA_SCORE=$((METADATA_SCORE + 10))
            log_category_detail "$ticket_key" "METADATA" "Priority Matrix Check" "PASS" "10" "Priority matches urgency/impact matrix ($PRIORITY)"
        elif [ "$((CALCULATED_PRIORITY - ASSIGNED_PRIORITY_NUM))" -le 1 ] && [ "$((ASSIGNED_PRIORITY_NUM - CALCULATED_PRIORITY))" -le 1 ]; then
            METADATA_SCORE=$((METADATA_SCORE + 7))
            log_category_detail "$ticket_key" "METADATA" "Priority Matrix Check" "PARTIAL" "7" "Priority close to calculated ($PRIORITY vs calculated $CALCULATED_PRIORITY)"
        else
            METADATA_SCORE=$((METADATA_SCORE + 3))
            ISSUES+=("Priority mismatch: assigned $PRIORITY (level $ASSIGNED_PRIORITY_NUM) but urgency=$URGENCY + impact=$IMPACT suggests priority $CALCULATED_PRIORITY")
            log_category_detail "$ticket_key" "METADATA" "Priority Matrix Check" "FAIL" "3" "Priority mismatch detected"
        fi
    else
        METADATA_SCORE=$((METADATA_SCORE + 6))
        log_category_detail "$ticket_key" "METADATA" "Priority Matrix Check" "PARTIAL" "6" "Cannot validate priority - missing urgency/impact data"
    fi
    
    log_category_score "$ticket_key" "METADATA" "$METADATA_SCORE" "10" "5" "Priority validation using business operations matrix"
    
    # Calculate weighted total score
    SUMMARY_WEIGHTED=$(echo "scale=2; $SUMMARY_SCORE * 0.25" | bc -l 2>/dev/null || echo "0")
    DESCRIPTION_WEIGHTED=$(echo "scale=2; $DESCRIPTION_SCORE * 0.35" | bc -l 2>/dev/null || echo "0") 
    TECHNICAL_WEIGHTED=$(echo "scale=2; $TECHNICAL_SCORE * 0.20" | bc -l 2>/dev/null || echo "0")
    BUSINESS_WEIGHTED=$(echo "scale=2; $BUSINESS_SCORE * 0.15" | bc -l 2>/dev/null || echo "0")
    METADATA_WEIGHTED=$(echo "scale=2; $METADATA_SCORE * 0.05" | bc -l 2>/dev/null || echo "0")
    
    TOTAL_SCORE=$(echo "scale=2; $SUMMARY_WEIGHTED + $DESCRIPTION_WEIGHTED + $TECHNICAL_WEIGHTED + $BUSINESS_WEIGHTED + $METADATA_WEIGHTED" | bc -l 2>/dev/null || echo "0")
    
    # Determine validation result and routing based on weighted score
    if (( $(echo "$TOTAL_SCORE > 5.0" | bc -l 2>/dev/null || echo "0") )); then
        if (( $(echo "$TOTAL_SCORE >= 8.0" | bc -l 2>/dev/null || echo "0") )); then
            VALIDATION_RESULT="APPROVED"
        elif (( $(echo "$TOTAL_SCORE >= 6.0" | bc -l 2>/dev/null || echo "0") )); then
            VALIDATION_RESULT="APPROVED_WITH_NOTES"
        else
            VALIDATION_RESULT="NEEDS_CLARIFICATION"
        fi
        ROUTING_STATUS="Eng Queue"
        ROUTING_LABEL="engq"
        ACTION="route_to_engineering"
    else
        VALIDATION_RESULT="PARKING_LOT"
        ROUTING_STATUS="Parking Lot"
        ROUTING_LABEL="parking_lot"
        ACTION="route_to_parking_lot"
    fi
    
    # Log validation summary
    log_validation_summary "$ticket_key" "$TOTAL_SCORE" "10.0" "$VALIDATION_RESULT" "$ROUTING_STATUS"
    
    # Log issues found
    if [ ${#ISSUES[@]} -gt 0 ]; then
        log "Issues identified:"
        for issue in "${ISSUES[@]}"; do
            log "  - $issue"
        done
    fi
    
    # Apply routing based on score
    apply_routing "$ticket_key" "$ROUTING_STATUS" "$ROUTING_LABEL" "$TOTAL_SCORE"
    
    # Generate feedback 
    generate_feedback "$ticket_key" "$VALIDATION_RESULT" "$TOTAL_SCORE" "${ISSUES[@]}"
    
    return 0
}

# Function: Track evaluation count for tickets
track_evaluation_count() {
    local ticket_key="$1"
    
    # Initialize evaluation counter file if it doesn't exist
    if [ ! -f "$EVALUATION_COUNTER_FILE" ]; then
        touch "$EVALUATION_COUNTER_FILE"
    fi
    
    # Get current count for this ticket
    local current_count=$(grep "^$ticket_key:" "$EVALUATION_COUNTER_FILE" | cut -d: -f2 || echo "0")
    if [ -z "$current_count" ]; then
        current_count=0
    fi
    
    # Increment count
    local new_count=$((current_count + 1))
    
    # Update or add entry in counter file
    if grep -q "^$ticket_key:" "$EVALUATION_COUNTER_FILE"; then
        # Create temporary file for macOS compatibility
        local temp_file=$(mktemp)
        sed "s/^$ticket_key:.*/$ticket_key:$new_count/" "$EVALUATION_COUNTER_FILE" > "$temp_file"
        mv "$temp_file" "$EVALUATION_COUNTER_FILE"
    else
        echo "$ticket_key:$new_count" >> "$EVALUATION_COUNTER_FILE"
    fi
    
    log "Evaluation count for $ticket_key: $new_count"
    
    # Check if admin review is needed
    if [ $new_count -ge $ADMIN_REVIEW_THRESHOLD ]; then
        log "⚠️ ADMIN REVIEW NEEDED: $ticket_key has been evaluated $new_count times"
        escalate_to_admin "$ticket_key" "$new_count"
    fi
}

# Function: Escalate ticket to manual evaluation
escalate_to_admin() {
    local ticket_key="$1"
    local evaluation_count="$2"

    log "🚨 ESCALATING TO MANUAL EVALUATION: $ticket_key"

    # Add triq_manual_eval label to exclude from future automatic evaluations
    log "Would add triq_manual_eval label to $ticket_key"
    # acli jira workitem edit "$ticket_key" --labels "triq_manual_eval"

    # Create admin notification
    local notification_file="/tmp/admin_notification_${ticket_key}.txt"
    cat > "$notification_file" << EOF
🚨 MANUAL EVALUATION REQUIRED

Ticket: $ticket_key
Evaluation Count: $evaluation_count
Status: Stuck in triage for multiple evaluation cycles
Label Applied: triq_manual_eval

This ticket has been evaluated $evaluation_count times while remaining in
"Initial Review" or "Parking Lot" status. Manual intervention is required.

AUTOMATIC EVALUATIONS DISABLED: This ticket will be excluded from future
automatic validation cycles until the "triq_manual_eval" label is removed.

Possible Actions:
- Review ticket quality requirements
- Provide submitter training
- Reassign or close if inappropriate
- Override triage decision if needed
- Remove "triq_manual_eval" label to re-enable automatic validation

Generated: $(date '+%Y-%m-%d %H:%M:%S')
EOF

    log "Admin notification created: $notification_file"
    log "Ticket $ticket_key marked for manual evaluation - excluded from future automatic processing"

    # In production, would send notification to project admin
    # This could be email, Slack, or JIRA comment to admin
}

# Function: Apply routing based on validation score
apply_routing() {
    local ticket_key="$1"
    local status="$2"
    local label="$3"
    local score="$4"
    
    log "Applying routing for $ticket_key: Status=$status, Label=$label"
    
    # Update ticket status
    log "Would update status to: $status"
    # acli jira workitem edit "$ticket_key" --status "$status"
    
    # Add validation and routing labels
    local labels="$VALIDATION_LABEL,quality_score_$score,$label"
    log "Would add labels: $labels"
    # acli jira workitem edit "$ticket_key" --labels "$labels"
    
    log "Routing applied successfully for $ticket_key"
}

# Function: Generate validation feedback
generate_feedback() {
    local ticket_key="$1"
    local result="$2"
    local score="$3"
    shift 3
    local issues=("$@")
    
    local feedback_file="/tmp/feedback_${ticket_key}.txt"
    
    case "$result" in
        "APPROVED")
            cat > "$feedback_file" << EOF
✅ VALIDATION PASSED - ROUTED TO ENGINEERING QUEUE

Your ticket has been validated and meets quality standards.

Quality Score: $score/10
Status: Moved to Engineering Queue with "engq" label
Next Step: Engineering team will review and prioritize your ticket

Thank you for the clear submission!
EOF
            ;;
        "APPROVED_WITH_NOTES")
            cat > "$feedback_file" << EOF
✅ VALIDATION PASSED - ROUTED TO ENGINEERING QUEUE

Your ticket has been approved for engineering work.

Quality Score: $score/10
Status: Moved to Engineering Queue with "engq" label

Minor suggestions for improvement:
$(for issue in "${issues[@]}"; do echo "- $issue"; done)

Next Steps: Engineering team will review and prioritize your ticket.
EOF
            ;;
        "NEEDS_CLARIFICATION")
            cat > "$feedback_file" << EOF
⚠️ ROUTED TO ENGINEERING QUEUE WITH CLARIFICATIONS NEEDED

Your ticket has been routed to engineering but needs additional information for effective troubleshooting.

Quality Score: $score/10
Status: Moved to Engineering Queue with "engq" label

Please provide:
$(for issue in "${issues[@]}"; do echo "- $issue"; done)

Engineering will work with you to gather the missing information.
EOF
            ;;
        "PARKING_LOT")
            cat > "$feedback_file" << EOF
⏸️ MOVED TO PARKING LOT

Your ticket needs additional information before it can be reviewed by engineering.

Quality Score: $score/10 (Below threshold of 5.0)

Required improvements:
$(for issue in "${issues[@]}"; do echo "- $issue"; done)

Status: Your ticket has been moved to the Parking Lot for re-evaluation during the next monitoring cycle.
Action: Please update your ticket with the missing information above.
EOF
            ;;
    esac
    
    # Log feedback content using verbose logging function
    local feedback_content=$(cat "$feedback_file")
    log_feedback_content "$ticket_key" "$result" "$feedback_content"
    
    log "Generated feedback for $ticket_key:"
    cat "$feedback_file" | tee -a "$LOG_FILE"
    
    # In production, would post this comment:
    # acli jira workitem comment "$ticket_key" --body "$(cat "$feedback_file")"
    log "(In demo mode - feedback not posted to JIRA)"
}

# Function: Generate daily metrics
generate_metrics() {
    log "Generating daily metrics..."
    
    # Count tickets by timeframe
    TODAY_COUNT=$(acli jira workitem search --jql "project = $PROJECT AND created >= -1d" --count 2>/dev/null || echo "0")
    WEEK_COUNT=$(acli jira workitem search --jql "project = $PROJECT AND created >= -7d" --count 2>/dev/null || echo "0")
    TOTAL_COUNT=$(acli jira workitem search --jql "project = $PROJECT" --count 2>/dev/null || echo "0")
    
    # Create metrics report
    cat > "$REPORT_FILE" << EOF
=== TriQ Daily Monitoring Report ===
Date: $(date '+%Y-%m-%d')
Time: $(date '+%H:%M:%S')

TICKET COUNTS:
- New today: $TODAY_COUNT
- New this week: $WEEK_COUNT  
- Total in project: $TOTAL_COUNT

VALIDATION ACTIVITY:
- Monitoring sessions: 1
- Tickets processed: $(grep -c "Processing ticket:" "$LOG_FILE" 2>/dev/null || echo "0")
- Validations completed: $(grep -c "Validation Result:" "$LOG_FILE" 2>/dev/null || echo "0")

SYSTEM STATUS:
- JIRA connectivity: ✓ Working
- ACLI status: ✓ Functional
- Monitoring script: ✓ Completed successfully

Next scheduled run: $(date -v +3M '+%Y-%m-%d %H:%M:%S')
EOF
    
    log "Daily report generated:"
    cat "$REPORT_FILE" | tee -a "$LOG_FILE"
}

# Function: Check for emergency situations
check_emergencies() {
    log "Checking for emergency situations..."
    
    # Look for emergency keywords in recent tickets
    EMERGENCY_TICKETS=$(acli jira workitem search --jql "project = $PROJECT AND created >= -1d AND (summary ~ 'production' OR summary ~ 'critical' OR summary ~ 'emergency' OR summary ~ 'urgent')" 2>/dev/null || echo "")
    
    if [ -n "$EMERGENCY_TICKETS" ] && [ "$EMERGENCY_TICKETS" != "No issues found." ]; then
        log "🚨 POTENTIAL EMERGENCY TICKETS FOUND:"
        echo "$EMERGENCY_TICKETS" | tee -a "$LOG_FILE"
        
        # In production, would trigger alerts here
        log "Would trigger emergency notification to on-call team"
    else
        log "No emergency situations detected"
    fi
}

# Main monitoring execution
main() {
    log "Starting comprehensive monitoring check..."
    
    # Core monitoring functions
    check_new_tickets
    check_emergencies
    generate_metrics
    
    log "=== TriQ Monitoring Session Completed ==="
    log "Log file: $LOG_FILE"
    log "Report file: $REPORT_FILE"
}

# Execute main function
main "$@"