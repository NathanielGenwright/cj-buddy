# Payment Processing System - Technical Setup Documentation

**Document Type:** Internal Technical Reference
**Target Audience:** Engineering, DevOps, Support Teams
**Format:** External Document (Copy to Confluence/SharePoint)

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Components](#2-architecture-components)
3. [Payment Gateways](#3-payment-gateways)
4. [RemoteCharge Lifecycle](#4-remotecharge-lifecycle)
5. [Purchaser Pattern](#5-purchaser-pattern)
6. [Convenience Fee Processing](#6-convenience-fee-processing)
7. [Token Management](#7-token-management)
8. [Payment Application](#8-payment-application)
9. [Gateway Health Monitoring](#9-gateway-health-monitoring)
10. [Autopay Integration](#10-autopay-integration)
11. [Configuration Requirements](#11-configuration-requirements)
12. [Failure Handling & Void Logic](#12-failure-handling--void-logic)
13. [Troubleshooting](#13-troubleshooting)
14. [Database Schema Reference](#14-database-schema-reference)
15. [Quick Reference](#15-quick-reference)

---

## 1. System Overview

### What is the Payment Processing System?

The MuniBilling Payment Processing System handles all electronic payment transactions including credit cards, e-checks, ACH transfers, and lockbox payments. It integrates with multiple payment gateways and supports both one-time and recurring (autopay) transactions.

### Key Capabilities

- **Multi-Gateway Support**: Heartland (SOAP) and Paya Connect (REST)
- **Split Transaction Processing**: Separate base amount and convenience fees
- **Token-Based Security**: PCI-compliant tokenized payment storage
- **Autopay/Recurring Payments**: Automated scheduled billing
- **Multiple Payment Types**: Credit, E-Check, ACH, Lockbox, IVR
- **Fee Calculation**: Tier-based convenience fee computation
- **Payment Distribution**: Automatic application to customer balances
- **Refund/Void Processing**: Transaction reversal capabilities

### Payment Types Supported

| Type | ID | String Constant | Description |
|------|----|-----------------|-------------|
| Credit Card | 1 | `credit` | Standard credit/debit card |
| E-Check | 2 | `onlinecheck` | Online check/ACH |
| ACH | 3 | `ach` | Direct bank transfer |
| Lockbox | 4 | `lockbox` | Bank lockbox payments |
| IVR Credit | 5 | `ivr_credit` | Phone system credit card |
| IVR E-Check | 6 | `ivr_echeck` | Phone system e-check |

---

## 2. Architecture Components

### File Structure

```
muni-billing/legacy/
├── lib/charges/
│   ├── main_factory.rb                      # Central factory for charge components
│   ├── logger.rb                            # Unified logging
│   ├── bridges/
│   │   ├── heartland.rb                     # Heartland gateway bridge (308 lines)
│   │   └── paya_connect.rb                  # Paya Connect bridge (235 lines)
│   ├── purchasers/
│   │   ├── factory.rb                       # Purchaser factory (42 lines)
│   │   ├── bridged_purchaser.rb             # Production purchaser (169 lines)
│   │   ├── abstract_purchaser.rb            # Base class
│   │   ├── dummy_purchaser.rb               # Test/dev purchaser
│   │   ├── early_failure.rb                 # Pre-purchase validation failures
│   │   └── final_result.rb                  # Purchase result wrapper
│   ├── utils/
│   │   ├── fee_calculator.rb                # Tier-based fee calculation (97 lines)
│   │   ├── remote_charge_manager.rb         # Batch processing (383 lines)
│   │   ├── recurring_charge_processor.rb    # Autopay processing (361 lines)
│   │   └── recurring_batch_processor.rb     # Batch autopay handling
│   ├── autopay/
│   │   ├── charge.rb                        # Autopay charge wrapper
│   │   └── charge_template.rb               # Autopay template builder
│   └── paya/
│       ├── fee_charger.rb                   # Paya fee transaction processor
│       ├── recurring_charger.rb             # Paya recurring payment handler
│       ├── health_checker.rb                # Gateway health monitoring
│       └── client_commons1.rb               # Shared Paya constants
├── app/
│   ├── models/
│   │   ├── remote_charge.rb                 # Payment transaction model (216 lines)
│   │   ├── recurring_charge.rb              # Autopay enrollment model
│   │   ├── payment_gateway_profile.rb       # Gateway configuration
│   │   ├── payment_gateway.rb               # Gateway definitions
│   │   └── payment_gateway_profile_tier.rb  # Fee tier configuration
│   └── gateways/
│       ├── heartland_gateway.rb             # Heartland SOAP client
│       └── paya_connect_gateway.rb          # Paya REST client
└── payments/
    └── remote_charge_payments_distributor.rb # Payment application logic
```

### Process Flow Overview

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Payment Request │────▶│  RemoteCharge    │────▶│  Purchaser       │
│  (Portal/API)    │     │  Created         │     │  Factory         │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                                           │
                                                           ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Payment         │◀────│  Gateway         │◀────│  Bridge          │
│  Distributed     │     │  Response        │     │  (HB/Paya)       │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

---

## 3. Payment Gateways

### Gateway Comparison

| Feature | Heartland | Paya Connect |
|---------|-----------|--------------|
| **Protocol** | SOAP/XML | REST/JSON |
| **Authentication** | API credentials in SOAP header | Bearer token |
| **Split Transactions** | Yes - dual merchant IDs | Yes - separate API calls |
| **Token Storage** | Multi-use token returned | Account vault ID |
| **Response Format** | XML envelope | JSON object |
| **Health Check** | Service availability | `/v1/transactions` endpoint |

### Heartland Gateway

**File:** `lib/charges/bridges/heartland.rb`

**Integration Details:**
- SOAP-based API with XML payloads
- Uses `HeartlandGateway` class for actual API calls
- Credentials stored in `payment_gateway.user_defined_1..5` fields:
  - `user_defined_1`: API username
  - `user_defined_2`: API password
  - `user_defined_3`: Fee merchant ID
  - `user_defined_4`: Service location URL
  - `user_defined_5`: SOAP action

**Key Methods:**
```ruby
# lib/charges/bridges/heartland.rb

def purchase(remote_charge)
  if remote_charge.recurring_charge_id.present?
    # Autopay: use stored token
    if remote_charge.customer_fee.positive?
      autopay_with_fee(remote_charge)
    else
      autopay_without_fee(remote_charge)
    end
  else
    # One-time: may need to exchange token
    if remote_charge.customer_fee.positive?
      pay_with_fee(remote_charge)
    else
      pay_without_fee(remote_charge)
    end
  end
end
```

**Transaction Flow with Fee:**
1. Process fee transaction on fee merchant → returns `transaction_id`
2. If fee succeeds, process base transaction on base merchant
3. If base fails after fee succeeds, **void the fee transaction**
4. Store both responses in `remote_charge`

### Paya Connect Gateway

**File:** `lib/charges/bridges/paya_connect.rb`

**Integration Details:**
- REST API with JSON payloads
- Uses account vault tokens for stored payments
- Response codes mapped to human-readable messages

**Response Code Mapping:**
```ruby
PAYA_RESPONSE_MESSAGES = {
  "1000" => 'Approved and Complete',
  "1500" => 'Do Not Honor / Insufficient Funds / Activity Limit Exceeded',
  "1608" => 'Invalid Card Number / No Credit Account',
  "1622" => 'Expired Card',
  "1618" => 'Transaction not PermittedCard',
  "1619" => 'Amount Greater than Limit',
  # ... additional codes
}
```

**Key Methods:**
```ruby
# lib/charges/bridges/paya_connect.rb

def purchase(remote_charge)
  if remote_charge.recurring_charge_id.present?
    # Recurring: initiate new transaction with stored token
    purchase_recurring(remote_charge)
  else
    # Online: finalize existing transaction
    finalize_transaction(
      remote_charge: remote_charge,
      base_transaction_data: online_data(remote_charge))
  end
end
```

**Paya Transaction Finalization:**
1. Retrieve base transaction data from `remote_raw_response`
2. If fee required, save base transaction and process convenience fee
3. Update RemoteCharge with all response data (AVS, CVV, batch number)

---

## 4. RemoteCharge Lifecycle

### Status Constants

```ruby
# app/models/remote_charge.rb

STATUS_PROCESSING = 1      # Transaction initiated
STATUS_SUCCESS = 2         # Approved and complete
STATUS_FAIL = 3            # Declined or error
STATUS_DUPLICATE = 4       # Duplicate transaction detected
STATUS_NO_RECURRING_MATCH = 5  # Autopay token not found
STATUS_PENDING = 6         # Started but potentially abandoned
```

### Status Lifecycle

```
┌─────────────────┐
│    PENDING      │  Customer started payment, not yet submitted
│      (6)        │
└────────┬────────┘
         │ Submit payment
         ▼
┌─────────────────┐
│   PROCESSING    │  Sent to gateway, awaiting response
│      (1)        │
└────────┬────────┘
         │ Gateway responds
         ▼
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌───────┐
│SUCCESS│ │ FAIL  │
│  (2)  │ │  (3)  │
└───────┘ └───────┘
```

### Dual Status Fields (Split Transactions)

When processing convenience fees, RemoteCharge uses **two sets of status fields**:

| Field Set | Without Fee | With Fee |
|-----------|-------------|----------|
| **Primary (status_id)** | Base transaction | Fee transaction |
| **Secondary (status_2_id)** | Unused | Base transaction |
| **Auth Code** | `remote_auth_code` | `remote_auth_code_2` |
| **Raw Response** | `remote_raw_response` | `remote_raw_response_2` |

**Code Reference:** `lib/charges/bridges/heartland.rb:62-91`

```ruby
def autopay_with_fee(remote_charge)
  # Fee transaction stored in primary fields
  fee_response = autopay_with_fee__fee_response(remote_charge)
  apply_response(remote_charge: remote_charge, response: fee_response)

  if remote_charge.remote_charge_status_id == RemoteCharge::STATUS_SUCCESS
    # Base transaction stored in secondary fields
    base_response = autopay_with_fee__base_response(remote_charge)
    remote_charge.remote_charge_status_2_id = to_status_id(base_response)
    # ...
  end
end
```

### Key RemoteCharge Fields

| Field | Purpose | Example |
|-------|---------|---------|
| `amount` | Total transaction amount | `155.00` |
| `net_amount` | Amount applied to balance | `150.00` |
| `customer_fee` | Convenience fee portion | `5.00` |
| `applied_payment_amount` | Base payment amount | `150.00` |
| `token` | Payment method token | `abc123...` |
| `token_2` | Secondary token (Heartland) | `def456...` |
| `remote_auth_code` | Authorization code | `A12345` |
| `remote_batch_id` | Settlement batch ID | `1234567` |
| `remote_batch_date` | Settlement date | `2025-01-08` |

---

## 5. Purchaser Pattern

### Factory Pattern Overview

The system uses a **Factory → Purchaser → Bridge → Gateway** pattern for payment processing.

**File:** `lib/charges/purchasers/factory.rb`

```ruby
module Charges
  module Purchasers
    class Factory
      def purchaser_for(remote_charge)
        if ENV['DUMMY_PURCHASER'].present?
          # Test mode - never in production
          raise ArgumentError if Rails.env.production?
          DummyPurchaser.new(remote_charge: remote_charge)
        else
          # Production: use bridged purchaser
          BridgedPurchaser.new(
            remote_charge: remote_charge,
            benchmark_collector: benchmark_collector)
        end
      end
    end
  end
end
```

### BridgedPurchaser

**File:** `lib/charges/purchasers/bridged_purchaser.rb`

**Responsibilities:**
1. Set charge to PROCESSING status before gateway call
2. Execute gateway purchase via bridge
3. Handle split transaction status logic
4. Create payment record on success
5. Return `FinalResult` with charge and payment

```ruby
def call
  benchmark_collector.collect_benchmark(...) do
    # Move to processing OUTSIDE transaction (persists even on error)
    set_charge_status

    Customer.transaction do
      perform_charge          # Call gateway via bridge
      check_charge_status     # Validate both statuses if split
      payment_record          # Create Payment if successful
      set_display_message

      Charges::Purchasers::FinalResult.new(
        remote_charge: remote_charge,
        payment: payment_record)
    end
  end
end
```

### Payment Distribution

On successful purchase, `RemoteChargePaymentsDistributor` applies the payment:

**File:** `app/payments/remote_charge_payments_distributor.rb`

```ruby
Payments::RemoteChargePaymentsDistributor.new(
  customer,
  remote_charge,
  payment_date
).distribute
```

This distributes the payment amount across the customer's open invoices/charges.

---

## 6. Convenience Fee Processing

### Overview

Convenience fees are **optional charges** passed to customers for using certain payment methods. The system supports both:
- **Pass-through**: Customer pays fee on top of bill amount
- **Absorb**: Company absorbs the fee (no customer charge)

### Fee Calculator

**File:** `lib/charges/utils/fee_calculator.rb`

The calculator uses **tier-based pricing** from `payment_gateway_profile_tiers`:

```ruby
module Charges
  module Utils
    class FeeCalculator
      def bind(payment_gateway_profile:, base_amount:)
        @pgp = payment_gateway_profile
        @base_amount = base_amount
        self
      end

      def standard_fee
        # Sum fees across all applicable tiers
        tiers.each do |tier|
          if base_amount >= tier.from
            tier_amount = calculate_tier_amount(tier)
            tmp += if tier.is_percent
                     tier_amount * (tier.fee / 100)
                   else
                     tier.fee
                   end
          end
        end
        tmp.round(2)
      end

      def absorb_fee
        # Same logic but uses tier.absorb_fee field
      end

      def non_fee
        # For non-fee transactions
      end
    end
  end
end
```

### Tier Configuration Example

| From | To | Fee | Is Percent | Absorb Fee |
|------|-----|-----|------------|------------|
| $0.01 | $100.00 | $2.50 | No | $0.00 |
| $100.01 | $500.00 | 2.5% | Yes | $0.00 |
| $500.01 | $99999.99 | 2.0% | Yes | $0.00 |

### Split Transaction Processing

When `customer_fee > 0`, the system processes **two separate transactions**:

**Heartland Flow:**
1. **Fee Transaction** → Fee Merchant Account
   - Amount: `customer_fee`
   - Stored in: `remote_charge_status_id`, `remote_raw_response`
2. **Base Transaction** → Base Merchant Account
   - Amount: `applied_payment_amount`
   - Stored in: `remote_charge_status_2_id`, `remote_raw_response_2`

**Paya Flow:**
1. **Base Transaction** → Primary endpoint
   - Stored in: `remote_charge_status_2_id`, `remote_raw_response_2`
2. **Fee Transaction** → Fee API endpoint
   - Uses `Charges::Paya::FeeCharger`
   - Stored in: `remote_charge_status_id`, `remote_raw_response`

**Code Reference:** `lib/charges/paya/fee_charger.rb`

```ruby
module Charges
  module Paya
    class FeeCharger
      def self.call(remote_charge, base_transaction_data)
        # Build fee transaction payload
        # POST to Paya fee endpoint
        # Return response data
      end
    end
  end
end
```

---

## 7. Token Management

### Token Types

| Token Field | Usage | Gateway |
|-------------|-------|---------|
| `token` | Primary payment token | Both |
| `token_2` | Permanent token after exchange | Heartland |
| `recurring_charge.token` | Stored autopay token | Both |

### Token Exchange (Heartland)

For one-time payments, Heartland requires a **token exchange**:

1. Customer enters card → receives temporary `token`
2. First transaction uses `make_quick_pay_blind_payment_return_token`
3. Response includes permanent `token_2` for second transaction

**Code Reference:** `lib/charges/bridges/heartland.rb:190-206`

```ruby
def pay_with_fee__fee_response(remote_charge)
  HeartlandGateway.new.make_quick_pay_blind_payment_return_token({
    token: remote_charge.token,
    amount: remote_charge.customer_fee.to_s,
    # ... returns permanent token
  })
end
```

### Paya Token Storage

Paya uses **account vault IDs** stored directly from the iframe response:

```ruby
def get_token(params)
  result = params['data']
  ValueObjects::GetTokenResponse.new(
    token: result['id'],  # Account vault ID
    success: status(params),
    # ...
  )
end
```

### Recurring Charge Token Storage

**File:** `lib/charges/utils/remote_charge_manager.rb:19-111`

When customer enrolls in autopay:
1. Token obtained from gateway
2. Stored in `recurring_charge.token`
3. Customer marked `automatic_payments = true`

```ruby
def save_payment_information(params = {})
  get_token_response = make_bridge(params[:payment_gateway_profile]).get_token(params)

  recurring_charge = RecurringCharge.new(
    customer_id: params[:customer_id],
    token: get_token_response.token,
    # ... other fields
  )

  if get_token_response.success
    recurring_charge.recurring_charge_status_id = RecurringCharge::STATUS_ACTIVE
    Customer.find(params[:customer_id]).update_attributes!(automatic_payments: true)
  end

  recurring_charge.save!
end
```

---

## 8. Payment Application

### RemoteChargePaymentsDistributor

When a payment succeeds, the system automatically applies it to the customer's balance:

**File:** `app/payments/remote_charge_payments_distributor.rb`

```ruby
class RemoteChargePaymentsDistributor
  def initialize(customer, remote_charge, payment_date)
    @customer = customer
    @remote_charge = remote_charge
    @payment_date = payment_date
  end

  def distribute
    # 1. Create Payment record
    # 2. Apply to open invoices (oldest first)
    # 3. Handle overpayment as credit
    # 4. Update customer balance
  end
end
```

### Payment Record Creation

For parcel owners (multi-account):
```ruby
Payments::ParcelOwnerPaymentManager.new.new_parcel_owner_payment(
  buyer.customers,
  parcel_owner_payment,
  buyer.company,
  entered_user,
  remote_charge.id
)
```

For single customers:
```ruby
Payments::RemoteChargePaymentsDistributor.new(
  buyer,
  remote_charge,
  payment_date
).distribute
```

### Skip Payment Conditions

Payment record creation is skipped when:
- Charge failed (`STATUS_FAIL`)
- Duplicate transaction (`STATUS_DUPLICATE`)
- Processing not complete (`STATUS_PROCESSING`)
- No recurring match (`STATUS_NO_RECURRING_MATCH`)

**Code Reference:** `lib/charges/purchasers/bridged_purchaser.rb:124-133`

---

## 9. Gateway Health Monitoring

### Paya Health Checker

**File:** `lib/charges/paya/health_checker.rb`

Provides real-time gateway availability status:

```ruby
module Charges
  module Paya
    class HealthChecker
      def self.check
        # Ping Paya /v1/transactions endpoint
        # Return status and response time
      end

      def self.healthy?
        check[:status] == :healthy
      end
    end
  end
end
```

### Health Check Integration

- Scheduled hourly via background job
- Status displayed in admin dashboard
- Affects customer portal payment availability messaging

### Heartland Health Check

Heartland health is checked via service availability:
- Verify SOAP endpoint responds
- Confirm authentication succeeds
- Check response time thresholds

---

## 10. Autopay Integration

### Recurring Charge Processing

**File:** `lib/charges/utils/recurring_charge_processor.rb`

The autopay system runs nightly to process scheduled payments:

```ruby
class RecurringChargeProcessor
  def call
    if recurring_amount > 0
      if needs_suspension?
        suspend_recurring_payment(reason: TOO_MANY_FAILURES)
      else
        process_recurring_payment
        suspend_recurring_payment(reason: TOO_MANY_FAILURES) if needs_suspension?
      end
    else
      mark_as_skipped(reason: "zero amount")
    end

    recurring_charge.save!
  end
end
```

### Retry Logic

```ruby
def max_attempts
  payment_gateway_profile.recurring_attempts  # Configurable per gateway
end

def can_retry_tomorrow?
  is_active? && (attempts_this_cycle < max_attempts)
end

def needs_suspension?
  is_active? && is_enabled? && (attempts_this_cycle > max_attempts)
end
```

### Outcome Handling

| Outcome | Action | Notification |
|---------|--------|--------------|
| **Success** | Reset attempts, advance to next date | `successful_payment` |
| **Fail (can retry)** | Increment attempts, try tomorrow | `payment_failed_and_will_retry` |
| **Fail (max retries)** | Suspend enrollment | `payment_failed_and_dropped` |
| **Zero amount** | Skip, advance to next date | None |

### Customer Flag Management

On suspension, the system clears the autopay enrollment flag:

```ruby
def clear_automatic_payments_indicator_for_customer
  # Raw SQL to avoid model callbacks and locking issues
  ActiveRecord::Base.connection.execute(
    "UPDATE customers SET automatic_payments=FALSE WHERE id = #{customer_id}"
  )
end
```

**Code Reference:** `lib/charges/utils/recurring_charge_processor.rb:115-117`

---

## 11. Configuration Requirements

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MUNI_ENV` | **Yes** | Environment (production, staging, demo) |
| `DUMMY_PURCHASER` | Dev only | Enable test purchaser (never in production) |

### Payment Gateway Configuration

**Table:** `payment_gateways`

| Field | Purpose | Example (Heartland) | Example (Paya) |
|-------|---------|---------------------|----------------|
| `name` | Gateway identifier | `Heartland` | `Paya Connect` |
| `user_defined_1` | API username | `api_user` | `api_key` |
| `user_defined_2` | API password | `api_pass` | `api_secret` |
| `user_defined_3` | Fee merchant ID | `fee_merch_123` | N/A |
| `user_defined_4` | Service URL | `https://api.heartland...` | `https://api.sandbox...` |
| `user_defined_5` | SOAP action | `MakeBlindPayment` | N/A |

### Payment Gateway Profile Configuration

**Table:** `payment_gateway_profiles`

| Field | Purpose | Default |
|-------|---------|---------|
| `company_id` | Associated company | Required |
| `payment_gateway_id` | Gateway reference | Required |
| `merchant_user_name` | Base merchant ID | Required |
| `enabled` | Profile active | TRUE |
| `recurring_attempts` | Max autopay retries | 3 |
| `recurring_charge_frequency_type_id` | Monthly/Weekly/etc | Monthly |
| `recurring_charge_frequency_interval` | Every N periods | 1 |
| `remote_charge_type_id` | Credit/E-Check | Credit |

### Fee Tier Configuration

**Table:** `payment_gateway_profile_tiers`

| Field | Type | Purpose |
|-------|------|---------|
| `payment_gateway_profile_id` | FK | Parent profile |
| `from` | Decimal | Tier start amount |
| `to` | Decimal | Tier end amount |
| `fee` | Decimal | Fee value |
| `is_percent` | Boolean | Fee as percentage |
| `absorb_fee` | Decimal | Company-absorbed fee |
| `absorb_fee_is_percent` | Boolean | Absorb as percentage |
| `non_fee` | Decimal | Non-fee transaction fee |
| `non_fee_is_percent` | Boolean | Non-fee as percentage |

---

## 12. Failure Handling & Void Logic

### Void on Split Transaction Failure

When the base transaction fails after a successful fee transaction, the system **automatically voids** the fee:

**Code Reference:** `lib/charges/bridges/heartland.rb:74-87`

```ruby
def autopay_with_fee(remote_charge)
  fee_response = autopay_with_fee__fee_response(remote_charge)
  apply_response(remote_charge: remote_charge, response: fee_response)

  if remote_charge.remote_charge_status_id == RemoteCharge::STATUS_SUCCESS
    base_response = autopay_with_fee__base_response(remote_charge)
    remote_charge.remote_charge_status_2_id = to_status_id(base_response)

    # If base fails after fee succeeds, void the fee
    if remote_charge.remote_charge_status_2_id == RemoteCharge::STATUS_FAIL &&
       fee_response.transaction_id
      void_response = void_transaction_response(
        remote_charge: remote_charge,
        transaction_id: fee_response.transaction_id)

      set_void_response(remote_charge: remote_charge, ...)
    end
  end
end
```

### Void Transaction (Heartland)

```ruby
def void_transaction_response(remote_charge:, transaction_id:)
  HeartlandGateway.new.void_transaction({
    api_user_name: remote_charge.payment_gateway_profile.payment_gateway.user_defined_1,
    api_password: remote_charge.payment_gateway_profile.payment_gateway.user_defined_2,
    charge_merchant: remote_charge.payment_gateway_profile.payment_gateway.user_defined_3,
    service_location: remote_charge.payment_gateway_profile.payment_gateway.user_defined_4,
    soap_action: remote_charge.payment_gateway_profile.payment_gateway.user_defined_5,
    void_comment: 'Void fee charge b/c secondary payment charge failed',
    transaction_id: transaction_id
  })
end
```

### Status Clearing on Failure

When a base transaction fails, the fee status is cleared:

```ruby
def clear_fee_status
  if should_have_fee?
    # Fee in primary fields - clear primary
    remote_charge.remote_charge_status_id = nil
  else
    # Fee in secondary fields - clear secondary
    remote_charge.remote_charge_status_2_id = nil
  end
end
```

### Early Failure Handling

Charges that fail business validation before gateway submission:

**File:** `lib/charges/purchasers/early_failure.rb`

```ruby
module Charges
  module Purchasers
    class EarlyFailure
      def self.build(remote_charge:, display_message:)
        # Return result without calling gateway
        # Charge marked as failed with validation errors
      end
    end
  end
end
```

---

## 13. Troubleshooting

### Common Issues

#### Issue 1: Payment Stuck in PROCESSING Status

**Symptoms:**
- `remote_charge_status_id = 1` for extended period
- No payment record created
- Customer charged but balance not updated

**Possible Causes:**
1. Gateway timeout during response
2. Network interruption
3. Database transaction failure after gateway call

**Resolution:**
```sql
-- Find stuck processing charges
SELECT id, customer_id, amount, created_at, remote_message
FROM remote_charges
WHERE remote_charge_status_id = 1
  AND created_at < DATE_SUB(NOW(), INTERVAL 1 HOUR);

-- Check gateway response
SELECT id, remote_raw_response, remote_raw_response_2
FROM remote_charges
WHERE id = [charge_id];
```

**Manual Recovery:**
1. Check gateway dashboard for actual transaction status
2. If successful at gateway, manually update status and create payment
3. If failed at gateway, update to FAIL status

#### Issue 2: Split Transaction Partial Success

**Symptoms:**
- Fee charged successfully
- Base transaction failed
- Fee not voided

**Causes:**
- Void API call failed
- Timeout during void operation

**Resolution:**
```sql
-- Find charges with fee success, base failure, no void
SELECT rc.id, rc.customer_id, rc.customer_fee, rc.applied_payment_amount,
       rc.remote_charge_status_id as fee_status,
       rc.remote_charge_status_2_id as base_status
FROM remote_charges rc
WHERE rc.remote_charge_status_id = 2  -- Fee success
  AND rc.remote_charge_status_2_id = 3  -- Base fail
  AND rc.customer_fee > 0;
```

**Manual Void:**
- Contact gateway provider to void fee transaction
- Update charge record with void confirmation

#### Issue 3: Autopay Token Invalid

**Symptoms:**
- `STATUS_NO_RECURRING_MATCH` (5)
- Customer enrolled but payment fails

**Causes:**
- Token expired at gateway
- Card replaced/expired
- Account closed at bank

**Resolution:**
1. Verify token exists in `recurring_charge.token`
2. Check gateway dashboard for token status
3. If invalid, suspend enrollment and notify customer

#### Issue 4: Fee Calculation Mismatch

**Symptoms:**
- Customer charged different fee than expected
- Tier configuration appears correct

**Causes:**
- Overlapping tier ranges
- Percent vs flat fee confusion
- Rounding differences

**Debug:**
```ruby
# Console debugging
pgp = PaymentGatewayProfile.find([profile_id])
calculator = Charges::Utils::FeeCalculator.new
calculator.bind(payment_gateway_profile: pgp, base_amount: 150.00)
puts calculator.standard_fee  # Expected fee
```

### Diagnostic SQL Queries

```sql
-- Payment success rate by gateway (last 7 days)
SELECT
  pg.name as gateway,
  COUNT(*) as total,
  SUM(CASE WHEN rc.remote_charge_status_id = 2 THEN 1 ELSE 0 END) as success,
  ROUND(SUM(CASE WHEN rc.remote_charge_status_id = 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate
FROM remote_charges rc
JOIN payment_gateway_profiles pgp ON rc.payment_gateway_profile_id = pgp.id
JOIN payment_gateways pg ON pgp.payment_gateway_id = pg.id
WHERE rc.created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY pg.name;

-- Recent failed payments with reasons
SELECT
  rc.id,
  rc.customer_id,
  rc.amount,
  rc.remote_message,
  rc.display_message,
  rc.created_at
FROM remote_charges rc
WHERE rc.remote_charge_status_id = 3
  AND rc.created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY rc.created_at DESC
LIMIT 50;

-- Autopay suspension reasons
SELECT
  rc2.display_message,
  COUNT(*) as count
FROM recurring_charges rc2
WHERE rc2.recurring_charge_status_id = 2  -- CANCELLED
  AND rc2.updated_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY rc2.display_message
ORDER BY count DESC;

-- Split transaction status analysis
SELECT
  CASE WHEN customer_fee > 0 THEN 'With Fee' ELSE 'No Fee' END as fee_type,
  remote_charge_status_id as status_1,
  remote_charge_status_2_id as status_2,
  COUNT(*) as count
FROM remote_charges
WHERE created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY fee_type, remote_charge_status_id, remote_charge_status_2_id
ORDER BY count DESC;
```

---

## 14. Database Schema Reference

### remote_charges

```sql
CREATE TABLE remote_charges (
  id INT AUTO_INCREMENT PRIMARY KEY,
  company_id INT NOT NULL,
  customer_id INT,
  parcel_owner_id INT,
  recurring_charge_id INT,
  payment_gateway_profile_id INT NOT NULL,

  -- Amounts
  amount DECIMAL(10,2),
  net_amount DECIMAL(10,2),
  customer_fee DECIMAL(10,2),
  applied_payment_amount DECIMAL(10,2),

  -- Status (Primary - Fee if split, Base if not)
  remote_charge_status_id INT,
  remote_auth_code VARCHAR(50),
  remote_raw_response TEXT,
  remote_message VARCHAR(255),

  -- Status (Secondary - Base if split)
  remote_charge_status_2_id INT,
  remote_auth_code_2 VARCHAR(50),
  remote_raw_response_2 TEXT,

  -- Tokens
  token VARCHAR(255),
  token_2 VARCHAR(255),

  -- Settlement
  remote_batch_id INT,
  remote_batch_date DATETIME,
  customer_fee_remote_batch_id INT,
  customer_fee_remote_batch_date DATETIME,

  -- Card Details (Paya)
  zip_code VARCHAR(20),
  account_name VARCHAR(255),
  expiration_month VARCHAR(2),
  expiration_year VARCHAR(4),

  -- Metadata
  remote_charge_type_id INT,
  remote_request TEXT,
  display_message VARCHAR(255),
  uuid VARCHAR(36),

  created_at DATETIME,
  updated_at DATETIME,

  INDEX idx_company (company_id),
  INDEX idx_customer (customer_id),
  INDEX idx_status (remote_charge_status_id),
  INDEX idx_created (created_at)
);
```

### recurring_charges

```sql
CREATE TABLE recurring_charges (
  id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  payment_gateway_profile_id INT NOT NULL,
  recurring_charge_status_id INT NOT NULL,

  -- Schedule
  start_date DATE,
  end_date DATE,
  next_charge_date DATE,
  recurring_charge_frequency_type_id INT,
  recurring_charge_frequency_interval INT,

  -- Amount
  recurring_amount DECIMAL(10,2),

  -- Token
  token VARCHAR(255),

  -- Card Details
  account_name VARCHAR(255),
  last_four_digits VARCHAR(4),
  zip_code VARCHAR(20),
  expiration_month VARCHAR(2),
  expiration_year VARCHAR(4),

  -- Processing
  attempts_this_cycle INT DEFAULT 0,
  display_message VARCHAR(255),
  remote_message VARCHAR(255),

  created_at DATETIME,
  updated_at DATETIME,

  INDEX idx_customer (customer_id),
  INDEX idx_next_charge (next_charge_date),
  INDEX idx_status (recurring_charge_status_id)
);
```

### payment_gateway_profiles

```sql
CREATE TABLE payment_gateway_profiles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  company_id INT NOT NULL,
  payment_gateway_id INT NOT NULL,
  merchant_user_name VARCHAR(255),
  enabled TINYINT(1) DEFAULT 1,

  -- Recurring Settings
  recurring_attempts INT DEFAULT 3,
  recurring_charge_frequency_type_id INT,
  recurring_charge_frequency_interval INT,
  remote_charge_type_id INT,

  created_at DATETIME,
  updated_at DATETIME,

  INDEX idx_company (company_id),
  INDEX idx_gateway (payment_gateway_id)
);
```

### payment_gateway_profile_tiers

```sql
CREATE TABLE payment_gateway_profile_tiers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  payment_gateway_profile_id INT NOT NULL,

  `from` DECIMAL(10,2) NOT NULL,
  `to` DECIMAL(10,2) NOT NULL,
  fee DECIMAL(10,4),
  is_percent TINYINT(1) DEFAULT 0,
  absorb_fee DECIMAL(10,4),
  absorb_fee_is_percent TINYINT(1) DEFAULT 0,
  non_fee DECIMAL(10,4),
  non_fee_is_percent TINYINT(1) DEFAULT 0,

  INDEX idx_profile (payment_gateway_profile_id)
);
```

---

## 15. Quick Reference

### Status Mapping

| Status | ID | Human Label | Payment Created |
|--------|-----|-------------|-----------------|
| PROCESSING | 1 | Processing | No |
| SUCCESS | 2 | Success | Yes |
| FAIL | 3 | Fail | No |
| DUPLICATE | 4 | Duplicate | No |
| NO_RECURRING_MATCH | 5 | No Match | No |
| PENDING | 6 | Pending | No |

### Gateway Selection

```ruby
# Determine gateway from remote_charge
remote_charge.paya_connect?  # => true/false
remote_charge.heartland?     # => true/false
remote_charge.payment_gateway_name  # => "Paya Connect" / "Heartland"
```

### Fee Calculation Quick Reference

```ruby
# Calculate fee for a payment
pgp = PaymentGatewayProfile.find(profile_id)
fee = Charges::Utils::FeeCalculator.new
        .bind(payment_gateway_profile: pgp, base_amount: amount)
        .standard_fee
```

### Key Code Entry Points

| Operation | Entry Point |
|-----------|-------------|
| Process Payment | `Charges::Purchasers::Factory.new.purchaser_for(charge).call` |
| Calculate Fee | `Charges::Utils::FeeCalculator.new.bind(...).standard_fee` |
| Save Autopay Token | `Charges::Utils::RemoteChargeManager.new.save_payment_information(...)` |
| Process Autopay Batch | `Charges::Utils::RemoteChargeManager.new.get_recurring_payments(date)` |
| Check Gateway Health | `Charges::Paya::HealthChecker.check` |

### Amount Relationship

```
amount = net_amount + customer_fee
applied_payment_amount = net_amount (base transaction amount)
```

### Emergency Contacts

- **Gateway Issues (Heartland):** Heartland Support Portal
- **Gateway Issues (Paya):** Paya Support
- **Split Transaction Problems:** DevOps Team
- **Autopay Failures:** Customer Support + Engineering

---

*Document Version: 1.0*
*Last Updated: January 2026*
*Maintained By: MuniBilling Engineering*
