# Neptune V4 Import - RDGDTLOW Record Data Mapping

## Overview
Documentation for the Neptune V4 Import system's handling of RDGDTLOW records, showing how data is extracted from the import file and mapped to system fields.

## Record Structure Constants
- **Record Type**: `RDGDT` (positions 0-4)
- **Line Length**: 257 characters (some files may be 214 characters)
- **Source File**: `/app/business_logic/jobs/imports/meter_import_neptune_v4_job.rb`

## Key Data Fields Extracted from RDGDTLOW

### 1. Low Register ID (positions 9-21)
- **Source**: `line[9..21].strip`
- **Target**: Used to match existing meters via `meters.low_register_id`
- **Purpose**: Primary meter identification for radio reads
- **Code Reference**: `meter_import_neptune_v4_job.rb:225`

### 2. Start Reading (positions 78-87)
- **Source**: `line[78..87]`
- **Target**: Not directly saved but available for processing
- **Purpose**: Previous meter reading value
- **Code Reference**: `meter_import_neptune_v4_job.rb:240`

### 3. End Reading (positions 88-97)
- **Source**: `line[88..97]`
- **Target**: `MeterReading.end_reading`
- **Purpose**: Current meter reading value
- **Processing**: If blank, defaults to 0
- **Code Reference**: `meter_import_neptune_v4_job.rb:237`

## Additional Context Data Used

### From Previous Records in File
- **Meter Serial Number**: From MTRDT record, used as fallback identification
- **End Reading Date**: From ORDST record, becomes `MeterReading.end_reading_date`

## System Fields Populated

The RDGDTLOW data is used to populate a new meter reading via the `save_reading` method:

```ruby
meter.save_reading(
  customer_id,           # From meter.parcel.current_customer.id
  false,                 # is_high_flow (hardcoded)
  last_reading_amt,      # Previous reading from existing data
  last_reading_date,     # Previous reading date from existing data
  end_reading,           # From RDGDTLOW positions 88-97
  end_reading_date,      # From ORDST record
  UNPOSTED_READING,      # Status (hardcoded)
  auto_read_type_id,     # From meter or default company setting
  nil,                   # note (null)
  entered_user_id,       # From job parameters
  company_id,            # From job parameters
  nil,                   # raw_account_number (null)
  nil,                   # raw_address (null)
  nil,                   # raw_name (null)
  true,                  # force_save
  true,                  # allow_delete
  nil,                   # meter_reading_link_id (null)
  false,                 # estimated_reading
  false,                 # register_id (null)
  true                   # is_imported
)
```

## Meter Matching Logic

The system uses a two-tier approach to match RDGDTLOW records to existing meters:

### 1. Primary Method - Low Register ID
- **Field**: `low_register_id` (positions 9-21 from RDGDTLOW)
- **Query**: Active meters with matching `low_register_id` in the same company
- **Use Case**: Radio reads
- **Code Reference**: `meter_import_neptune_v4_job.rb:250-253`

### 2. Fallback Method - Serial Number
- **Field**: Meter serial number from preceding MTRDT record
- **Query**: Active meters with matching `number` field in the same company
- **Use Case**: Manual reads when low_register_id matching fails
- **Code Reference**: `meter_import_neptune_v4_job.rb:256-260`

### Requirements
- Meter must be active (`meter_status_id = 1`)
- Meter must belong to the correct company
- Non-empty identification fields

## Example RDGDTLOW Record

```
RDGDTLOW 1541642140          1541642140          07070000L999999999900000000000000180856000018298101829810  RR   0 0       0209 03                   0
```

### Field Breakdown
- Positions 0-4: `RDGDT` (record type)
- Positions 9-21: `1541642140` (low register ID)
- Positions 78-87: `0000000000` (start reading)
- Positions 88-97: `0000018085` (end reading)

## Error Handling

### Validation Errors
- Line length validation (must be 257 or 214 characters)
- End reading must be numeric
- Meter must exist and be active

### Processing Behavior
- If no matching meter found, creates placeholder meter record
- If end reading is blank, defaults to 0
- All readings imported with `UNPOSTED_READING` status

## Related Files
- **Main Job**: `/app/business_logic/jobs/imports/meter_import_neptune_v4_job.rb`
- **Test Fixtures**: `/test/fixtures/files/meter_readings/neptune_reading_import_1088.exp`
- **Test Specs**: `/spec/business_logic/jobs/imports/meter_import_neptune_v4_job_spec.rb`

---
*Generated on: 2025-10-08*
*Source: Muni Billing System Codebase Analysis*