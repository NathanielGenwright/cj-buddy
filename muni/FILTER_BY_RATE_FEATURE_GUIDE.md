# Filter By Rate Feature - Comprehensive Guide

## Overview
The "Filter By Rate" feature in the Muni Billing system controls which billing types are available for selection when creating bills, adjustments, or payments for specific customers. This feature enables billing types to be context-aware, showing only billing types that are relevant to a customer's rate structure while always including universal billing types.

## Technical Implementation

### Database Field Details
- **Field**: `filter_by_rate` (boolean, default: false)
- **Location**: `billing_types` table, line 14 in structure.sql
- **UI Label**: "Filter By Rate" (column 26 in billing types index)
- **Export Field**: `filter_by_rate` maps directly to `billing_type.filter_by_rate`

### Core Files
- **Main Logic**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/app/models/billing_type.rb:89-95`
- **Helper Method**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/app/models/billing_type.rb:138-152`
- **UI Display**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/app/views/billing_types/index.html.erb:26`
- **Form Control**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/app/views/billing_types/_billing_type_record.html.erb:15`
- **Data Export**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/lib/data_export_billing_types_file.rb:39`

## How The Filtering Logic Works

### 1. Core Filtering Query
```ruby
def self.filtered_for_customer(customer_id, company_id)
  where(company_id: company_id, is_display: true).where(
    BillingType[:id].in(billing_type_ids_for_filtered_for_customer(customer_id, company_id)).or(
      BillingType[:filter_by_rate].eq(false)
    )
  ).order(BillingType[:filter_by_rate].desc, :name)
end
```

### 2. Rate-Based Billing Type Discovery
```ruby
def self.billing_type_ids_for_filtered_for_customer(customer_id, company_id)
  result = Customer
    .joins(parcels: :rates)
    .where(id: customer_id, company_id: company_id)
    .select(
      'GROUP_CONCAT(DISTINCT(rates.billing_type_id)) AS ids1, ' \
      'GROUP_CONCAT(DISTINCT(rates.late_fee_billing_type_id)) AS ids2'
    )
    .group(:company_id)
    
  return [] if result.first.nil?
  
  (result.first[:ids1].split(',') + result.first[:ids2].split(',')).sort.uniq
end
```

### 3. Key Filtering Rules
**The filtering logic works as follows:**

1. **Always Include**: Billing types with `filter_by_rate = false` (universal billing types)
2. **Conditionally Include**: Billing types with `filter_by_rate = true` only if:
   - The customer has a rate that uses this billing type (`rates.billing_type_id`)
   - OR the customer has a rate with late fees using this billing type (`rates.late_fee_billing_type_id`)
3. **Ordering**: Results are ordered by `filter_by_rate` DESC, then by `name` ASC

## Usage Context

### Where This Filtering is Applied

1. **Miscellaneous Bills Controller** (`/Users/munin8/_myprojects/muni/muni-billing/legacy/app/controllers/miscellaneous_bills_controller.rb:26`)
   ```ruby
   @billing_types = BillingType.filtered_for_customer(@customer.id, current_company_id)
   ```

2. **Account Adjustments Controller** (`/Users/munin8/_myprojects/muni/muni-billing/legacy/app/controllers/account_adjustments_controller.rb:30`)
   ```ruby
   @billing_types = BillingType.filtered_for_customer(@customer.id, current_company_id)
   ```

3. **Payment Billing Type Lists** (`/Users/munin8/_myprojects/muni/muni-billing/legacy/lib/presenters/payments/btl_factory.rb:39-41`)
   ```ruby
   filtered_billing_types = BillingType.filtered_for_customer(
     build_opts[:customer].id,
     build_opts[:current_company].id
   ).to_a
   ```

## Detailed Examples

### Example 1: Residential Customer Water Service

**Setup:**
- Customer has residential parcel with "Residential Water" rate
- Rate uses billing type "Water Service" (ID: 5, `filter_by_rate = true`)
- Rate has late fees using "Late Fee" billing type (ID: 8, `filter_by_rate = true`)
- System also has "Administrative Fee" billing type (ID: 12, `filter_by_rate = false`)

**Available Billing Types for This Customer:**
```
✓ Water Service     (ID: 5)  - Included: Customer has rate using this billing type
✓ Late Fee          (ID: 8)  - Included: Customer has rate with late fees using this
✓ Administrative Fee (ID: 12) - Included: filter_by_rate = false (universal)
✗ Commercial Tax    (ID: 15) - Excluded: filter_by_rate = true but customer has no rates using it
✗ Industrial Surcharge (ID: 18) - Excluded: filter_by_rate = true but customer has no rates using it
```

### Example 2: Multi-Service Commercial Customer

**Setup:**
- Customer has commercial parcel with multiple rates:
  - "Commercial Water" rate → billing type "Water Service" (ID: 5, `filter_by_rate = true`)
  - "Commercial Sewer" rate → billing type "Sewer Service" (ID: 7, `filter_by_rate = true`)
  - "Storm Water" rate → billing type "Storm Water" (ID: 9, `filter_by_rate = true`)
- Universal billing types available to all customers

**Available Billing Types for This Customer:**
```
✓ Water Service      (ID: 5)  - Included: Has Commercial Water rate
✓ Sewer Service      (ID: 7)  - Included: Has Commercial Sewer rate  
✓ Storm Water        (ID: 9)  - Included: Has Storm Water rate
✓ Administrative Fee (ID: 12) - Included: filter_by_rate = false
✓ Processing Fee     (ID: 13) - Included: filter_by_rate = false
✗ Residential Tax    (ID: 15) - Excluded: filter_by_rate = true, no applicable rates
✗ Industrial Waste   (ID: 20) - Excluded: filter_by_rate = true, no applicable rates
```

### Example 3: Customer with No Active Rates

**Setup:**
- Customer exists but has no parcels or no active rates
- Only universal billing types should be available

**SQL Result Without Rates:**
```sql
WHERE billing_types.company_id = 1 
  AND billing_types.is_display = TRUE 
  AND (1=0 OR billing_types.filter_by_rate = FALSE)
ORDER BY billing_types.filter_by_rate DESC, billing_types.name ASC
```

**Available Billing Types:**
```
✓ Administrative Fee (ID: 12) - Included: filter_by_rate = false
✓ Processing Fee     (ID: 13) - Included: filter_by_rate = false
✗ Water Service      (ID: 5)  - Excluded: filter_by_rate = true, no rates
✗ Sewer Service      (ID: 7)  - Excluded: filter_by_rate = true, no rates
```

### Example 4: Industrial Customer with Special Rates

**Setup:**
- Customer has industrial parcel with specialized rates:
  - "Industrial Water" rate → billing type "Industrial Water" (ID: 25, `filter_by_rate = true`)
  - "Hazmat Disposal" rate → billing type "Hazmat Fee" (ID: 28, `filter_by_rate = true`)
  - Late fees use "Industrial Late Fee" billing type (ID: 30, `filter_by_rate = true`)

**Available Billing Types:**
```
✓ Industrial Water    (ID: 25) - Included: Has Industrial Water rate
✓ Hazmat Fee         (ID: 28) - Included: Has Hazmat Disposal rate
✓ Industrial Late Fee (ID: 30) - Included: Late fee billing type from rates
✓ Administrative Fee  (ID: 12) - Included: filter_by_rate = false
✗ Water Service      (ID: 5)  - Excluded: filter_by_rate = true, not in customer's rates
✗ Residential Tax    (ID: 15) - Excluded: filter_by_rate = true, not in customer's rates
```

## Business Logic and Benefits

### 1. **Context-Aware Billing**
- Staff only see billing types relevant to the customer's service configuration
- Reduces errors from selecting inappropriate billing types
- Streamlines billing workflows by eliminating irrelevant options

### 2. **Flexible Service Models**
- Supports different customer types (residential, commercial, industrial)
- Enables specialized billing types for specific rate structures
- Maintains universal billing types for common fees and adjustments

### 3. **Administrative Efficiency**
- **Shorter Lists**: Staff deal with smaller, relevant billing type lists
- **Faster Processing**: Quicker selection of appropriate billing types
- **Error Prevention**: Impossible to select billing types not related to customer's services

### 4. **System Scalability**
- Large utilities can have hundreds of billing types
- Filtering keeps interface manageable for each customer type
- Easy to add new specialized billing types without cluttering all customer views

## Configuration Scenarios

### Scenario 1: Universal Billing Types
**When to use `filter_by_rate = false`:**
- Administrative fees that apply to all customers
- Processing charges that can be added to any account
- Penalty fees that might apply regardless of service type
- Adjustment types for credits or corrections

**Examples:**
- "Administrative Fee" - applies to all customers
- "NSF Fee" - insufficient funds penalty for any customer
- "Account Credit" - credits can be applied to any account type

### Scenario 2: Service-Specific Billing Types
**When to use `filter_by_rate = true`:**
- Billing types tied to specific utility services
- Specialized fees for particular customer classes
- Service-specific taxes or surcharges
- Industry-specific environmental fees

**Examples:**
- "Residential Water Tax" - only for residential water customers
- "Commercial Sewer Surcharge" - only for commercial customers with sewer service
- "Industrial Waste Fee" - only for industrial customers with waste disposal rates

## Implementation Examples

### Example 1: Setting Up Residential vs Commercial Billing Types

**Step 1: Create Service-Specific Billing Types**
```
Residential Water Service (filter_by_rate = true)
Commercial Water Service  (filter_by_rate = true)
Industrial Water Service  (filter_by_rate = true)
```

**Step 2: Create Universal Billing Types**
```
Administrative Fee (filter_by_rate = false)
NSF Fee           (filter_by_rate = false)
Account Credit    (filter_by_rate = false)
```

**Step 3: Configure Rates**
- Residential Water Rate → uses "Residential Water Service" billing type
- Commercial Water Rate → uses "Commercial Water Service" billing type
- Industrial Water Rate → uses "Industrial Water Service" billing type

**Result:**
- Residential customers only see: Residential Water Service + Universal types
- Commercial customers only see: Commercial Water Service + Universal types
- Industrial customers only see: Industrial Water Service + Universal types

### Example 2: Multi-Utility Setup (Water + Electric)

**Service-Specific Billing Types (`filter_by_rate = true`):**
```
Water Service Base Charge
Water Service Usage Charge
Electric Service Base Charge
Electric Service Usage Charge
Water Connection Fee
Electric Connection Fee
```

**Universal Billing Types (`filter_by_rate = false`):**
```
Late Payment Fee
Administrative Fee
Returned Check Fee
Service Credit
```

**Customer Results:**
- Water-only customer: Water billing types + Universal types
- Electric-only customer: Electric billing types + Universal types  
- Dual-service customer: Water + Electric billing types + Universal types

## Technical Implementation Notes

### 1. **Database Relationships**
- Customers → Parcels → Rates → Billing Types
- The filtering follows this relationship chain to determine relevance
- Both primary billing types and late fee billing types are included

### 2. **Performance Considerations**
- Query uses JOINs across Customer → Parcel → Rate relationships
- GROUP_CONCAT aggregates billing type IDs efficiently
- Results are cached and reused within the same request context

### 3. **Ordering Strategy**
- `filter_by_rate DESC` puts customer-specific types first
- `name ASC` provides alphabetical ordering within each group
- This makes the most relevant billing types appear at the top of lists

### 4. **Error Handling**
- Returns empty array if customer has no rates
- Gracefully handles customers without parcels
- Always includes universal billing types as fallback

## Configuration Steps

1. **Navigate to**: `/billingtypes` in the admin interface
2. **Identify**: Billing types that should be service-specific
3. **Check**: The "Filter By Rate" checkbox for service-specific billing types
4. **Leave Unchecked**: Universal billing types that apply to all customers
5. **Test**: Create miscellaneous bills for different customer types to verify filtering

## Benefits and Limitations

### **Benefits:**
- **Improved User Experience**: Staff see only relevant billing types
- **Error Reduction**: Impossible to select inappropriate billing types
- **Scalability**: Supports complex multi-service utility operations
- **Flexibility**: Easy to configure which billing types are universal vs. service-specific

### **Limitations:**
- **Setup Complexity**: Requires careful configuration of rates and billing types
- **Maintenance Overhead**: New rates must properly reference appropriate billing types
- **Training Required**: Staff need to understand why billing type lists vary by customer

### **Best Practices:**
- Use `filter_by_rate = false` for truly universal fees and adjustments
- Use `filter_by_rate = true` for service-specific charges and taxes
- Document billing type filtering rules for customer service training
- Test filtering behavior when adding new rates or billing types

## Code References

- **Main filtering method**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/app/models/billing_type.rb:89-95`
- **Billing type discovery**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/app/models/billing_type.rb:138-152`
- **Miscellaneous bills usage**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/app/controllers/miscellaneous_bills_controller.rb:26`
- **Account adjustments usage**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/app/controllers/account_adjustments_controller.rb:30`
- **Payment processing usage**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/lib/presenters/payments/btl_factory.rb:39-41`
- **Database schema**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/db/structure.sql:14` (filter_by_rate field)
- **UI configuration**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/app/views/billing_types/_billing_type_record.html.erb:15`

This feature enables sophisticated billing type management in complex utility environments while maintaining simplicity for end users through intelligent context-aware filtering.