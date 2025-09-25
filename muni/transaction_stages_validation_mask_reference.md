# Transaction Stages Validation Mask Reference Guide

## Overview
The `validation_mask` field in the `transaction_stages` table uses bitwise flags to track validation errors in staged transaction records. Records with validation errors must be corrected before they can be successfully posted to create payment transactions.

**Note**: This model is very similar to PaymentStage but appears to be a separate staging table for transaction imports.

## Validation Rules
- **validation_mask = 1**: Record is VALID and ready to post
- **validation_mask > 1**: Record has validation ERRORS that must be corrected
- Multiple errors can be combined using bitwise OR operations

## Individual Validation Mask Values

| Value | Constant | Error Description | Required Correction |
|-------|----------|-------------------|-------------------|
| 1 | V_MASK | Valid record | No action needed - ready to post |
| 2 | V_CUSTOMER | Missing or invalid customer | Link to valid customer record |
| 4 | V_PAYMENT_TYPE | Missing payment type | Select valid payment type |
| 8 | V_ENTERED_USER | Missing entered user | Assign valid user who entered transaction |
| 32 | V_PAYMENT_DATE | Missing payment date | Enter valid payment date |
| 64 | V_AMOUNT | Missing transaction amount | Enter transaction amount |
| 128 | V_POSTED_CUSTOMER_DATE | Posted customer date missing | Enter posted customer date |
| 256 | V_POSTED_ACCOUNTING_DATE | Posted accounting date missing | Enter posted accounting date |
| 512 | V_DISCOUNT_AMOUNT | Discount amount validation error | Verify discount amount |
| 1024 | V_DUPLICATE_PAYMENT | Duplicate transaction detected | Verify not duplicate OR override duplicate check |
| 2048 | V_PAYMENT_DATE_INVALID | Invalid payment date format | Enter valid payment date format |
| 4096 | V_POSTED_CUSTOMER_DATE_INVALID | Invalid posted customer date format | Fix posted customer date format |
| 8192 | V_POSTED_ACCOUNTING_DATE_INVALID | Invalid posted accounting date format | Fix posted accounting date format |
| 16384 | V_INACTIVE_CUSTOMER | Customer account is closed | Reopen customer account OR override inactive customer |
| 32768 | V_INVALID_PERIOD | Payment date not in valid company period | Enter payment date within open company period |

## Common Combined Values

| Value | Combination | Errors Present | Required Corrections |
|-------|-------------|----------------|-------------------|
| 3 | V_MASK + V_CUSTOMER | Missing customer | Link to valid customer record |
| 5 | V_MASK + V_PAYMENT_TYPE | Missing payment type | Select valid payment type |
| 9 | V_MASK + V_ENTERED_USER | Missing entered user | Assign valid user |
| 33 | V_MASK + V_PAYMENT_DATE | Missing payment date | Enter valid payment date |
| 65 | V_MASK + V_AMOUNT | Missing amount | Enter transaction amount |
| 1025 | V_MASK + V_DUPLICATE_PAYMENT | Duplicate transaction | Verify uniqueness or override |
| 16385 | V_MASK + V_INACTIVE_CUSTOMER | Inactive customer | Reactivate customer or override |
| 32769 | V_MASK + V_INVALID_PERIOD | Invalid period | Enter date in open period |

## How to Use This Guide

### For Customer Service Representatives:
1. Look up the validation_mask value in the table above
2. Follow the "Required Correction" instructions
3. Make necessary changes to the staged transaction record
4. Re-validate the record (validation_mask should become 1)
5. Post the record when validation_mask = 1

### Transaction-Specific Validation Rules:
- **Duplicate Detection**: System checks for existing payments with same customer, amount, and date
- **Date Format Validation**: Validates that raw date fields can be parsed into valid dates
- **Period Validation**: Only applies if company uses accounting periods
- **Customer Status**: Cannot post transactions for closed/inactive customers without override
- **Amount Required**: Transaction amount cannot be null or blank

### Override Options Available:
- `override_duplicate_payment`: Allows posting duplicate transactions
- `override_inactive_customer`: Allows transactions for closed customers

## Important Notes

1. **Validation Disabled**: The `before_save :validate` callback is commented out (line 10)
2. **Billing Type Skipped**: Billing type validation is intentionally disabled (lines 21, 54-56)
3. **Date Parsing**: Invalid date format flags are set when raw dates can't be parsed
4. **Duplicate Logic**: Uses same duplicate detection as PaymentStage
5. **Period Validation**: Only validates if company.use_periods is enabled
6. **Error Messages**: Includes additional error_message field for staging errors

## Processing Notes

- Records with `validation_mask <= 1` are considered valid for posting
- Validation method exists but may not be automatically called (callback commented out)
- Manual validation can be triggered by calling the validate method
- Billing type is intentionally allowed to be blank (indicates distribute to existing balance)
- Date format validation only applies when raw date fields are provided

## Differences from PaymentStage

1. **Validation Callback**: TransactionStage has validation callback commented out
2. **Error Scope**: Includes `with_errors` scope for records with error messages
3. **Date Logic**: Simplified date validation logic compared to PaymentStage
4. **Age Limits**: No maximum age validation on dates like PaymentStage has

## Troubleshooting Common Issues

- **Value 3**: Missing customer - verify customer exists and is linked properly
- **Value 33**: Missing payment date - provide valid payment date
- **Value 65**: Missing amount - enter transaction amount
- **Value 1025**: Duplicate transaction - verify if legitimate or use override
- **Value 2049**: Invalid payment date format - check raw_payment_date format
- **Value 16385**: Customer is inactive - reactivate customer or use override
- **Value 32769**: Payment date outside valid period - adjust date or check period settings

## Known Issues

⚠️ **Important**: The validation callback is commented out on line 10, so automatic validation may not occur. Manual validation may be required by calling the validate method explicitly.

---
*Generated from TransactionStage model constants in muni-billing/legacy/app/models/transaction_stage.rb*