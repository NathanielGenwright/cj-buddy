# Bill Stages Validation Mask Reference Guide

## Overview
The `validation_mask` field in the `bill_stages` table uses bitwise flags to track validation errors in staged bill records. Records with validation errors must be corrected before they can be successfully posted to create actual bill transactions.

## Validation Rules
- **validation_mask = 1**: Record is VALID and ready to post
- **validation_mask > 1**: Record has validation ERRORS that must be corrected
- Multiple errors can be combined using bitwise OR operations

## Individual Validation Mask Values

| Value | Constant | Error Description | Required Correction |
|-------|----------|-------------------|-------------------|
| 1 | V_MASK | Valid record | No action needed - ready to post |
| 2 | V_CUSTOMER | Missing or invalid customer | Link to valid customer record |
| 4 | V_ENTERED_USER | Missing entered user | Assign valid user who entered bill |
| 8 | V_BILLING_TYPE | Missing billing type | Select valid billing type |
| 16 | V_BILL_DATE | Missing bill date | Enter valid bill date |
| 32 | V_RATE_ID_INVALID | Invalid rate code | Provide valid rate code for billing |
| 64 | V_BILL_DATE_INVALID | Invalid bill date format/parsing | Fix bill date format |
| 128 | V_START_READING_DATE_INVALID | Invalid start reading date | Fix start reading date format |
| 256 | V_END_READING_DATE_INVALID | Invalid end reading date | Fix end reading date format |
| 512 | V_PENALTY_DATE_INVALID | Invalid penalty date | Fix penalty date format |
| 1024 | V_DISCOUNT_DATE_INVALID | Invalid discount date | Fix discount date format |
| 2048 | V_PRINT_DATE_INVALID | Invalid print date | Fix print date format |
| 4096 | V_POSTED_ACCOUNTING_DATE_INVALID | Invalid posted accounting date | Fix posted accounting date format |
| 8192 | V_FIRST_READING_OLD_METER_DATE_INVALID | Invalid first reading old meter date | Fix first reading old meter date format |
| 16384 | V_LAST_READING_OLD_METER_DATE_INVALID | Invalid last reading old meter date | Fix last reading old meter date format |
| 32768 | V_POSTED_CUSTOMER_DATE_INVALID | Invalid posted customer date | Fix posted customer date format |
| 65536 | V_INVALID_PERIOD | Bill date not in valid company period | Enter bill date within open company period |

## Common Combined Values

| Value | Combination | Errors Present | Required Corrections |
|-------|-------------|----------------|-------------------|
| 3 | V_MASK + V_CUSTOMER | Missing customer | Link to valid customer record |
| 5 | V_MASK + V_ENTERED_USER | Missing entered user | Assign valid user |
| 9 | V_MASK + V_BILLING_TYPE | Missing billing type | Select valid billing type |
| 17 | V_MASK + V_BILL_DATE | Missing bill date | Enter valid bill date |
| 33 | V_MASK + V_RATE_ID_INVALID | Invalid rate code | Provide valid rate code |
| 65 | V_MASK + V_BILL_DATE_INVALID | Invalid bill date format | Fix bill date format |
| 65537 | V_MASK + V_INVALID_PERIOD | Invalid period | Enter bill date in open period |

## How to Use This Guide

### For Customer Service Representatives:
1. Look up the validation_mask value in the table above
2. Follow the "Required Correction" instructions
3. Make necessary changes to the staged bill record
4. Re-validate the record (validation_mask should become 1)
5. Post the record when validation_mask = 1

### Bill-Specific Validation Rules:

#### Required Fields:
- **Customer**: Must link to valid customer record
- **Entered User**: Must assign user who entered the bill
- **Billing Type**: Must select appropriate billing type
- **Bill Date**: Must provide valid bill date

#### Date Validation Logic:
- **Date Missing vs Invalid**: System differentiates between missing dates (not validated) and invalid date formats
- **Raw Date Fields**: When `raw_*` date fields are provided but can't be parsed, corresponding invalid flags are set
- **Format Requirements**: Dates must be parseable into valid Date objects

#### Rate Validation:
- **Rate ID**: When `raw_rate` is provided but doesn't match a valid rate_id, V_RATE_ID_INVALID is set
- **Rate Matching**: Rate codes must exist in the rate lookup table

#### Period Validation:
- **Company Periods**: If company uses accounting periods, bill date must fall within an open period
- **Period Check**: System validates bill_date against open company periods

## Date Fields Validated

The following date fields undergo format validation when raw values are provided:
- `bill_date` / `raw_bill_date`
- `start_reading_date` / `raw_start_reading_date`
- `end_reading_date` / `raw_end_reading_date`
- `penalty_date` / `raw_penalty_date`
- `discount_date` / `raw_discount_date`
- `print_date` / `raw_print_date`
- `posted_accounting_date` / `raw_posted_accounting_date`
- `first_reading_old_meter_date` / `raw_first_reading_old_meter_date`
- `last_reading_old_meter_date` / `raw_last_reading_old_meter_date`
- `posted_customer_date` / `raw_posted_customer_date`

## Important Notes

1. **Date Parsing**: Invalid date format flags are only set when raw date values are provided but can't be parsed
2. **Rate Validation**: Rate validation occurs when raw_rate is provided but doesn't resolve to valid rate_id
3. **Company Periods**: Period validation only applies if company.use_periods is enabled
4. **Missing vs Invalid**: The system distinguishes between missing required fields and invalid format fields
5. **Billing Types**: Unlike payment stages, billing type is required for bill stages

## Troubleshooting Common Issues

- **Value 17**: Missing bill date - provide valid bill date
- **Value 33**: Invalid rate code - check rate code against company's rate table
- **Value 65**: Invalid bill date format - check date format in raw_bill_date field
- **Value 65537**: Bill date outside valid period - adjust date or check period settings
- **Multiple date errors**: Check all raw_* date fields for format issues

## Processing Notes

- Records with `validation_mask <= 1` are considered valid for posting
- Bill staging supports meter reading imports with multiple date validations
- Date parsing failures preserve original raw values while flagging validation errors
- Rate code validation ensures billing uses valid company rates
- Period validation prevents bills from being created in closed accounting periods

---
*Generated from BillStage model constants in muni-billing/legacy/app/models/bill_stage.rb*