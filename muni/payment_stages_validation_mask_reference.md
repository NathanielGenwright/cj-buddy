# Payment Stages Validation Mask Reference Guide

## Overview
The `validation_mask` field in the `payment_stages` table uses bitwise flags to track validation errors in staged payment records. Records with validation errors must be corrected before they can be successfully posted to create actual payment transactions.

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
| 8 | V_ENTERED_USER | Missing entered user | Assign valid user who entered payment |
| 32 | V_PAYMENT_DATE | Missing payment date | Enter valid payment date |
| 64 | V_AMOUNT | Missing payment amount | Enter payment amount |
| 128 | V_POSTED_CUSTOMER_DATE | Posted customer date missing | Enter posted customer date |
| 256 | V_POSTED_ACCOUNTING_DATE | Posted accounting date missing | Enter posted accounting date |
| 512 | V_DISCOUNT_AMOUNT | Discount amount validation error | Verify discount amount |
| 1024 | V_DUPLICATE_PAYMENT | Duplicate payment detected | Verify not duplicate OR override duplicate check |
| 2048 | V_PAYMENT_DATE_INVALID | Invalid payment date format/range | Enter valid payment date (within allowed age limit) |
| 4096 | V_POSTED_CUSTOMER_DATE_INVALID | Invalid posted customer date | Enter valid posted customer date (within allowed age limit) |
| 8192 | V_POSTED_ACCOUNTING_DATE_INVALID | Invalid posted accounting date | Enter valid posted accounting date (within allowed age limit) |
| 16384 | V_INACTIVE_CUSTOMER | Customer account is closed | Reopen customer account OR override inactive customer |
| 32768 | V_INVALID_PERIOD | Payment date not in valid company period | Enter payment date within open company period |

## Common Combined Values

| Value | Combination | Errors Present | Required Corrections |
|-------|-------------|----------------|-------------------|
| 3 | V_MASK + V_CUSTOMER | Missing customer | Link to valid customer record |
| 5 | V_MASK + V_PAYMENT_TYPE | Missing payment type | Select valid payment type |
| 9 | V_MASK + V_ENTERED_USER | Missing entered user | Assign valid user |
| 33 | V_MASK + V_PAYMENT_DATE | Missing payment date | Enter valid payment date |
| 65 | V_MASK + V_AMOUNT | Missing amount | Enter payment amount |
| 1025 | V_MASK + V_DUPLICATE_PAYMENT | Duplicate payment | Verify uniqueness or override |
| 2049 | V_MASK + V_PAYMENT_DATE_INVALID | Invalid payment date | Fix payment date format/range |
| 16385 | V_MASK + V_INACTIVE_CUSTOMER | Inactive customer | Reactivate customer or override |
| 32769 | V_MASK + V_INVALID_PERIOD | Invalid period | Enter date in open period |

## How to Use This Guide

### For Customer Service Representatives:
1. Look up the validation_mask value in the table above
2. Follow the "Required Correction" instructions
3. Make necessary changes to the staged payment record
4. Re-validate the record (validation_mask should become 1)
5. Post the record when validation_mask = 1

### Payment-Specific Validation Rules:
- **Duplicate Detection**: System checks for existing payments with same customer, amount, and date
- **Date Validation**: Payment dates must be within the maximum age limit (defined by Payment::MAX_AGE)
- **Period Validation**: Only applies if company uses accounting periods - payment date must fall within an open period
- **Customer Status**: Cannot post payments for closed/inactive customers without override
- **Amount Required**: Payment amount cannot be null or blank

### Override Options Available:
- `override_duplicate_payment`: Allows posting duplicate payments
- `override_inactive_customer`: Allows payments for closed customers

## Important Notes

1. **Date Range Limits**: Payment dates, posted customer dates, and posted accounting dates must be within the maximum age limit
2. **Company Periods**: If the company uses accounting periods, payment date must fall within an open period
3. **Billing Type**: Blank billing type is allowed (indicates distribute payment to existing balance)
4. **Duplicate Detection**: System automatically detects potential duplicate payments based on customer ID, amount, and payment date
5. **Customer Validation**: Customer must exist and be active (unless overridden)

## Troubleshooting Common Issues

- **Value 1025**: Duplicate payment detected - verify if legitimate or use override
- **Value 16385**: Customer is inactive - reactivate customer account or use override
- **Value 32769**: Payment date outside valid period - adjust date or check period settings
- **Value 2049**: Invalid payment date format - check date format and age limits
- **Multiple errors**: Decode each bit flag to identify all validation issues

## Processing Notes

- Records with `validation_mask <= 1` are considered valid for posting
- Payment staging supports various import formats via raw_* fields
- Date parsing failures result in date invalid flags rather than missing date flags
- Override flags can bypass certain validation rules for special circumstances

---
*Generated from PaymentStage model constants in muni-billing/legacy/app/models/payment_stage.rb*