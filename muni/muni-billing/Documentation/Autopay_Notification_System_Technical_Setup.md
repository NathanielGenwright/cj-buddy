# Autopay Notification System - Technical Setup Documentation

**Document Type:** Internal Technical Reference
**Target Audience:** Engineering, DevOps, Support Teams
**Format:** External Document (Copy to Confluence/SharePoint)

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Components](#2-architecture-components)
3. [Notification Types](#3-notification-types)
4. [Happy Path Flow](#4-happy-path-flow)
5. [Customer Eligibility Requirements](#5-customer-eligibility-requirements)
6. [Configuration Requirements](#6-configuration-requirements)
7. [Email Addresses & Accounts](#7-email-addresses--accounts)
8. [SendGrid Templates](#8-sendgrid-templates)
9. [Retry Logic & Failure Handling](#9-retry-logic--failure-handling)
10. [Environment Differences](#10-environment-differences)
11. [Scheduling & Jobs](#11-scheduling--jobs)
12. [Database Schema Reference](#12-database-schema-reference)
13. [Known Bottlenecks & Troubleshooting](#13-known-bottlenecks--troubleshooting)
14. [Monitoring & Observability](#14-monitoring--observability)
15. [Quick Reference](#15-quick-reference)

---

## 1. System Overview

### What is Autopay?

Autopay (Recurring Payments) is the automated payment system that charges customers on a scheduled basis using stored payment credentials. The notification system sends emails (and optionally SMS/voice) to customers at key points in the autopay lifecycle.

### Four Notification Types

| Notification | Purpose | Timing |
|--------------|---------|--------|
| **10-Day Warning** | Advance notice of upcoming charge | 10 days before charge date |
| **Successful Payment** | Confirm payment processed | Immediately after success |
| **Failed - Will Retry** | Payment failed, retrying tomorrow | After each failed attempt |
| **Failed - Dropped** | Payment failed, enrollment cancelled | After max retries exhausted |

### Key Capabilities

- Multi-channel delivery (Email, SMS, Voice)
- Configurable retry attempts per payment gateway
- Automatic enrollment suspension after max failures
- Customer-specific notification preferences
- Company-specific branding and templates
- SendGrid template-based emails

---

## 2. Architecture Components

### File Structure

```
muni-billing/legacy/
├── app/
│   ├── jobs/
│   │   ├── remote_charge_manager_job.rb              # 8 PM - Process autopay
│   │   └── remote_charge_manager_notifications_job.rb # 6 PM - 10-day warnings
│   ├── gateways/
│   │   └── sendgrid_gateway.rb                       # SendGrid API integration
│   ├── models/
│   │   ├── recurring_charge.rb                       # Autopay enrollment record
│   │   ├── payment_gateway_profile.rb                # Gateway configuration
│   │   ├── remote_charge.rb                          # Individual charge record
│   │   └── recurring_charge_validator.rb             # Validation rules
│   └── lib/notices/
│       ├── builders/
│       │   ├── recurring_charge_notice.rb            # Notice router
│       │   └── recurring_charges/
│       │       ├── common.rb                         # Shared utilities
│       │       ├── upcoming_autopay_notice.rb        # 10-day warning
│       │       ├── successful_autopay_notice.rb      # Success notification
│       │       ├── failed_will_retry_autopay_notice.rb    # Retry notification
│       │       ├── failed_cancelling_autopay_notice.rb    # Dropped notification
│       │       └── service_options/
│       │           ├── sendgrid_upcoming_autopay_notice.rb
│       │           ├── sendgrid_successful_autopay_notice.rb
│       │           ├── sendgrid_failed_will_retry_autopay_notice.rb
│       │           └── sendgrid_failed_cancelling_autopay_notice.rb
│       └── service_option_base/
│           └── sendgrid_email.rb                     # Base SendGrid class
├── lib/charges/
│   └── utils/
│       ├── remote_charge_manager.rb                  # Orchestration layer
│       ├── recurring_batch_processor.rb              # Batch processing
│       └── recurring_charge_processor.rb             # Individual charge processing
└── config/
    └── schedule.yml                                  # Cron job definitions
```

### Process Flow Overview

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  6 PM Daily         │     │  8 PM Daily         │     │  Charge Processor   │
│  10-Day Warnings    │     │  Process Autopay    │     │  Decision Tree      │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
         │                           │                           │
         ▼                           ▼                           ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  Find charges due   │     │  RecurringBatch     │     │  Success?           │
│  in 10 days         │     │  Processor          │     │  → Success Notice   │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
         │                           │                           │
         ▼                           ▼                           ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  SendGrid API       │     │  For each charge:   │     │  Fail + Retry?      │
│  10-Day Template    │     │  RecurringCharge    │     │  → Retry Notice     │
└─────────────────────┘     │  Processor          │     └─────────────────────┘
                            └─────────────────────┘              │
                                     │                           ▼
                                     ▼                  ┌─────────────────────┐
                            ┌─────────────────────┐     │  Max Failures?      │
                            │  Process Payment    │     │  → Dropped Notice   │
                            │  via Gateway        │     │  + Unenroll         │
                            └─────────────────────┘     └─────────────────────┘
```

---

## 3. Notification Types

### 3.1 Ten-Day Warning (Upcoming Autopay)

| Attribute | Value |
|-----------|-------|
| **Purpose** | Advance notice of scheduled charge |
| **Template ID** | `ee494e99-bd7f-484d-bd5a-fb4f22adef9b` |
| **Subject** | "Automatic Payment Scheduled" |
| **Trigger** | Cron job at 6 PM daily |
| **Class** | `UpcomingAutopayNotice` → `SendgridUpcomingAutopayNotice` |
| **Timing** | 10 days before `next_charge_date` |

### 3.2 Successful Payment

| Attribute | Value |
|-----------|-------|
| **Purpose** | Confirm successful autopay charge |
| **Template ID** | `132e00ee-e9a8-44c3-9d1a-c29235afd28b` |
| **Subject** | "Successful Autopayment" |
| **Trigger** | Payment processes successfully |
| **Class** | `SuccessfulAutopayNotice` → `SendgridSuccessfulAutopayNotice` |
| **Timing** | Immediately after successful charge |

### 3.3 Failed - Will Retry Tomorrow

| Attribute | Value |
|-----------|-------|
| **Purpose** | Inform customer of failure, indicate retry |
| **Template ID** | `36c89d58-edce-49a6-a425-cc85c7b738fb` |
| **Subject** | "Autopayment Failed - Retrying Tomorrow" |
| **Trigger** | Payment fails but retries remain |
| **Class** | `FailedWillRetryAutopayNotice` → `SendgridFailedWillRetryAutopayNotice` |
| **Timing** | After each failed attempt (if retries available) |

### 3.4 Failed - Enrollment Dropped

| Attribute | Value |
|-----------|-------|
| **Purpose** | Inform customer autopay is cancelled |
| **Template ID** | `5470a6f1-1212-4dc3-9150-a37cdee02c64` |
| **Subject** | "Autopayment Failed - Unenrolled from Autopay" |
| **Trigger** | Max retries exhausted |
| **Class** | `FailedCancellingAutopayNotice` → `SendgridFailedCancellingAutopayNotice` |
| **Timing** | After final failed attempt |

---

## 4. Happy Path Flow

### Phase 1: 10-Day Warning (6 PM Daily)

1. `RemoteChargeManagerNotificationsJob.perform()` executes
2. Calls `RemoteChargeManager.recurring_payments_notification(Date.current + 10)`
3. Finds all active recurring charges with `next_charge_date` = today + 10 days
4. For each eligible charge:
   - Builds personalization data (account, amount, dates)
   - Calls `notice_builder.for(:ten_day_notification).call(personalizations)`
5. `SendgridUpcomingAutopayNotice` sends via SendGrid API

**Code Reference:** `lib/charges/utils/remote_charge_manager.rb:181-231`

### Phase 2: Payment Processing (8 PM Daily)

1. `RemoteChargeManagerJob.perform()` executes
2. Calls `RemoteChargeManager.get_recurring_payments(Date.current)`
3. Creates `RecurringBatchProcessor` with today's date
4. `RecurringBatchProcessor.call()`:
   - Finds all active charges due today
   - For each: creates `RecurringChargeProcessor`

**Code Reference:** `lib/charges/utils/remote_charge_manager.rb:138-178`

### Phase 3: Individual Charge Processing

For each recurring charge:

1. `RecurringChargeProcessor.call()` executes
2. Validates charge (amount > 0, gateway match, customer match)
3. Creates autopay template and charge
4. Submits to payment gateway
5. **Decision Tree:**

```ruby
if purchase_result.successful_purchase?
  mark_as_successful(reason: "RemoteCharge::STATUS_SUCCESS")
  send_success_notification()  # → SuccessfulAutopayNotice
elsif can_retry_tomorrow?
  mark_for_retry(reason: "RemoteCharge::STATUS_FAIL")
  send_retry_notification()    # → FailedWillRetryAutopayNotice
else
  mark_for_suspension(reason: TOO_MANY_FAILURES)
  send_suspension_notification() # → FailedCancellingAutopayNotice
end
```

**Code Reference:** `lib/charges/utils/recurring_charge_processor.rb:119-130`

### Phase 4: SendGrid API Call

```bash
curl -X POST "https://api.sendgrid.com/v3/mail/send" \
  -H "Authorization: Bearer ${SENDGRID_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "personalizations": [{
      "to": [{"email": "customer@example.com"}],
      "substitutions": {
        "-account_number-": "ending in #1234",
        "-customer_name-": "John Doe",
        "-company_name-": "Acme Water District",
        "-recurring_amount-": "125.50",
        "-date-": "01/25/2026"
      }
    }],
    "from": {"email": "customerservice@munibilling.com"},
    "template_id": "ee494e99-bd7f-484d-bd5a-fb4f22adef9b",
    "categories": ["billing"]
  }'
```

---

## 5. Customer Eligibility Requirements

### Autopay Enrollment Eligibility

| # | Condition | Field/Check | Notes |
|---|-----------|-------------|-------|
| 1 | Payment method enabled | `customer.payment_credit_card_enable` OR `customer.payment_checking_enable` | At least one |
| 2 | Gateway available | `PaymentGatewayProfile.enabled = true` | Company must have active gateway |
| 3 | Gateway supports autopay | `payment_gateway_profile.recurring_attempts > 0` | 0 = autopay disabled |
| 4 | No existing enrollment | Validator checks uniqueness | One active enrollment per customer |
| 5 | Customer active | `customer.status = ACTIVE` | Account in good standing |

### Notification Eligibility

| # | Condition | Field/Check | Notes |
|---|-----------|-------------|-------|
| 1 | Email exists | `customer.email IS NOT NULL AND <> ''` | Required for email notifications |
| 2 | Enrollment active | `recurring_charge.recurring_charge_status_id = 1` | STATUS_ACTIVE |
| 3 | Notice preference | `NoticeRecipientPreference.enabled = true` | Auto-created on customer creation |

### Notification Check in Code

```ruby
# recurring_charge_processor.rb
def can_receive_notices?
  recurring_charge.customer.email.present?
end

# All notification methods check this before sending
def send_success_notification
  if can_receive_notices?
    # Send notification
  else
    Charges::Logger.info(message: "user cannot receive notices")
  end
end
```

---

## 6. Configuration Requirements

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `MUNI_ENV` | **Yes** | Environment identifier | `production`, `staging` |
| `SENDGRID_API_KEY` | **Yes** | SendGrid API bearer token | `SG.xxxxxxxxx...` |
| `DUMMY_PURCHASER` | Optional | If set, disables all notifications | Used for testing |

### Payment Gateway Profile Settings

| Field | Type | Purpose | Default |
|-------|------|---------|---------|
| `enabled` | Boolean | Gateway is active | FALSE |
| `recurring_attempts` | Integer | Max retry attempts (0 = no autopay) | 0 |
| `recurring_start_date` | Date | When autopay cycles begin | Required |
| `recurring_charge_frequency_type_id` | FK | DAY, WEEK, or MONTH | Required |
| `recurring_charge_frequency_interval` | Integer | Frequency multiplier | 1 |
| `autopay_on_due_date` | Boolean | Charge on bill due date | FALSE |
| `customer_portal_recurring` | Boolean | Allow portal signup | FALSE |

### Recurring Charge Frequency Types

| Type | ID | Example Usage |
|------|-----|---------------|
| `DAY` | - | Daily charges (interval=1), every 2 days (interval=2) |
| `WEEK` | - | Weekly charges (interval=1), biweekly (interval=2) |
| `MONTH` | - | Monthly charges (interval=1), quarterly (interval=3) |

### Customer Settings

| Field | Type | Purpose |
|-------|------|---------|
| `payment_credit_card_enable` | Boolean | Customer can pay by credit card |
| `payment_checking_enable` | Boolean | Customer can pay by e-check |
| `automatic_payments` | Boolean | Customer currently enrolled in autopay |
| `email` | String | Email for notifications |

---

## 7. Email Addresses & Accounts

### System Email Addresses

| Address | Purpose | Used In |
|---------|---------|---------|
| `customerservice@munibilling.com` | FROM address for all autopay notifications | All 4 notice types |
| `testing@munibilling.com` | Non-prod email redirect | Dev/staging environments |

### Configuration Reference

```ruby
# app/models/notice.rb:24
MUNI_CUSTOMER_SERVICE_EMAIL = 'customerservice@munibilling.com'.freeze

# All autopay SendGrid classes use this as the FROM address
```

### Per-Company Settings

| Field | Purpose |
|-------|---------|
| `company.customer_service_phone` | Support phone shown in emails |
| `company.url_name` | Used to construct portal URL |

---

## 8. SendGrid Templates

### Template IDs and Purpose

| Template ID | Notification Type | Class |
|-------------|-------------------|-------|
| `ee494e99-bd7f-484d-bd5a-fb4f22adef9b` | 10-Day Warning | `SendgridUpcomingAutopayNotice` |
| `132e00ee-e9a8-44c3-9d1a-c29235afd28b` | Successful Payment | `SendgridSuccessfulAutopayNotice` |
| `36c89d58-edce-49a6-a425-cc85c7b738fb` | Failed - Will Retry | `SendgridFailedWillRetryAutopayNotice` |
| `5470a6f1-1212-4dc3-9150-a37cdee02c64` | Failed - Dropped | `SendgridFailedCancellingAutopayNotice` |

### Template Variables (All Types)

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `-account_number-` | Obfuscated account (last 4) | `ending in #1234` |
| `-full_account_number-` | Complete account number | `1234567890` |
| `-customer_name-` | Customer full name | `John Doe` |
| `-company_name-` | Company/utility name | `Acme Water District` |
| `-company_support_number-` | Customer service phone | `555-123-4567` |
| `-customer_portal_url-` | Portal URL for updates | `https://acme.secure.munibilling.com` |
| `-recurring_amount-` | Payment amount | `125.50` |

### Type-Specific Variables

**10-Day Warning:**
| Variable | Description |
|----------|-------------|
| `-date-` | Scheduled payment date (10 days out) |
| `-process_date-` | Date of notification |

**Successful Payment:**
| Variable | Description |
|----------|-------------|
| `-payment_date-` | Date payment processed |
| `-next_pmt_date-` | Next scheduled payment date |

**Failed - Will Retry:**
| Variable | Description |
|----------|-------------|
| `-payment_date-` | Date of failed attempt |
| `-next_pmt_date-` | Next retry date (tomorrow) |

**Failed - Dropped:**
| Variable | Description |
|----------|-------------|
| `-process_date-` | Date of final failed attempt |

### Template Management

- **Location:** SendGrid Dashboard (not in codebase)
- **Access:** Requires SendGrid admin credentials
- **Changes:** Coordinate with DevOps for template updates

---

## 9. Retry Logic & Failure Handling

### Retry Configuration

```ruby
# payment_gateway_profile.recurring_attempts determines max attempts
# Value map:
#   0         = Autopay disabled, no charges processed
#   1         = Single attempt only, no retries
#   2+        = Up to N total attempts (1 initial + N-1 retries)
```

### Retry Decision Logic

```ruby
# recurring_charge_processor.rb

def max_attempts
  @max_attempts ||= payment_gateway_profile.recurring_attempts
end

def needs_suspension?
  # attempts_this_cycle gets incremented on each failure
  is_active? && is_enabled? && (attempts_this_cycle > max_attempts)
end

def can_retry_tomorrow?
  is_active? && (attempts_this_cycle < max_attempts)
end
```

### State Transitions

```
                     ┌─────────────────┐
                     │  ACTIVE (1)     │
                     │  attempts = 0   │
                     └────────┬────────┘
                              │
                    Payment Attempt
                              │
              ┌───────────────┴───────────────┐
              │                               │
         SUCCESS                           FAIL
              │                               │
              ▼                               ▼
    ┌─────────────────┐             ┌─────────────────┐
    │  Reset cycle    │             │  attempts += 1  │
    │  attempts = 0   │             └────────┬────────┘
    │  next_date =    │                      │
    │  next_payment   │           ┌──────────┴──────────┐
    └────────┬────────┘           │                     │
             │              attempts < max        attempts >= max
             │                    │                     │
             ▼                    ▼                     ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │  SUCCESS        │  │  RETRY          │  │  CANCELLED (3)  │
    │  notification   │  │  notification   │  │  notification   │
    └─────────────────┘  │  next_date =    │  │  Unenroll       │
                         │  tomorrow       │  │  customer       │
                         └─────────────────┘  └─────────────────┘
```

### Suspension Actions

When enrollment is suspended (too many failures):

```ruby
def suspend_recurring_payment(reason:)
  # 1. Mark for suspension
  mark_for_suspension(reason: reason, increment: 0)

  # 2. Clear customer's automatic_payments flag
  clear_automatic_payments_indicator_for_customer()

  # 3. Send notification
  send_suspension_notification()
end

def clear_automatic_payments_indicator_for_customer
  # Direct SQL to avoid model callbacks and locking issues
  ActiveRecord::Base.connection.execute(
    "UPDATE customers SET automatic_payments=FALSE WHERE id = #{customer_id}"
  )
end
```

### Status Code Reference

**RecurringCharge Status:**
| Status | ID | Description |
|--------|-----|-------------|
| ACTIVE | 1 | Enrollment active, charges processing |
| PENDING | 2 | Enrollment pending activation |
| CANCELLED | 3 | Enrollment suspended/cancelled |

**RemoteCharge Status:**
| Status | ID | Description |
|--------|-----|-------------|
| PROCESSING | 1 | Currently processing |
| SUCCESS | 2 | Payment successful |
| FAIL | 3 | Payment failed |
| DUPLICATE | 4 | Duplicate charge detected |
| NO_RECURRING_MATCH | 5 | No matching recurring charge |
| PENDING | 6 | Pending/abandoned |

---

## 10. Environment Differences

### Email Routing by Environment

| Environment | `MUNI_ENV` | Email Destination |
|-------------|------------|-------------------|
| **Production** | `production` | **Actual customer email** |
| **Staging** | `staging` | `testing@munibilling.com` |
| **Demo** | `demo` | `testing@munibilling.com` |
| **Development** | `dev*` | `testing@munibilling.com` |

### Production Guard

```ruby
# remote_charge_manager_job.rb
def perform(date_str = nil)
  return unless Rails.env.production?  # Jobs only run in production
  # ...
end

# remote_charge_manager_notifications_job.rb
def perform(date_str = nil)
  return unless Rails.env.production?  # Jobs only run in production
  # ...
end
```

### Non-Production Email Redirect

```ruby
# remote_charge_manager.rb:187-198
def recurring_payments_notification(date_to_charge)
  if Rails.env.development? || Billing::Application.config.staged_environment?
    # Non-production: redirect ALL emails to testing inbox
    personalizations << {
      "email" => 'testing@munibilling.com',
      # ... other fields
    }
  else
    # Production: send to actual customer
    personalizations << {
      "email" => rc.email,
      # ... other fields
    }
  end
end
```

### Dummy Purchaser Mode

```ruby
# recurring_charge_notice.rb
def self.for(notification_event)
  if ENV['DUMMY_PURCHASER'].present?
    NullAutopayNotice.new  # No-op, skips all notifications
  else
    # Normal notification routing
  end
end
```

---

## 11. Scheduling & Jobs

### Daily Schedule

| Time | Job | Class | Purpose |
|------|-----|-------|---------|
| 6:00 PM | `remote_charge_manager_notifications` | `RemoteChargeManagerNotificationsJob` | Send 10-day warnings |
| 8:00 PM | `recurring_payments` | `RemoteChargeManagerJob` | Process autopay charges |
| 11:40 PM | `water_smart_autopay` | `Jobs::Exports::WaterSmartAutopayJob` | Export to WaterSmart |

### Schedule Configuration

**File:** `config/schedule.yml`

```yaml
# Lines 52-55: Payment Processing
recurring_payments:
  cron: "0 20 * * *"  # 8 PM daily
  class: RemoteChargeManagerJob
  queue: v5_distributed_queue_1

# Lines 57-60: 10-Day Notifications
remote_charge_manager_notifications:
  cron: "0 18 * * *"  # 6 PM daily
  class: RemoteChargeManagerNotificationsJob
  queue: default_rails5

# Lines 27-30: WaterSmart Export
water_smart_autopay:
  cron: "40 23 * * *"  # 11:40 PM daily
  class: Jobs::Exports::WaterSmartAutopayJob
  queue: default_rails5
```

### Job Queue Configuration

| Queue | Purpose |
|-------|---------|
| `v5_distributed_queue_1` | High-priority payment processing |
| `default_rails5` | Standard notifications and exports |

### Manual Job Execution

```ruby
# Process autopay for specific date
RemoteChargeManagerJob.new.perform("2026-01-15")

# Send 10-day notifications for specific date
RemoteChargeManagerNotificationsJob.new.perform("2026-01-25")

# Or via Sidekiq
RemoteChargeManagerJob.perform_async("2026-01-15")
```

---

## 12. Database Schema Reference

### recurring_charges

```sql
CREATE TABLE recurring_charges (
  id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  recurring_charge_status_id INT NOT NULL DEFAULT 1,
  recurring_amount DECIMAL(10,2) NOT NULL,
  next_charge_date DATE NOT NULL,
  attempts_this_cycle INT DEFAULT 0,
  payment_gateway_profile_id INT NOT NULL,
  remote_charge_type_id INT NOT NULL,
  recurring_charge_frequency_type_id INT,
  recurring_charge_frequency_interval INT DEFAULT 1,
  start_date DATE,
  end_date DATE,
  token VARCHAR(255),
  account_name VARCHAR(255),
  last_four_digits VARCHAR(4),
  expiration_month VARCHAR(2),
  expiration_year VARCHAR(4),
  zip_code VARCHAR(10),
  display_message TEXT,
  created_at DATETIME,
  updated_at DATETIME,

  INDEX idx_customer_id (customer_id),
  INDEX idx_status (recurring_charge_status_id),
  INDEX idx_next_charge_date (next_charge_date),
  INDEX idx_payment_gateway_profile (payment_gateway_profile_id)
);
```

### recurring_charge_status (Reference Data)

| ID | Name | Description |
|----|------|-------------|
| 1 | ACTIVE | Enrollment active |
| 2 | PENDING | Pending activation |
| 3 | CANCELLED | Suspended/cancelled |

### payment_gateway_profiles

```sql
CREATE TABLE payment_gateway_profiles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  company_id INT NOT NULL,
  payment_gateway_id INT NOT NULL,
  remote_charge_type_id INT NOT NULL,
  enabled BOOLEAN DEFAULT FALSE,
  recurring_attempts INT DEFAULT 0,
  recurring_start_date DATE,
  recurring_charge_frequency_type_id INT,
  recurring_charge_frequency_interval INT DEFAULT 1,
  autopay_on_due_date BOOLEAN DEFAULT FALSE,
  customer_portal_recurring BOOLEAN DEFAULT FALSE,
  created_at DATETIME,
  updated_at DATETIME,

  INDEX idx_company_id (company_id),
  INDEX idx_enabled (enabled)
);
```

### remote_charges

```sql
CREATE TABLE remote_charges (
  id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  company_id INT NOT NULL,
  recurring_charge_id INT,
  remote_charge_status_id INT NOT NULL,
  payment_amount DECIMAL(10,2),
  applied_payment_amount DECIMAL(10,2),
  convenience_fee DECIMAL(10,2),
  total_amount DECIMAL(10,2),
  remote_charge_type_id INT,
  created_at DATETIME,
  updated_at DATETIME,

  INDEX idx_customer_id (customer_id),
  INDEX idx_recurring_charge_id (recurring_charge_id),
  INDEX idx_status (remote_charge_status_id)
);
```

### notice_recipient_preferences

```sql
CREATE TABLE notice_recipient_preferences (
  id INT AUTO_INCREMENT PRIMARY KEY,
  recipient_id INT NOT NULL,
  recipient_type VARCHAR(255) NOT NULL,
  process_event_type_id INT NOT NULL,
  notice_delivery_type_id INT NOT NULL,
  enabled BOOLEAN DEFAULT TRUE,
  effective_date DATE,
  created_at DATETIME,
  updated_at DATETIME,

  INDEX idx_recipient (recipient_id, recipient_type)
);

-- Auto-created for customers with:
-- process_event_type_id = ProcessEventType::SEND_AUTOPAY_NOTICES
-- notice_delivery_type_id = NoticeDeliveryType::EMAIL
-- enabled = true
```

---

## 13. Known Bottlenecks & Troubleshooting

### Common Issues

#### Issue 1: 10-Day Notifications Not Sending

**Symptoms:**
- Customers not receiving advance notice emails
- No errors in logs

**Possible Causes:**
1. Job not running (check Sidekiq)
2. `Rails.env.production?` returns false
3. No charges due in 10 days
4. Customer email missing

**Resolution Steps:**
```bash
# 1. Check if job ran
grep "RemoteChargeManagerNotificationsJob" log/production.log

# 2. Check for eligible charges
SELECT COUNT(*) FROM recurring_charges
WHERE recurring_charge_status_id = 1
  AND next_charge_date = DATE_ADD(CURDATE(), INTERVAL 10 DAY);

# 3. Manual trigger (in Rails console)
RemoteChargeManagerNotificationsJob.new.perform
```

#### Issue 2: Payments Failing Silently

**Symptoms:**
- Recurring charges not processing
- No success/failure notifications

**Possible Causes:**
1. `recurring_attempts = 0` (autopay disabled)
2. Payment gateway unhealthy
3. `DUMMY_PURCHASER` env var set

**Resolution Steps:**
```bash
# 1. Check gateway configuration
SELECT id, enabled, recurring_attempts
FROM payment_gateway_profiles
WHERE company_id = XXX;

# 2. Check for DUMMY_PURCHASER
echo $DUMMY_PURCHASER

# 3. Check gateway health
# In Rails console:
PaymentGatewayProfile.find(XXX).enabled_and_healthy?
```

#### Issue 3: Customer Stuck in Retry Loop

**Symptoms:**
- Daily failure notifications
- Never gets suspended

**Possible Causes:**
1. `recurring_attempts` set very high
2. `attempts_this_cycle` not incrementing

**Resolution Steps:**
```sql
-- Check current state
SELECT id, attempts_this_cycle, recurring_charge_status_id, next_charge_date
FROM recurring_charges
WHERE customer_id = XXX;

-- Check gateway max attempts
SELECT recurring_attempts
FROM payment_gateway_profiles
WHERE id = (SELECT payment_gateway_profile_id
            FROM recurring_charges WHERE customer_id = XXX);
```

#### Issue 4: Duplicate Notifications

**Symptoms:**
- Customer receives multiple emails for same event

**Possible Causes:**
1. Job running multiple times
2. Batch processor re-processing same charges

**Resolution Steps:**
```bash
# Check for duplicate job runs
grep "RecurringChargeProcessor" log/production.log | grep "entering"

# Check process history
SELECT * FROM process_histories
WHERE process_rule_id = (SELECT id FROM process_rules
                         WHERE name = 'RECURRING_PAYMENTS')
ORDER BY created_at DESC LIMIT 10;
```

### Troubleshooting SQL Queries

```sql
-- Check autopay enrollments for a customer
SELECT rc.*, pgp.recurring_attempts, pgp.enabled
FROM recurring_charges rc
JOIN payment_gateway_profiles pgp ON rc.payment_gateway_profile_id = pgp.id
WHERE rc.customer_id = XXX;

-- Find failed charges in last 7 days
SELECT rc.id, c.account_number, rc.attempts_this_cycle,
       rc.next_charge_date, rc.recurring_charge_status_id
FROM recurring_charges rc
JOIN customers c ON rc.customer_id = c.id
WHERE rc.recurring_charge_status_id = 3  -- CANCELLED
  AND rc.updated_at > DATE_SUB(NOW(), INTERVAL 7 DAY);

-- Check notification preferences
SELECT * FROM notice_recipient_preferences
WHERE recipient_id = XXX
  AND recipient_type = 'Customer'
  AND process_event_type_id = 6;  -- SEND_AUTOPAY_NOTICES

-- Check charges due today
SELECT rc.*, c.email, c.account_number, co.name as company_name
FROM recurring_charges rc
JOIN customers c ON rc.customer_id = c.id
JOIN companies co ON c.company_id = co.id
WHERE rc.recurring_charge_status_id = 1
  AND rc.next_charge_date = CURDATE();

-- Check charges due in 10 days (for notification job)
SELECT COUNT(*) as count, co.name as company
FROM recurring_charges rc
JOIN customers c ON rc.customer_id = c.id
JOIN companies co ON c.company_id = co.id
JOIN payment_gateway_profiles pgp ON rc.payment_gateway_profile_id = pgp.id
WHERE rc.recurring_charge_status_id = 1
  AND rc.next_charge_date = DATE_ADD(CURDATE(), INTERVAL 10 DAY)
  AND pgp.enabled = 1
  AND pgp.recurring_attempts > 0
  AND c.email IS NOT NULL AND c.email != ''
GROUP BY co.name;
```

---

## 14. Monitoring & Observability

### Job Health Checks

```bash
# Check Sidekiq queues
bundle exec sidekiq-client queue:stats

# Check recent job runs
grep "RemoteChargeManager" log/production.log | tail -50

# Check for errors
grep -i "error\|exception\|fail" log/production.log | grep -i "recurring\|autopay"
```

### Key Metrics to Monitor

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| Daily charges processed | Process history | Alert if 0 for 24h |
| Failure rate | remote_charges table | Alert if > 10% |
| Notification job completion | Sidekiq | Alert if not completed by 7 PM |
| Payment job completion | Sidekiq | Alert if not completed by 10 PM |
| Suspended enrollments | recurring_charges | Monitor trend |

### Process History Tracking

```sql
-- Check if jobs ran today
SELECT * FROM process_histories
WHERE process_rule_id IN (
  SELECT id FROM process_rules
  WHERE name IN ('RECURRING_PAYMENTS', 'RECURRING_PAYMENTS_NOTIFICATION')
)
AND created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY created_at DESC;
```

### Admin UI Endpoints

| URL | Purpose |
|-----|---------|
| `/jobs/sidekiq` | Sidekiq dashboard |
| `/jobs/sidekiq/busy` | Active job monitoring |
| `/recurring_charges` | View recurring charge records |
| `/payment_gateway_profiles` | Gateway configuration |

### SendGrid Monitoring

- **Activity Feed:** View individual notification status
- **Stats Dashboard:** Delivery metrics for autopay category
- **Suppressions:** Manage blocked addresses

---

## 15. Quick Reference

### Notification Decision Tree

```
RecurringChargeProcessor.call()
│
├─ Zero amount?
│  └─ SKIP (no notification)
│
├─ Already needs suspension?
│  └─ SUSPEND → FailedCancellingAutopayNotice
│
└─ Process Payment
   │
   ├─ SUCCESS?
   │  └─ SuccessfulAutopayNotice
   │     • Reset attempts = 0
   │     • Set next_date = next_payment_date
   │
   ├─ FAIL + CAN RETRY?
   │  └─ FailedWillRetryAutopayNotice
   │     • Increment attempts
   │     • Set next_date = tomorrow
   │
   └─ FAIL + NO RETRIES?
      └─ FailedCancellingAutopayNotice
         • Set status = CANCELLED
         • Clear customer.automatic_payments
```

### Daily Schedule

| Time | Event |
|------|-------|
| 6:00 PM | Send 10-day warning notifications |
| 8:00 PM | Process autopay charges |
| 11:40 PM | Export to WaterSmart |

### Key Template IDs

| Notification | Template ID |
|--------------|-------------|
| 10-Day Warning | `ee494e99-bd7f-484d-bd5a-fb4f22adef9b` |
| Success | `132e00ee-e9a8-44c3-9d1a-c29235afd28b` |
| Retry | `36c89d58-edce-49a6-a425-cc85c7b738fb` |
| Dropped | `5470a6f1-1212-4dc3-9150-a37cdee02c64` |

### Key Email Addresses

| Purpose | Address |
|---------|---------|
| FROM address | `customerservice@munibilling.com` |
| Non-prod redirect | `testing@munibilling.com` |

### Status Constants

| RecurringCharge | RemoteCharge |
|-----------------|--------------|
| 1 = ACTIVE | 1 = PROCESSING |
| 2 = PENDING | 2 = SUCCESS |
| 3 = CANCELLED | 3 = FAIL |

### Emergency Contacts

- **SendGrid Issues:** SendGrid Support Portal
- **Gateway Issues:** Paya/Heartland Support
- **Database Issues:** Database Team
- **Job/Sidekiq Issues:** DevOps Team

---

*Document Version: 1.0*
*Last Updated: January 2026*
*Maintained By: MuniBilling Engineering*
