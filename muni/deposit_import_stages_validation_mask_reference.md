# Deposit Import Stages Validation Mask Reference Guide

## Overview
The `validation_mask` field in the `deposit_import_stages` table uses bitwise flags to track validation errors in staged deposit records. Records with validation errors must be corrected before they can be successfully posted to create actual customer deposits.

## Validation Rules
- **validation_mask = 1**: Record is VALID and ready to post
- **validation_mask > 1**: Record has validation ERRORS that must be corrected
- Multiple errors can be combined using bitwise OR operations

## Individual Validation Mask Values

| Value | Constant | Error Description | Required Correction |
|-------|----------|-------------------|-------------------|
| 1 | V_MASK | Valid record | No action needed - ready to post |
| 2 | V_CUSTOMER | Missing or invalid customer | Link to valid customer record |
| 4 | V_ENTERED_USER | Missing entered user | Assign valid user who entered deposit |
| 8 | V_AMOUNT | Missing deposit amount | Enter deposit amount |
| 16 | V_DEPOSIT_TYPE | Missing or invalid deposit type | Select valid deposit type |
| 32 | V_INACTIVE_CUSTOMER | Customer account is closed | Reopen customer account OR override inactive customer |
| 64 | V_DEPOSIT_DATE | Missing or invalid deposit date | Enter valid deposit date |

## Common Combined Values

| Value | Combination | Errors Present | Required Corrections |
|-------|-------------|----------------|-------------------|
| 3 | V_MASK + V_CUSTOMER | Missing customer | Link to valid customer record |
| 5 | V_MASK + V_ENTERED_USER | Missing entered user | Assign valid user |
| 9 | V_MASK + V_AMOUNT | Missing amount | Enter deposit amount |
| 17 | V_MASK + V_DEPOSIT_TYPE | Missing deposit type | Select valid deposit type |
| 33 | V_MASK + V_INACTIVE_CUSTOMER | Inactive customer | Reactivate customer or override |
| 65 | V_MASK + V_DEPOSIT_DATE | Missing deposit date | Enter valid deposit date |

## How to Use This Guide

### For Customer Service Representatives:
1. Look up the validation_mask value in the table above
2. Follow the "Required Correction" instructions
3. Make necessary changes to the staged deposit record
4. Re-validate the record (validation_mask should become 1)
5. Post the record when validation_mask = 1

### Deposit-Specific Validation Rules:

#### Required Fields:
- **Customer**: Must link to valid, active customer record
- **Entered User**: Must assign user who entered the deposit
- **Amount**: Must provide deposit amount (cannot be null)
- **Deposit Type**: Must select appropriate deposit type
- **Deposit Date**: Must provide valid deposit date

#### Customer Status Validation:
- **Active Customer Check**: System validates that customer account is not closed
- **Close Date Logic**: If customer has close_date and it's before deposit date, V_INACTIVE_CUSTOMER flag is set
- **Override Available**: `override_inactive_customer` flag can bypass inactive customer validation

#### Import File Format:
The system supports CSV import files with the following column order:
1. **account_number** (index 0)
2. **deposit_date** (index 1) - Format: MM/DD/YYYY
3. **amount** (index 2)
4. **deposit_type** (index 3)

## Override Options Available:
- `override_inactive_customer`: Allows deposits for closed customers

## Date Handling

- **Date Format**: Import files expect MM/DD/YYYY format (`IMPORT_FILE_STRFTIME = '%m/%d/%Y'`)
- **Date Validation**: Deposit date must be a valid Date object
- **Today Reference**: Uses company timezone today, or system today as fallback

## Important Notes

1. **Customer Lookup**: When account_number changes, system automatically looks up customer_id
2. **Unique Customer**: Customer lookup must find exactly one matching customer record
3. **Deposit Types**: Must reference valid deposit_type records in the system
4. **Amount Validation**: Amount cannot be nil (but can be zero)
5. **User Assignment**: Entered user must be a valid User record

## Troubleshooting Common Issues

- **Value 3**: Missing customer - verify account number exists in customer table
- **Value 9**: Missing amount - provide deposit amount in import file
- **Value 17**: Missing deposit type - verify deposit type exists and is valid
- **Value 33**: Customer is closed - reactivate customer account or use override
- **Value 65**: Missing deposit date - provide valid date in MM/DD/YYYY format

## Processing Notes

- Records with `validation_mask <= 1` are considered valid for posting
- System automatically updates customer_id when account_number changes
- Import file processing expects specific column order and date format
- Validation occurs on every save operation
- Customer status is checked against current date (today)

## Import File Example

```csv
12345,03/15/2024,150.00,Security Deposit
67890,03/15/2024,75.50,Connection Fee
```

Column mapping:
- Column 0: Account Number (12345, 67890)
- Column 1: Deposit Date (03/15/2024)
- Column 2: Amount (150.00, 75.50)
- Column 3: Deposit Type (Security Deposit, Connection Fee)

---
*Generated from DepositImportStage model constants in muni-billing/legacy/app/models/deposit_import_stage.rb*