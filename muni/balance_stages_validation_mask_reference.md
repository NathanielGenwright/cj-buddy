# Balance Stages Validation Mask Reference Guide

## Overview
The `validation_mask` field in the `balance_stages` table uses bitwise flags to track validation errors in staged balance import records. Records with validation errors must be corrected before they can be successfully posted to create customer balance adjustments.

## Validation Rules
- **validation_mask = 1**: Record is VALID and ready to post
- **validation_mask > 1**: Record has validation ERRORS that must be corrected
- Multiple errors can be combined using bitwise OR operations

## Individual Validation Mask Values

| Value | Constant | Error Description | Required Correction |
|-------|----------|-------------------|-------------------|
| 1 | V_MASK | Valid record | No action needed - ready to post |
| 2 | V_CUSTOMER | Missing or invalid customer | Link to valid customer record |
| 4 | V_ENTERED_USER | Missing entered user | Assign valid user who entered balance |
| 8 | V_BILLING_TYPE | Missing billing type | Select valid billing type |
| 16 | V_BALANCE_DATE | Missing balance date | Enter valid balance date |
| 32 | V_RATE | Invalid rate code | Provide valid rate code |
| 64 | V_EXISTING_BALANCE | Customer has existing balance records | Review existing balances before import |

## Common Combined Values

| Value | Combination | Errors Present | Required Corrections |
|-------|-------------|----------------|-------------------|
| 3 | V_MASK + V_CUSTOMER | Missing customer | Link to valid customer record |
| 5 | V_MASK + V_ENTERED_USER | Missing entered user | Assign valid user |
| 9 | V_MASK + V_BILLING_TYPE | Missing billing type | Select valid billing type |
| 17 | V_MASK + V_BALANCE_DATE | Missing balance date | Enter valid balance date |
| 33 | V_MASK + V_RATE | Invalid rate code | Provide valid rate code |
| 65 | V_MASK + V_EXISTING_BALANCE | Existing balance conflict | Review existing balances |

## How to Use This Guide

### For Customer Service Representatives:
1. Look up the validation_mask value in the table above
2. Follow the "Required Correction" instructions
3. Make necessary changes to the staged balance record
4. Re-validate the record (validation_mask should become 1)
5. Post the record when validation_mask = 1

### Balance-Specific Validation Rules:

#### Required Fields:
- **Customer**: Must link to valid customer record via account number
- **Entered User**: Must assign user who entered the balance
- **Billing Type**: Must select appropriate billing type
- **Balance Date**: Must provide valid balance date (Note: There appears to be a bug in the code where balance date validation sets billing type flag)

#### Customer Lookup Logic:
- **Account Number Matching**: System looks up customer by `raw_identifier` (account number)
- **Company Scoping**: Customer lookup is scoped to the appropriate company
- **Date Ordering**: If multiple customers found, uses earliest establish_date
- **Automatic Linking**: System automatically sets customer_id when account number changes

#### Rate Validation:
- **Optional Rate**: Rate is only validated if `raw_rate` is provided
- **Rate Code Lookup**: When raw_rate provided, must resolve to valid rate_id
- **Blank Rates Allowed**: If no raw_rate provided, rate validation is skipped

#### Existing Balance Check:
- **Bill Balance Check**: Looks for existing bills from balance imports or with open balances
- **Payment Balance Check**: Looks for existing payments from balance imports or unallocated payments
- **Conflict Prevention**: Prevents duplicate balance imports for the same customer

## Important Notes

1. **Code Bug**: The `validate_balance_date` method incorrectly sets `V_BILLING_TYPE` flag instead of `V_BALANCE_DATE` (line 68)
2. **Update Only**: Validation only runs on record updates (`before_update` callback)
3. **Automatic Customer Lookup**: System automatically resolves customer_id from account number
4. **Existing Balance Detection**: System prevents duplicate balance imports
5. **Optional Rate**: Rate validation only occurs when raw_rate is provided

## Existing Balance Detection Logic

The system checks for existing balance records to prevent duplicates:

### Bill Balance Checks:
- Bills marked as `from_balance_import = true`
- Bills with `open_balance > 0` and `posted_customer = true`

### Payment Balance Checks:
- Payments marked as `from_balance_import = true`
- Payments with `bill_id = null` (unallocated payments)

## Troubleshooting Common Issues

- **Value 3**: Missing customer - verify account number exists in customer table
- **Value 5**: Missing entered user - assign valid user for balance entry
- **Value 9**: Missing billing type - select appropriate billing type for balance
- **Value 17**: Missing balance date - provide valid date (may show as billing type error due to bug)
- **Value 33**: Invalid rate code - verify rate code exists in rate table
- **Value 65**: Existing balance found - review customer's current balance records before importing

## Processing Notes

- Records with `validation_mask <= 1` are considered valid for posting
- Balance imports are used to establish opening balances for new systems
- System prevents duplicate balance imports for data integrity
- Customer lookup automatically occurs when account number changes
- Rate validation is optional and only applies when rate code is provided

## Known Issues

⚠️ **Bug Alert**: The `validate_balance_date` method on line 68 incorrectly sets the `V_BILLING_TYPE` flag instead of the `V_BALANCE_DATE` flag. This means balance date validation errors will appear as billing type errors.

## Best Practices

1. **Pre-Import Validation**: Check for existing balance records before importing
2. **Account Number Verification**: Ensure account numbers match existing customers
3. **Rate Code Validation**: If using rate codes, verify they exist in the rate table
4. **Clean Imports**: Remove or resolve existing balance records before re-importing
5. **User Assignment**: Ensure entered_user is assigned for audit trail

---
*Generated from BalanceStage model constants in muni-billing/legacy/app/models/balance_stage.rb*