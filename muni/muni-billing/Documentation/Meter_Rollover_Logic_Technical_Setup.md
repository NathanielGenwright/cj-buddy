# Meter Rollover Logic - Technical Setup Documentation

**Document Type:** Internal Technical Reference
**Target Audience:** Engineering, DevOps, Support Teams
**Format:** External Document (Copy to Confluence/SharePoint)

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Rollover Detection Logic](#2-rollover-detection-logic)
3. [Consumption Calculation](#3-consumption-calculation)
4. [Configuration Settings](#4-configuration-settings)
5. [Database Schema](#5-database-schema)
6. [Model Relationships](#6-model-relationships)
7. [Admin Configuration UI](#7-admin-configuration-ui)
8. [Special Scenarios](#8-special-scenarios)
9. [Warnings & Validation](#9-warnings--validation)
10. [Data Imports & Exports](#10-data-imports--exports)
11. [Troubleshooting](#11-troubleshooting)
12. [Quick Reference](#12-quick-reference)

---

## 1. System Overview

### What is Meter Rollover?

Meter rollover occurs when a utility meter's odometer-style reading reaches its maximum value and "rolls over" to zero (or a low starting value). For example, a 5-digit meter displaying 99999 will roll to 00000 on the next increment.

**Common Rollover Scenarios:**
- 4-digit meter: 9999 → 0000 (max reading: 10,000)
- 5-digit meter: 99999 → 00000 (max reading: 100,000)
- 6-digit meter: 999999 → 000000 (max reading: 1,000,000)

### Why Rollover Handling Matters

Without proper rollover detection, a reading like:
- Previous: 9,500
- Current: 200

Would calculate as: `200 - 9,500 = -9,300` (incorrect negative consumption)

With rollover handling (max 10,000):
- Calculation: `10,000 - 9,500 + 200 = 700` (correct consumption)

### Key System Capabilities

- **Automatic Detection**: System detects when current reading < previous reading
- **Configurable Max Reading**: Each meter size defines its rollover threshold
- **Low/High Flow Support**: Separate rollover settings for compound meters
- **Negative Reading Policy**: Company-level control for handling edge cases
- **Warning System**: Flags unusual consumption patterns for review

---

## 2. Rollover Detection Logic

### Primary Detection Method

**File:** `app/models/meter_reading.rb` (Lines 97-141)

The system detects rollover when **both conditions** are true:
1. `end_reading < start_reading` (negative delta)
2. `max_consumption > 0` (meter supports rollover)

```ruby
def set_consumption
  if self.meter.present? && self.meter.persisted?
    # ... validation ...

    start_reading_deci = MuniDecimal.build(self.start_reading)
    end_reading_deci = MuniDecimal.build(self.end_reading)
    reading_delta = end_reading_deci - start_reading_deci

    # Get max reading based on flow type
    max_consumption = self.is_high_flow ?
      MuniDecimal.build(self.meter.meter_size.high_max_reading) :
      MuniDecimal.build(self.meter.meter_size.low_max_reading)

    # ROLLOVER DETECTION
    if (reading_delta < 0) && (max_consumption > 0)
      # Rollover occurred
      self.consumption = max_consumption + reading_delta
    else
      # Normal reading
      self.consumption = reading_delta
    end

    # ... negative handling ...
  end
end
```

### Detection Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  New Meter Reading Entered                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                ┌─────────────────────────────┐
                │ Calculate reading_delta =    │
                │ end_reading - start_reading  │
                └─────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Is delta < 0?   │
                    └─────────────────┘
                     │              │
                   Yes             No
                     │              │
                     ▼              ▼
        ┌───────────────────┐   ┌───────────────────┐
        │ Is max_reading    │   │ Normal Consumption│
        │ > 0 (rollover     │   │ = delta           │
        │ enabled)?         │   └───────────────────┘
        └───────────────────┘
           │           │
         Yes          No
           │           │
           ▼           ▼
┌───────────────────┐  ┌───────────────────┐
│ ROLLOVER DETECTED │  │ Negative delta    │
│ consumption =     │  │ (meter doesn't    │
│ max + delta       │  │ support rollover) │
└───────────────────┘  └───────────────────┘
```

### Estimation Method (Alternative)

**File:** `app/models/meter.rb` (Lines 145-160)

Used for consumption estimation before readings are finalized:

```ruby
def estimate_consumption(is_high_flow, end_reading)
  consumption = 0
  max_consumption = is_high_flow ?
    self.meter_size.high_max_reading :
    self.meter_size.low_max_reading

  # Same rollover detection logic
  if end_reading < self.last_reading.end_reading && max_consumption > 0
    consumption = (max_consumption - self.last_reading.end_reading) + end_reading
  else
    consumption = end_reading - self.last_reading.end_reading
  end

  # Clamp to 0 if negative
  consumption = 0 if consumption < 0

  return consumption
end
```

---

## 3. Consumption Calculation

### Standard Formula (No Rollover)

```
consumption = end_reading - start_reading
```

**Example:**
- Start: 5,000
- End: 5,500
- Consumption: `5,500 - 5,000 = 500 units`

### Rollover Formula

```
consumption = max_reading + (end_reading - start_reading)
            = max_reading - start_reading + end_reading
```

**Example (4-digit meter, max 10,000):**
- Start: 9,500
- End: 200
- Delta: `200 - 9,500 = -9,300`
- Consumption: `10,000 + (-9,300) = 700 units`

**Breakdown:**
- Units from 9,500 to rollover: `10,000 - 9,500 = 500`
- Units after rollover to 200: `200`
- Total: `500 + 200 = 700 units`

### Multiplier Application

After consumption is calculated, it's multiplied by the meter size's multiplier:

```ruby
self.report_consumption = (self.consumption * self.meter.meter_size.multiplier) > 0
```

**Common Multiplier Values:**
| Meter Type | Multiplier | Example |
|------------|------------|---------|
| Direct read | 1.0 | 500 units → 500 gallons |
| 10x factor | 10.0 | 500 units → 5,000 gallons |
| 100x factor | 100.0 | 500 units → 50,000 gallons |

### Precision Handling

All calculations use `MuniDecimal` class for decimal precision:

```ruby
start_reading_deci = MuniDecimal.build(self.start_reading)
end_reading_deci = MuniDecimal.build(self.end_reading)
```

Database fields use `DECIMAL(16,6)` for maximum precision.

---

## 4. Configuration Settings

### Meter Size Configuration

The rollover threshold is configured per **meter size**, not per individual meter.

| Field | Purpose | Example Values |
|-------|---------|----------------|
| `low_max_reading` | Max reading for low-flow register | 10000, 100000, 1000000 |
| `high_max_reading` | Max reading for high-flow register | 10000, 100000, 1000000 |

**Special Value:**
- `0` = Rollover disabled for this register

### Company-Level Settings

**File:** `app/views/companies/_gs_section_readings.html.erb` (Line 37)

| Setting | Purpose | Default |
|---------|---------|---------|
| `allow_negative_reads` | Allow negative consumption values | FALSE |
| `reading_variance_percent_warning` | Threshold for variance warnings | 20% |
| `validate_meter_register_id` | Validate register IDs on import | FALSE |

**Negative Reads Handling:**

```ruby
# app/models/meter_reading.rb, lines 124-129
if self.customer_id.present? && !self.company.allow_negative_reads?
  if self.consumption < 0
    self.consumption = 0
  end
end
```

When `allow_negative_reads = FALSE`:
- Negative consumption is clamped to 0
- `warning_no_consumption` flag is set
- Reading appears in warning reports

When `allow_negative_reads = TRUE`:
- Negative consumption is allowed (for meter adjustments, credits)
- Used by some utilities for specific business cases

### Meter Metadata Fields

These fields are **informational only** and don't affect rollover calculation:

| Field | Purpose | Example |
|-------|---------|---------|
| `low_dial_count` | Number of dials on meter face | 5 |
| `low_stationary_zeros` | Fixed zero positions | 1 |
| `high_dial_count` | High-flow dial count | 4 |
| `high_stationary_zeros` | High-flow fixed zeros | 0 |
| `low_standard_read_type` | Manual read type code | "STD" |
| `low_radio_read_type` | AMR/AMI read type | "RADIO" |
| `high_standard_read_type` | High-flow manual type | "STD" |
| `high_radio_read_type` | High-flow AMR type | "RADIO" |

---

## 5. Database Schema

### meter_sizes Table

```sql
CREATE TABLE meter_sizes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  company_id INT NOT NULL,
  size VARCHAR(20),
  description VARCHAR(255),

  -- LOW FLOW REGISTER
  low_dial_count INT,
  low_stationary_zeros INT,
  low_standard_read_type VARCHAR(50),
  low_radio_read_type VARCHAR(50),
  low_max_reading INT DEFAULT 0,          -- ROLLOVER THRESHOLD

  -- HIGH FLOW REGISTER
  high_dial_count INT,
  high_stationary_zeros INT,
  high_standard_read_type VARCHAR(50),
  high_radio_read_type VARCHAR(50),
  high_max_reading INT DEFAULT 0,         -- ROLLOVER THRESHOLD

  -- METER SETTINGS
  is_compound TINYINT(1) DEFAULT 0,       -- Has both low & high registers
  multiplier DECIMAL(16,6) DEFAULT 1.0,
  unit_type_id INT,
  round_decimal_places INT,

  -- USER DEFINED FIELDS
  user_defined_1 VARCHAR(255),
  user_defined_2 VARCHAR(255),
  user_defined_3 VARCHAR(255),
  user_defined_4 VARCHAR(255),
  user_defined_5 VARCHAR(255),
  user_defined_6 VARCHAR(255),
  user_defined_7 VARCHAR(255),

  created_at DATETIME,
  updated_at DATETIME,

  INDEX idx_company (company_id)
);
```

### meter_readings Table

```sql
CREATE TABLE meter_readings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  meter_id INT NOT NULL,
  customer_id INT,
  company_id INT,
  company_billing_period_id INT,

  -- READINGS
  start_reading DECIMAL(16,6),
  end_reading DECIMAL(16,6),
  consumption DECIMAL(16,6),              -- CALCULATED (with rollover)
  consumption_adjustment DECIMAL(16,6),   -- Manual override

  -- DATES
  start_reading_date DATE,
  end_reading_date DATE,
  days INT,

  -- REGISTER INFO
  register_id VARCHAR(50),
  is_high_flow TINYINT(1) DEFAULT 0,

  -- STATUS
  meter_reading_status_id INT,
  meter_read TINYINT(1),
  report_consumption TINYINT(1),

  -- WARNING FLAGS
  warning_no_consumption TINYINT(1) DEFAULT 0,
  warning_no_meter TINYINT(1) DEFAULT 0,
  warning_no_customer TINYINT(1) DEFAULT 0,
  warning_reading_variance TINYINT(1) DEFAULT 0,
  warning_missing_end_date TINYINT(1) DEFAULT 0,
  warning_bad_register_id TINYINT(1) DEFAULT 0,

  created_at DATETIME,
  updated_at DATETIME,

  INDEX idx_meter (meter_id),
  INDEX idx_customer (customer_id),
  INDEX idx_status (meter_reading_status_id),
  INDEX idx_end_date (end_reading_date)
);
```

### meters Table (Relevant Fields)

```sql
CREATE TABLE meters (
  id INT AUTO_INCREMENT PRIMARY KEY,
  parcel_id INT NOT NULL,
  meter_size_id INT NOT NULL,           -- Links to rollover config
  meter_status_id INT NOT NULL,

  meter_number VARCHAR(50),
  serial_number VARCHAR(50),

  -- REGISTER IDS
  low_register_id VARCHAR(50),
  high_register_id VARCHAR(50),

  install_date DATE,
  last_service_date DATE,

  -- ... other fields ...

  INDEX idx_meter_size (meter_size_id),
  INDEX idx_parcel (parcel_id)
);
```

### companies Table (Relevant Fields)

```sql
-- Relevant columns only
ALTER TABLE companies ADD COLUMN allow_negative_reads TINYINT(1) DEFAULT 0;
ALTER TABLE companies ADD COLUMN reading_variance_percent_warning INT DEFAULT 20;
ALTER TABLE companies ADD COLUMN validate_meter_register_id TINYINT(1) DEFAULT 0;
```

---

## 6. Model Relationships

### Entity Relationship Diagram

```
Company (1)
    │
    ├──► (many) MeterSize
    │         │
    │         │    ┌─── low_max_reading (rollover config)
    │         │    └─── high_max_reading (rollover config)
    │         │
    │         └──► (many) Meter
    │                    │
    │                    └──► (many) MeterReading
    │                              │
    │                              ├── start_reading
    │                              ├── end_reading
    │                              ├── consumption (calculated)
    │                              └── is_high_flow (determines which max to use)
    │
    └──► allow_negative_reads (company policy)
```

### Model Code References

**MeterReading Model:**
```ruby
# app/models/meter_reading.rb
belongs_to :meter
has_one :meter_size, through: :meter

before_validation :set_consumption  # Rollover calculation happens here
before_save :validate_reading_warnings
```

**Meter Model:**
```ruby
# app/models/meter.rb
belongs_to :meter_size
has_many :meter_readings

def estimate_consumption(is_high_flow, end_reading)
  # Alternative rollover calculation for estimation
end
```

**MeterSize Model:**
```ruby
# app/models/meter_size.rb
belongs_to :company
has_many :meters

# Key fields: low_max_reading, high_max_reading, multiplier
```

---

## 7. Admin Configuration UI

### Meter Sizes Configuration

**Location:** Admin → Settings → Meter Sizes (or similar path)

**Controller:** `app/controllers/meter_sizes_controller.rb`

**View:** `app/views/meter_sizes/_meter_size_record.html.erb`

### Configuration Fields Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Size: [____]  Description: [________________________]                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  LOW REGISTER:                                                               │
│  ┌──────────┬──────────┬───────────┬───────────┬─────────────┐             │
│  │Dial Count│Stat Zeros│Std Read   │Radio Read │MAX READING  │             │
│  │[__5____] │[__1____] │[_STD____] │[_RADIO__] │[__10000___] │◄── ROLLOVER │
│  └──────────┴──────────┴───────────┴───────────┴─────────────┘             │
│                                                                              │
│  HIGH REGISTER:                                                              │
│  ┌──────────┬──────────┬───────────┬───────────┬─────────────┐             │
│  │Dial Count│Stat Zeros│Std Read   │Radio Read │MAX READING  │             │
│  │[__4____] │[__0____] │[_STD____] │[_RADIO__] │[__10000___] │◄── ROLLOVER │
│  └──────────┴──────────┴───────────┴───────────┴─────────────┘             │
│                                                                              │
│  Unit Type: [Gallons ▼]  Multiplier: [_1.0___]  Compound: [✓]               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Setting Max Reading Values

**Guidelines for Common Meter Types:**

| Meter Digits | Max Reading Value | Notes |
|--------------|-------------------|-------|
| 4 digits | 10000 | Rolls at 9999 → 0000 |
| 5 digits | 100000 | Rolls at 99999 → 00000 |
| 6 digits | 1000000 | Rolls at 999999 → 000000 |
| Doesn't roll | 0 | Set to 0 to disable |

**Important:** The max reading should be `10^n` where `n` is the number of digits, not `10^n - 1`. This accounts for the full range (0 through 9999 = 10,000 possible values).

### Company Negative Reads Setting

**Location:** Admin → Company Settings → Meter Reading Options

```erb
<!-- app/views/companies/_gs_section_readings.html.erb -->
<%= f.check_box :allow_negative_reads %>
```

---

## 8. Special Scenarios

### Scenario 1: Normal Reading (No Rollover)

```
Meter Size: low_max_reading = 100000
Previous Reading: 45,000
Current Reading: 45,750

Calculation:
  delta = 45,750 - 45,000 = 750
  delta > 0, so NO rollover
  consumption = 750 units
```

### Scenario 2: Rollover Detected

```
Meter Size: low_max_reading = 10000
Previous Reading: 9,500
Current Reading: 200

Calculation:
  delta = 200 - 9,500 = -9,300
  delta < 0 AND max_reading > 0, so ROLLOVER DETECTED
  consumption = 10,000 + (-9,300) = 700 units
```

### Scenario 3: Rollover Disabled (max = 0)

```
Meter Size: low_max_reading = 0
Previous Reading: 9,500
Current Reading: 200

Calculation:
  delta = 200 - 9,500 = -9,300
  delta < 0 BUT max_reading = 0, so NO ROLLOVER
  consumption = -9,300 units

  If allow_negative_reads = FALSE:
    consumption = 0 (clamped)
    warning_no_consumption = TRUE
```

### Scenario 4: Compound Meter (Low + High Flow)

```
Meter Size:
  low_max_reading = 100000
  high_max_reading = 10000
  is_compound = TRUE

LOW FLOW READING (is_high_flow = FALSE):
  Uses low_max_reading (100000) for rollover calculation

HIGH FLOW READING (is_high_flow = TRUE):
  Uses high_max_reading (10000) for rollover calculation
```

### Scenario 5: Multiple Rollovers (Edge Case)

If a meter has been unread for an extended period and has rolled over multiple times, the system **cannot detect this**. The calculation assumes at most one rollover occurred.

```
Meter Size: low_max_reading = 10000
Previous Reading: 5,000
Current Reading: 6,000
(Meter actually rolled over twice: 5000 → 10000 → 0 → 10000 → 0 → 6000)

Calculated consumption: 1,000 units (INCORRECT)
Actual consumption: 21,000 units

WARNING: This scenario requires manual intervention.
The variance warning system may flag this for review.
```

### Scenario 6: Meter Replacement Mid-Cycle

When a meter is replaced, the new meter starts at 0 or a low value:

```
Old Meter Final Reading: 85,000
New Meter Initial Reading: 0
Next Reading: 500

If not handled properly, system might calculate:
  delta = 500 - 85,000 = -84,500
  This would trigger (incorrect) rollover detection

SOLUTION:
  - Create final reading for old meter (85,000)
  - Create initial reading for new meter (0) as start_reading
  - Next reading (500) calculates correctly: 500 - 0 = 500
```

---

## 9. Warnings & Validation

### Warning Flags

**File:** `app/models/meter_reading.rb` (Lines 149-196)

| Flag | Trigger Condition | Purpose |
|------|-------------------|---------|
| `warning_no_consumption` | `consumption <= 0` | Flags zero or negative usage |
| `warning_no_meter` | `meter_id IS NULL` | Reading not linked to meter |
| `warning_no_customer` | `meter exists but customer_id IS NULL` | Orphaned reading |
| `warning_reading_variance` | Exceeds variance threshold | Unusual consumption pattern |
| `warning_missing_end_date` | Invalid date range | Date validation failure |
| `warning_bad_register_id` | Register ID mismatch | Import validation issue |

### Variance Warning Logic

```ruby
# app/models/meter_reading.rb, lines 198-200
def current_reading_variance_warning?
  return true if (MuniDecimal.build(last_reading.try(:consumption)) == 0) &&
                 (MuniDecimal.build(consumption) > 0)
  return true if calculate_variance? && exceeds_variance_threshold?
end
```

**Triggers variance warning when:**
1. Previous consumption was 0, current consumption > 0
2. Current consumption differs from historical average by more than `reading_variance_percent_warning`%

### Validation Before Save

```ruby
before_validation :set_days
before_validation :set_consumption     # Rollover calc
before_save :validate_reading_warnings # Set warning flags
```

### Required Field Validation

```ruby
# Lines 100-108
if self.start_reading.nil?
  errors.add(:start_reading, "cannot be blank")
  raise ActiveRecord::RecordInvalid.new(self)
end

if self.end_reading.nil?
  errors.add(:end_reading, "cannot be blank")
  raise ActiveRecord::RecordInvalid.new(self)
end
```

---

## 10. Data Imports & Exports

### Import Processing

When importing meter readings from external systems (AMR/AMI, handheld devices):

**Files:**
- `app/business_logic/data_imports/meter_stage_import_file.rb`
- `app/business_logic/data_imports/meter_quadlogic_import_file.rb`

**Process:**
1. Import creates `MeterReading` records
2. `before_validation :set_consumption` triggers automatically
3. Rollover detection occurs during consumption calculation
4. Warning flags are set during `before_save`

### Export Processing

**File:** `app/business_logic/jobs/exports/datamatic_meter_export_job.rb`

Exports include meter specifications:
- `low_dial_count`
- `low_stationary_zeros`
- `high_dial_count`
- `high_stationary_zeros`

These help external systems understand meter configuration.

### Register ID Validation

For imports with register identifiers:

```ruby
# app/models/meter_reading.rb, lines 185-193
unless self.meter.nil?
  if self.register_id.blank? || self.register_id.to_s == self.meter.low_register_id.to_s
    self.is_high_flow = false
  elsif self.register_id.to_s == self.meter.high_register_id.to_s && !self.meter.high_register_id.blank?
    self.is_high_flow = true
  elsif self.company.validate_meter_register_id
    self.warning_bad_register_id = true
  end
end
```

---

## 11. Troubleshooting

### Issue 1: Unexpected Negative Consumption

**Symptoms:**
- Consumption shows as 0 or negative
- `warning_no_consumption` is TRUE

**Possible Causes:**
1. `max_reading` is set to 0 (rollover disabled)
2. Reading entered in wrong order
3. Meter replacement not properly handled
4. Multiple rollovers occurred (undetectable)

**Resolution:**
```sql
-- Check meter size configuration
SELECT ms.id, ms.size, ms.description,
       ms.low_max_reading, ms.high_max_reading
FROM meter_sizes ms
JOIN meters m ON m.meter_size_id = ms.id
WHERE m.id = [meter_id];

-- If max_reading = 0, update it:
UPDATE meter_sizes
SET low_max_reading = 10000  -- or appropriate value
WHERE id = [meter_size_id];
```

### Issue 2: Rollover Not Detected

**Symptoms:**
- Large negative consumption calculated
- Expected rollover didn't occur

**Possible Causes:**
1. `max_reading` is 0
2. Wrong flow type (is_high_flow mismatch)
3. Meter linked to wrong meter_size

**Resolution:**
```sql
-- Verify meter configuration
SELECT m.id, m.meter_number,
       ms.low_max_reading, ms.high_max_reading,
       mr.is_high_flow, mr.start_reading, mr.end_reading, mr.consumption
FROM meter_readings mr
JOIN meters m ON mr.meter_id = m.id
JOIN meter_sizes ms ON m.meter_size_id = ms.id
WHERE mr.id = [reading_id];
```

### Issue 3: Incorrect Consumption After Rollover

**Symptoms:**
- Consumption calculated but seems wrong
- Customer billed incorrect amount

**Possible Causes:**
1. Wrong `max_reading` value configured
2. Multiple rollovers (long reading gap)
3. Meter digits counted incorrectly

**Resolution:**
```sql
-- Manually recalculate
-- For max_reading = 10000, start = 9500, end = 200:
-- Expected: 10000 + (200 - 9500) = 700

SELECT
  mr.start_reading,
  mr.end_reading,
  mr.consumption as stored_consumption,
  ms.low_max_reading,
  ms.low_max_reading + (mr.end_reading - mr.start_reading) as calculated_consumption
FROM meter_readings mr
JOIN meters m ON mr.meter_id = m.id
JOIN meter_sizes ms ON m.meter_size_id = ms.id
WHERE mr.id = [reading_id];
```

### Issue 4: Company Allows Negative Reads Unexpectedly

**Symptoms:**
- Negative consumption appearing on bills
- Expected to be clamped to 0

**Resolution:**
```sql
-- Check company setting
SELECT id, name, allow_negative_reads
FROM companies
WHERE id = [company_id];

-- Disable if needed
UPDATE companies
SET allow_negative_reads = 0
WHERE id = [company_id];
```

### Diagnostic SQL Queries

```sql
-- Find readings with potential rollover issues
SELECT mr.id, mr.meter_id, mr.start_reading, mr.end_reading,
       mr.consumption, mr.is_high_flow,
       ms.low_max_reading, ms.high_max_reading,
       mr.warning_no_consumption
FROM meter_readings mr
JOIN meters m ON mr.meter_id = m.id
JOIN meter_sizes ms ON m.meter_size_id = ms.id
WHERE mr.end_reading < mr.start_reading
  AND mr.created_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY mr.created_at DESC;

-- Find meter sizes with rollover disabled
SELECT id, size, description, low_max_reading, high_max_reading
FROM meter_sizes
WHERE low_max_reading = 0 OR high_max_reading = 0;

-- Find readings with zero consumption warnings
SELECT mr.id, m.meter_number, mr.start_reading, mr.end_reading,
       mr.consumption, mr.end_reading_date
FROM meter_readings mr
JOIN meters m ON mr.meter_id = m.id
WHERE mr.warning_no_consumption = 1
  AND mr.end_reading_date > DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY mr.end_reading_date DESC
LIMIT 100;

-- Verify rollover calculation
SELECT
  mr.id,
  mr.start_reading,
  mr.end_reading,
  mr.consumption as stored,
  CASE
    WHEN mr.end_reading < mr.start_reading
         AND COALESCE(ms.low_max_reading, 0) > 0
    THEN ms.low_max_reading + (mr.end_reading - mr.start_reading)
    ELSE mr.end_reading - mr.start_reading
  END as calculated,
  ms.low_max_reading as max_reading
FROM meter_readings mr
JOIN meters m ON mr.meter_id = m.id
JOIN meter_sizes ms ON m.meter_size_id = ms.id
WHERE mr.id = [reading_id];
```

---

## 12. Quick Reference

### Rollover Detection Summary

| Condition | Result |
|-----------|--------|
| `end >= start` | Normal: `consumption = end - start` |
| `end < start` AND `max > 0` | Rollover: `consumption = max + (end - start)` |
| `end < start` AND `max = 0` | Negative (may clamp to 0) |

### Key Configuration Fields

| Field | Location | Purpose |
|-------|----------|---------|
| `low_max_reading` | `meter_sizes` | Low-flow rollover threshold |
| `high_max_reading` | `meter_sizes` | High-flow rollover threshold |
| `allow_negative_reads` | `companies` | Allow negative consumption |
| `is_high_flow` | `meter_readings` | Which max to use |
| `multiplier` | `meter_sizes` | Consumption multiplier |

### Common Max Reading Values

| Meter Digits | Max Reading | Use Case |
|--------------|-------------|----------|
| 4 | 10,000 | Small residential |
| 5 | 100,000 | Standard residential |
| 6 | 1,000,000 | Commercial/Industrial |
| 0 | Disabled | Non-rolling meters |

### Code Entry Points

| Operation | File | Method |
|-----------|------|--------|
| Primary Calculation | `meter_reading.rb` | `set_consumption` |
| Estimation | `meter.rb` | `estimate_consumption` |
| Warning Validation | `meter_reading.rb` | `validate_reading_warnings` |
| Admin UI | `_meter_size_record.html.erb` | Form fields |

### Warning Flags Reference

| Flag | Meaning | Action |
|------|---------|--------|
| `warning_no_consumption` | Zero or negative | Review reading |
| `warning_reading_variance` | Unusual pattern | Verify accuracy |
| `warning_bad_register_id` | Register mismatch | Check import |
| `warning_no_meter` | No meter linked | Link meter |
| `warning_no_customer` | No customer | Assign customer |

---

*Document Version: 1.0*
*Last Updated: January 2026*
*Maintained By: MuniBilling Engineering*
