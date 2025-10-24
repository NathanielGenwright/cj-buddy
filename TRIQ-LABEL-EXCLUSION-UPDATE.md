# TriQ Label-Based Exclusion System Update

**Date:** 2025-10-23
**Status:** Implemented (Demo Mode)

---

## Overview

Updated TriQ monitoring system to automatically exclude tickets from future automatic validation after 5+ evaluation cycles. This prevents the system from repeatedly evaluating tickets that clearly need manual intervention.

---

## Changes Made

### 1. Updated JQL Query (triq-monitor.sh:113)

**Before:**
```bash
NEW_TICKETS=$(acli jira workitem search --jql "project = $PROJECT AND status IN ('Initial Review', 'Parking Lot')" 2>/dev/null || echo "")
```

**After:**
```bash
NEW_TICKETS=$(acli jira workitem search --jql "project = $PROJECT AND status IN ('Initial Review', 'Parking Lot') AND labels NOT IN (triq_manual_eval)" 2>/dev/null || echo "")
```

**Effect:** Tickets with "triq_manual_eval" label will NOT appear in search results and will be excluded from automatic processing.

---

### 2. Updated Escalation Function (triq-monitor.sh:502-544)

**Label Changed:**
- Old: `admin_review_needed`
- New: `triq_manual_eval`

**Function Behavior:**
```bash
escalate_to_admin() {
    # When ticket hits 5+ evaluations:
    # 1. Adds "triq_manual_eval" label (line 511 - currently commented)
    # 2. Creates admin notification file
    # 3. Logs escalation with exclusion notice
}
```

**Admin Notification Enhanced:**
- Clearly states label applied: `triq_manual_eval`
- Explains automatic evaluations are disabled
- Provides instructions to re-enable (remove label)

---

### 3. Updated Documentation (TRIQ-TODO.md)

**Added New Section:** "LABEL-BASED EXCLUSION SYSTEM"
- Explains how the label works
- Shows how to find escalated tickets
- Documents admin actions for resolution
- Provides commands to re-enable automatic validation

**Updated Sections:**
- Pre-Live Deployment Checklist (line 17-21)
- System Configuration (line 77)
- Daily Monitoring Tasks (line 86)
- Escalation Workflows (line 208-216)

---

## How It Works

### Automatic Escalation Workflow

```
Ticket enters "Initial Review" or "Parking Lot"
                ↓
TriQ validates ticket (evaluation #1)
                ↓
Score < 5.0 → stays in Parking Lot
                ↓
Next monitoring cycle (3 minutes later)
                ↓
TriQ validates again (evaluation #2)
                ↓
... continues up to evaluation #5 ...
                ↓
Evaluation #5 reached
                ↓
✅ Add "triq_manual_eval" label
✅ Create admin notification
✅ Log escalation warning
                ↓
🚫 EXCLUDED from future automatic cycles
```

### Manual Intervention Required

Admin must:
1. Review ticket quality
2. Provide guidance or training to submitter
3. Take one of these actions:
   - **Route to Eng Queue** (if appropriate despite low score)
   - **Close ticket** (if spam/duplicate/invalid)
   - **Improve ticket** and remove label to re-enable validation
   - **Provide training** and close if pattern of poor quality

---

## Finding Escalated Tickets

### List All Manual Evaluation Tickets
```bash
acli jira workitem search --jql "project = EP AND labels = triq_manual_eval"
```

### Check Specific Ticket
```bash
acli jira workitem view EP-XXX
```

### Review Admin Notifications
```bash
ls /tmp/admin_notification_*.txt
cat /tmp/admin_notification_EP-XXX.txt
```

---

## Re-enabling Automatic Validation

### Remove the Label
```bash
# After ticket is improved or manually resolved
acli jira workitem edit EP-XXX --labels "-triq_manual_eval"
```

**Effect:** Ticket will appear in next monitoring cycle (within 3 minutes) and TriQ will evaluate it again.

---

## Benefits

1. **Prevents Infinite Loops:** Stops system from repeatedly evaluating hopeless tickets
2. **Reduces Noise:** Log files and metrics focus on actionable tickets
3. **Clear Escalation Path:** Admin knows which tickets need intervention
4. **Easy Re-enabling:** Simple label removal restarts automatic processing
5. **Audit Trail:** Admin notifications document why tickets were escalated

---

## Current Status (Demo Mode)

**Label Addition:** Currently commented out (line 511)
**When Enabled:** Requires uncommenting ACLI command

```bash
# DEMO MODE (current)
# acli jira workitem edit "$ticket_key" --labels "triq_manual_eval"

# LIVE MODE (uncomment when ready)
acli jira workitem edit "$ticket_key" --labels "triq_manual_eval"
```

---

## Testing Recommendations

Before going live:

1. **Test JQL Exclusion:**
   ```bash
   # Manually add label to test ticket
   acli jira workitem edit EP-999 --labels "triq_manual_eval"
   
   # Verify it's excluded from search
   acli jira workitem search --jql "project = EP AND status IN ('Initial Review', 'Parking Lot') AND labels NOT IN (triq_manual_eval)"
   ```

2. **Test Label Removal:**
   ```bash
   # Remove label
   acli jira workitem edit EP-999 --labels "-triq_manual_eval"
   
   # Verify it appears in search again
   ```

3. **Verify Escalation Threshold:**
   - Check `/tmp/triq-evaluation-counts.txt` accuracy
   - Confirm count reaches 5 before escalation
   - Verify admin notification file creation

---

## Migration Path

### Current State
- System tracks evaluation counts
- Escalation triggers at 5+ evaluations
- Label addition is commented out (demo mode)
- JQL exclusion is active (already filtering)

### To Enable Live Mode
1. Uncomment line 511 in `triq-monitor.sh`
2. Test with low-quality test ticket
3. Verify label is applied at evaluation #5
4. Verify ticket is excluded from next cycle
5. Test label removal and re-validation

---

## Documentation Updates

All documentation has been updated:
- ✅ TRIQ-TODO.md (comprehensive guide)
- ✅ triq-monitor.sh (inline comments)
- ✅ This migration document

---

## Future Enhancements

Potential improvements:
- Dashboard view showing all `triq_manual_eval` tickets
- Email/Slack notifications when tickets are escalated
- Automatic label removal after X days of inactivity
- Reporting on escalation rate trends
- Integration with TriQ dashboard "Manual Intervention Queue"

---

**Updated By:** Claude Code  
**Last Updated:** 2025-10-23
