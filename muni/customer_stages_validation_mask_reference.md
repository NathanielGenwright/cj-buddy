# Customer Stages Validation Mask Reference Guide

## Overview
The `validation_mask` field in the `customer_stages` table uses bitwise flags to track validation errors in staged customer records. Records with validation errors must be corrected before they can be successfully posted to create or update customer accounts.

## Validation Rules
- **validation_mask = 1**: Record is VALID and ready to post
- **validation_mask > 1**: Record has validation ERRORS that must be corrected
- Multiple errors can be combined (e.g., 9 = account number + billing address errors)

## Individual Validation Mask Values

| Value | Constant | Error Description | Required Correction |
|-------|----------|-------------------|-------------------|
| 1 | V_MASK | Valid record | No action needed - ready to post |
| 2 | V_ACCOUNT_NUMBER | Account number validation error | Provide valid account number |
| 4 | V_PARCEL_NUMBER | Parcel number validation error | Provide valid parcel number |
| 8 | V_BILL_ADDRESS_1 | Missing billing address line 1 | Enter billing address line 1 |
| 16 | V_BILL_CITY | Missing billing city | Enter billing city |
| 32 | V_BILL_STATE | Missing billing state | Select billing state |
| 64 | V_BILL_ZIP_CODE | Missing billing zip code | Enter billing zip code |
| 128 | V_SERVICE_ADDRESS_1 | Missing service address line 1 | Enter service address line 1 |
| 256 | V_SERVICE_CITY | Missing service city | Enter service city |
| 512 | V_SERVICE_STATE | Missing service state | Select service state |
| 1024 | V_SERVICE_ZIP_CODE | Missing service zip code | Enter service zip code |
| 2048 | V_TENANT_BILL_ADDRESS_1 | Missing tenant billing address line 1 | Enter tenant billing address line 1 |
| 4096 | V_TENANT_BILL_CITY | Missing tenant billing city | Enter tenant billing city |
| 8192 | V_TENANT_BILL_STATE | Missing tenant billing state | Select tenant billing state |
| 16384 | V_TENANT_BILL_ZIP_CODE | Missing tenant billing zip code | Enter tenant billing zip code |
| 32768 | V_ACCOUNT_TYPE | Missing or invalid account type | Select valid account type |
| 65536 | V_ACCOUNT_CATEGORY | Missing or invalid account category | Select valid account category |
| 131072 | V_LAST_NAME | Missing last name | Enter customer last name |
| 262144 | V_EMAIL | Missing email when email delivery enabled | Enter email address OR disable email delivery |
| 524288 | V_TENANT_EMAIL | Missing tenant email when tenant email delivery enabled | Enter tenant email address OR disable tenant email delivery |
| 1048576 | V_RATE | Invalid rate code | Provide valid rate code for customer |
| 2097152 | V_ACCOUNT_NUMBER_DUPLICATE | Duplicate account number detected | Change to unique account number |
| 4194304 | V_PARCEL_NUMBER_DUPLICATE | Duplicate parcel number detected | Change to unique parcel number |
| 8388608 | V_ROUTE_CODE | Missing route code | Select valid route code |
| 16777216 | V_ESTABLISH_DATE | Missing establish date | Enter customer establish date |

## Common Combined Values

| Value | Combination | Errors Present | Required Corrections |
|-------|-------------|----------------|-------------------|
| 3 | V_MASK + V_ACCOUNT_NUMBER | Account number error | Fix account number |
| 5 | V_MASK + V_PARCEL_NUMBER | Parcel number error | Fix parcel number |
| 9 | V_MASK + V_BILL_ADDRESS_1 | Billing address missing | Enter billing address line 1 |
| 17 | V_MASK + V_BILL_CITY | Billing city missing | Enter billing city |
| 33 | V_MASK + V_BILL_STATE | Billing state missing | Select billing state |
| 65 | V_MASK + V_BILL_ZIP_CODE | Billing zip missing | Enter billing zip code |
| 129 | V_MASK + V_SERVICE_ADDRESS_1 | Service address missing | Enter service address line 1 |
| 257 | V_MASK + V_SERVICE_CITY | Service city missing | Enter service city |
| 513 | V_MASK + V_SERVICE_STATE | Service state missing | Select service state |
| 1025 | V_MASK + V_SERVICE_ZIP_CODE | Service zip missing | Enter service zip code |

## How to Use This Guide

### For Customer Service Representatives:
1. Look up the validation_mask value in the table above
2. Follow the "Required Correction" instructions
3. Make the necessary changes to the staged record
4. Re-validate the record (validation_mask should become 1)
5. Post the record when validation_mask = 1

### For Developers:
- Values are calculated using bitwise OR operations
- To check for specific errors: `validation_mask & ERROR_CONSTANT != 0`
- To decode multiple errors, check each bit flag individually
- Records with `validation_mask <= 1` are processed as valid

### For Data Import Teams:
- Review all records with validation_mask > 1 before posting
- Address the most common errors first (account numbers, addresses)
- Use batch correction tools for systematic issues
- Verify corrections reduce validation_mask to 1

## Important Notes

1. **Multiple Errors**: A single record can have multiple validation errors combined
2. **Posting Rules**: Only records with validation_mask = 1 can be successfully posted
3. **Error Priority**: Fix critical errors (account numbers, duplicates) before address errors
4. **Required Fields**: Some fields are only required based on customer/parcel stage type (insert vs update)
5. **Address Dependencies**: 
   - Bill address fields only required if `bill_address_different = true`
   - Tenant address fields only required if `tenant_bill_address_different = true`
   - Email only required if email delivery is enabled

## Troubleshooting Common Issues

- **Value 2097153**: Duplicate account number + base mask - change account number
- **Value 4194305**: Duplicate parcel number + base mask - change parcel number
- **Large values**: Multiple errors combined - decode each bit to identify all issues
- **Value 1**: Ready to post - no corrections needed

---
*Generated from CustomerStage model constants in muni-billing/legacy/app/models/customer_stage.rb*