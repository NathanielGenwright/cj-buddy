# Meter Reading Codes: Complete System Guide

## Table of Contents
1. [System Overview](#system-overview)
2. [Database Architecture](#database-architecture)
3. [Implementation Workflow](#implementation-workflow)
4. [User Interface Locations](#user-interface-locations)
5. [Code Usage & Methods](#code-usage--methods)
6. [Active Company Examples](#active-company-examples)
7. [Reporting & Export Integration](#reporting--export-integration)
8. [Current Usage Analysis](#current-usage-analysis)
9. [Implementation Recommendations](#implementation-recommendations)

---

## System Overview

**Meter Reading Codes** are company-specific labels used to categorize and track different types of meter readings in the Muni Billing system. They provide operational insights into reading collection methods and data quality tracking.

### Purpose
- **Categorize Reading Methods**: Track how meter readings were obtained (AMI, manual, drive-by, etc.)
- **Data Quality Tracking**: Identify reading sources for billing accuracy and troubleshooting
- **Reporting & Analytics**: Group readings by collection method for operational insights
- **Audit Trail**: Provide context for billing accuracy verification

### Key Features
- **Company-Scoped**: Each company manages its own set of codes
- **Many-to-Many**: Single reading can have multiple codes; single code can apply to multiple readings
- **Optional Metadata**: Enhances operational data without affecting core billing logic
- **Integration Ready**: Works with both manual entry and automated import systems

---

## Database Architecture

### Core Tables

#### `meter_reading_codes`
```sql
- id (Primary Key)
- company_id (Foreign Key to companies)
- name (Short identifier, e.g., "AMI", "MANUAL")
- description (Detailed explanation)
- created_at, updated_at
```

#### `meter_reading_meter_reading_codes` (Join Table)
```sql
- meter_reading_id (Foreign Key to meter_readings)
- meter_reading_code_id (Foreign Key to meter_reading_codes)
```

#### `meter_readings` (Enhanced)
```ruby
has_many :meter_reading_meter_reading_codes
has_many :meter_reading_codes, through: :meter_reading_meter_reading_codes
```

### Relationships
- **Company** → `has_many :meter_reading_codes`
- **MeterReadingCode** → `belongs_to :company`
- **MeterReading** → `has_many :meter_reading_codes`

### Validation
- **Uniqueness**: Code names must be unique within company scope
- **Paper Trail**: Full audit logging enabled
- **Cascade Rules**: Restrict deletion if codes are in use

---

## Implementation Workflow

### Phase 1: Setup & Configuration

#### Step 1: Access Administration Panel
- **URL**: `/meter_reading_codes`
- **Navigation**: Dashboard → System Info → "Meter Reading Codes"
- **Permissions**: Admin-level access required

#### Step 2: Define Code Categories
**Recommended Standard Codes:**
```
AMI         - Advanced Metering Infrastructure  
AMR         - Automated Meter Reading
MANUAL      - Manual field readings
DRIVE-BY    - Drive-by collection
SMART       - Smart meter readings  
WIRELESS    - IoT/wireless sensors
SELF        - Customer self-reporting
```

#### Step 3: Create Codes
- Click "Add New" 
- Enter **Name** (short identifier, e.g., "AMI")
- Enter **Description** (detailed explanation)
- Codes automatically scoped to current company

#### Step 4: Validate Setup
- Verify codes appear in reading entry forms
- Test with sample meter reading

### Phase 2: Daily Operations

#### Manual Reading Entry
1. **Individual Reading Entry**
   - **URL**: `/meter_readings/[id]/edit`
   - **Feature**: Checkboxes for multiple code selection
   - **Usage**: Manual tagging during reading entry/correction

2. **Bulk Reading Entry**
   - **URL**: `/meters/[id]/readings` (inline editing)
   - **Feature**: Quick code selection during rapid entry

3. **Initial Meter Setup**
   - **URL**: `/meters/[id]/enter_initial_readings`
   - **Feature**: Tag first reading when installing meters

#### Automated Import Integration
- **Stealth Reader**: Uses `raw_name` field to auto-assign codes
- **Quadlogic Import**: Loads company codes for processing
- **Custom Imports**: Can be enhanced to assign codes based on data patterns

### Phase 3: Monitoring & Analysis

#### Reading History Review
- **Location**: Meter readings table
- **Display**: Codes appear as bullet points alongside system flags
- **Audit**: Provides trail for billing accuracy verification

---

## User Interface Locations

### Primary Display: Reading History

#### URL Path
```
/meters/[meter_id]/readings
```

#### Navigation Path
1. Dashboard → Meters (or search for specific meter)
2. Click on Meter ID 
3. Click "Readings" tab/link

#### Column Layout
| Column | Content |
|--------|---------|
| Current Reading | End reading value |
| Date | Reading date |
| Prior Reading | Previous reading |
| Date | Previous date |
| Days | Days between readings |
| Usage | Consumption amount |
| **Codes/Addl.** | **📍 CODES APPEAR HERE** |
| Entered By | User who entered reading |
| Notes | Reading notes |

#### Display Format
**Location**: `/app/views/meter_readings/_readings.html.erb:84-92`

```erb
<div class="col-xs-<%= cols[8] %> row-cell textAlignRight">
  <ul>
    <% if r.is_high_flow %><li>High Flow</li><% end %>
    <% if r.estimated_reading %><li>Estimated</li><% end %>
    <% r.meter_reading_codes.order(:name).each do |code| %>
      <li><%= code.name %></li>
    <% end %>
  </ul>
</div>
```

#### Visual Example
```
┌─────────────────┬─────────┬─────────────────┬─────────┬──────┬──────┬─────────────┐
│ Current Reading │   Date  │ Prior Reading   │   Date  │ Days │ Usage│ Codes/Addl.│
├─────────────────┼─────────┼─────────────────┼─────────┼──────┼──────┼─────────────┤
│      12,450     │ 09/15/25│      12,200     │ 08/15/25│  31  │ 250  │ • High Flow │
│                 │         │                 │         │      │      │ • AMI       │
│                 │         │                 │         │      │      │ • SMART     │
├─────────────────┼─────────┼─────────────────┼─────────┼──────┼──────┼─────────────┤
│      12,200     │ 08/15/25│      11,950     │ 07/15/25│  31  │ 250  │ • Estimated │
│                 │         │                 │         │      │      │ • MANUAL    │
└─────────────────┴─────────┴─────────────────┴─────────┴──────┴──────┴─────────────┘
```

### Secondary Locations

#### Manual Entry Forms
- **Reading Edit**: `/meter_readings/[id]/edit`
- **Initial Setup**: `/meters/[id]/enter_initial_readings`
- **Quick Entry**: `/meters/[id]/readings` (inline)

#### Administrative Interface
- **Code Management**: `/meter_reading_codes`
- **System Info**: Dashboard → System Info (line 300)

---

## Code Usage & Methods

### Manual Reading Entry Integration

#### Individual Reading Forms
**Location**: `/app/views/meter_readings/_form.html.erb:73-87`
```erb
<% if @presenter.meter_reading_codes.length > 0 %>
  <tr>
    <td>Reading Codes</td>
    <td>
      <table>
        <% @presenter.meter_reading_codes.each do |code| %>
        <tr>
          <td><%= check_box_tag 'meter_reading[meter_reading_code_ids][]', 
                  code.id, @presenter.meter_reading.meter_reading_code_ids.include?(code.id) %></td>
          <td><%= code.name %></td>
        </tr>
        <% end %>
      </table>
    </td>
  </tr>
<% end %>
```

#### Bulk Entry Forms
**Location**: `/app/views/meters/enter_initial_readings.html.erb:70-79`
```erb
<b>Reading Codes</b>
<table>
  <% @meter_reading_codes.each do |code| %>
  <tr>
    <td><%= check_box_tag 'meter_reading_code_ids[]', code.id %></td>
    <td><%= code.name %></td>
  </tr>
  <% end %>
</table>
```

### Backend Service Integration

#### Meter Service Operations
**Location**: `/lib/services/meters/meter_service.rb:108-115`
```ruby
if params[:meter_reading_code_ids].present?
  params[:meter_reading_code_ids].each do |id|
    code = MeterReadingMeterReadingCode.new
    code.meter_reading_code_id = id
    code.meter_reading_id = meter_reading_id
    code.save!
  end
end
```

#### Reading Updates
**Location**: `/app/controllers/meter_readings_controller.rb:168`
```ruby
@meter_reading.attributes = { meter_reading_code_ids: [] }.merge(mr_opts)
```

### Automated Import Integration

#### Stealth Reader Import
**Location**: `/app/business_logic/data_imports/stealth_reader_import_file.rb:197-204`
```ruby
mrc = MeterReadingCode.where("company_id = ? and name = ?", 
      @company.id, import_record.raw_name).first
if !mrc.nil?
  mrmrc = MeterReadingMeterReadingCode.new()
  mrmrc.meter_reading_id = reading_id
  mrmrc.meter_reading_code_id = mrc.id
  mrmrc.save!
end
```

#### Quadlogic Import
**Location**: `/app/business_logic/data_imports/meter_quadlogic_import_file.rb:10`
```ruby
@meter_reading_codes = MeterReadingCode.where('company_id = ?', company_id)
```

### Special Features

#### Read Instructions Filter
**Location**: `/app/models/meter_reading.rb:305`
```ruby
def read_instructions
  mrc_list = self.meter_reading_codes.where("name like 'RI%'")
end
```

#### Background Job Processing
**Location**: `/app/business_logic/jobs/meters/use_readings_from_saved_document_job.rb:109`
```ruby
.includes(:meter, :customer, :meter_reading_codes)
```

---

## Active Company Examples

### Company 124: Consolidated Utilities, Inc ✅ **HIGHLY ACTIVE**

#### Usage Statistics
- **Recent Activity**: 2,311 readings tagged (March-September 2025)
- **Code Usage**: 4 distinct codes
- **Pattern**: Heavy automation with manual backup

#### Active Codes
| Code | Description | Usage Count | Percentage |
|------|-------------|-------------|------------|
| A | Allegro (AMR system) | 2,013 | 87.1% |
| M | Manual | 284 | 12.3% |
| G | 3G cellular | 13 | 0.6% |
| O | Octave | 1 | <0.1% |

#### Live Examples
**Recent readings you can view in UI:**

1. **Allegro Reading**
   - **URL**: `/meters/1307131/readings`
   - **Meter**: #114068731
   - **Date**: 09/11/2025
   - **Codes**: `• A`

2. **Manual Reading**
   - **URL**: `/meters/852573/readings`
   - **Meter**: #2307588
   - **Date**: 09/04/2025
   - **Consumption**: 155 units
   - **Codes**: `• M`

3. **High Volume Allegro**
   - **URL**: `/meters/1272939/readings`
   - **Meter**: #1843754
   - **Date**: 09/04/2025
   - **Consumption**: 139,559 units
   - **Codes**: `• A`

### Company 1624: City of Big Lake ✅ **ACTIVE**

#### Usage Statistics
- **Recent Activity**: 289 readings tagged (March-September 2025)
- **Code Usage**: Primarily "MANUAL" code
- **Pattern**: Manual reading workflow

#### Live Examples

1. **Standard Manual**
   - **URL**: `/meters/1185745/readings`
   - **Meter**: #22T784924
   - **Date**: 09/09/2025
   - **Codes**: `• MANUAL`

2. **High Consumption**
   - **URL**: `/meters/1249280/readings`
   - **Meter**: #242146882
   - **Date**: 09/09/2025
   - **Consumption**: 7,700 units
   - **Codes**: `• MANUAL`

3. **Regular Service**
   - **URL**: `/meters/1184660/readings`
   - **Meter**: #1065223
   - **Date**: 09/09/2025
   - **Consumption**: 30 units
   - **Codes**: `• MANUAL`

### Company 112: HMUA ⚠️ **HISTORICAL USAGE ONLY**

#### Usage Statistics
- **Total Historical**: 2,950 readings with codes
- **Period**: 2014 data only
- **Status**: No recent usage (inactive feature)

#### Historical Examples (2014)

1. **Multiple Codes**
   - **URL**: `/meters/74302/readings`
   - **Meter**: #35317694
   - **Account**: 006283001
   - **Codes**: `• S • SC-01`

2. **Standard Code**
   - **URL**: `/meters/74280/readings`
   - **Meter**: #39970390
   - **Account**: 005830001
   - **Codes**: `• N`

### Companies with Template Setup (Unused)

**Similar Configuration Pattern** (7 codes each):
- **Company 857** - AMI, AMR, MANUAL, SELF, SMART, WIRELESS
- **Company 1641** - AMI, MANUAL, SELF, SMART, WIRELESS  
- **Company 1689** - AMI, MANUAL, SELF, SMART, WIRELESS
- **Company 1829** - AMI, AMR, MANUAL, SELF, SMART, WIRELESS
- **Company 1830** - AMI, AMR, MANUAL, SELF, SMART, WIRELESS
- **Company 1831** - AMI, AMR, MANUAL, SELF, SMART, WIRELESS
- **Company 1803** - AMI, AMR, MANUAL, SELF, SMART, WIRELESS, DRIVE-BY

**Status**: All configured but **0% usage** (no readings tagged)

---

## Reporting & Export Integration

### Current Visibility

#### Where Codes ARE Displayed
✅ **Reading History Views**
- Location: `/meters/[id]/readings`
- Display: Bullet points in "Codes/Addl." column
- Context: Alongside "High Flow", "Estimated" flags

✅ **Manual Entry Forms**
- Reading edit forms show checkboxes for code selection
- Initial meter setup includes code options
- Bulk entry interfaces include code selection

✅ **Administrative Interfaces**
- Code management at `/meter_reading_codes`
- System info panel includes configuration link

✅ **Background Processing**
- Job processing includes codes for performance optimization
- Import systems can auto-assign codes

#### Where Codes Are NOT Displayed
❌ **Standard Exports**
- Meter reading exports do not include code information
- CSV exports missing code columns
- Data export files lack code integration

❌ **Reports**
- Consumption reports don't break down by reading method
- No code-based filtering in standard reports
- Quality analysis reports don't leverage code data

❌ **Customer-Facing**
- Customer portal doesn't show reading codes
- Bills/statements don't include reading method context
- Self-service portals lack code visibility

❌ **Operational Dashboards**
- No code-based operational metrics
- Missing reading method efficiency analysis
- Quality control dashboards don't use codes

### Export Enhancement Opportunities

#### Current Export Structure
**File**: `/lib/data_export_meter_readings_file.rb`
**Current Fields**: Reading dates, consumption, meter info, customer data
**Missing**: Meter reading codes

#### Potential Enhancement
```ruby
def get_entity_hash(meter_reading_id)
  # Current code exports basic meter reading data
  # Enhancement: Add meter_reading_codes to the hash
  {
    meter_reading: meter_reading,
    meter: meter,
    parcel: parcel,
    customer: customer,
    # ADD: reading_codes: meter_reading.meter_reading_codes.pluck(:name).join(',')
  }
end
```

#### Reporting Integration Points
1. **Consumption Reports**: Add code breakdown columns
2. **Quality Reports**: Reading method accuracy metrics
3. **Operational Reports**: Collection method efficiency
4. **Export Files**: Include codes in CSV/data exports

---

## Current Usage Analysis

### Usage Statistics (Last 6 Months)

| Company | Name | Readings Tagged | Last Usage | Primary Codes |
|---------|------|----------------|------------|---------------|
| 124 | Consolidated Utilities | 2,311 | 2025-09-16 | A, M, G, O |
| 1624 | City of Big Lake | 289 | 2025-09-10 | MANUAL |
| 1313 | Southwest Regional | 46 | 2025-08-22 | AMR, Manual |
| 677 | Walton Public Service | 2 | 2025-09-15 | Mixed |
| 1792 | Rural Water District #6 | 2 | 2025-08-09 | Single code |
| 133 | Town of Altha | 1 | 2025-07-11 | Single code |
| 1784 | City of Lafayette | 1 | 2025-05-27 | Single code |

### Usage Patterns

#### Successful Implementations
1. **Simple Naming**: "A", "M", "G" vs complex descriptive names
2. **Clear Distinction**: Each code represents distinct collection method
3. **Automated Integration**: Import systems auto-assign codes
4. **Consistent Application**: Regular staff usage

#### Common Challenges
1. **User Adoption**: Many configured companies show 0% usage
2. **Training Gap**: Staff unclear on when/how to use codes
3. **Workflow Integration**: Codes feel like extra step
4. **Value Perception**: Benefits not immediately apparent

#### Template vs. Custom Approach
- **Template Setup**: Standard 7-code configuration (low adoption)
- **Custom Setup**: Company-specific simplified codes (higher adoption)
- **Success Factor**: Codes match actual operational workflow

---

## Implementation Recommendations

### For New Companies

#### Phase 1: Pilot Implementation
1. **Start Simple**: Begin with 3 codes maximum
   - AUTO (any automated reading)
   - MANUAL (field readings)
   - ESTIMATED (estimated readings)

2. **Staff Training**: Focus on when/why to use each code
3. **Monitor Usage**: Track adoption rates monthly
4. **Gather Feedback**: Understand user pain points

#### Phase 2: Expansion
1. **Assess Value**: Determine if codes provide operational value
2. **Add Gradually**: Introduce additional codes based on need
3. **Automate First**: Integrate with import processes
4. **Report Creation**: Build operational reports using codes

### For Existing Companies (like Company 1803)

#### Assessment Phase
1. **Review Current Setup**: Evaluate existing 7-code configuration
2. **Analyze Workflow**: Match codes to actual reading processes
3. **Simplify**: Consider reducing to 3-4 primary codes
4. **Staff Input**: Gather user feedback on current configuration

#### Implementation Phase
1. **Import Integration**: Connect codes with automated imports first
2. **Training Program**: Provide clear usage guidelines
3. **Gradual Rollout**: Start with automated tagging, add manual later
4. **Success Metrics**: Track usage adoption and operational value

#### Optimization Phase
1. **Report Development**: Create code-based operational reports
2. **Export Enhancement**: Add codes to standard data exports
3. **Quality Analysis**: Use codes for reading accuracy metrics
4. **Continuous Improvement**: Refine based on operational insights

### Technical Implementation Steps

#### Database Configuration
1. **Company Setup**: Ensure codes exist in `meter_reading_codes`
2. **Import Enhancement**: Modify import processes to assign codes
3. **Export Enhancement**: Add codes to export file generation
4. **Report Integration**: Include codes in report queries

#### User Interface Enhancements
1. **Form Optimization**: Ensure code selection is intuitive
2. **Display Enhancement**: Make codes more prominent in reading history
3. **Reporting UI**: Add code-based filtering to report interfaces
4. **Dashboard Integration**: Include code metrics in operational dashboards

### Success Metrics

#### Adoption Metrics
- Percentage of readings with assigned codes
- Number of active users assigning codes
- Code usage distribution across reading methods

#### Operational Metrics
- Reading accuracy by collection method
- Processing time by reading type
- Quality issues by code category

#### Business Value Metrics
- Operational efficiency improvements
- Data quality enhancements
- Billing accuracy improvements

---

## Conclusion

Meter Reading Codes provide a powerful framework for operational insight and data quality tracking in the Muni Billing system. While the infrastructure is robust and well-designed, success depends heavily on:

1. **Thoughtful Implementation**: Match codes to actual operational workflows
2. **User Adoption**: Ensure staff understand value and usage
3. **Integration**: Connect codes with automated processes
4. **Reporting**: Leverage codes for operational insights

Companies that implement simple, meaningful codes with proper staff training show high adoption rates and operational value. The key is starting simple and expanding based on demonstrated value rather than implementing complex configurations upfront.

The system is ready for enhanced reporting and export integration, representing significant opportunities to increase the visibility and value of meter reading code data across the entire platform.

---

*Document compiled from system analysis conducted September 2025*
*Source data includes database analysis, code review, and active usage examples*