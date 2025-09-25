# Santa Clara Valley Water District - Barcode Implementation Documentation

## Overview
This document provides comprehensive technical documentation for the barcode implementation used on water production statements for Santa Clara Valley Water District (Company ID 423).

## Barcode Specifications

### Font Information
- **Font Family**: "3 of 9 Barcode"
- **Barcode Type**: Code 39 (3 of 9)
- **Font Size**: 24px
- **Character Encoding**: Alphanumeric (0-9, A-Z) plus special characters

### Scanner Requirements
- **Compatible Scanners**: Any standard barcode scanner supporting Code 39 format
- **Special Equipment**: None required - Code 39 is universally supported
- **Scanner Types**: Handheld, fixed-mount, or mobile device scanners

## Technical Implementation

### Database Configuration
```sql
-- Company-level barcode enablement
companies.enable_statement_barcode: BOOLEAN
-- When TRUE, renders barcode on statements

-- Barcode data source
companies.bill_note: VARCHAR
-- Contains the data to be encoded in the barcode
```

### Code Location
- **Primary Template**: `/app/views/bills/statement_trifold.html.erb:184`
- **String Processing**: `/lib/single_bill_export_array.rb:175-177`
- **Print Job**: `/lib/jobs/printing/print_invoice_job.rb`
- **Export Framework**: `/lib/export_file.rb`
- **Company Configuration**: Company ID 423 (SCVWD constant)

### CSS Implementation
```css
.barcode {
    font-family: "3 of 9 Barcode";
    font-size: 24px;
}
```

### Data Flow
1. **Source**: `company.bill_note` field in database
2. **String Processing**: Carriage returns (`\r`) and newlines (`\n`) replaced with spaces in `SingleBillExportArray.get_entity_hash()` (lines 175-177)
3. **Processing**: Data is wrapped with asterisks (`*data*`) for Code 39 format
4. **Positioning**: Placed at index 79 in statement data array
5. **Rendering**: Displayed in "DO NOT WRITE IN THIS SPACE" section of statement

## Code 39 Format Details

### Character Set
- **Numbers**: 0-9
- **Letters**: A-Z (uppercase only)
- **Special Characters**: Space, $, %, +, -, ., /
- **Start/Stop**: Asterisk (*) characters

### Format Structure
```
*[DATA]*
```
- Leading asterisk: Start character
- Data content: Variable length alphanumeric string
- Trailing asterisk: Stop character

### Error Detection
- **Built-in Validation**: Code 39 includes modulo 43 checksum (optional)
- **Self-Checking**: Invalid characters cannot be encoded
- **Redundancy**: Wide/narrow bar pattern provides error resistance

## Implementation Details

### Template Rendering
```erb
<% if statement_data[79].present? && company.enable_statement_barcode %>
  <div class="barcode">
    *<%= statement_data[79] %>*
  </div>
<% end %>
```

### Company Identification
- **Company Name**: Santa Clara Valley Water District
- **Company ID**: 423
- **Constant Reference**: `SCVWD = 423`
- **Workflow Type**: `WorkflowType::SCVWD_SW`

### Integration Points
- **Statement Generation**: Integrated with trifold statement layout
- **Print Workflow**: Compatible with PDF generation and printing
- **Bootstrap Framework**: Uses Bootstrap CSS classes and grid system
- **Responsive Design**: Adapts to different paper sizes and orientations

## Configuration Management

### Enabling Barcodes
```sql
UPDATE companies 
SET enable_statement_barcode = 1 
WHERE id = 423;
```

### Setting Barcode Data
```sql
UPDATE companies 
SET bill_note = 'DESIRED_BARCODE_CONTENT' 
WHERE id = 423;
```

### Workflow Configuration
- **Statement Type**: SCVWD Statement Workflow (`SCVWD_SW`)
- **Template**: Trifold statement with barcode section
- **Processing**: Specialized SCVWD statement processing job

## Testing and Validation

### Barcode Testing
1. **Visual Verification**: Barcode appears in "DO NOT WRITE IN THIS SPACE" section
2. **Scanner Testing**: Test with Code 39 compatible scanner
3. **Data Validation**: Verify scanned data matches processed `company.bill_note` (with spaces replacing line breaks)
4. **Print Quality**: Ensure adequate contrast and resolution for scanning

### String Processing Behavior
- **Carriage Returns (`\r`)**: Automatically replaced with spaces during statement generation
- **Newlines (`\n`)**: Automatically replaced with spaces during statement generation
- **Scanned Result**: Contains spaces where original data had line breaks
- **Processing Location**: `SingleBillExportArray.get_entity_hash()` method

### Common Issues
- **Font Missing**: Ensure "3 of 9 Barcode" font is installed on print servers
- **Data Length**: Code 39 supports variable length but consider scanner limitations
- **Character Set**: Only use supported Code 39 characters
- **Contrast**: Ensure sufficient black/white contrast for reliable scanning

## Security Considerations

### Data Content
- **Public Data**: Barcode content appears on customer statements
- **No Sensitive Information**: Avoid encoding confidential data
- **Customer Identification**: Consider privacy implications of encoded data

### Print Security
- **Template Access**: Restrict access to statement templates
- **Data Validation**: Validate barcode content before rendering
- **Audit Trail**: Log barcode generation and modifications

## Maintenance and Support

### Font Management
- **Installation**: Ensure "3 of 9 Barcode" font is available on all print servers
- **Licensing**: Verify proper licensing for barcode font usage
- **Backup**: Maintain backup copies of barcode fonts

### Troubleshooting
1. **Barcode Not Appearing**: Check `enable_statement_barcode` setting
2. **Scanner Not Reading**: Verify Code 39 scanner compatibility
3. **Incorrect Data**: Validate `company.bill_note` content
4. **Print Quality**: Adjust font size or contrast settings

## Related Documentation
- Statement Generation Workflow Documentation
- SCVWD-Specific Business Logic
- Print Template Customization Guide
- Database Schema Documentation

## Change History
- **Implementation Date**: [Original implementation date]
- **Font Selection**: "3 of 9 Barcode" chosen for Code 39 compatibility
- **Template Integration**: Added to trifold statement layout
- **Configuration**: Company-level enablement and data management
- **2025-01-11**: Documented string processing behavior - carriage returns and newlines replaced with spaces

## Key Technical Findings

### String Processing Implementation
```ruby
# Location: /lib/single_bill_export_array.rb:175-177
note = hash_company.bill_note.to_s.gsub(/\r/, WHSP)
note = note.gsub(/\n/, WHSP)
hash_company.bill_note = note
```

### Barcode Scanning Characteristics
- **No carriage returns or tabs in scanned output**
- **Line breaks from database become spaces in barcode**
- **Processing occurs before barcode rendering**
- **Ensures clean, scannable barcode format**

---

**Document Version**: 1.1  
**Last Updated**: 2025-01-11  
**Author**: System Documentation  
**Review Required**: Print Services Team, SCVWD Operations