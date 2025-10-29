# Test Plan: SAAS-1390 - Update File Formats to Use Customer Custom Fields

## Overview
This test plan validates the implementation of system functions for customer custom fields in file formats, enabling unlimited custom field support through label-based referencing.

## Test Environment Setup
- Test company with multiple customer custom fields configured
- File formats configured for import/export testing
- Sample CSV files with various custom field scenarios
- Statement and invoice templates for generation testing

## Test Data Requirements
- Customers with existing custom field data
- Custom fields with various label types (simple, spaces, special characters)
- Legacy custom fields (custom_field_1 through custom_field_6) for compatibility testing

## Test Categories

### 1. Custom Field Label Import Testing
### 2. File Format Configuration Testing
### 3. Export Processing Testing
### 4. Statement/Invoice Generation Testing
### 5. Error Handling & Edge Cases
### 6. Backward Compatibility Testing
### 7. Company Scope & Migration Testing
### 8. Performance Testing

---

## Detailed Test Scripts

### 1. Custom Field Label Import Testing

#### Test Case 1.1: Basic Custom Field Import
**Objective**: Verify system.customer_custom_field() function works with simple labels

**Test Data**: 
```csv
Account#,Gender,Age,Meter_Type
1000-100203,M,34,Water
1000-100204,F,28,Electric
1000-100205,M,45,Gas
```

**File Format Configuration**:
- Position 2: `system.customer_custom_field('Gender')`
- Position 3: `system.customer_custom_field('Age')`
- Position 4: `system.customer_custom_field('Meter_Type')`

**Test Steps**:
1. Navigate to System Info → File Formats
2. Create/edit import file format
3. Configure positions with system function syntax
4. Upload CSV file for import
5. Review staging interface
6. Process import
7. Verify customer custom field data in database

**Expected Results**:
- Staging shows custom field values correctly
- Import processes without errors
- Customer records contain correct custom field data
- Values match CSV input exactly

#### Test Case 1.2: Labels with Spaces and Special Characters
**Objective**: Verify handling of complex label names

**Test Data**:
```csv
Account#,Preferred Contact Method,Service Notes,Last Updated
1000-100203,Email & Phone,Customer requests morning calls only!,2025-01-15
1000-100204,Text Message,Billing address differs from service,2025-01-16
```

**File Format Configuration**:
- Position 2: `system.customer_custom_field('Preferred Contact Method')`
- Position 3: `system.customer_custom_field('Service Notes')`
- Position 4: `system.customer_custom_field('Last Updated')`

**Test Steps**:
1. Create custom fields with spaces and special characters
2. Configure file format with exact label matches (case-sensitive)
3. Import CSV data
4. Verify staging interface handles special characters
5. Process and validate database storage

**Expected Results**:
- Labels with spaces are recognized correctly
- Special characters (&, !) are preserved
- No data corruption during import
- Staging UI displays all characters properly

#### Test Case 1.3: Unlimited Custom Fields (>6)
**Objective**: Verify no limitation on number of custom fields

**Test Data**:
```csv
Account#,Field1,Field2,Field3,Field4,Field5,Field6,Field7,Field8,Field9,Field10
1000-100203,Val1,Val2,Val3,Val4,Val5,Val6,Val7,Val8,Val9,Val10
```

**File Format Configuration**:
- Positions 2-11: `system.customer_custom_field('Field1')` through `system.customer_custom_field('Field10')`

**Test Steps**:
1. Create 10+ custom fields for test company
2. Configure file format with all 10 system functions
3. Import CSV with 10 custom field columns
4. Verify staging shows expand/collapse for >8 fields
5. Process import and validate all fields stored

**Expected Results**:
- All 10 custom fields import successfully
- No legacy 6-field limitation errors
- Staging UI shows expand/collapse functionality
- Database contains all 10 custom field values

#### Test Case 1.4: Case Sensitivity Testing
**Objective**: Verify label matching is case-sensitive

**Test Data**:
```csv
Account#,gender,Gender,GENDER
1000-100203,lowercase,Propercase,UPPERCASE
```

**Setup**:
- Create custom field with label 'Gender' (proper case)
- Configure file format with different case variations

**Test Steps**:
1. Test `system.customer_custom_field('gender')` - should return empty
2. Test `system.customer_custom_field('Gender')` - should return 'Propercase'
3. Test `system.customer_custom_field('GENDER')` - should return empty
4. Verify only exact case match works

**Expected Results**:
- Only exact case match ('Gender') returns data
- Other case variations return empty values
- No errors during processing
- Clear indication of case sensitivity requirement

### 2. File Format Configuration Testing

#### Test Case 2.1: File Format Setup Validation
**Objective**: Verify proper configuration of system functions in file formats

**Test Steps**:
1. Navigate to System Info → File Formats
2. Create new file format or edit existing
3. Add new field with system function
4. Configure field properties:
   - Field Type: Select 'string'
   - Import Column: `system.customer_custom_field('TestLabel')`
   - Export Column: `system.customer_custom_field('TestLabel')`
   - Position: Available position number
   - Label: Descriptive name

**Validation Points**:
- System function syntax is accepted in import/export column fields
- Field type selection works correctly
- Position assignment functions properly
- Configuration saves without errors

**Expected Results**:
- File format accepts system function syntax
- No validation errors during setup
- Configuration persists after save
- Field appears in file format list

#### Test Case 2.2: Multiple System Functions in Single Format
**Objective**: Verify multiple custom field functions in one file format

**Test Steps**:
1. Configure file format with 5+ system functions
2. Use different label types (simple, spaces, special chars)
3. Assign sequential positions
4. Save configuration
5. Test import/export functionality

**Configuration Example**:
- Position 2: `system.customer_custom_field('Gender')`
- Position 3: `system.customer_custom_field('Age Group')`
- Position 4: `system.customer_custom_field('Service Type')`
- Position 5: `system.customer_custom_field('Billing Preference')`
- Position 6: `system.customer_custom_field('Contact Method')`

**Expected Results**:
- All system functions configure successfully
- No conflicts between multiple functions
- Import/export processes all fields correctly
- Performance remains acceptable

#### Test Case 2.3: Mixed Legacy and System Function Configuration
**Objective**: Verify compatibility between legacy and new system functions

**Test Steps**:
1. Configure file format with both legacy and system functions:
   - Position 2: `import.custom_field_1` (legacy)
   - Position 3: `system.customer_custom_field('NewField')` (new)
   - Position 4: `import.custom_field_2` (legacy)
   - Position 5: `system.customer_custom_field('AnotherField')` (new)
2. Test import with mixed data
3. Verify both types process correctly

**Expected Results**:
- Both legacy and system functions work together
- No conflicts or interference
- Data maps correctly to respective fields
- Backward compatibility maintained

### 3. Export Processing Testing

#### Test Case 3.1: Basic Customer Export with Custom Fields
**Objective**: Verify export functionality includes custom field data

**Setup**:
- Create customers with custom field data populated
- Configure export file format with system functions
- Test data includes various custom field types

**Test Steps**:
1. Navigate to Reports → System Information → Export Data
2. Select file format configured with system functions
3. Choose customers with populated custom fields
4. Generate export file
5. Review exported data for accuracy

**File Format Configuration**:
- Position 1: Account Number (standard)
- Position 2: `system.customer_custom_field('Gender')`
- Position 3: `system.customer_custom_field('Service Type')`
- Position 4: `system.customer_custom_field('Billing Preference')`

**Expected Results**:
- Export file contains custom field values
- Data matches customer records exactly
- Empty fields show as blank (not error)
- File format follows configured positions

#### Test Case 3.2: Export with Missing Custom Field Data
**Objective**: Verify graceful handling of customers without custom field data

**Test Steps**:
1. Include customers with and without custom field data in export
2. Export using file format with system functions
3. Verify handling of empty/missing data

**Expected Results**:
- Customers without data show empty values
- No errors during export process
- Export completes successfully
- File structure remains consistent

#### Test Case 3.3: Large Dataset Export Performance
**Objective**: Verify performance with large customer datasets

**Test Steps**:
1. Export 1000+ customers with multiple custom fields
2. Monitor export processing time
3. Verify file completeness
4. Check system resource usage

**Expected Results**:
- Export completes within reasonable timeframe
- All customer data included in export
- No timeout errors
- Acceptable system performance impact

### 4. Statement/Invoice Generation Testing

#### Test Case 4.1: Statement Generation with Custom Fields
**Objective**: Verify custom fields display correctly on customer statements

**Setup**:
- Configure statement file format with custom field system functions
- Test customer has populated custom field data
- Statement template includes custom field display sections

**Test Steps**:
1. Edit statement file format (e.g., "DO NOT USE - RTC - Standard Statement (Copy This) - copy1")
2. Add system function configuration:
   - Label: "Gender"
   - Value: `system.customer_custom_field('Gender')`
3. Generate statement for test customer
4. Review PDF output for custom field display

**Expected Results**:
- Custom field label displays on statement
- Custom field value shows correctly
- Formatting matches statement design
- No data corruption or display issues

#### Test Case 4.2: Invoice Generation with Multiple Custom Fields
**Objective**: Verify multiple custom fields on invoices

**Test Steps**:
1. Configure invoice file format with multiple system functions
2. Include various custom field types (text, numbers, dates)
3. Generate invoice for customer with populated fields
4. Verify all custom fields appear correctly

**Configuration Example**:
- Service Type: `system.customer_custom_field('Service Type')`
- Account Manager: `system.customer_custom_field('Account Manager')`
- Special Instructions: `system.customer_custom_field('Special Instructions')`

**Expected Results**:
- All configured custom fields appear on invoice
- Data displays in correct format
- Layout accommodates variable content length
- Professional appearance maintained

#### Test Case 4.3: Batch Statement/Invoice Generation
**Objective**: Verify custom fields work in bulk generation

**Test Steps**:
1. Generate statements/invoices for multiple customers
2. Include customers with varying custom field data
3. Monitor batch processing performance
4. Review generated documents for consistency

**Expected Results**:
- Batch processing completes successfully
- Custom fields appear correctly across all documents
- Performance remains acceptable
- No processing errors or failures

### 5. Error Handling & Edge Cases

#### Test Case 5.1: Invalid Label Names
**Objective**: Verify system handles non-existent custom field labels gracefully

**Test Steps**:
1. Configure file format with invalid label: `system.customer_custom_field('NonExistentField')`
2. Attempt import with data for this position
3. Verify error handling and processing continuation

**Test Data**:
```csv
Account#,InvalidField
1000-100203,SomeValue
```

**Expected Results**:
- Function returns empty value for invalid label
- Import processing continues without failure
- No errors logged for invalid function
- Other valid fields process correctly

#### Test Case 5.2: Malformed System Function Syntax
**Objective**: Verify handling of incorrect function syntax

**Test Cases**:
- Missing quotes: `system.customer_custom_field(Gender)`
- Wrong function name: `system.custom_field('Gender')`
- Missing parentheses: `system.customer_custom_field'Gender'`
- Extra parameters: `system.customer_custom_field('Gender', 'Extra')`

**Expected Results**:
- Invalid syntax is detected during configuration
- Clear error messages indicate syntax issues
- Valid functions continue to work
- System provides guidance on correct syntax

#### Test Case 5.3: Special Characters in Label Names
**Objective**: Test handling of various special characters in labels

**Test Labels**:
- `system.customer_custom_field('Field with "quotes"')`
- `system.customer_custom_field('Field with \backslash')`
- `system.customer_custom_field('Field with 'apostrophe'')`
- `system.customer_custom_field('Field with $pecial Ch@rs!')`

**Expected Results**:
- System handles special characters appropriately
- Proper escaping or encoding applied
- Data integrity maintained
- No SQL injection or parsing errors

#### Test Case 5.4: Large Data Values in Custom Fields
**Objective**: Test handling of large text values

**Test Data**:
- Very long text strings (>1000 characters)
- Multi-line text with line breaks
- Unicode characters and emojis
- Binary-like data (base64 strings)

**Expected Results**:
- Large values are stored and retrieved correctly
- Text truncation handled appropriately if limits exist
- Character encoding preserved
- Performance remains acceptable

#### Test Case 5.5: Concurrent Access Testing
**Objective**: Verify system function performance under concurrent usage

**Test Steps**:
1. Simulate multiple users importing/exporting simultaneously
2. Use file formats with system functions
3. Monitor for race conditions or conflicts
4. Verify data integrity across concurrent operations

**Expected Results**:
- No data corruption during concurrent access
- Performance degradation within acceptable limits
- No deadlocks or system lockups
- All operations complete successfully

### 6. Backward Compatibility Testing

#### Test Case 6.1: Legacy Custom Field Migration
**Objective**: Verify existing legacy custom fields continue to work

**Setup**:
- Existing file formats using `import.custom_field_1` through `import.custom_field_6`
- Companies with data in legacy custom field columns
- Mixed usage scenarios

**Test Steps**:
1. Test existing file formats with legacy syntax
2. Import data using legacy custom field references
3. Verify data maps to correct legacy columns
4. Test export with legacy custom field data

**Expected Results**:
- Legacy syntax continues to function
- Existing data remains accessible
- No migration required for current implementations
- Legacy and new system can coexist

#### Test Case 6.2: Mixed Legacy and System Function Usage
**Objective**: Verify seamless operation of both legacy and new approaches

**File Format Configuration**:
- Position 2: `import.custom_field_1` (legacy)
- Position 3: `system.customer_custom_field('NewField')` (new)
- Position 4: `import.custom_field_2` (legacy)
- Position 5: `system.customer_custom_field('AnotherField')` (new)

**Test Steps**:
1. Import CSV with data for both legacy and new fields
2. Verify all data processes correctly
3. Test export with mixed field types
4. Validate database storage for both approaches

**Expected Results**:
- Both legacy and system functions work together
- No interference between different approaches
- Data maps correctly to appropriate storage
- Export includes both legacy and new field data

#### Test Case 6.3: Upgrade Path Testing
**Objective**: Verify smooth transition from legacy to system functions

**Migration Scenario**:
1. Start with legacy file format using `custom_field_1`, `custom_field_2`
2. Create equivalent custom fields with descriptive labels
3. Update file format to use system functions
4. Test data continuity and functionality

**Expected Results**:
- Data remains accessible after migration
- New system functions provide equivalent functionality
- Improved usability with descriptive labels
- No data loss during transition

### 7. Company Scope & Migration Testing

#### Test Case 7.1: Company-Specific Custom Field Configuration
**Objective**: Verify custom fields are properly scoped per company

**Setup**:
- Company A with custom fields: Gender, Age, Service Type
- Company B with custom fields: Department, Cost Center, Manager
- File formats configured for each company

**Test Steps**:
1. Configure file formats for each company with their specific fields
2. Test imports for both companies
3. Verify custom field data is company-specific
4. Test cross-company isolation

**Expected Results**:
- Custom fields are isolated per company
- No cross-contamination of data
- Each company sees only their configured fields
- File formats work correctly for intended company

#### Test Case 7.2: File Format Copying Between Companies
**Objective**: Verify behavior when copying file formats across companies

**Test Steps**:
1. Create file format in Company A with system functions
2. Copy file format to Company B
3. Test with Company B's different custom field labels
4. Verify handling of mismatched labels

**Expected Results**:
- System warns about mismatched/missing labels
- Only matching labels are populated
- No errors during processing
- Clear indication of which fields couldn't be mapped

#### Test Case 7.3: Custom Field Label Changes
**Objective**: Verify handling when custom field labels are modified

**Test Steps**:
1. Create custom field with label "OriginalLabel"
2. Configure file format using `system.customer_custom_field('OriginalLabel')`
3. Change custom field label to "NewLabel"
4. Test import using old file format configuration

**Expected Results**:
- Old label reference returns empty values
- No errors during processing
- System continues processing other fields
- Clear indication that label no longer exists

#### Test Case 7.4: Custom Field Deletion Impact
**Objective**: Verify system behavior when referenced custom fields are deleted

**Test Steps**:
1. Configure file format with system function referencing custom field
2. Delete the referenced custom field
3. Attempt import/export using the file format
4. Monitor error handling

**Expected Results**:
- Deleted field references return empty values
- Processing continues without fatal errors
- Clear logging of missing field references
- Other fields continue to function normally

### 8. Performance Testing

#### Test Case 8.1: Large Dataset Processing
**Objective**: Verify system performance with large customer datasets

**Test Parameters**:
- 10,000+ customer records
- 5+ custom fields per customer
- Multiple system functions in file format

**Test Steps**:
1. Prepare large CSV file with custom field data
2. Configure file format with multiple system functions
3. Import large dataset
4. Monitor processing time and resource usage
5. Verify data completeness and accuracy

**Performance Metrics**:
- Processing time per 1000 records
- Memory usage during import
- Database query performance
- System responsiveness during processing

**Expected Results**:
- Processing completes within acceptable timeframe
- Memory usage remains within limits
- No performance degradation compared to legacy custom fields
- System remains responsive to other users

#### Test Case 8.2: Concurrent User Testing
**Objective**: Verify system performance under multiple concurrent users

**Test Setup**:
- 5+ users importing/exporting simultaneously
- Each user using file formats with system functions
- Various file sizes and custom field configurations

**Test Steps**:
1. Simulate concurrent import/export operations
2. Monitor system response times
3. Check for resource contention
4. Verify data integrity across all operations

**Expected Results**:
- All concurrent operations complete successfully
- Response times remain within acceptable limits
- No data corruption or conflicts
- System handles concurrent load appropriately

---

## Test Data Templates

### Sample CSV Files

#### Basic Import Test Data
```csv
Account#,Gender,Age,Service_Type,Billing_Preference
1000-100203,M,34,Water,Email
1000-100204,F,28,Electric,Mail
1000-100205,M,45,Gas,Email
1000-100206,F,52,Water,Online
```

#### Complex Labels Test Data
```csv
Account#,Preferred Contact Method,Service Notes,Special Instructions
1000-100203,Email & Phone,Customer requests morning calls only!,Leave packages at side door
1000-100204,Text Message,Billing address differs from service,Ring doorbell twice
1000-100205,Email Only,VIP customer - priority service,Contact manager for any issues
```

#### Large Dataset Template
```csv
Account#,Gender,Age,Service_Type,Billing_Preference,Contact_Method,Special_Notes,Account_Manager,Last_Updated,Priority_Level,Custom_Field_10
[Generated 10,000+ rows with varied data]
```

## Test Environment Requirements

### System Configuration
- Test database with sample customer data
- Multiple test companies with different custom field configurations
- File formats configured for various test scenarios
- Statement and invoice templates for generation testing

### User Access Requirements
- Admin access for file format configuration
- Import/export permissions for data testing
- Statement/invoice generation capabilities
- System monitoring tools access

### Data Cleanup Procedures
- Reset test data between test runs
- Clear staging tables after import tests
- Remove test custom fields after testing
- Restore original file format configurations

## Test Execution Checklist

### Pre-Test Setup
- [ ] Verify test environment is ready
- [ ] Create required custom fields for testing
- [ ] Prepare test CSV files
- [ ] Configure test file formats
- [ ] Set up monitoring tools

### Test Execution
- [ ] Execute all test cases in sequence
- [ ] Document results for each test case
- [ ] Capture screenshots of key functionality
- [ ] Record performance metrics
- [ ] Note any deviations from expected results

### Post-Test Activities
- [ ] Clean up test data
- [ ] Reset test environment
- [ ] Compile test results report
- [ ] Document any issues discovered
- [ ] Provide recommendations for production deployment

## Success Criteria

The SAAS-1390 implementation will be considered successful when:

1. **Core Functionality**: All system function syntax works correctly across import, export, and generation scenarios
2. **Unlimited Fields**: No artificial limitations on number of custom fields
3. **Label Support**: Complex labels with spaces and special characters function properly
4. **Backward Compatibility**: Existing legacy custom field implementations continue to work
5. **Error Handling**: Graceful handling of invalid labels, missing data, and edge cases
6. **Performance**: Acceptable performance with large datasets and concurrent users
7. **Company Isolation**: Proper scoping of custom fields per company
8. **Migration Support**: Clear upgrade path from legacy to system functions

## Risk Mitigation

### Identified Risks
- **Performance Impact**: System functions may introduce processing overhead
- **Data Migration**: Existing legacy data needs continued access
- **User Training**: Teams need to understand new syntax and capabilities
- **Backward Compatibility**: Must not break existing implementations

### Mitigation Strategies
- Comprehensive performance testing with realistic datasets
- Parallel support for legacy and new approaches
- Documentation and training materials for new functionality
- Gradual rollout with monitoring of system performance
