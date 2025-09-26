# Customer Stage Rates Validation Mask Reference Guide

## Overview
The `validation_mask` field in the `customer_stage_rates` table uses bitwise flags to track validation errors in staged customer rate assignments. This is a child table of `customer_stages` that handles rate code validation for customer staging records.

## Validation Rules
- **validation_mask = 1**: Record is VALID and ready to post
- **validation_mask > 1**: Record has validation ERRORS that must be corrected
- Multiple errors can be combined using bitwise OR operations

## Individual Validation Mask Values

| Value | Constant | Error Description | Required Correction |
|-------|----------|-------------------|-------------------|
| 1 | V_MASK | Valid record | No action needed - ready to post |
| 2 | V_RATE | Invalid rate code | Provide valid rate code for customer |

## Common Combined Values

| Value | Combination | Errors Present | Required Corrections |
|-------|-------------|----------------|-------------------|
| 3 | V_MASK + V_RATE | Invalid rate code | Provide valid rate code for customer |

## How to Use This Guide

### For Customer Service Representatives:
1. Look up the validation_mask value in the table above
2. Follow the "Required Correction" instructions
3. Make necessary changes to the staged customer rate record
4. Re-validate the record (validation_mask should become 1)
5. Post the record when validation_mask = 1

### Rate-Specific Validation Rules:

#### Rate Code Validation:
- **Optional Rate**: Rate validation only occurs when `raw_rate_code` is provided
- **Rate Lookup**: When raw_rate_code is provided, it must resolve to a valid rate_id
- **Company Scoping**: Rate codes are looked up within the customer's company context
- **Blank Rates Allowed**: If no raw_rate_code is provided, no validation occurs

#### Parent Relationship:
- **Customer Stage Link**: Each customer_stage_rate belongs to a customer_stage record
- **Company Context**: Company ID is derived from the parent customer_stage
- **Nested Validation**: Rate validation is part of the overall customer staging process

## Important Notes

1. **Update Only**: Validation only runs on record updates (`before_update` callback)
2. **Optional Field**: Rate validation only applies when raw_rate_code is provided
3. **Parent Dependency**: Company context comes from the parent customer_stage
4. **Simple Validation**: Only validates rate code lookup, no other fields
5. **Nested Attributes**: Typically managed through customer_stage nested attributes

## Rate Code Resolution Process

1. **Raw Code Provided**: System checks if `raw_rate_code` is not blank
2. **Rate Lookup**: Attempts to resolve rate_id from the raw code
3. **Validation**: If raw code provided but rate_id is nil, sets V_RATE flag
4. **Success**: If rate_id is found, validation passes

## Processing Context

- **Parent-Child Relationship**: Customer stages can have multiple rate assignments
- **Staging Workflow**: Rate validation is part of customer import staging process  
- **Company-Specific**: Rate codes are validated against company's rate table
- **Optional Assignment**: Customers can have zero or more rate assignments

## Troubleshooting Common Issues

- **Value 3**: Invalid rate code provided
  - Check that the rate code exists in the company's rate table
  - Verify the rate code spelling and format
  - Ensure the rate is active and available for customer assignment
  - Remove the raw_rate_code if no rate assignment is needed

## Best Practices

1. **Rate Code Verification**: Always verify rate codes exist before staging
2. **Company Context**: Ensure rate codes are valid for the specific company
3. **Optional Usage**: Leave raw_rate_code blank if no specific rate needed
4. **Bulk Import**: Validate all rate codes before processing large imports
5. **Error Handling**: Address rate code errors before processing parent customer stage

## Integration with Customer Stages

Customer stage rates are processed as part of the customer staging workflow:

1. **Customer Stage Creation**: Parent customer_stage record is created
2. **Rate Assignment**: One or more customer_stage_rate records are created
3. **Rate Validation**: Each rate code is validated against company rates
4. **Overall Validation**: Customer stage validation includes rate validation
5. **Processing**: Valid customer stages with valid rates are processed together

---
*Generated from CustomerStageRate model constants in muni-billing/legacy/app/models/customer_stage_rate.rb*