# Itron Import/Export User Guide
*Version 1.0 - MuniBilling System*

## Table of Contents
1. [Overview](#overview)
2. [File Formats Supported](#file-formats-supported)
3. [Current Client Deployments](#current-client-deployments)
4. [Setting Up Imports](#setting-up-imports)
5. [Setting Up Exports](#setting-up-exports)
6. [Field Reference](#field-reference)
7. [Complete Field Mapping Reference](#complete-field-mapping-reference)
8. [Database Relationships](#database-relationships)
9. [Technical Implementation](#technical-implementation)
10. [Troubleshooting Guide](#troubleshooting-guide)
11. [Best Practices](#best-practices)

---

## Overview

The Itron integration allows MuniBilling to exchange meter reading data with Itron handheld devices and software systems. This includes:

- **Importing** meter readings from Itron devices
- **Exporting** meter and customer data to Itron systems
- Support for both legacy text files and modern XML formats

### When to Use Itron Integration
- Your field staff uses Itron handheld reading devices
- You need to export meter setup data to Itron systems
- You want automated processing of meter reading files
- You need to track reading codes and equipment status

---

## File Formats Supported

### 1. Fixed-Width Text Format (.dat files)
**Best for**: Legacy Itron devices, simple setups
- Fixed column positions for all data
- Multiple record types in single file
- Requires specific file format configuration

### 2. XML Format (.xml files)  
**Best for**: Modern Itron MDI systems, comprehensive data exchange
- Structured XML with full meter/customer details
- Self-documenting format
- Better error handling

---

## Current Client Deployments

### Production Companies Using Itron Integration

The following 35+ companies currently use Itron integration with various file format configurations:

#### **Major Municipal Clients**

| **Company** | **Company ID** | **File Format ID** | **Format Name** | **Record Match Strategy** |
|-------------|----------------|-------------------|-----------------|---------------------------|
| **Beach City Utilities** | 1720 | 19951 | Itron Import | Account + Meter Number |
| **City of Arcadia** | 1085 | 10693 | Neptune and Itron - D1 Neptune | Meter Number |
| **City of Buffalo** | 1823 | 20594 | Itron FCS Meter Read Import | Meter Number |
| **City of Grass Valley** | 989 | 9660 | Z Itron | Meter Number |
| **City of Kennedale** | 973 | 9531 | Z Itron | Meter Number |
| **City of Onamia, MN** | 1783 | 20191 | Itron Import | Account + Meter Number |
| **HMUA** | 112 | 589/631 | Itron Import/Export | Account + Meter Number |
| **King George County Service Authority** | 1120 | 11567 | Z Itron | Meter Number |
| **Santa Clara Valley Water District** | 423 | 3505 | Z Itron | Meter Number |

#### **Water Utility Groups**

**Hope Water Companies** (5 locations):
- Hope Water - South (1801)
- Hope Water - Sunland (1843) 
- Hope Water - Valley (1802)
- IMP Hope Water - Horseshoe Bend (1844)
- IMP Hope Water - Lone Star (1845)
- IMP Hope Water - North (1841)
- IMP Hope Water - Sandario (1842)

All use format: "Itron Import" with Account + Meter Number matching.

#### **Private Utilities**
- **Parkland Utilities, Inc** (730) - Z Itron format
- **Riverwood Community Development District** (737) - Z Itron format
- **Red Energy** (449) - Z Itron format
- **Westridge Utilities Inc.** (121) - Standard Itron format

### File Format Usage Patterns

#### **Most Common Configurations**

1. **"Z Itron" Standard Format** (16 companies: 423, 449, 730, 737, 973, 989, 990, 1083, 1092, 1094, 1106, 1120, 1136, 1220, 1254, 1720)
   - Fixed-width text format
   - Meter Number matching strategy
   - Legacy handheld device compatibility

2. **"Itron Import" Modern Format** (10 companies: 112, 1720, 1783, 1801, 1802, 1841, 1842, 1843, 1844, 1845)
   - Enhanced precision with Account + Meter Number matching
   - Better multi-meter account support
   - Newer implementations

3. **"Neptune and Itron" Hybrid** (2 companies: 507, 1085)
   - Mixed vendor environments
   - Specialized configurations for dual systems

#### **Record Matching Strategy Distribution**
- **Meter Number Only**: 19 companies (58% - companies: 423, 449, 507, 730, 737, 973, 989, 990, 1083, 1085, 1092, 1094, 1106, 1120, 1136, 1220, 1254, 1720, 1823)
- **Account + Meter Number**: 10 companies (30% - companies: 112, 1720, 1783, 1801, 1802, 1841, 1842, 1843, 1844, 1845)
- **Account Number Only**: 2 companies (6% - companies: 112, 121)
- **Auxiliary Account Number**: 1 company (3% - company: 22)
- **Register Number**: 1 company (3% - company: 1823)

### Special Implementation Notes

#### **Companies with Hardcoded Export Customizations**
- **King George County** (1120): Custom route filler "01W0"
- **Parkland Utilities** (730): Special meter location formatting
- **Riverwood CDD** (737): Custom validation and reading calculations

#### **Multi-Format Companies**
Several companies maintain multiple Itron formats:
- **Beach City Utilities**: Standard + Modified Itron
- **City of Buffalo**: FCS Import + Legacy Z Itron  
- **HMUA**: Both Import and Export configurations
- **Red Energy**: Active Z Itron + Deprecated xDNU Itron

### Integration Statistics
- **Total Active Configurations**: 35 file formats across 28 unique companies
- **Company IDs**: 22, 112, 121, 423, 449, 507, 730, 737, 973, 989, 990, 1083, 1085, 1092, 1094, 1106, 1120, 1136, 1220, 1254, 1720, 1783, 1801, 1802, 1823, 1841, 1842, 1843, 1844, 1845
- **File Type**: All use meter reading imports (file_type_id = 2)
- **Geographic Distribution**: Nationwide deployment
- **Utility Types**: Municipal water, private utilities, water districts

This deployment data shows Itron integration is a mature, widely-used feature across diverse utility types and geographic regions.

---

## Setting Up Imports

### Prerequisites
✅ Active meters in MuniBilling with correct meter numbers  
✅ Parcels with matching account numbers  
✅ File format configured (if using fixed-width)  
✅ User account for import processing  

### Step 1: Configure File Format (Fixed-Width Only)

If using `.dat` files, you'll need to configure the file format:

1. **Navigate to**: Admin → File Formats
2. **Create new format** with these settings:
   - **Name**: "Itron Meter Import"
   - **File Type**: Fixed Width
   - **Record Match Type**: Choose based on your data:
     - **Account + Meter Number**: Most accurate (recommended)
     - **Account Number Only**: If meters are unique per account
     - **Meter Number Only**: If meter numbers are globally unique

3. **Configure Fields**: Add these key fields:

| Field Name | Import Column | Description | Required |
|------------|---------------|-------------|----------|
| End Reading | `itron_reading.end_reading` | Current meter reading | ✅ Yes |
| Reading Date | `itron_reading.end_reading_date` | Date reading was taken | ✅ Yes |
| Auto Read Type | `itron_reading.raw_meter_auto_read_type` | R/W/M code | No |
| Reading Code | `itron_reading.meter_reading_code` | Status codes | No |
| Skip Code | `itron_reading.skip_code` | Skip reasons | No |
| Trouble Codes | `itron_reading.trouble_code_1/2` | Equipment issues | No |

### Step 2: Process Import File

1. **Navigate to**: Meters → Import Readings
2. **Select**: "Itron Import"
3. **Choose file** and **file format** (if fixed-width)
4. **Select user** for processing
5. **Click Import**

### Step 3: Review Results

After import, check:
- **Records Processed**: Should match expected count
- **Warnings**: Review any unmatched accounts/meters
- **Reading Status**: Verify readings are "Unposted"
- **Meter Reading Codes**: Check if codes were applied correctly

---

## Setting Up Exports

### Export Types Available

#### 1. Standard Meter Export
**Purpose**: Send meter and customer data to Itron devices
- Includes customer info, meter details, and last readings
- Creates route files for organized reading

#### 2. XML Master Data Export  
**Purpose**: Full data synchronization with Itron MDI systems
- Complete meter installation details
- GPS coordinates and service information
- Advanced meter configuration

### Step 1: Configure Export Parameters

**Navigate to**: Meters → Export Data → Itron Export

**Key Settings**:
- **Meter Manufacturers**: Select Itron-compatible manufacturers
- **Route Codes**: Choose reading routes to include
- **Account Categories**: Filter by customer types
- **Date Filters**: Include meters installed/serviced after date

### Step 2: Generate Export File

1. **Select export type**: Standard or XML
2. **Choose filters** (routes, manufacturers, etc.)
3. **Set filename** (use route/date naming)
4. **Click Generate**

### Step 3: Transfer to Itron System

- **Fixed-width files**: Load into handheld devices
- **XML files**: Import into Itron MDI software
- Verify meter count matches expectations

---

## Field Reference

### Import Data Fields

#### Customer/Account Information
- **Account Number**: Must match MuniBilling parcel account number
- **Customer Name**: For verification only (not imported)
- **Address**: For verification only (not imported)

#### Meter Information  
- **Meter Number**: Must match meter number in MuniBilling
- **Register ID**: For multi-register meters (radio/wand readings)
- **Auto Read Type**: 
  - `R` = Radio reading
  - `W` = Wand reading  
  - `M` = Manual reading

#### Reading Data
- **End Reading**: Current meter reading value
- **Reading Date**: When reading was taken
- **Consumption**: Calculated automatically
- **Reading Codes**: Equipment and reading status

#### Status Codes
- **Standard Codes**: OK, LEAK, BROKEN, etc.
- **Skip Codes**: SC-01, SC-02, etc. (reasons reading was skipped)
- **Trouble Codes**: TC-01, TC-02, etc. (equipment problems)
- **Audit Codes**: Quality control flags

### Export Data Fields

#### Customer Data
- Account number and customer name
- Service address with GPS coordinates
- Account type and category

#### Meter Details
- Meter serial number and size
- Installation and service dates
- Location codes and reading instructions
- Register IDs for radio/wand readings

#### Route Information
- Route codes and reading sequences
- Reading type counters
- Geographic groupings

---

## Complete Field Mapping Reference

This section provides comprehensive field mappings between Itron files and MuniBilling database fields. Use this for detailed technical configuration and troubleshooting.

### Import Field Mappings (Fixed-Width Format)

The Itron import process handles 5 record types in this precedence order:
- **CUS** (Customer/Parcel record)
- **MTR** (Meter record)  
- **RDG** (Reading record)
- **RFF** (Radio Frequency record)
- **WRR** (Wand Reading record)

#### Detailed Import Field Mappings

| **Itron File Field** | **File Position** | **Database Field** | **Database Table** | **Description** | **Notes** |
|---------------------|-------------------|-------------------|-------------------|-----------------|-----------|
| **CUS Record - Customer/Account Data** |
| Account Number | 14-34 (20 chars) | `account_number` | `parcels` | Customer account identifier | Must match existing parcel |
| Customer Name | 34-54 (20 chars) | N/A | N/A | Display only | Not imported, used for verification |
| Street Number | 54-60 (6 chars) | N/A | N/A | Display only | Not imported |
| Street Code | 60-74 (14 chars) | N/A | N/A | Display only | Not imported |
| **MTR Record - Meter Information** |
| Meter Number | 45-57 (12 chars) | `number` | `meters` | Physical meter serial number | Must match existing meter |
| Location Code | varies | `location` | `meter_locations` | Meter physical location | 2-character code |
| Read Instructions 1 | varies | `name` | `meter_reading_codes` | Reading instruction code | Last 2 digits used |
| Read Instructions 2 | varies | `name` | `meter_reading_codes` | Additional instruction | Last 2 digits used |
| **RDG Record - Reading Data** |
| Auto Read Type | varies | `code` | `meter_auto_read_types` | Reading method | R=Radio, W=Wand, M=Manual |
| End Reading | varies | `end_reading` | `meter_readings` | Current meter reading value | Adjusted for decimal places |
| End Reading Date | varies | `end_reading_date` | `meter_readings` | Date reading was taken | Date format varies by configuration |
| Read Time | varies | `read_time` | temp field | Time reading was taken | Not permanently stored |
| Meter Reading Code | varies | `name` | `meter_reading_codes` | Equipment/reading status | Standard codes (OK, LEAK, etc.) |
| Skip Code | varies | `name` | `meter_reading_codes` | Skip reason code | Format: SC-XX |
| Audit Code | varies | `name` | `meter_reading_codes` | Audit/quality flag | Varies by company |
| Trouble Code 1 | varies | `name` | `meter_reading_codes` | Equipment issue 1 | Format: TC-XX |
| Trouble Code 2 | varies | `name` | `meter_reading_codes` | Equipment issue 2 | Format: TC-XX |
| Low Dial Count | varies | `meter_code_1` | `meters` | Number of dials on meter | Updates meter configuration |
| Low Decimal Count | varies | `meter_code_2` | `meters` | Decimal precision | Updates meter configuration |
| **RFF Record - Radio Frequency Data** |
| Register ID | 11-19 (8 chars) | `register_id` | `meter_readings` | Radio frequency register ID | Links to meter's low_register_id |
| Frequency | 27-40 | N/A | N/A | Radio frequency | Not imported |
| Channel | 41-44 | N/A | N/A | Radio channel | Not imported |
| **WRR Record - Wand Reading Data** |
| Register ID | 11-25 (14 chars) | `register_id` | `meter_readings` | Wand reading register ID | Links to meter's register IDs |
| Device Type | 25-29 | N/A | N/A | Device identifier | METR or ERT |

### Export Field Mappings (Fixed-Width Format)

#### File Structure Records

| **Record Type** | **Purpose** | **Key Fields** | **Database Source** |
|-----------------|-------------|---------------|-------------------|
| FHD | File Header | File format version | Hardcoded values |
| FTR | File Trailer | File completion | Hardcoded values |
| CHD | Cycle Header | Cycle identifier | Route information |
| CTR | Cycle Trailer | Cycle completion | Route information |
| RHD | Route Header | Route counters, statistics | Calculated from route data |
| RTR | Route Trailer | Route completion | Calculated from route data |

#### Data Records - Export Mappings

| **Record Type** | **Database Source** | **Field** | **File Position** | **Description** | **Processing Notes** |
|-----------------|-------------------|-----------|-------------------|-----------------|-------------------|
| **CUS - Customer/Account Record** |
| | `route_codes.name` | Route Code | 3-11 | Reading route identifier | Format: "01R" + route name |
| | `parcels.meters.count` | Meter Count | 11-14 | Number of meters for account | Calculated |
| | `parcels.account_number` | Account Number | 14-34 | Account identifier | Left-padded with spaces |
| | `customers.first_name + last_name` | Customer Name | 34-54 | Full customer name | Truncated to 20 chars |
| | `gis_addresses.street_number` | Street Number | 54-60 | Address number | From GIS data if available |
| | `gis_streets.code` | Street Code | 60-74 | Street identifier | From GIS data if available |
| **MTR - Meter Record** |
| | `route_codes.name` | Route Code | 3-11 | Reading route identifier | Format: "01R" + route name |
| | `meter_sizes.is_compound` | Reading Count | 11-14 | Number of registers | 1 or 2 based on meter type |
| | `meters.number` | Meter Number | 45-57 | Meter serial number | 12 characters, right-padded |
| | `meter_locations.location` | Location Code | varies | Meter location | 2-character code |
| | `meter_reading_codes.name` | Read Instructions | varies | Reading instructions | Last 2 digits of code |
| **RDG - Reading Record** |
| | `route_codes.name` | Route Code | 3-11 | Reading route identifier | Format: "01R" + route name |
| | `meter_auto_read_types.code` | Read Type | varies | Reading method | R/W/M code |
| | `meter_sizes.low_dial_count` | Dial Count | varies | Number of dials | From meter size configuration |
| | `meter_readings.end_reading` | Last Reading | varies | Previous reading value | Adjusted for stationary zeros |
| | `meter_readings.consumption` | Consumption | varies | Usage calculation | Calculated field |
| | Calculated | Consumption (Gallons) | varies | Usage in gallons | Consumption * 0.25 |
| **RFF - Radio Frequency Record** |
| | `route_codes.name` | Route Code | 3-11 | Reading route identifier | Format: "01R" + route name |
| | `meters.low_register_id` | Register ID | 11-19 | RF register identifier | 8 characters, zero-padded |
| | Hardcoded | Frequency | 27-40 | Radio frequency | "000956.35625" |
| | Hardcoded | Channel | 41-44 | Radio channel | "0013" |
| **WRR - Wand Reading Record** |
| | `route_codes.name` | Route Code | 3-11 | Reading route identifier | Format: "01R" + route name |
| | `meters.low_register_id` | Register ID | 11-25 | Wand register identifier | 14 characters, left-padded |
| | `meter_auto_read_types.code` | Device Type | 25-29 | Device identifier | "METR" for wand, "ERT" for radio |

### XML Export Field Mappings (MDI Format)

#### Service Point Information

| **XML Element** | **Database Source** | **Field** | **Description** | **Processing** |
|-----------------|-------------------|-----------|-----------------|---------------|
| **SetServicePoint** |
| | `service_types.name` | CommodityType | Service type mapping | Water→Water, Gas→Gas, Electric→Electric |
| | Fixed | EquipmentType | Equipment classification | Always "Endpoint" |
| | `parcels.account_number` | PremiseId | Property identifier | Direct mapping |
| | Fixed | PrimaryCollectionSystem | Collection method | Always "OpenWayRiva" |
| | `parcels.account_number` | ServicePointId | Service point identifier | Same as PremiseId |
| | `companies.time_zone` | TimeZone | Time zone mapping | Converted to Itron format |

#### Account Information

| **XML Element** | **Database Source** | **Field** | **Description** | **Processing** |
|-----------------|-------------------|-----------|-----------------|---------------|
| **SetAccount** |
| | `parcels.account_number` | AccountId | Account identifier | Direct mapping |
| | `parcels.account_number` | AccountNumber | Account number | Duplicate for compatibility |
| | `customers.first_name` | CustomerFirstName | Customer first name | From current customer |
| | `customers.last_name` | CustomerLastName | Customer last name | From current customer |

#### Address Information

| **XML Element** | **Database Source** | **Field** | **Description** | **Processing** |
|-----------------|-------------------|-----------|-----------------|---------------|
| **Address** |
| | `parcels.city` | City | City name | Direct mapping |
| | Fixed | Country | Country name | Always "United States" |
| | `americanstates.abbreviation` | State | State abbreviation | 2-character code |
| | `parcels.display_address` | StreetAddress | Full street address | Formatted address |
| | `parcels.zipcode` | Zip | Postal code | Direct mapping |
| | `parcels.latitude` | Latitude | GPS latitude | Optional, if available |
| | `parcels.longitude` | Longitude | GPS longitude | Optional, if available |

#### Meter Configuration

| **XML Element** | **Database Source** | **Field** | **Description** | **Processing** |
|-----------------|-------------------|-----------|-----------------|---------------|
| **SetMeter** |
| | `meters.number` | MeterId | Meter identifier | Cleaned of H/L suffixes |
| | `meters.number` | MeterNumber | Meter number | Same as MeterId |
| | `meters.number` | MeterSerialNumber | Serial number | Same as MeterId |
| | `meter_sizes.size` | MeterSize | Physical meter size | Direct mapping |
| | `meter_manufacturers.description` | MeterType | Manufacturer/model | Direct mapping |
| | `meters.install_date` | MeterInstallationDate | Install date | ISO 8601 format |

#### Channel Configuration

| **XML Element** | **Database Source** | **Field** | **Description** | **Processing** |
|-----------------|-------------------|-----------|-----------------|---------------|
| **SetChannel** |
| | Fixed | ChannelNumber | Channel number | Always 1 for water/gas |
| | Fixed | HasIntervalData | Interval capability | Always true |
| | `unit_types.name` | Unit | Unit of measurement | CF→CF, GAL→GAL, KWH→KWH |

#### Device Configuration

| **XML Element** | **Database Source** | **Field** | **Description** | **Processing** |
|-----------------|-------------------|-----------|-----------------|---------------|
| **SetDevice** |
| | Fixed | Active | Device status | Always true for active meters |
| | `custom_fields` + `meters.low_register_id` | DeviceId | Device identifier | Prefix + register ID |
| | Fixed | DeviceType | Device type code | Always 27 (OpenWay Riva Water) |

#### Device Configuration Details

| **XML Element** | **Database Source** | **Field** | **Description** | **Processing** |
|-----------------|-------------------|-----------|-----------------|---------------|
| **DecodeType** |
| | `meter_sizes.low_dial_count` | Dials | Number of dials | Direct mapping |
| | Fixed | Multiplier | Reading multiplier | Always 1 |
| | `meter_codes.name` | Truncation | Reading truncation | From meter code |

---

## Database Relationships

Understanding the database relationships is crucial for troubleshooting and configuration.

### Core Table Relationships

```
companies (1) → parcels (many)
    ↓
parcels (1) → meters (many)
    ↓
meters (1) → meter_readings (many)
```

### Key Database Tables and Fields

#### Meters Table
**Primary Purpose**: Physical meter information
- **Key Fields**: `number`, `low_register_id`, `high_register_id`, `install_date`
- **Configuration**: `meter_code_1` (dial count), `meter_code_2` (decimal count)
- **Relationships**: `parcel_id`, `meter_manufacturer_id`, `meter_size_id`

#### Meter Readings Table
**Primary Purpose**: Reading data and calculations
- **Key Fields**: `end_reading`, `end_reading_date`, `consumption`, `register_id`
- **Status**: `meter_reading_status_id` (Posted, Unposted, etc.)
- **Relationships**: `meter_id`, `customer_id`, `meter_reading_link_id`

#### Parcels Table
**Primary Purpose**: Service locations and customer accounts
- **Key Fields**: `account_number`, `address_line1`, `city`, `latitude`, `longitude`
- **Organization**: `route_code_id`, `account_type_id`, `account_category_id`
- **Relationships**: `company_id`, `current_customer_id`

#### Supporting Tables
- **`meter_reading_codes`**: Status codes (OK, LEAK, SC-01, TC-01, etc.)
- **`meter_auto_read_types`**: Reading methods (Radio, Wand, Manual)
- **`meter_sizes`**: Physical specifications and dial configurations
- **`meter_manufacturers`**: Equipment manufacturers
- **`route_codes`**: Reading route organization
- **`customers`**: Customer information linked to parcels

### Record Matching Strategies

The import system supports multiple matching methods:

1. **ACCOUNT_NUMBER_AND_METER_NUMBER** (Recommended)
   - Most precise matching
   - Handles multiple meters per account
   - Best for complex installations

2. **ACCOUNT_NUMBER**
   - Single meter per account
   - Simpler configuration
   - Good for residential routes

3. **METER_NUMBER**
   - Globally unique meter numbers
   - Independent of account structure
   - Useful for mixed meter types

4. **METER_NUMBER_AND_REGISTER_NUMBER**
   - Multi-register meters (compound meters)
   - Handles high/low flow separately
   - Required for complex commercial meters

### Data Flow During Import

1. **File Parsing**: Parse record types (CUS→MTR→RDG→RFF→WRR)
2. **Record Linking**: Group related records via `meter_reading_link_id`
3. **Meter Matching**: Find meter using configured strategy
4. **Reading Creation**: Create `meter_reading` record
5. **Code Assignment**: Link `meter_reading_codes` for status
6. **Calculation**: Compute consumption and apply adjustments

### Data Flow During Export

1. **Parcel Selection**: Filter by routes, categories, manufacturers
2. **Meter Enumeration**: Find active meters for each parcel
3. **Customer Lookup**: Get current customer information
4. **Reading Retrieval**: Get last reading for each meter/register
5. **Format Generation**: Create fixed-width or XML output
6. **Route Organization**: Group by routes with counters

---

## Technical Implementation

### System Architecture

The Itron integration is implemented through a multi-layered job processing system with background queue support:

#### **Core Implementation Files**

**Import Processing:**
- `app/business_logic/jobs/imports/meter_import_itron_job.rb` - Fixed-width file processor
- `app/business_logic/jobs/imports/meter_import_itron_xml_job.rb` - XML file processor  
- `lib/itron_meter_import_file.rb` - Fixed-width parsing engine (386 lines)
- `lib/itron_meter_import_xml_file.rb` - XML parsing with Nokogiri (74 lines)

**Export Processing:**
- `app/business_logic/jobs/exports/itron_meter_export_job.rb` - Main export engine (551 lines)
- `app/business_logic/jobs/exports/itron_meter_export_xml_job.rb` - XML MDI export
- `lib/itron_meter_export_xml_file.rb` - XML generation with Builder (409 lines)
- `lib/xsd/itron_mdi_export.xsd` - XML schema validation

### Job Processing Flow

#### **Import Workflow**
1. **File Upload**: Web interface → Temporary storage
2. **Job Creation**: Background job queued via Sidekiq/DelayedJob
3. **Format Detection**: Fixed-width requires `file_format_id`, XML auto-detected
4. **Record Processing**: 
   - **Fixed-width**: CUS→MTR→RDG→RFF→WRR precedence order
   - **XML**: Channel-based reading extraction
5. **Meter Matching**: Database lookup via configured strategy
6. **Reading Creation**: Insert with status "Unposted"
7. **Code Assignment**: Link meter reading codes (OK, LEAK, SC-XX, TC-XX)

#### **Export Workflow**  
1. **Parameter Configuration**: Routes, manufacturers, date filters
2. **Data Retrieval**: Stored procedure `sp_itron_meter_export()`
3. **File Generation**: 
   - **Fixed-width**: Header→Customer→Meter→Reading→Footer structure
   - **XML**: MDI-compliant with SetServicePoint→SetAccount→SetMeter hierarchy
4. **Route Processing**: Organized by reading routes with counters
5. **File Output**: Saved to `export_temp_path` directory

### Record Processing Details

#### **Fixed-Width Record Types (itron_meter_import_file.rb:30)**
```ruby
row_precedence = ["CUS","MTR","RDG","RFF","WRR"]
```

- **CUS**: Customer/Account data (account number extraction)
- **MTR**: Meter information (meter number, location codes)  
- **RDG**: Reading data (end_reading, date, codes)
- **RFF**: Radio Frequency data (register IDs for radio readings)
- **WRR**: Wand Reading data (register IDs for wand readings)

#### **Record Matching Strategies (itron_meter_import_file.rb:131-161)**
```ruby
case @file_format.record_match_type.key
when RecordMatchType::ACCOUNT_NUMBER_AND_METER_NUMBER
  # Most precise - recommended for multi-meter accounts
when RecordMatchType::ACCOUNT_NUMBER  
  # Single meter per account scenarios
when RecordMatchType::METER_NUMBER
  # Globally unique meter numbers
when RecordMatchType::METER_NUMBER_AND_REGISTER_NUMBER
  # Compound/multi-register meters
```

### XML MDI Implementation

#### **Schema Compliance (itron_meter_export_xml_file.rb:9-16)**
- **Namespace**: `http://www.itron.com/masterdata/2013/03`
- **Schema**: Itron MDI MasterDataImport.xsd
- **Validation**: Nokogiri XML schema validation
- **Structure**: ServicePoint→Account→Address→Meter→Channel→Device

#### **Key XML Elements**
- **SetServicePoint**: Commodity type, equipment type, premise ID
- **SetAccount**: Account details and customer information  
- **SetMeter**: Meter configuration and installation data
- **SetDevice**: Device ID with custom prefix, decode parameters

### Company-Specific Customizations

#### **Hardcoded Export Logic (itron_meter_export_job.rb)**
```ruby
# King George County special handling
route_filler = "01W0" if company_id == Company::KING_GEORGE

# Parkland/Riverwood formatting
if parkland_or_riverwood?(master_company, company_id)
  meter_location = r[METER_LOCATION].to_s[0..19].ljust(20,' ')
  # Special validation calculations
end
```

#### **Database Integration Points**
- **Companies**: 28 unique companies (IDs: 22, 112, 121, 423, 449, 507, 730, 737, 973, 989, 990, 1083, 1085, 1092, 1094, 1106, 1120, 1136, 1220, 1254, 1720, 1783, 1801, 1802, 1823, 1841, 1842, 1843, 1844, 1845) with 35 active Itron file format configurations
- **File Formats**: Configurable field mappings in `file_formats` table
- **Meter Readings**: Status tracking with `MeterReadingStatus::UNPOSTED_READING`
- **Reading Codes**: Standardized codes (OK, LEAK, SC-XX, TC-XX) in `meter_reading_codes`

### Performance Considerations

#### **Import Processing**
- **Batch Processing**: Records processed in memory before database commits
- **Progress Tracking**: Real-time job progress updates via `ProgressUpdater`
- **Error Handling**: Graceful failure with detailed logging

#### **Export Processing**
- **Stored Procedures**: `sp_itron_meter_export()` for optimized data retrieval
- **Memory Management**: Streaming file generation for large datasets
- **Route-Based Organization**: Efficient grouping by reading routes

### Configuration Requirements

#### **Database Prerequisites** 
- Active meters with correct meter numbers
- Parcels with matching account numbers
- File format configuration (fixed-width only)
- Route codes assigned to parcels

#### **System Dependencies**
- **Ruby Gems**: Nokogiri (XML), Builder (XML generation)
- **Job Processing**: Sidekiq or DelayedJob for background processing
- **File Storage**: Configured `export_temp_path` directory
- **Database**: MySQL stored procedures for export queries

This technical implementation supports both legacy handheld devices and modern MDI systems with robust error handling and performance optimization.

---

## Troubleshooting Guide

### Common Import Issues

#### ❌ "No meters found for account"
**Cause**: Account number mismatch
**Solution**: 
1. Check account number format (leading zeros, spaces)
2. Verify account exists in MuniBilling
3. Confirm account is active

#### ❌ "Meter number not found"  
**Cause**: Meter number mismatch
**Solution**:
1. Compare meter numbers exactly (case sensitive)
2. Check for extra characters (H, L suffixes)
3. Verify meter status is "Active"

#### ❌ "Invalid register ID"
**Cause**: Register ID doesn't match meter configuration
**Solution**:
1. Check meter's low/high register ID fields
2. Update meter register IDs if needed
3. Consider using account-only matching

#### ❌ "Date format errors"
**Cause**: Date not in expected format
**Solution**:
1. Check file format date configuration
2. Verify date fields are properly positioned
3. Ensure dates are valid (not future dates)

### Common Export Issues

#### ❌ "No meters found to export"
**Cause**: Filter criteria too restrictive
**Solution**:
1. Check manufacturer filter settings
2. Verify route codes are assigned to parcels
3. Expand date range filters
4. Check meter status (must be Active)

#### ❌ "Missing GPS coordinates"
**Cause**: Parcel coordinates not populated
**Solution**:
1. Update parcel latitude/longitude
2. Use GIS address matching if available
3. Consider manual coordinate entry

#### ❌ "Invalid XML format"
**Cause**: Missing required data fields
**Solution**:
1. Ensure all meters have install dates
2. Verify customer names are complete
3. Check for special characters in addresses

### Performance Issues

#### 🐌 "Import/Export taking too long"
**Solutions**:
- Process files in smaller batches
- Run during off-peak hours
- Check database performance
- Consider route-based processing

#### 🔄 "Timeouts during processing"
**Solutions**:
- Increase job timeout settings
- Process files by route or date range
- Check system resources
- Monitor job queue status

---

## Best Practices

### File Management
✅ **Use consistent naming**: Route_Date_Type.dat (e.g., R01_20241013_readings.dat)  
✅ **Keep backups**: Archive processed files for 90+ days  
✅ **Validate before import**: Check file format and record counts  
✅ **Process promptly**: Import readings within 24-48 hours  

### Data Quality
✅ **Regular meter audits**: Verify meter numbers match physical tags  
✅ **Route maintenance**: Keep route assignments current  
✅ **Address updates**: Maintain GPS coordinates for mobile devices  
✅ **Reading code training**: Ensure field staff use correct codes  

### Troubleshooting Workflow
1. **Check file format**: Verify columns/structure
2. **Test with small sample**: Process 10-20 records first  
3. **Review error logs**: Check specific failure reasons
4. **Validate source data**: Confirm meters/accounts exist
5. **Check timing**: Avoid concurrent processing

### Security Considerations  
✅ **File permissions**: Restrict access to import/export directories  
✅ **Data validation**: Verify file contents before processing  
✅ **Audit trail**: Log all import/export activities  
✅ **Backup verification**: Test restore procedures regularly  

---

## Support Information

### Getting Help
- **System Logs**: Check Rails logs for detailed error messages
- **Job Queue**: Monitor background job status
- **Database Queries**: Verify data relationships
- **File Samples**: Request sample files for format verification

### Contact Information
For technical support with Itron integration:
- Check system logs first
- Gather sample files and error messages
- Document steps to reproduce issues
- Include system environment details

---

*Last Updated: October 17, 2024*  
*Document Version: 2.0 - Enhanced with Production Deployment Data and Technical Implementation Details*