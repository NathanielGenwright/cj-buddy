# TriQ System - Perpetual TODO List

**Last Updated:** 2025-10-23
**Purpose:** Master checklist for all TriQ system work - ALWAYS consult before planning or executing tasks

**🎉 NEW: TriQ Dashboard POC Available!** See "Monitoring & Dashboard" section below.

---

## PRE-LIVE DEPLOYMENT CHECKLIST

### 🚨 CRITICAL: Enable Live JIRA Updates
**File:** `/Users/munin8/_myprojects/triq-monitor.sh`

**Required Changes to Go Live:**

- [ ] **Line 511** - Uncomment manual evaluation label addition:
  ```bash
  # CURRENT: # acli jira workitem edit "$ticket_key" --labels "triq_manual_eval"
  # CHANGE TO: acli jira workitem edit "$ticket_key" --labels "triq_manual_eval"
  ```

- [ ] **Line 551** - Uncomment status update (Eng Queue / Parking Lot routing):
  ```bash
  # CURRENT: # acli jira workitem edit "$ticket_key" --status "$status"
  # CHANGE TO: acli jira workitem edit "$ticket_key" --status "$status"
  ```

- [ ] **Line 556** - Uncomment validation labels addition:
  ```bash
  # CURRENT: # acli jira workitem edit "$ticket_key" --labels "$labels"
  # CHANGE TO: acli jira workitem edit "$ticket_key" --labels "$labels"
  ```

- [ ] **Line 640** - Uncomment feedback comment posting:
  ```bash
  # CURRENT: # acli jira workitem comment "$ticket_key" --body "$(cat "$feedback_file")"
  # CHANGE TO: acli jira workitem comment "$ticket_key" --body "$(cat "$feedback_file")"
  ```

- [ ] **Line 641** - Remove demo mode log message:
  ```bash
  # DELETE: log "(In demo mode - feedback not posted to JIRA)"
  ```

**What This Enables:**
- ✅ Automatic ticket status updates (route to Eng Queue or Parking Lot)
- ✅ Automatic label addition (triq_validated, quality_score_X, engq, parking_lot)
- ✅ Automatic feedback comments on tickets
- ✅ Manual evaluation escalation for stuck tickets (5+ evaluations)
  - Adds "triq_manual_eval" label
  - Excludes ticket from future automatic processing
  - Requires manual intervention to resolve

---

## SYSTEM CONFIGURATION

### Pre-Deployment Testing
- [ ] Verify ACLI authentication: `acli jira project list --limit 1`
- [ ] Test JIRA connectivity from monitoring script
- [ ] Run triq-monitor.sh in current demo mode to verify logic
- [ ] Review verbose logging output for accuracy
- [ ] Test urgency/impact custom field extraction (cf[10450], cf[10451])

### Monitoring Schedule
- [ ] Configure cron job or scheduled task (currently: every 3 minutes)
- [ ] Set up log rotation for `/tmp/triq-monitor.log`
- [ ] Configure admin notification delivery mechanism
- [ ] Test emergency ticket detection workflow

### JIRA Project Configuration
- [ ] Verify "Eng Queue" status exists in EP project workflow
- [ ] Verify "Parking Lot" status exists in EP project workflow
- [ ] Verify "Initial Review" status for intake tickets
- [ ] Confirm custom fields cf[10450] (Urgency) and cf[10451] (Impact) are populated
- [ ] Understand "triq_manual_eval" label usage for manual escalation exclusions

---

## LABEL-BASED EXCLUSION SYSTEM

### triq_manual_eval Label
**Purpose:** Exclude tickets from automatic validation after 5+ failed evaluation cycles

**How It Works:**
1. TriQ tracks evaluation count per ticket in `/tmp/triq-evaluation-counts.txt`
2. When ticket reaches 5 evaluations while stuck in "Initial Review" or "Parking Lot":
   - Adds "triq_manual_eval" label to ticket
   - Creates admin notification file: `/tmp/admin_notification_{ticket}.txt`
   - Logs escalation warning
3. JQL query excludes tickets with this label: `labels NOT IN (triq_manual_eval)`
4. Ticket will NOT appear in future monitoring cycles

**Re-enabling Automatic Validation:**
```bash
# Remove the label to allow TriQ to process the ticket again
acli jira workitem edit EP-XXX --labels "-triq_manual_eval"
```

**Finding Escalated Tickets:**
```bash
# List all tickets needing manual intervention
acli jira workitem search --jql "project = EP AND labels = triq_manual_eval"

# Check specific ticket status
acli jira workitem view EP-XXX
```

**Admin Actions for Escalated Tickets:**
- Review ticket quality and provide guidance to submitter
- Provide training if pattern of poor quality submissions
- Override validation and manually route to Eng Queue if appropriate
- Close ticket if it's spam, duplicate, or inappropriate
- Remove "triq_manual_eval" label to re-enable automatic processing

---

## ONGOING MAINTENANCE

### Daily Monitoring Tasks
- [ ] Review evaluation counter: `/tmp/triq-evaluation-counts.txt`
- [ ] Check manual evaluation escalations: `/tmp/admin_notification_*.txt`
- [ ] Review tickets with "triq_manual_eval" label needing intervention
- [ ] Analyze validation logs: `/tmp/triq-monitor.log`
- [ ] Review daily metrics: `/tmp/triq-daily-report.txt`
- [ ] Monitor tickets stuck in "Parking Lot" for improvement patterns

### Weekly Analysis
- [ ] Review quality score trends
- [ ] Analyze most common validation failures
- [ ] Identify submitters needing additional training
- [ ] Evaluate feedback template effectiveness
- [ ] Check SLA compliance for priority assignments

### Monthly Optimization
- [ ] Update validation rules based on patterns: `jira-validation-rules.md`
- [ ] Refine quality rubric scoring: `jira-triage-quality-rubric.md`
- [ ] Update feedback templates: `jira-feedback-templates.md`
- [ ] Review and adjust admin escalation threshold (currently: 5 evaluations)

---

## DOCUMENTATION REFERENCES

### Core Agent Files
- **Agent Definition:** `/Users/munin8/_myprojects/.claude/agents/jira-triage-validator.md`
- **Quality Rubric:** `/Users/munin8/_myprojects/jira-triage-quality-rubric.md`
- **Validation Rules:** `/Users/munin8/_myprojects/jira-validation-rules.md`
- **Feedback Templates:** `/Users/munin8/_myprojects/jira-feedback-templates.md`
- **Operational Workflows:** `/Users/munin8/_myprojects/triq-workflows.md`
- **Deployment Guide:** `/Users/munin8/_myprojects/triq-deployment-guide.md`

### Monitoring & Analysis
- **Monitoring Script:** `/Users/munin8/_myprojects/triq-monitor.sh`
- **TRI Workflow Analysis:** `/Users/munin8/_myprojects/TRI_Workflow_Analysis_Report.md`
- **Triage Board Assessment:** `/Users/munin8/_myprojects/triage-board-assessment-2025-10-02.md`

### Business Operations Integration
- **MuniBilling Priority Matrix:** Issue Classifications.docx (OneDrive)
- **Custom Field Mappings:**
  - cf[10413]: Company field
  - cf[10450]: Urgency field (Critical/High/Medium/Low)
  - cf[10451]: Impact field

---

## PRIORITY VALIDATION FRAMEWORK

### Urgency + Impact → Priority Matrix
```
              Impact
            High  Medium  Low
Urgency High   1     2     3
       Medium  2     3     4
        Low    3     4     5
```

### SLA Expectations by Priority
- **Priority 1 (Critical):** 15 min response, 2 hour resolution
- **Priority 2 (High):** 30 min response, 1 business day resolution
- **Priority 3 (Medium):** 1 hour response, 2 business days resolution
- **Priority 4 (Low):** 4 hours response, 5 business days resolution
- **Priority 5 (Very Low):** 1 business day response, 10 business days resolution

---

## QUALITY SCORING THRESHOLDS

### Weighted Category Scoring
1. **Summary Validation:** 25% weight
2. **Description Validation:** 35% weight
3. **Technical Context:** 20% weight
4. **Business Context:** 15% weight
5. **Metadata Validation:** 5% weight

### Routing Decisions
- **9.5-10.0:** APPROVE → Eng Queue + engq label
- **9.0-9.4:** APPROVE → Eng Queue + engq label
- **8.5-8.9:** APPROVE_WITH_NOTES → Eng Queue + engq label
- **8.0-8.4:** APPROVE_WITH_NOTES → Eng Queue + engq label
- **7.5-7.9:** APPROVE_WITH_NOTES → Eng Queue + engq label
- **7.0-7.4:** APPROVE_WITH_NOTES → Eng Queue + engq label
- **6.0-6.9:** NEEDS_CLARIFICATION → Eng Queue + engq label
- **5.1-5.9:** NEEDS_CLARIFICATION → Eng Queue + engq label
- **≤5.0:** PARKING_LOT → Parking Lot status for re-evaluation

---

## MONITORING & DASHBOARD

### TriQ Dashboard POC (NEW!)
**Location:** `/Users/munin8/_myprojects/triq-dashboard/`

**Quick Start:**
```bash
cd /Users/munin8/_myprojects/triq-dashboard
./start.sh
# Open browser: http://localhost:5000
```

**Features:**
- ✅ Real-time metrics: Total tickets, avg score, approval rates
- ✅ Tickets table with color-coded scores (green/yellow/red)
- ✅ Auto-refresh every 180 seconds (3 minutes)
- ✅ SQLite database (no infrastructure needed)
- ✅ Flask web UI (minimal dependencies)

**Updating Data:**
```bash
# Re-parse logs anytime for fresh data
python3 triq_db.py

# Dashboard auto-refreshes within 3 minutes
```

**Documentation:**
- Quick Start: `triq-dashboard/QUICK_START.txt`
- Full Docs: `triq-dashboard/README.md`

**Current Stats (as of 2025-10-23):**
- 13,358 log entries parsed
- 8 unique tickets tracked
- 238 scored validations
- 3.79/10 average quality score

---

## ESCALATION WORKFLOWS

### Manual Evaluation Escalation (5+ Evaluations)
- **Evaluation threshold:** 5+ evaluations in "Initial Review" or "Parking Lot"
- **Auto-actions:**
  - Add "triq_manual_eval" label to ticket
  - Generate notification file: `/tmp/admin_notification_{ticket}.txt`
  - Log escalation warning
  - **EXCLUDE from future automatic evaluations** (ticket needs manual intervention)
- **Effect:** Ticket will NOT appear in future TriQ monitoring cycles until label is removed
- **Re-enable automatic validation:** Remove "triq_manual_eval" label from ticket

### Emergency Ticket Handling
- **Keywords:** "production down", "system unavailable", "all users affected", "critical"
- **Response:** Bypass validation for immediate escalation (15-minute SLA)
- **Template:** S1 (Emergency escalation)

### Security Issue Routing
- **Keywords:** "login", "password", "unauthorized", "authentication", "security"
- **Actions:**
  - Apply Template R3
  - Flag for security review
  - Escalate to security team within 1 hour

---

## TROUBLESHOOTING GUIDE

### Common Issues
- **ACLI connectivity failures:** Check `acli jira project list --limit 1`
- **Custom field extraction errors:** Verify cf[10450] and cf[10451] exist and are populated
- **Evaluation counter not incrementing:** Check write permissions on `/tmp/triq-evaluation-counts.txt`
- **Admin notifications not generating:** Verify threshold logic (line 495-498 in triq-monitor.sh)

### Log Analysis Commands
```bash
# Check recent validations
tail -n 100 /tmp/triq-monitor.log | grep "VALIDATION"

# Count evaluations by ticket
cat /tmp/triq-evaluation-counts.txt | sort -t: -k2 -rn

# Find tickets needing admin review
grep "ADMIN REVIEW NEEDED" /tmp/triq-monitor.log

# Check emergency ticket detection
grep "EMERGENCY TICKETS" /tmp/triq-monitor.log
```

---

## USAGE INSTRUCTIONS

### Before Any TriQ Work:
1. **Read this file completely**
2. **Check current system status** (demo mode vs live mode)
3. **Review uncompleted checklist items**
4. **Update this file** with new requirements or changes
5. **Proceed with planned work**

### After Completing Work:
1. **Update checklist items** (mark complete or add new items)
2. **Document changes** in this file
3. **Update "Last Updated" date** at top of file
4. **Commit changes** to version control

---

## CHANGE LOG

| Date | Change | Updated By |
|------|--------|------------|
| 2025-10-23 | Initial perpetual TODO list created | Claude |
| | Identified 5 demo mode lines blocking JIRA updates | |
| | Documented all pre-live deployment requirements | |

---

**⚠️ REMINDER:** This is a living document. Keep it updated as TriQ evolves!
