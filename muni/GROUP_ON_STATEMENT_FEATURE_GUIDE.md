# Group On Statement Feature - Comprehensive Guide

## Overview
The "Group On Statement" feature in the Muni Billing system consolidates multiple bills of the same billing type into a single line item on customer statements. This feature reduces statement complexity and improves customer readability while maintaining complete data integrity for accounting and regulatory purposes.

## Technical Implementation

### Database Field Details
- **Field**: `is_tax` (boolean, default: false)
- **Location**: `billing_types` table, line 15 in structure.sql
- **UI Label**: "Group On Statement" (column 27 in billing types index)
- **Export Field**: `group_on_statement` maps to `billing_type.is_tax`

### Core Files
- **Main Logic**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/lib/business_logic/bills/printing.rb:81-109`
- **UI Display**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/app/views/billing_types/index.html.erb:27`
- **Form Control**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/app/views/billing_types/_billing_type_record.html.erb:16`
- **Data Export**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/lib/data_export_billing_types_file.rb:40`

## How The Grouping Logic Works

### 1. Bill Separation
```ruby
# Separate bills into two categories
bills = ungrouped_bills.select { |a| !a.billing_type.is_tax }      # Regular bills
tax_bills = ungrouped_bills.select { |a| a.billing_type.is_tax }   # Bills to be grouped
```

### 2. Consolidation Process
```ruby
# Group bills by billing_type_id for printing
last_tax_billing_type_id = 0
temp_bill = nil
tax_bills.each do |b|
  if last_tax_billing_type_id != b.billing_type_id
    # New billing type - save previous group and start new one
    bills << temp_bill if temp_bill.present?
    temp_bill = b
    last_tax_billing_type_id = b.billing_type_id
  else
    # Same billing_type_id = combine into existing group
    temp_bill.amount += b.amount         # Consolidate amounts
    temp_bill.consumption += b.consumption  # Consolidate consumption
  end
end
```

### 3. Key Grouping Rule
**Bills are grouped by `billing_type_id` ONLY when `is_tax = true`**
- Same `billing_type_id` + `is_tax = true` = Combined into one line
- Different `billing_type_id` = Separate lines (even if both have `is_tax = true`)
- `is_tax = false` = Always separate lines regardless of billing type

## Detailed Examples

### Example 1: Municipal Utility Tax Scenario

**BEFORE Grouping (is_tax = false):**
```
Customer Statement - Account #12345
=====================================
Water Service         $45.00    1,500 gal
Municipal Tax         $3.38     
State Tax             $2.25     
Federal Surcharge     $1.12     
Municipal Tax         $1.69     (additional charge)
State Tax             $0.75     (additional charge)
=====================================
Total:                $54.19
```

**AFTER Grouping (is_tax = true):**
```
Customer Statement - Account #12345
=====================================
Water Service         $45.00    1,500 gal
Municipal Tax         $5.07     (3.38 + 1.69)
State Tax             $3.00     (2.25 + 0.75)
Federal Surcharge     $1.12     
=====================================
Total:                $54.19
```

### Example 2: Service Fee Consolidation

**BEFORE Grouping:**
```
Monthly Statement
==========================================
Base Water Charge       $32.50   
Service Fee - Maintenance $5.00   
Service Fee - Admin      $3.00   
Service Fee - Processing  $2.50   
Sewer Charge            $18.75   
Service Fee - Billing    $1.50   
==========================================
Total:                  $63.25
```

**AFTER Grouping (Service Fee billing type has is_tax = true):**
```
Monthly Statement
==========================================
Base Water Charge       $32.50   
Service Fees            $12.00   (5.00+3.00+2.50+1.50)
Sewer Charge            $18.75   
==========================================
Total:                  $63.25
```

### Example 3: Multiple Rates, Same Billing Type

**Individual Bills in Database:**
- Rate A: Water Service - Billing Type ID: 5 (`is_tax = true`) - $25.00, 500 gal
- Rate B: Water Service - Billing Type ID: 5 (`is_tax = true`) - $18.50, 300 gal  
- Rate C: Water Service - Billing Type ID: 5 (`is_tax = true`) - $12.75, 200 gal

**BEFORE Grouping (Individual Bills):**
```
Customer #12345 Statement
============================
Water Service (Rate A)    $25.00    500 gal
Water Service (Rate B)    $18.50    300 gal  
Water Service (Rate C)    $12.75    200 gal
============================
Total:                    $56.25   1000 gal
```

**AFTER Grouping (Same billing_type_id = 5):**
```
Customer #12345 Statement  
============================
Water Service             $56.25   1000 gal
============================
Total:                    $56.25   1000 gal
```

### Example 4: Mixed Billing Types with Grouping

**Bills:**
- Rate A: Billing Type "Water Service" (ID: 5, `is_tax = true`) - $25.00
- Rate B: Billing Type "Water Service" (ID: 5, `is_tax = true`) - $18.50  
- Rate C: Billing Type "Sewer Service" (ID: 8, `is_tax = true`) - $15.00
- Rate D: Billing Type "Storm Water" (ID: 12, `is_tax = false`) - $8.00

**Statement Display:**
```
Water Service    $43.50  (Rate A + Rate B grouped by billing_type_id = 5)
Sewer Service    $15.00  (Rate C separate - different billing_type_id = 8)
Storm Water      $8.00   (Rate D separate - is_tax = false)
```

### Example 5: Complex Multi-Rate Scenario

**Individual Bills in Database:**
- Billing Type: "Environmental Fee" (ID: 15, is_tax = true)
  - Bill #1: $2.15 (Base rate)
  - Bill #2: $0.85 (Peak usage surcharge)  
  - Bill #3: $1.25 (Seasonal adjustment)
  - Bill #4: $0.45 (Regulatory fee)

**Statement Display:**
```
Environmental Fee        $4.70    (2.15+0.85+1.25+0.45)
```

## Payment Grouping

The same logic applies to payments and credits:

```ruby
if company.group_credit_payments_on_statement?
  # Group credit payments for billing types with is_tax = true
  credit_payments_to_group = all_payments.select do |payment|
    payment.billing_type.present? && 
    payment.billing_type.is_tax && 
    payment.payment_type.name == PaymentType::CREDIT
  end
  
  # Apply same consolidation logic to payments
end
```

## Business Benefits

### 1. **Statement Clarity**
- Reduces 15+ line items to 3-5 summary lines
- Eliminates customer confusion about duplicate charges
- Creates cleaner, more professional-looking statements

### 2. **Customer Service Efficiency**
- Fewer calls asking "Why am I charged tax twice?"
- Simplified explanation of consolidated charges
- Easier to identify actual billing issues vs. display confusion

### 3. **Regulatory Compliance**
- Maintains detailed transaction records for auditing
- Presents simplified view for customer understanding
- Supports various tax and fee structures

### 4. **Administrative Control**
- Configure per billing type (some grouped, others detailed)
- Consistent with accounting requirements
- Flexible for different service categories

## Technical Implementation Details

### 1. **Database Integrity**
- Individual bills remain separate in the database
- Grouping only affects statement presentation
- Full audit trail preserved for accounting

### 2. **Sorting and Organization**
- Grouped bills sorted by: `parcel_id`, `sort_order`, `bill_date`
- Maintains chronological and logical order
- Consistent presentation across all statements

### 3. **Company-Specific Logic**
- Special handling for certain companies (e.g., Redmond)
- Configurable grouping rules per organization
- Support for various municipal billing patterns

### 4. **Performance Considerations**
- Grouping happens during statement generation
- Minimal impact on database queries
- Efficient consolidation algorithm

## Configuration Steps

1. **Navigate to**: `/billingtypes` in the admin interface
2. **Locate**: The billing type you want to group
3. **Check**: The "Group On Statement" checkbox (is_tax field)
4. **Save**: Changes apply to future statement generations
5. **Test**: Generate sample statements to verify grouping

## Important Considerations

### **Benefits:**
- Simplifies statements when multiple rates apply to same service
- Reduces customer confusion about duplicate-looking charges
- Clean presentation for tiered rate structures
- Professional appearance for municipal billing

### **Limitations:**
- Customers can't see individual rate breakdowns on statements
- Rate-specific descriptions, tiers, etc. are not visible to customers
- May require explanation if customers ask about rate details
- Customer service needs access to detailed bill records for inquiries

### **Best Practices:**
- Use for similar charges that customers expect to see consolidated
- Avoid grouping conceptually different services
- Document which billing types use grouping for customer service training
- Consider customer communication needs before enabling

## Code References

- **Main grouping logic**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/lib/business_logic/bills/printing.rb:92-103`
- **Bill separation**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/lib/business_logic/bills/printing.rb:81-86`
- **Payment grouping**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/lib/business_logic/bills/printing.rb:116-149`
- **Database schema**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/db/structure.sql:15` (is_tax field)
- **UI configuration**: `/Users/munin8/_myprojects/muni/muni-billing/legacy/app/views/billing_types/_billing_type_record.html.erb:16`

This feature significantly improves customer statement readability while maintaining complete data integrity for accounting and regulatory purposes. The grouping occurs purely at the presentation layer, ensuring that all underlying billing data remains intact and auditable.