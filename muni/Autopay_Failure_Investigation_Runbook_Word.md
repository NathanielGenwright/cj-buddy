# Autopay Failure Investigation Runbook

**Document Version:** 1.0  
**Last Updated:** September 16, 2025  
**Document Owner:** Engineering Team  
**Review Cycle:** Quarterly  

---

## Executive Summary

This runbook provides a systematic approach to diagnose and resolve autopay failures for any company in the Muni billing system. The autopay process runs daily at 8:00 PM and processes recurring payments for all companies.

**Key System Information:**
- Job Name: RemoteChargeManagerJob
- Schedule: Daily at 8:00 PM (20:00)
- Queue: default_rails5
- Environment: Production only

---

## Table of Contents

1. Overview
2. Incident Response Priority
3. Investigation Checklist
   - Phase 1: Initial Triage (5 minutes)
   - Phase 2: System-Wide Failure Investigation
   - Phase 3: Company-Specific Investigation
   - Phase 4: Individual Customer Issues
4. Resolution Actions
5. Post-Incident Actions
6. Quick Reference Commands
7. Contact Information
8. Appendix

---

## 1. Overview

This runbook provides a systematic approach to diagnose and resolve autopay failures for any company in the Muni billing system. The autopay process runs daily at 8:00 PM and processes recurring payments for all companies.

### System Architecture Overview
- **Main Job:** RemoteChargeManagerJob (scheduled)
- **Processor:** RecurringBatchProcessor (batch logic)
- **Individual:** RecurringChargeProcessor (per customer)
- **Queue:** default_rails5 (Sidekiq)

---

## 2. Incident Response Priority

### Severity Levels

**P1 (Critical)**
- Description: Multiple companies affected, widespread autopay failure
- Response Time: 15 minutes
- Impact: System-wide revenue impact

**P2 (High)**
- Description: Single large company affected, >100 customers impacted
- Response Time: 30 minutes
- Impact: Significant revenue impact

**P3 (Medium)**
- Description: Single small company affected, <100 customers impacted
- Response Time: 2 hours
- Impact: Limited revenue impact

---

## 3. Investigation Checklist

### Phase 1: Initial Triage (5 minutes)

#### Step 1.1: Confirm Job Execution

**Objective:** Verify if the autopay job ran at all

**SQL Query:**
```
-- Look for ProcessHistory record (indicates successful completion)
SELECT * FROM process_histories 
WHERE process_rule_id = (SELECT id FROM process_rules WHERE rule_name = 'RECURRING_PAYMENTS')
AND created_at BETWEEN '[DATE] 19:00:00' AND '[DATE+1] 02:00:00';
```

**Expected Result:** One record created after 8:00 PM

**Decision Tree:**
- ✅ Record exists: Job completed successfully → Go to Phase 2
- ❌ No record: Job failed or didn't run → Go to Section 2.1

#### Step 1.2: Check System-Wide Impact

**SQL Query:**
```
-- Count companies that should have had autopay activity
SELECT c.company_name, COUNT(rc.id) as autopay_accounts
FROM companies c
JOIN customers cust ON c.id = cust.company_id  
JOIN recurring_charges rc ON cust.id = rc.customer_id
WHERE rc.next_charge_date = '[DATE]'
AND rc.recurring_charge_status_id = 1
GROUP BY c.id, c.company_name
HAVING COUNT(rc.id) > 0
ORDER BY COUNT(rc.id) DESC;
```

**Decision Point:**
- Multiple companies: P1 incident → System-wide failure
- Single company: P2/P3 incident → Company-specific issue

---

### Phase 2: System-Wide Failure Investigation

#### Step 2.1: Job Scheduling & Queue Issues

**Check Sidekiq Status:**
```
# In production environment
docker exec [container] bash -c "bundle exec rails runner \"
puts 'Sidekiq Queues:'
require 'sidekiq/api'
Sidekiq::Queue.new('default_rails5').each do |job|
  puts job.inspect if job.klass == 'RemoteChargeManagerJob'
end
\""
```

**Check Cron Job Status:**
```
# Verify whenever gem/cron is running
docker logs [job-container] --since [DATE]T20:00:00 | grep -i "recurring\|autopay"
```

**Potential Issues & Remediation:**
- Queue backed up: Scale Sidekiq workers or clear stuck jobs
- Cron not running: Restart job scheduler container
- Job failed: Check error logs and retry manually

#### Step 2.2: Database Connectivity Issues

**Test Database Performance:**
```
-- Test database performance
SELECT COUNT(*) FROM recurring_charges; -- Should return quickly

-- Check for locks
SHOW PROCESSLIST;
```

**Common Issues:**
- Long-running queries blocking autopay
- Database connection pool exhausted
- MySQL server issues

#### Step 2.3: Payment Gateway Status

**SQL Query:**
```
-- Check gateway health across all companies
SELECT pg.gateway_name, pgp.company_id, c.company_name, pgp.enabled, pgp.recurring_attempts
FROM payment_gateways pg
JOIN payment_gateway_profiles pgp ON pg.id = pgp.payment_gateway_id
JOIN companies c ON pgp.company_id = c.id
WHERE pgp.enabled = true AND pgp.recurring_attempts > 0
ORDER BY pg.gateway_name, c.company_name;
```

**Look For:**
- All profiles disabled (mass configuration change)
- Gateway-wide issues (Heartland/Paya down)

---

### Phase 3: Company-Specific Investigation

#### Step 3.1: Payment Gateway Configuration

**SQL Query:**
```
-- Check specific company's gateway setup
SELECT pgp.id, pgp.enabled, pgp.recurring_attempts, pgp.recurring_start_date, 
       pg.gateway_name, pgp.merchant_user_name
FROM payment_gateway_profiles pgp
JOIN payment_gateways pg ON pgp.payment_gateway_id = pg.id
WHERE pgp.company_id = [COMPANY_ID];
```

**Red Flags:**
- ❌ enabled = false → Gateway disabled
- ❌ recurring_attempts = 0 → Autopay disabled
- ❌ No records → No payment gateway configured

**Fix:** Re-enable gateway or contact company to configure autopay

#### Step 3.2: Customer Autopay Status

**SQL Query:**
```
-- Analyze customer autopay accounts for the company
SELECT 
  rc.recurring_charge_status_id,
  CASE rc.recurring_charge_status_id
    WHEN 1 THEN 'ACTIVE'
    WHEN 2 THEN 'CANCELLED' 
    ELSE 'UNKNOWN'
  END as status,
  COUNT(*) as customer_count,
  AVG(rc.recurring_amount) as avg_amount
FROM recurring_charges rc
JOIN customers c ON rc.customer_id = c.id
WHERE c.company_id = [COMPANY_ID]
GROUP BY rc.recurring_charge_status_id
ORDER BY rc.recurring_charge_status_id;
```

**Analysis:**
- All CANCELLED: Mass suspension due to failures → Check error logs
- Mixed status: Normal → Check individual failure reasons

#### Step 3.3: Next Charge Date Analysis

**SQL Query:**
```
-- Check when customers are scheduled for autopay
SELECT 
  rc.next_charge_date,
  COUNT(*) as customer_count
FROM recurring_charges rc
JOIN customers c ON rc.customer_id = c.id
WHERE c.company_id = [COMPANY_ID]
AND rc.recurring_charge_status_id = 1
GROUP BY rc.next_charge_date
ORDER BY rc.next_charge_date DESC
LIMIT 10;
```

**Expected:** Customers scheduled for target date

**Issues:**
- No customers scheduled for incident date
- All dates in the past (scheduling issue)
- All dates in the future (premature scheduling)

#### Step 3.4: Recent Error Investigation

**SQL Query:**
```
-- Check for system notifications/errors
SELECT created_at, title, description
FROM notifications
WHERE created_at BETWEEN '[DATE] 19:00:00' AND '[DATE+1] 02:00:00'
AND (description LIKE '%[COMPANY_NAME]%' 
     OR description LIKE '%autopay%' 
     OR description LIKE '%recurring%')
ORDER BY created_at DESC;
```

---

### Phase 4: Individual Customer Issues

#### Step 4.1: Detailed Customer Analysis

**SQL Query:**
```
-- Get specific customer details that should have processed
SELECT 
  c.id as customer_id,
  c.customer_number,
  c.automatic_payments,
  rc.recurring_amount,
  rc.next_charge_date,
  rc.attempts_this_cycle,
  rc.display_message,
  pgp.recurring_attempts as max_attempts
FROM customers c
JOIN recurring_charges rc ON c.id = rc.customer_id
JOIN payment_gateway_profiles pgp ON rc.payment_gateway_profile_id = pgp.id
WHERE c.company_id = [COMPANY_ID]
AND rc.next_charge_date = '[DATE]'
AND rc.recurring_charge_status_id = 1
LIMIT 10;
```

**Red Flags:**
- automatic_payments = false → Customer flag disabled
- attempts_this_cycle >= max_attempts → Customer hit retry limit
- recurring_amount = 0 → Nothing to charge

#### Step 4.2: Payment History Analysis

**SQL Query:**
```
-- Check recent payment attempts for patterns
SELECT 
  rc.remote_response_code,
  rc.remote_message,
  rc.display_message,
  COUNT(*) as occurrence_count
FROM remote_charges rc
JOIN customers c ON rc.customer_id = c.id
WHERE c.company_id = [COMPANY_ID]
AND rc.created_at >= DATE_SUB('[DATE]', INTERVAL 7 DAY)
AND rc.remote_charge_type_id IN (
  SELECT id FROM remote_charge_types WHERE charge_type LIKE '%AUTO%'
)
GROUP BY rc.remote_response_code, rc.remote_message, rc.display_message
ORDER BY COUNT(*) DESC;
```

---

## 4. Resolution Actions

### Immediate Fixes

#### Option 1: Manual Job Trigger (Recommended)

**Steps:**
1. Navigate to Admin → Tools → Nightly Jobs
2. Set batch date to incident date
3. Click "Launch autopay job"
4. Monitor progress in logs

#### Option 2: Rails Console Manual Trigger

**Ruby Code:**
```
# In production Rails console
date = Date.parse('[INCIDENT_DATE]')
Charges::Utils::RemoteChargeManager.new.get_recurring_payments(date)
```

#### Option 3: Company-Specific Processing

**Ruby Code:**
```
# Process specific company only
company_id = [COMPANY_ID]
batch_processor = Charges::Utils::RecurringBatchProcessor.new(
  batch_date: Date.parse('[DATE]'),
  batch_reason: "Manual recovery - Incident #[TICKET]"
)

# Get affected customers
customers = batch_processor.recurring_charges.joins(:customer)
                          .where(customers: {company_id: company_id})

# Process each customer
customers.find_each do |recurring_charge|
  batch_processor.process_one(
    recurring_charge: recurring_charge,
    call_reason: "Manual recovery"
  )
end
```

### Configuration Fixes

#### Re-enable Payment Gateway

**SQL Query:**
```
UPDATE payment_gateway_profiles 
SET enabled = true, recurring_attempts = 3
WHERE company_id = [COMPANY_ID] AND enabled = false;
```

#### Reset Suspended Customers

**SQL Query:**
```
-- Re-activate suspended autopay accounts
UPDATE recurring_charges rc
JOIN customers c ON rc.customer_id = c.id
SET rc.recurring_charge_status_id = 1,
    rc.attempts_this_cycle = 0,
    rc.display_message = 'Reactivated after incident',
    c.automatic_payments = true
WHERE c.company_id = [COMPANY_ID]
AND rc.recurring_charge_status_id = 2;
```

#### Fix Next Charge Dates

**Ruby Code:**
```
# Reschedule all customers to next appropriate date
company_id = [COMPANY_ID]
RecurringCharge.joins(:customer)
               .where(customers: {company_id: company_id})
               .find_each do |rc|
  rc.next_charge_date = rc.payment_gateway_profile.next_payment_date
  rc.save!
end
```

---

## 5. Post-Incident Actions

### Verification Steps
1. **Confirm fix:** Re-run investigation queries to verify resolution
2. **Test next cycle:** Monitor next night's autopay run
3. **Customer communication:** Notify affected customers if payments were delayed
4. **Document findings:** Update incident tracking system

### Preventive Measures
1. **Add monitoring:** Set up alerts for ProcessHistory records
2. **Health checks:** Implement payment gateway health monitoring
3. **Documentation:** Update runbook with any new findings
4. **Review:** Schedule post-incident review if P1/P2 severity

---

## 6. Quick Reference Commands

### Emergency Manual Trigger
```
# One-liner to manually run autopay for specific date
docker exec [container] bash -c "cd /usr/src/app && bundle exec rails runner \"Charges::Utils::RemoteChargeManager.new.get_recurring_payments(Date.parse('[YYYY-MM-DD]'))\""
```

### Status Check
```
-- Quick health check query
SELECT 
  'Job Execution' as check_type,
  CASE WHEN COUNT(*) > 0 THEN '✅ PASS' ELSE '❌ FAIL' END as status
FROM process_histories 
WHERE process_rule_id = (SELECT id FROM process_rules WHERE rule_name = 'RECURRING_PAYMENTS')
AND created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)

UNION ALL

SELECT 
  'Active Gateways' as check_type,
  CONCAT('✅ ', COUNT(*), ' companies') as status
FROM payment_gateway_profiles 
WHERE enabled = true AND recurring_attempts > 0;
```

### Common Company IDs

**Beach City:** 1720 (Example from incident)
**[Add others]:** [ID] ([Notes])

---

## 7. Contact Information

### Primary Contacts

**On-call Engineer**
- Name: [Name]
- Phone: [Phone]
- Email: [Email]

**Database Admin**
- Name: [Name]
- Phone: [Phone]
- Email: [Email]

**Payment Gateway Support**
- Vendor: [Vendor]
- Phone: [Phone]
- Email: [Email]

**Escalation Manager**
- Name: [Name]
- Phone: [Phone]
- Email: [Email]

### Vendor Support
- **Heartland:** [Contact info]
- **Paya Connect:** [Contact info]

---

## 8. Appendix

### A. Database Tables

**process_histories** - Job execution tracking
**recurring_charges** - Customer autopay records
**payment_gateway_profiles** - Gateway configuration
**customers** - Customer autopay flags
**notifications** - System error messages

### B. Key Status Codes

**recurring_charge_status_id = 1** → ACTIVE
**recurring_charge_status_id = 2** → CANCELLED
**automatic_payments = true** → Customer enrolled
**enabled = true** → Gateway active
**recurring_attempts > 0** → Retries allowed

### C. System Requirements

**Environment:** Production only
**Database:** MySQL with SSL required
**Queue System:** Sidekiq (default_rails5 queue)
**Job Scheduler:** Whenever gem with cron syntax

---

**Document Control:**
- Created: September 16, 2025
- Format: Word compatible
- Distribution: Engineering Team, Support Team, Management
- Classification: Internal Use

**⚠️ IMPORTANT:** Always test fixes in staging first unless it's a P1 incident requiring immediate production intervention.