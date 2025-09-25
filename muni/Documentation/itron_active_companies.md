# ITRON Metering Import/Export Functions - Active Companies

## Overview
This document lists the active companies in the Muni billing system that utilize ITRON metering import/export functions, along with their specific configurations and customizations.

## Active Companies Using ITRON Functions

### 1. Parkland Utilities, Inc
- **Company ID**: 730
- **Master Company**: INMK or FS
- **Special Features**:
  - Custom high/low read calculations based on consumption averages
  - Dynamic read limits: High = avg × 1.8 (min 10), Low = avg × 0.4 (max 10)
  - Special meter location and number formatting (left-justified)
  - HHF flag enabled
  - Custom validation codes (000 instead of 099)
  - Account category used as filler field

### 2. Riverwood Community Development District  
- **Company ID**: 737
- **Master Company**: INMK or FS
- **Special Features**:
  - Same specialized logic as Parkland
  - Custom high/low read calculations based on consumption history
  - Special meter sequence calculation (combines two sequence fields)
  - HHF flag enabled
  - Custom validation and percentage settings

### 3. King George County Service Authority
- **Company ID**: 1120
- **Special Features**:
  - Custom route filler: "01W0" instead of standard "0100"
  - Special RF ERT ID formatting (left-justified instead of right-justified)
  - Read type code "00" instead of standard "01"
  - Address/account number swapping logic
  - Uses customer account number instead of parcel number
  - Service address becomes primary, billing address becomes secondary

### 4. New Wilmington Borough
- **Company ID**: 1254
- **Special Features**:
  - Has ITRON-related meter data update scripts
  - Uses `low_register_id` for meter identification
  - CSV processing for meter codes and read types
  - Meter data synchronization with ITRON export files

## ITRON Export Job Classes

### Available Export Types

1. **ItronMeterExportJob**
   - Standard ITRON export format
   - Basic meter reading export functionality
   - Company-specific customizations for routing and formatting

2. **ItronMeterExportWithRffJob** 
   - Enhanced version with Radio Frequency (RFF) data
   - Includes RF ERT ID and frequency information
   - Used for radio-read meter systems

3. **ItronMeterExportWithRffNoUnpostedReadsJob**
   - RFF version that excludes unposted meter readings
   - Ensures only verified readings are exported

4. **ItronMeterExportWithoutCsxMtsNoUnpostedReadsJob**
   - Version without Customer Extra (CSX) and Meter Special Message (MTS) records
   - Streamlined export for specific ITRON configurations

5. **ItronMeterExportXmlJob**
   - XML format export instead of fixed-width text
   - Uses `ItronMeterExportXmlFile` class for XML generation

## Technical Implementation Details

### Database Integration
- All exports use the `sp_itron_meter_export` stored procedure
- Stored procedure accepts parameters for:
  - Company ID
  - Account category ID
  - Account type ID  
  - Route code IDs
  - Meter category IDs
  - Meter manufacturer IDs

### File Format Structure
ITRON exports follow a hierarchical structure:
1. **File Header (FHD)** - File-level metadata
2. **Cycle Header (CHD)** - Billing cycle information
3. **Route Header (RHD)** - Route-specific data
4. **Customer (CUS)** - Customer account information
5. **Customer Extra (CSX)** - Extended customer data
6. **Meter (MTR)** - Meter hardware details
7. **Meter Special Message (MTS)** - Meter-specific messages
8. **Reading (RDG)** - Meter reading parameters
9. **Radio Frequency (RFF)** - RF meter configuration (when applicable)
10. **Route Trailer (RTR)** - Route summary
11. **Cycle Trailer (CTR)** - Cycle summary
12. **File Trailer (FTR)** - File completion marker

### Company-Specific Customizations

#### Parkland/Riverwood Logic
- Master company check: `[MasterCompany::INMK, MasterCompany::FS].include?(master_company)`
- Dynamic read calculations based on historical consumption
- Special meter formatting and location handling

#### King George Logic  
- Route filler override
- Address field swapping
- RF ERT ID formatting differences
- Read type code modifications

### File Processing
- Files are generated in the configured export temp path
- `Printer` class handles file saving and company association
- Binary file writing with specific character encoding requirements

## Usage Notes

- All companies use the same core stored procedure but with different formatting logic
- Company-specific logic is handled through conditional statements in the job classes
- Export files are saved with company-specific naming conventions
- File generation includes validation and error handling for data integrity

## Maintenance Considerations

- Regular testing of company-specific export logic during updates
- Validation of ITRON file format compliance
- Monitoring of export file sizes and processing times
- Coordination with ITRON system administrators for format changes