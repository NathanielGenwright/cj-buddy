# eBill Email System - Technical Setup Documentation

**Document Type:** Internal Technical Reference
**Target Audience:** Engineering, DevOps, Support Teams
**Format:** External Document (Copy to Confluence/SharePoint)

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Components](#2-architecture-components)
3. [Happy Path Flow](#3-happy-path-flow)
4. [Customer Eligibility Requirements](#4-customer-eligibility-requirements)
5. [Configuration Requirements](#5-configuration-requirements)
6. [Email Addresses & Accounts](#6-email-addresses--accounts)
7. [SendGrid Templates](#7-sendgrid-templates)
8. [Rails Email Templates](#8-rails-email-templates)
9. [Environment Differences](#9-environment-differences)
10. [Scheduling & Jobs](#10-scheduling--jobs)
11. [Failure Handling](#11-failure-handling)
12. [Known Bottlenecks & Troubleshooting](#12-known-bottlenecks--troubleshooting)
13. [Database Schema Reference](#13-database-schema-reference)
14. [Monitoring & Observability](#14-monitoring--observability)
15. [Quick Reference](#15-quick-reference)

---

## 1. System Overview

### What is eBill?

eBill is the automated email delivery system that sends billing statements/invoices to customers after bill posting. The system uses **SendGrid** as the email delivery provider and supports two delivery mechanisms.

### Delivery Mechanisms

| Mechanism | Description | When Used |
|-----------|-------------|-----------|
| **eBill Daemon** | Standalone Ruby process polling database for queued invoices | Invoice2 system (`use_invoices = TRUE`) |
| **Email Jobs** | Sidekiq/Delayed::Job workers processing batches | Legacy billing, one-off resends |

### Key Capabilities

- Automated bill delivery after posting
- Multi-recipient support (comma/semicolon separated)
- Tenant email support for rental properties
- Company-specific branding and templates
- White-label domain support
- Delivery status tracking via SendGrid webhooks
- Failure notifications to company support

---

## 2. Architecture Components

### File Structure

```
muni-billing/legacy/
├── daemons/
│   ├── ebill_daemon.rb                    # Daemon launcher
│   └── ebill/
│       ├── ebill_process_execute.rb       # Main daemon logic (179 lines)
│       └── ebill_process_sql_lib.rb       # Database operations (55 lines)
├── bin/
│   └── ebill_entrypoint                   # Bash launcher script
├── app/
│   ├── gateways/
│   │   └── sendgrid_gateway.rb            # SendGrid API integration
│   ├── mailers/
│   │   └── customer_mailer.rb             # Rails ActionMailer
│   ├── views/customer_mailer/
│   │   ├── invoice_alert.html.erb         # Invoice notification template
│   │   ├── usage_bill.html.erb            # Usage bill wrapper
│   │   ├── _usage_bill_standard.html.erb  # Standard usage bill (586 lines)
│   │   ├── _usage_bill_sahuarita.html.erb # Sahuarita-specific
│   │   ├── _usage_bill_wesley.html.erb    # Wesley-specific
│   │   └── bill_email_failure.html.erb    # Failure notification
│   ├── models/
│   │   ├── email_batch.rb                 # Batch tracking
│   │   ├── customers_email_batch.rb       # Per-customer status
│   │   ├── bills_email_batch.rb           # Bill-to-batch mapping
│   │   ├── email_status.rb                # Status constants
│   │   └── email_batch_status.rb          # Batch status constants
│   ├── helpers/
│   │   └── email_helper.rb                # SendGrid webhook processing
│   ├── controllers/
│   │   ├── email_batches_controller.rb    # Batch management UI
│   │   └── customers_email_batches_controller.rb
│   ├── services/
│   │   └── email_rate_limiter.rb          # Microsoft throttle protection
│   └── business_logic/jobs/
│       ├── email_bills_job.rb             # Multi-threaded email delivery
│       ├── email_bills2_job.rb            # Invoice-based delivery
│       ├── email_bills_one_offs_job.rb    # One-off resends
│       └── bills/
│           └── post_bills_job.rb          # Bill posting orchestrator
└── config/
    └── initializers/
        └── send_grid_header.rb            # Webhook middleware
```

### Process Flow Overview

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Bill Posting    │────▶│  Email Batch     │────▶│  eBill Daemon    │
│  (PostBillsJob)  │     │  Created         │     │  (30s polling)   │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                                           │
                                                           ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Status Update   │◀────│  SendGrid        │◀────│  SendGrid API    │
│  (Webhook)       │     │  Delivers        │     │  mail/send       │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

---

## 3. Happy Path Flow

### Phase 1: Bill Posting

1. Admin initiates bill posting via UI
2. `PostBillsJob.perform_now()` executes
3. Invoices generated with saved_documents (PDFs)
4. `EmailBatch` record created:
   - `email_batch_status_id = MAILED`
   - `post_billing_job_id = current job ID`
5. `CustomersEmailBatch` records created for each eligible customer:
   - `email_status_id = 8` (QUEUED_INV)

**Code Reference:** `app/business_logic/jobs/bills/post_bills_job.rb:142-178`

### Phase 2: Daemon Polling (Every 30 seconds)

1. `EbillProcessExecute.launch(true)` runs continuously
2. `find_invoices()` calls stored procedure: `sp_email_invoices(8, 2)`
   - Parameter 8 = QUEUED_INV status
   - Parameter 2 = SavedDocumentStatus::SUCCESS
3. Returns invoices matching ALL criteria:
   - `company.use_invoices = TRUE`
   - `customer.deliver_bill_email = TRUE`
   - `customer.email IS NOT NULL AND <> ''`
   - `customers_email_batches.email_status_id = 8`
   - `saved_documents.saved_document_status_id = 2`
4. If no records: `sleep(30 seconds)`, repeat
5. If records found: process batch

**Code Reference:** `daemons/ebill/ebill_process_execute.rb:44-56`

### Phase 3: Email Preparation

For each invoice:

1. Build SendGrid JSON payload:
```json
{
  "personalizations": [{
    "to": [{"email": "customer@example.com"}],
    "substitutions": {
      "-company_logo_path-": "/logos/company.png",
      "-company_name-": "Acme Water District",
      "-customer_name-": "John Doe",
      "-account_number-": "123456",
      "-amount_due-": "$150.00",
      "-account_code-": "ABC123",
      "-customer_portal_url-": "https://acme.secure.munibilling.com"
    }
  }],
  "from": {"email": "noreply@safemaildelivery.net"},
  "reply_to": {"email": "customerservice@acme.gov"},
  "template_id": "ad152bee-e411-4e94-a558-4186aa9cdb94",
  "custom_args": {
    "customer_id": "12345",
    "email_batch_id": "678"
  },
  "categories": ["billing"]
}
```

2. Update status **BEFORE** sending:
   - `sp_update_emailed_customers_email_batch(id)` → status = 1 (SENT)

**Code Reference:** `daemons/ebill/ebill_process_execute.rb:69-111`

### Phase 4: SendGrid API Call

```bash
curl -X POST "https://api.sendgrid.com/v3/mail/send" \
  -H "Authorization: Bearer ${SENDGRID_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{json_payload}'
```

SendGrid accepts email and queues for async delivery.

**Code Reference:** `daemons/ebill/ebill_process_execute.rb:154-158`

### Phase 5: Delivery Tracking (Async via Webhooks)

1. SendGrid delivers email to recipient's mail server
2. SendGrid sends webhook event to: `POST /email_batches/process_email_events`
3. Webhook payload contains:
   - `event`: "delivered" | "bounce" | "dropped" | "spamreport"
   - `customer_id` (from custom_args)
   - `email_batch_id` (from custom_args)
   - `category`: "billing"
4. `EmailHelper.process_bill_response()`:
   - Updates `customers_email_batches.email_status_id`
   - Updates `bills_email_batches.email_status_id`
   - On failure: updates `email_batch.status = MAILED_ERRORS`
   - On failure: sends notification to company support

**Code Reference:** `app/helpers/email_helper.rb`, `app/controllers/email_batches_controller.rb:process_email_events`

---

## 4. Customer Eligibility Requirements

### All Conditions Must Be TRUE

| # | Condition | Database Field | Notes |
|---|-----------|----------------|-------|
| 1 | Company uses invoices | `companies.use_invoices = TRUE` | Or `is_invoice_2 = TRUE` |
| 2 | Customer opted in | `customers.deliver_bill_email = TRUE` | User preference |
| 3 | Email address exists | `customers.email IS NOT NULL AND <> ''` | Non-empty |
| 4 | Invoice generated | `invoices` record exists | From bill posting |
| 5 | PDF document ready | `saved_documents.saved_document_status_id = 2` | SUCCESS status |
| 6 | Queued for email | `customers_email_batches.email_status_id = 8` | QUEUED_INV |
| 7 | Customer is active | `customers.close_date IS NULL` | OR has positive balance |

### Tenant Override

If **both** conditions are true:
- `customers.tenant_deliver_bill_email = TRUE`
- `customers.tenant_email IS NOT NULL AND <> ''`

Then the **tenant** receives the eBill instead of the primary customer.

### Exclusions

- Customers with `exclude_third_party_printing = TRUE` (when feature enabled)
- Customers with zero balance (when `exclude_0_balance = TRUE` parameter set)
- Customers with closed parcels (unless tenant email configured)

---

## 5. Configuration Requirements

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `MUNI_ENV` | **Yes** | Environment identifier | `production`, `staging`, `demo`, `development` |
| `SENDGRID_API_KEY` | **Yes** | SendGrid API bearer token | `SG.xxxxxxxxx...` |
| `MUNI_MYSQL2_HOST` | **Yes** | Database hostname | `db.munibilling.com` |
| `MUNI_MYSQL2_USERNAME` | **Yes** | Database username | `muni_app` |
| `MUNI_MYSQL2_PASS` | **Yes** | Database password | `*****` |
| `MUNI_MYSQL2_DB` | **Yes** | Database name | `muni_production` |
| `HOST` | Dev only | Local hostname | `localhost:3000` |
| `MICROSOFT_EMAIL_DELAY_SECONDS` | Optional | Rate limit delay (default: 2) | `2` |

### Company Settings (Database)

| Field | Type | Purpose | Default |
|-------|------|---------|---------|
| `use_invoices` | Boolean | Enable Invoice1 system | FALSE |
| `is_invoice_2` | Boolean | Enable Invoice2 system | FALSE |
| `url_name` | String | Subdomain for portal URLs | Required |
| `customer_service_email` | String | Reply-to address | Optional |
| `logo_path` | String | Company logo URL | Optional |
| `ebill_subject_line` | String | Custom email subject | Falls back to `bill_title` |
| `ebill_note` | Text | Custom message in eBill | Optional |
| `white_label_domain_id` | FK | Custom domain | NULL = use standard |
| `from_email_address` | String | FROM address for Rails mailer | Required |

### Customer Settings (Database)

| Field | Type | Purpose |
|-------|------|---------|
| `deliver_bill_email` | Boolean | Opt-in for eBill |
| `email` | String | Primary email address |
| `tenant_deliver_bill_email` | Boolean | Tenant eBill opt-in |
| `tenant_email` | String | Tenant email address |

---

## 6. Email Addresses & Accounts

### System Email Addresses

| Address | Purpose | Used In | Notes |
|---------|---------|---------|-------|
| `noreply@safemaildelivery.net` | FROM address (daemon) | `ebill_process_execute.rb:29` | Default sender |
| `support@munibilling.com` | FROM address (ApplicationMailer) | `application_mailer.rb` | General app emails |
| `customerservice@munibilling.com` | FROM address (notices) | `notice.rb:24`, `sendgrid_gateway.rb` | Autopay notifications |
| `testing@munibilling.com` | Non-prod email redirect | `ebill_process_execute.rb:128` | **All non-prod emails go here** |
| `admin@munibilling.com` | Admin notifications | `config/application.rb:116` | Fallback support |
| `lockbox_reports@munibilling.com` | Lockbox reports | `config/application.rb:117` | Payment processing |
| `server_alerts@munibilling.com` | Server alerts | `config/application.rb:118` | System monitoring |
| `sales@munibilling.com` | Sales inquiries | `customer_mailer.rb:102` | Lead capture |
| Company's `customer_service_email` | Reply-to address | Per company | Customer replies |
| Company's `from_email_address` | FROM (Rails mailer) | Per company | Branded sender |

### Configuration Reference

```ruby
# config/application.rb:115-118
config.customer_service_email = 'customerservice@munibilling.com'
config.admin_email = 'admin@munibilling.com'
config.lockbox_reports_email = 'lockbox_reports@munibilling.com'
config.server_alerts_email = 'server_alerts@munibilling.com'
```

---

## 7. SendGrid Templates

### Template IDs and Purpose

| Template ID | Purpose | Used By |
|-------------|---------|---------|
| `ad152bee-e411-4e94-a558-4186aa9cdb94` | **eBill Invoice** | Daemon, SendgridGateway |
| `ee494e99-bd7f-484d-bd5a-fb4f22adef9b` | 10-Day Autopay Warning | SendgridUpcomingAutopayNotice |
| `132e00ee-e9a8-44c3-9d1a-c29235afd28b` | Successful Autopay | SendgridSuccessfulAutopayNotice |
| `36c89d58-edce-49a6-a425-cc85c7b738fb` | Payment Failed (Will Retry) | SendgridFailedWillRetryAutopayNotice |
| `5470a6f1-1212-4dc3-9150-a37cdee02c64` | Payment Failed (Dropped) | SendgridFailedCancellingAutopayNotice |

### eBill Template Variables

**Template ID:** `ad152bee-e411-4e94-a558-4186aa9cdb94`

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `-company_logo_path-` | URL to company logo | `https://munibilling.com/logos/acme.png` |
| `-company_name-` | Company display name | `Acme Water District` |
| `-customer_name-` | Customer full name | `John Doe` |
| `-account_number-` | Customer account number | `123456` |
| `-amount_due-` | Formatted amount due | `$150.00` |
| `-account_code-` | Portal access code | `ABC123` |
| `-customer_portal_url-` | Link to customer portal | `https://acme.secure.munibilling.com` |

### Template Management

- **Location:** SendGrid Dashboard (not in codebase)
- **Access:** Requires SendGrid admin credentials
- **Changes:** Coordinate with DevOps for template updates
- **Testing:** Use staging environment with `testing@munibilling.com` redirect

---

## 8. Rails Email Templates

### Template Selection Logic

```ruby
# customer_mailer.rb - usage_bill method selects template based on company
if company.part_of?(MasterCompany::WESLEY)
  render 'usage_bill_wesley'
elsif company.is?(Company::SAHUARITA)
  render 'usage_bill_sahuarita'
else
  render 'usage_bill_standard'    # Default template
end
```

### Invoice Alert Template

**File:** `app/views/customer_mailer/invoice_alert.html.erb`

Simple notification with:
- Link to view bill online (or setup account if first login)
- Bill overview (Amount + Due Date)

```html
<% if @resource.sign_in_count == 0 %>
  Your bill is now available for you to view online.
  <%= link_to 'Click here to setup your account.', @confirmation_url %>
<% else %>
  Your bill is now available for you to
  <%= link_to 'view online here', portal_url %>.
<% end %>

Bill Overview:
  Amount: <%= number_to_currency(calculated_total) %>
  Due: <%= @invoice.penalty_date %>
```

### Standard Usage Bill Template

**File:** `app/views/customer_mailer/_usage_bill_standard.html.erb` (586 lines)

**Sections:**
1. **Header** - Bill title, due date
2. **Summary Box** - Customer name, account number, totals breakdown
3. **Customer Service Info** - Phone, email, portal link
4. **Remit Address** - Where to mail checks
5. **QR Code** - If enabled (`company.will_print_with_qr_code?`)
6. **eBill Note** - Custom company message
7. **Bill Details** - Line items by service address
8. **Payments/Adjustments** - Recent transactions
9. **Meter Readings** - Usage data if applicable
10. **Return Stub** - For mailed payments (with OCR if lockbox enabled)

**Key Variables Available:**
- `@company` - Company record
- `@customer_full_name` - Customer or tenant name
- `@usage_bill_data` - Bill calculation object with totals, dates, line items
- `@parcel` - Service address
- `@qr_label`, `@qr_uri` - QR code if enabled

### Failure Notification Template

**File:** `app/views/customer_mailer/bill_email_failure.html.erb`

Sent to company support (`company.email_1, email_2, email_3`) when delivery fails:

```
The following customer did not receive an email bill because of an
invalid address, or issues with the recipients email settings:

Account Number: 123456
John Doe
Email Address: john@invalid.com
```

---

## 9. Environment Differences

### Email Routing by Environment

| Environment | `MUNI_ENV` | Email Destination | Portal URL Host |
|-------------|------------|-------------------|-----------------|
| **Production** | `production` | **Actual customer email** | `secure.munibilling.com` |
| **Staging** | `staging` | `testing@munibilling.com` | `staging.munibilling.com` |
| **Demo** | `demo` | `testing@munibilling.com` | `demo.munibilling.com` |
| **Development** | `dev*` | `testing@munibilling.com` | `ENV['HOST']` |

### Critical: Non-Production Safety

```ruby
# ebill_process_execute.rb:126-145
def sanitize_emails(email_string, customer_info_hash)
  if !production?
    # ALL non-production emails redirected to testing inbox
    customer_info_hash["to"] << { "email" => 'testing@munibilling.com' }
  else
    # Production only: route to actual customer(s)
    # Supports comma or semicolon-separated addresses
    ...
  end
end

def production?
  ENV['MUNI_ENV'] == 'production'
end
```

**This prevents accidental customer emails from non-production environments.**

### URL Construction

```ruby
case ENV['MUNI_ENV'].to_s
when /^dev/
  PROTOCOL = 'http://'
  URL_HOST = ENV['HOST']           # localhost:3000
when 'staging'
  PROTOCOL = 'https://'
  URL_HOST = 'staging.munibilling.com'
when 'demo'
  PROTOCOL = 'https://'
  URL_HOST = 'demo.munibilling.com'
when 'production'
  PROTOCOL = 'https://'
  URL_HOST = 'secure.munibilling.com'
end

# Final URL: #{PROTOCOL}#{company.url_name}.#{URL_HOST}
# Example: https://acme.secure.munibilling.com
```

### Logging by Environment

| Environment | Log Destination | Error Log |
|-------------|-----------------|-----------|
| Kubernetes | `STDOUT` | `STDERR` |
| Traditional | `log/ebill_process_execute.log` | `log/ebill_process_execute.log.ERROR` |

```ruby
def k8s?
  (ENV.keys & K8S_ENV_KEYS).length == K8S_ENV_KEYS.length
end

# K8S_ENV_KEYS = ['KUBERNETES_SERVICE_HOST', 'KUBERNETES_SERVICE_PORT', 'KUBERNETES_PORT']
```

---

## 10. Scheduling & Jobs

### eBill Daemon

- **Type:** Standalone daemon process
- **Poll Interval:** 30 seconds
- **Launch Command:** `bin/ebill_entrypoint` or `bundle exec ruby daemons/ebill_daemon.rb`
- **Kubernetes:** Runs as dedicated pod with restart policy

### Related Scheduled Jobs

**File:** `config/schedule.yml`

| Job | Schedule | Purpose |
|-----|----------|---------|
| `recurring_payments` | Daily 8 PM | Process autopay charges |
| `remote_charge_manager_notifications` | Daily 6 PM | Send 10-day autopay warnings |
| `water_smart_autopay` | Daily 11:40 PM | WaterSmart autopay exports |

### Email Job Classes

| Job | Queue | Concurrency | Usage |
|-----|-------|-------------|-------|
| `EmailBillsJob` | `default_rails5` | Up to 20 threads | Regular bill emails |
| `EmailBills2Job` | `default_rails5` | Sequential | Invoice-based emails |
| `EmailBillsOneOffsJob` | `default_rails5` | Sequential | Failed email resends |

### Job Invocation

```ruby
# Typical invocation from PostBillsJob or manual trigger
BillingJob.enqueue_job(
  billing_job_type_id: BillingJobType::EMAIL_BILLS,
  param_hash: { company_id: 123, ... }
)
```

---

## 11. Failure Handling

### Email Status Lifecycle

```
QUEUED_INV (8)
    │
    ▼ (daemon picks up)
SENT (1)
    │
    ▼ (SendGrid webhook)
    ├──▶ DELIVERED (2)   ✓ Success
    ├──▶ BOUNCED (3)     ✗ Hard/soft bounce
    ├──▶ DROPPED (4)     ✗ Invalid/suppressed
    ├──▶ SPAM (5)        ✗ Marked as spam
    └──▶ FAILED (7)      ✗ Retries exhausted
```

### Status Code Reference

| Status | ID | SendGrid Event | Description | Action |
|--------|-----|----------------|-------------|--------|
| QUEUED_INV | 8 | - | Waiting for daemon | None - daemon processes |
| SENDING | 6 | - | In transit | Transient state |
| SENT | 1 | - | Handed to SendGrid | Await webhook |
| DELIVERED | 2 | `delivered` | Confirmed delivery | **Success** |
| BOUNCED | 3 | `bounce` | Server rejected | Notify company |
| DROPPED | 4 | `dropped` | SendGrid dropped | Notify company |
| SPAM | 5 | `spamreport` | Spam complaint | Notify company |
| FAILED | 7 | - | Retries exhausted | Notify company |

### Retry Logic (EmailBillsJob)

```ruby
MAIL_RETRY_MAX = 10

while retry_count < MAIL_RETRY_MAX && status == SENDING
  begin
    EmailRateLimiter.apply_rate_limit(email_address)
    CustomerMailer.invoice_alert(...).deliver_now
    status = SENT
    break
  rescue => e
    retry_count += 1
    # Log error, continue retrying
  end
end

# After loop: convert stuck SENDING → FAILED
if status == SENDING
  update_to_failed
end
```

### Failure Notification Flow

```ruby
# email_helper.rb:process_bill_response
def self.process_bill_response(params)
  email_status = get_email_status(params['event'])

  # Update individual records
  customers_email_batch.email_status = email_status
  bills_email_batch.email_status = email_status

  # Update batch status on failure
  if [DROPPED, BOUNCED, SPAM].include?(email_status.name)
    email_batch.email_batch_status = MAILED_ERRORS

    # Notify company support team
    CustomerMailer.bill_email_failure(customer, company).deliver_now
  end
end
```

---

## 12. Known Bottlenecks & Troubleshooting

### Common Issues

#### Issue 1: Emails Stuck in QUEUED_INV Status

**Symptoms:**
- Emails not being sent
- `customers_email_batches.email_status_id = 8` for extended period

**Possible Causes:**
1. eBill daemon not running
2. Saved document generation failed
3. Database connectivity issues

**Resolution Steps:**
```bash
# 1. Check if daemon is running
ps aux | grep ebill
kubectl get pods | grep ebill  # If Kubernetes

# 2. Check daemon logs
tail -f log/ebill_process_execute.log
kubectl logs -f <ebill-pod>    # If Kubernetes

# 3. Check for document generation failures
SELECT COUNT(*) FROM saved_documents WHERE saved_document_status_id != 2;

# 4. Verify database connectivity
mysql -h $MUNI_MYSQL2_HOST -u $MUNI_MYSQL2_USERNAME -p$MUNI_MYSQL2_PASS $MUNI_MYSQL2_DB -e "SELECT 1"
```

#### Issue 2: Microsoft Email Throttling

**Symptoms:**
- Delivery delays for Outlook/Hotmail addresses
- Temporary failures from Microsoft servers

**Cause:** Microsoft rate limits bulk email senders

**Affected Domains:**
- outlook.com, hotmail.com, live.com, msn.com
- International variants (.co.uk, .fr, .de, etc.)
- outlook.com.br, live.com.au, etc.

**Mitigation:**
```ruby
# EmailRateLimiter adds configurable delay
ENV['MICROSOFT_EMAIL_DELAY_SECONDS'] = '2'  # Default

# Implementation uses Redis for distributed rate limiting
# Fail-open design: continues if Redis unavailable
```

#### Issue 3: SendGrid Webhook Not Updating Status

**Symptoms:**
- Status stuck at SENT, never updates
- No DELIVERED/BOUNCED status recorded

**Possible Causes:**
1. Webhook endpoint not accessible from internet
2. Middleware not parsing SendGrid's JSON format
3. Webhook not configured in SendGrid dashboard

**Verification:**
```bash
# Test webhook endpoint manually
curl -X POST https://your-app/email_batches/process_email_events \
  -H "Content-Type: application/json" \
  -d '[{"event":"delivered","customer_id":"123","email_batch_id":"456","category":"billing"}]'

# Check SendGrid webhook configuration in their dashboard
# Activity Feed shows delivery attempts
```

#### Issue 4: High Memory Usage

**Symptoms:**
- eBill daemon memory growth over time
- OOM kills in Kubernetes

**Cause:** Large batch processing without garbage collection

**Mitigation:**
- Daemon processes in batches with sleep intervals
- Configure pod memory limits appropriately
- Consider daemon restart schedule if persistent

### Troubleshooting SQL Queries

```sql
-- Check email status distribution
SELECT es.name, COUNT(*) as count
FROM customers_email_batches ceb
JOIN email_statuses es ON ceb.email_status_id = es.id
WHERE ceb.created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY es.name;

-- Find stuck emails (QUEUED_INV for > 1 hour)
SELECT ceb.*, c.email, c.account_number
FROM customers_email_batches ceb
JOIN customers c ON ceb.customer_id = c.id
WHERE ceb.email_status_id = 8
  AND ceb.created_at < DATE_SUB(NOW(), INTERVAL 1 HOUR)
LIMIT 100;

-- Check recent batch status
SELECT
  eb.id,
  ebs.name as status,
  eb.created_at,
  COUNT(ceb.id) as email_count,
  SUM(CASE WHEN ceb.email_status_id = 2 THEN 1 ELSE 0 END) as delivered,
  SUM(CASE WHEN ceb.email_status_id IN (3,4,5,7) THEN 1 ELSE 0 END) as failed
FROM email_batches eb
JOIN email_batch_statuses ebs ON eb.email_batch_status_id = ebs.id
LEFT JOIN customers_email_batches ceb ON ceb.email_batch_id = eb.id
WHERE eb.created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY eb.id, ebs.name, eb.created_at
ORDER BY eb.created_at DESC
LIMIT 20;

-- Check saved document failures blocking emails
SELECT sd.saved_document_status_id, COUNT(*)
FROM saved_documents sd
JOIN invoices i ON sd.id = i.saved_document_id
WHERE i.created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY sd.saved_document_status_id;

-- Find companies with email delivery issues
SELECT
  co.name as company,
  COUNT(*) as total,
  SUM(CASE WHEN ceb.email_status_id IN (3,4,5,7) THEN 1 ELSE 0 END) as failures
FROM customers_email_batches ceb
JOIN customers c ON ceb.customer_id = c.id
JOIN companies co ON c.company_id = co.id
WHERE ceb.created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY co.name
HAVING failures > 0
ORDER BY failures DESC;
```

### Performance Recommendations

| Factor | Current | Recommendation |
|--------|---------|----------------|
| Poll interval | 30 seconds | Optimal - don't reduce |
| Batch processing | Unlimited | Consider chunking 100-500 |
| Thread count | Up to 20 | Keep at 20 max |
| Microsoft delay | 2 seconds | Minimum - increase if throttled |
| Daemon restarts | Manual | Consider daily restart |

---

## 13. Database Schema Reference

### email_batches

```sql
CREATE TABLE email_batches (
  id INT AUTO_INCREMENT PRIMARY KEY,
  company_id INT NOT NULL,
  email_batch_status_id INT,
  run_for_multiple_customers TINYINT(1) DEFAULT 1,
  post_billing_job_id INT,
  created_at DATETIME,
  updated_at DATETIME,

  INDEX idx_company_id (company_id),
  INDEX idx_post_billing_job_id (post_billing_job_id),
  FOREIGN KEY (email_batch_status_id) REFERENCES email_batch_statuses(id)
);
```

### customers_email_batches

```sql
CREATE TABLE customers_email_batches (
  id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  email_batch_id INT NOT NULL,
  email_status_id INT NOT NULL,
  email VARCHAR(255),
  created_at DATETIME,
  updated_at DATETIME,

  INDEX idx_customer_batch (customer_id, email_batch_id),
  INDEX idx_batch_customer (email_batch_id, customer_id),
  INDEX idx_status (email_status_id),
  FOREIGN KEY (email_status_id) REFERENCES email_statuses(id)
);
```

### email_statuses (Reference Data)

| ID | Name | Description |
|----|------|-------------|
| 1 | SENT | Successfully handed off |
| 2 | DELIVERED | Confirmed delivery |
| 3 | BOUNCED | Hard/soft bounce |
| 4 | DROPPED | SendGrid dropped |
| 5 | SPAM | Spam complaint |
| 6 | SENDING | In progress |
| 7 | FAILED | Delivery failed |
| 8 | QUEUED_INV | Queued for invoice |

### email_batch_statuses (Reference Data)

| Name | Description |
|------|-------------|
| MAILED | Initial state - in progress |
| COMPLETE_SUCCESS | All emails delivered |
| MAILED_ERRORS | One or more failures |

### Stored Procedures

**sp_email_invoices(p_email_status_id, p_saved_document_status_id)**
- Returns invoices ready for email delivery
- Called by daemon with parameters (8, 2)

**sp_update_emailed_customers_email_batch(p_customers_email_batch_id)**
- Updates status to SENT (1)
- Called after email handed to SendGrid

---

## 14. Monitoring & Observability

### Daemon Health Checks

```bash
# Check process running
pgrep -f ebill_daemon
ps aux | grep ebill

# Kubernetes
kubectl get pods -l app=ebill-daemon
kubectl describe pod <ebill-pod>

# Check recent logs
tail -100 log/ebill_process_execute.log
kubectl logs --tail=100 <ebill-pod>

# Check for errors
grep -i error log/ebill_process_execute.log.ERROR
```

### Key Metrics to Monitor

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| Daemon uptime | Process/Pod | Restart if down > 5 min |
| Queue depth (QUEUED_INV) | Database | Alert if > 1000 pending |
| Failure rate | email_status counts | Alert if > 5% failures |
| Delivery latency | SENT → DELIVERED time | Alert if > 1 hour |
| Memory usage | Pod metrics | Alert at 80% limit |

### Admin UI Endpoints

| URL | Purpose |
|-----|---------|
| `/email_batches` | List all email batches |
| `/email_batches/:id/emails_sent` | Batch detail with per-customer status |
| `/email_batches/poll_status` | AJAX status polling |
| `/jobs/sidekiq` | Sidekiq dashboard |

### SendGrid Monitoring

- **Activity Feed:** View individual email status
- **Stats Dashboard:** Delivery metrics, bounce rates
- **Suppressions:** Manage blocked addresses
- **Webhook Settings:** Configure event notifications

---

## 15. Quick Reference

### Status Flow Diagram

```
Bill Posted
    │
    ▼
EmailBatch Created (status: MAILED)
    │
    ▼
CustomersEmailBatch Created (status: QUEUED_INV)
    │
    ▼
Daemon Polls (every 30s)
    │
    ▼
sp_email_invoices(8, 2) → Returns eligible invoices
    │
    ▼
Build SendGrid payload + Mark SENT
    │
    ▼
POST api.sendgrid.com/v3/mail/send
    │
    ▼
SendGrid Webhook Event
    │
    ├──▶ DELIVERED (success)
    │
    └──▶ BOUNCED/DROPPED/SPAM (failure)
              │
              ▼
         Notify Company Support
```

### Key Email Addresses

| Purpose | Address |
|---------|---------|
| Daemon FROM | `noreply@safemaildelivery.net` |
| Notice FROM | `customerservice@munibilling.com` |
| Non-prod redirect | `testing@munibilling.com` |
| Company reply-to | Per company configuration |

### Key Template IDs

| Template | ID |
|----------|-----|
| eBill | `ad152bee-e411-4e94-a558-4186aa9cdb94` |
| Autopay Warning | `ee494e99-bd7f-484d-bd5a-fb4f22adef9b` |

### Environment URL Mapping

| Env | Portal URL |
|-----|------------|
| Production | `https://{url_name}.secure.munibilling.com` |
| Staging | `https://{url_name}.staging.munibilling.com` |
| Demo | `https://{url_name}.demo.munibilling.com` |

### Emergency Contacts

- **SendGrid Issues:** SendGrid Support Portal
- **Database Issues:** Database Team
- **Daemon/K8s Issues:** DevOps Team

---

*Document Version: 1.0*
*Last Updated: January 2026*
*Maintained By: MuniBilling Engineering*
