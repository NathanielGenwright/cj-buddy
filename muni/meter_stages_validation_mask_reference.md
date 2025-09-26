# Meter Stages Validation Mask Reference Guide

## Overview
The `validation_mask` field in the `meter_stages` table uses bitwise flags to track validation errors in staged meter records. Records with validation errors must be corrected before they can be successfully posted to create or update meter records.

## Validation Rules
- **validation_mask = 1**: Record is VALID and ready to post
- **validation_mask > 1**: Record has validation ERRORS that must be corrected
- Multiple errors can be combined using bitwise OR operations

## Individual Validation Mask Values

| Value | Constant | Error Description | Required Correction |
|-------|----------|-------------------|-------------------|
| 1 | V_MASK | Valid record | No action needed - ready to post |
| 2 | V_METER_NUMBER | Missing or invalid meter number | Provide valid meter number |
| 4 | V_PARCEL_NUMBER | Missing or invalid parcel number | Link to valid parcel record |
| 8 | V_METER_CATEGORY | Missing meter category | Select valid meter category |
| 16 | V_METER_AUTO_READ_TYPE | Missing meter auto read type | Select valid auto read type |
| 32 | V_METER_LOCATION | Missing meter location | Select valid meter location |
| 64 | V_METER_STATUS | Missing meter status | Select valid meter status |
| 128 | V_METER_SIZE | Missing meter size | Select valid meter size |
| 256 | V_METER_MANUFACTURER | Missing meter manufacturer | Select valid meter manufacturer |

## Common Combined Values

| Value | Combination | Errors Present | Required Corrections |
|-------|-------------|----------------|-------------------|
| 3 | V_MASK + V_METER_NUMBER | Missing meter number | Provide valid meter number |
| 5 | V_MASK + V_PARCEL_NUMBER | Missing parcel number | Link to valid parcel record |
| 9 | V_MASK + V_METER_CATEGORY | Missing meter category | Select valid meter category |
| 17 | V_MASK + V_METER_AUTO_READ_TYPE | Missing auto read type | Select valid auto read type |
| 33 | V_MASK + V_METER_LOCATION | Missing meter location | Select valid meter location |
| 65 | V_MASK + V_METER_STATUS | Missing meter status | Select valid meter status |
| 129 | V_MASK + V_METER_SIZE | Missing meter size | Select valid meter size |
| 257 | V_MASK + V_METER_MANUFACTURER | Missing manufacturer | Select valid meter manufacturer |

## How to Use This Guide

### For Customer Service Representatives:
1. Look up the validation_mask value in the table above
2. Follow the "Required Correction" instructions
3. Make necessary changes to the staged meter record
4. Re-validate the record (validation_mask should become 1)
5. Post the record when validation_mask = 1

### Meter-Specific Validation Rules:

#### Stage Type Dependency:
- **INSERT Operations**: All meter attributes are required when creating new meters
- **UPDATE Operations**: Attributes are only validated if raw values are provided for changes

#### Parcel and Meter Number Logic:
- **Raw Identifier**: Used to look up parcel by account number
- **Meter Number**: Used to identify specific meter for updates
- **Parcel Linking**: System automatically links meter to correct parcel during validation
- **Active Meter Logic**: For updates, system finds active meters on the parcel

#### Required Fields for Insert Operations:
- **Parcel Number**: Must link to existing parcel record
- **Meter Category**: Must select valid meter category
- **Meter Auto Read Type**: Must select valid auto read type
- **Meter Location**: Must select valid meter location
- **Meter Status**: Must select valid meter status
- **Meter Size**: Must select valid meter size
- **Meter Manufacturer**: Must select valid meter manufacturer

#### Update Operation Logic:
- **Meter Lookup**: System finds existing meter by number and parcel
- **Status Priority**: Orders by meter_status_id when multiple matches found
- **Active Meter Fallback**: If meter number not found, uses active meter on parcel
- **Partial Updates**: Only validates attributes with provided raw values

## Meter Lookup Logic

### For Insert Operations:
1. Look up parcel by `raw_identifier` (account number)
2. Set `parcel_id` if parcel found, otherwise flag V_PARCEL_NUMBER error

### For Update Operations:
1. Look up parcel by `raw_identifier`
2. Look up meter by `number` within company
3. If meter found, use its parcel and meter ID
4. If meter not found, try to find active meter on parcel
5. If no meter found, flag V_METER_NUMBER error

## Important Notes

1. **Stage Type Dependency**: Validation rules differ based on INSERT vs UPDATE operations
2. **Automatic Linking**: System automatically resolves parcel_id and meter_id during validation
3. **Raw Attributes**: Update operations only validate attributes with corresponding raw_ values
4. **Active Meter Priority**: For updates without specific meter number, system uses active meter
5. **Company Scoping**: All lookups are scoped to the appropriate company

## Troubleshooting Common Issues

- **Value 3**: Invalid meter number - verify meter exists and is properly formatted
- **Value 5**: Invalid parcel number - verify account number exists in parcel table
- **Value 9**: Missing meter category - provide valid meter category from lookup table
- **Value 17**: Missing auto read type - select appropriate auto read type
- **Value 6 (V_PARCEL_NUMBER + V_METER_NUMBER)**: Both parcel and meter lookup failed
- **Multiple attribute errors**: Check that all required meter attributes are provided for insert operations

## Processing Notes

- Records with `validation_mask <= 1` are considered valid for posting
- System performs complex lookup logic to link meters to parcels
- Insert operations require all meter attributes
- Update operations only validate changed attributes (those with raw_ values)
- Meter number lookups consider meter status priority for disambiguation

## Lookup Tables Referenced

- **meter_categories**: Valid categories for meter classification
- **meter_auto_read_types**: Automatic reading configuration types
- **meter_locations**: Physical location descriptions
- **meter_statuses**: Current operational status (Active, Inactive, etc.)
- **meter_sizes**: Meter size specifications
- **meter_manufacturers**: Meter manufacturer information

---
*Generated from MeterStage model constants in muni-billing/legacy/app/models/meter_stage.rb*