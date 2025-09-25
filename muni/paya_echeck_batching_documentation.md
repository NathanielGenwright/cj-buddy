# Paya eCheck Payment Batching Documentation

## Overview

The Muni billing system integrates with Paya Connect gateway to process online eCheck (electronic check) payments. This document details how eCheck payments are batched, processed, and reconciled within the system for companies using Paya gateway profiles.

## What is eCheck Batching?

eCheck batching is the process where individual electronic check transactions are grouped together by the payment processor (Paya) for settlement with the banking system. Unlike credit card transactions that settle quickly, eCheck transactions go through a batching process where:

1. Individual eCheck payments are collected throughout the day
2. Paya groups these transactions into batches at specific intervals
3. Each batch is assigned a unique batch ID and batch date
4. The batch is submitted to the ACH network for processing
5. Settlement occurs 1-3 business days later

## Database Schema and Key Tables

### Core Tables

#### `remote_charges` Table
Primary table for storing all online payment transactions:
```sql
- id: Primary key
- customer_id: Link to customers table
- company_id: Company this charge belongs to
- remote_charge_type_id: Payment type (2 = eCheck, 1 = Credit Card, 3 = ACH)
- amount: Transaction amount
- remote_batch_id: Batch ID assigned by Paya (populated after processing)
- remote_batch_date: Date when batch was created by Paya
- remote_charge_status_id: Status (1=Pending, 2=Success, 3=Failed)
- uuid: Unique identifier for transaction tracking
- created_at: When transaction was initiated
```

#### `payment_gateway_profiles` Table
Configuration for Paya gateway connections:
```sql
- id: Primary key
- company_id: Company this profile belongs to
- payment_gateway_id: Reference to payment_gateways table
- merchant_user_name: Paya merchant identifier
- paya_user_identifier: Encrypted Paya user ID
- paya_user_apikey: Encrypted Paya API key
- paya_user_hashkey: Encrypted Paya hash key
- enabled: Whether this profile is active
```

#### `payment_gateways` Table
Gateway type definitions:
```sql
- id: Primary key
- name: Gateway name
- key_value: 'PCON' for Paya Connect
```

#### `remote_charge_reconciliations` Table
Tracks reconciliation status for each transaction:
```sql
- id: Primary key
- remote_charge_id: Link to remote_charges table
- reconcile_batch_id: Reference to billing_jobs table for reconciliation run
- status: 'success' or 'fail'
- message: Error details if reconciliation failed
```

#### `companies` Table
Company-level configuration affecting batching:
```sql
- reconcile_by_remote_batch: Boolean flag controlling reconciliation method
```

### Database Relationships

```
companies
    └── payment_gateway_profiles
        └── remote_charges
            └── remote_charge_reconciliations
```

## eCheck Payment Flow

### 1. Payment Initiation
- Customer initiates eCheck payment through customer portal
- System creates `remote_charge` record with:
  - `remote_charge_type_id = 2` (eCheck)
  - `remote_charge_status_id = 1` (Pending)
  - Unique `uuid` for tracking

### 2. Paya Processing
- Transaction data sent to Paya Connect API
- Paya validates bank account information
- If successful, Paya assigns transaction to a batch
- Paya returns batch information including:
  - `transaction_batch_id` (stored as `remote_batch_id`)
  - Batch creation timestamp

### 3. Status Update
- System updates `remote_charge` record with:
  - `remote_batch_id`: Batch ID from Paya
  - `remote_batch_date`: Date batch was created
  - `remote_charge_status_id`: Success (2) or Failed (3)

### 4. Settlement
- Paya submits batch to ACH network
- Settlement occurs 1-3 business days later
- Funds are deposited to merchant account

## Batching Mechanism

### How Batches Are Created

1. **Paya-Side Batching**: Paya automatically groups eCheck transactions into batches based on:
   - Time intervals (typically every few hours)
   - Transaction volume thresholds
   - Business rules configured in Paya system

2. **Batch Identification**: Each batch receives:
   - Unique batch ID (integer)
   - Batch creation timestamp
   - List of included transactions

3. **Transaction Assignment**: When a transaction is processed:
   - Paya assigns it to the current active batch
   - Returns batch ID in the API response
   - Muni system stores this in `remote_batch_id` field

### Batch Processing Timeline

```
Day 1: 
- 9:00 AM: Batch #12345 started
- 9:05 AM: eCheck transaction #1 added to batch
- 10:30 AM: eCheck transaction #2 added to batch
- 12:00 PM: Batch #12345 closed, submitted to ACH
- 12:01 PM: Batch #12346 started

Day 2-4:
- ACH processing occurs

Day 4:
- Funds settled to merchant account
```

## Reconciliation Process

### Daily Reconciliation Job

The system runs a daily reconciliation process via `Charges::Paya::Reconciler` class:

**Location**: `/muni-billing/legacy/lib/charges/paya/reconciler.rb`

**Process**:
1. **Company Discovery**: Find all companies with enabled Paya profiles
2. **Date Range**: Process transactions from specified date range
3. **API Query**: For each merchant, query Paya API for transaction details
4. **Comparison**: Compare Paya data with local `remote_charges` records
5. **Reconciliation**: Create `remote_charge_reconciliations` records with status

### Reconciliation Logic

For each transaction found in Paya system:
1. **Match Transaction**: Find local `remote_charge` by `uuid`
2. **Validate Amount**: Compare transaction amounts
3. **Check Status**: Verify success/failure status matches
4. **Update Batch Info**: Store/update `remote_batch_id` and `remote_batch_date`
5. **Record Result**: Create reconciliation record with success/failure status

### Reconciliation Queries

**Find transactions missing from Paya**:
```ruby
remote_charges(company_id: company_id, merchant_user_name: merchant.merchant_user_name)
  .where.not(id: already_updated_remote_charge_ids.uniq!, uuid: nil)
  .where('remote_charge_status_2_id = ? or remote_charge_status_id = ?', 
         RemoteCharge::STATUS_SUCCESS, RemoteCharge::STATUS_SUCCESS)
```

**Batch data retrieval from Paya**:
```ruby
paya_client.post('/api/service/v1/get-transactions', {
  from_ts: start_timestamp,
  to_ts: end_timestamp,
  location_id: merchant_user_name,
  page_number: page_offset,
  page_size: 50
})
```

## Code Implementation

### Key Classes and Methods

#### `Charges::Paya::Reconciler`
**Location**: `/muni-billing/legacy/lib/charges/paya/reconciler.rb`

**Purpose**: Daily reconciliation of Paya transactions
**Key Methods**:
- `call()`: Main reconciliation process
- `process_company(company_id:)`: Process single company
- `validate_remote_charge()`: Compare local vs Paya data
- `batch_data()`: Retrieve transaction data from Paya API

#### `Charges::Paya::PurchaseCreator`
**Location**: `/muni-billing/legacy/lib/charges/paya/purchase_creator.rb`

**Purpose**: Process successful payments from Paya
**Key Methods**:
- `call()`: Main processing workflow
- `perform_managed_purchase()`: Create payment records
- `save_transaction()`: Store transaction in Paya adapter

#### `Charges::Bridges::PayaConnect`
**Location**: `/muni-billing/legacy/lib/charges/bridges/paya_connect.rb`

**Purpose**: Interface between Muni system and Paya API
**Key Methods**:
- `purchase()`: Process payment transaction
- `purchase_from_data()`: Handle Paya response data

#### `RemoteCharge` Model
**Location**: `/muni-billing/legacy/app/models/remote_charge.rb`

**Purpose**: ActiveRecord model for payment transactions
**Key Constants**:
- `PAYMENT_TYPE_ECHECK = 'onlinecheck'`
- `PAYMENT_TYPE_ID_ECHECK = 2`
- `STATUS_PENDING = 1`
- `STATUS_SUCCESS = 2`
- `STATUS_FAIL = 3`

### Payment Type Identification

eCheck transactions are identified by:
```ruby
# In remote_charges table
remote_charge_type_id = 2  # eCheck type

# In code
RemoteCharge::PAYMENT_TYPE_ID_ECHECK = 2
RemoteCharge::PAYMENT_TYPE_ECHECK = 'onlinecheck'
```

### Batch Information Storage

When Paya processes a transaction:
```ruby
# Response from Paya includes batch info
remote_charge.remote_batch_response_id = data["batch"]
remote_charge.remote_batch_id = record['transaction_batch_id']  # From reconciliation
remote_charge.remote_batch_date = Time.at(record["created_ts"])  # From reconciliation
```

## Configuration

### Payment Gateway Profile Setup

For eCheck processing, companies need:

1. **Paya Connect Gateway Profile**:
   - `payment_gateway_id` pointing to Paya Connect gateway
   - `merchant_user_name` from Paya
   - Encrypted API credentials
   - `enabled = true`

2. **Company Settings**:
   - `reconcile_by_remote_batch`: Controls reconciliation method
   - Remote charge fees configuration

### Environment Configuration

Paya integration requires:
- API endpoints configured in environment
- Encryption keys for credential storage
- Timeout settings for API calls

## Monitoring & Troubleshooting

### Tracking Batch Status

**Find transactions without batch IDs**:
```sql
SELECT id, customer_id, amount, created_at, remote_charge_status_id
FROM remote_charges 
WHERE remote_charge_type_id = 2 
  AND remote_batch_id IS NULL 
  AND remote_charge_status_id = 2
  AND created_at > DATE_SUB(NOW(), INTERVAL 7 DAY);
```

**Check reconciliation results**:
```sql
SELECT r.status, COUNT(*) as count
FROM remote_charge_reconciliations r
JOIN remote_charges rc ON r.remote_charge_id = rc.id
WHERE rc.remote_charge_type_id = 2
  AND r.created_at > DATE_SUB(NOW(), INTERVAL 1 DAY)
GROUP BY r.status;
```

**Find failed reconciliations**:
```sql
SELECT rc.id, rc.uuid, rc.amount, r.message
FROM remote_charges rc
JOIN remote_charge_reconciliations r ON r.remote_charge_id = rc.id
WHERE rc.remote_charge_type_id = 2
  AND r.status = 'fail'
  AND r.created_at > DATE_SUB(NOW(), INTERVAL 7 DAY);
```

### Common Issues

#### 1. Missing Batch IDs
**Symptom**: Successful transactions without `remote_batch_id`
**Cause**: Reconciliation hasn't run or failed
**Solution**: Run manual reconciliation for date range

#### 2. Reconciliation Failures
**Symptom**: `remote_charge_reconciliations` records with status='fail'
**Cause**: Amount mismatches, status discrepancies, or missing transactions
**Solution**: Review reconciliation messages and correct data

#### 3. API Connection Issues
**Symptom**: Reconciliation job failing completely
**Cause**: Invalid credentials or API endpoint issues
**Solution**: Verify gateway profile credentials and API connectivity

### Manual Reconciliation

To run reconciliation manually:
```ruby
# In Rails console
reconciler = Charges::Paya::Reconciler.new(
  start_date: '2024-01-01',
  end_date: '2024-01-02'
)
reconciler.call
```

### Debugging Tools

**Check reconciliation info**:
```ruby
reconciler = Charges::Paya::Reconciler.new(start_date: '2024-01-01', end_date: '2024-01-02')
reconciler.charges_info
# Returns breakdown by company, payment type, and status
```

**Explain specific charge**:
```ruby
reconciler.explain(remote_charge_id: 12345)
# Returns detailed reconciliation message for specific charge
```

### Logging

Reconciliation activity is logged with:
- Company processing progress
- Transaction comparison results
- API call responses
- Error details for failed reconciliations

Log files can be found in standard Rails log directory with entries tagged with file names and line numbers for tracing.

## Important Notes

1. **eCheck Settlement Time**: Unlike credit cards, eCheck transactions take 1-3 business days to settle
2. **Batch Assignment**: Paya assigns transactions to batches automatically; Muni cannot control batch composition
3. **Reconciliation Frequency**: Daily reconciliation is recommended to catch discrepancies early
4. **API Rate Limits**: Paya API has rate limits; reconciliation process includes throttling
5. **Data Retention**: Batch information is stored permanently for audit purposes

## Related Documentation

- Payment Gateway Configuration Guide
- Paya Connect API Integration
- Remote Charge Processing Overview
- Reconciliation Job Configuration