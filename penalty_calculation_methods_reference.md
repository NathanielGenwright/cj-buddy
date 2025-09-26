# PENALTY CALCULATION METHODS - TECHNICAL REFERENCE

## 📚 **COMPLETE METHOD INVENTORY**

### **Method #1: penalty_print_total_bills**
**Location**: `deposit_charges.rb:157`, `email_manager.rb:255`  
**Trigger**: `company.penalty_print_total_bills = 1`  
**Formula**: 
```ruby
penalty_due = total_due + (penalty_bill_total * company.penalty_print_percent).round(2)
```
**Beach City Status**: DISABLED (flag = 0)

---

### **Method #2: penalty_print_total_balance**  
**Location**: `deposit_charges.rb:159`, `email_manager.rb:257`  
**Trigger**: `company.penalty_print_total_balance = 1`  
**Formula**:
```ruby
penalty_due = total_due + (total_due * company.penalty_print_percent).round(2)  
```
**Beach City Status**: DISABLED (flag = 0)

---

### **Method #3: Default/Individual Penalties**
**Location**: `deposit_charges.rb:161`, `email_manager.rb:259`  
**Trigger**: Both above methods disabled  
**Formula**:
```ruby
penalty_due = total_due + penalty_amount
```
**Beach City Status**: ACTIVE ✅

---

### **Method #4: PrintableInvoiceDecorator**
**Location**: `printable_invoice_decorator.rb:23`  
**Used For**: Invoice processing/export  
**Formula**:
```ruby
if company.penalty_print_total_bills?
  total_due + (total_billed * company.penalty_print_percent).round(2)
elsif company.penalty_print_total_balance?
  total_due + (total_due * company.penalty_print_percent).round(2)
else
  0  # Returns 0 when flags disabled
end
```
**Beach City Result**: 0

---

### **Method #5: Individual Bill Calculation**
**Location**: `bill_lib.rb:177`, `customers_controller.rb:868`  
**Used For**: Per-bill penalty calculation  
**Formula**:
```ruby
if rate.include_balance_in_penalty
  penalty_due_amount = ((grand_total + customer.balance_current) * rate.penalty_percentage) + rate.penalty_amount
else
  penalty_due_amount = (grand_total * rate.penalty_percentage) + rate.penalty_amount
end
```
**Beach City Result**: Individual penalties ($35.84 total)

---

## 🔧 **CALCULATION RESULTS FOR CUSTOMER 3178854**

| Method | Expected Result | Notes |
|--------|----------------|-------|
| Method #1 | N/A | Disabled for Beach City |
| Method #2 | N/A | Disabled for Beach City |
| Method #3 | **$571.36** | Should be used ✅ |
| Method #4 | $0 | Invoice processing |
| Method #5 | $35.84 | Individual penalties only |
| **ACTUAL** | **$838.29** | ❌ UNEXPLAINED |

---

## 🧮 **STEP-BY-STEP METHOD #3 CALCULATION**

### **Customer Data:**
```
Customer Balance: $296.59
New Bills Total: $238.93  
Total Due: $535.52
```

### **Individual Penalty Calculation:**
```ruby
# Each bill: amount × 0.15 (since include_balance_in_penalty = 0)
Bill 168604424: $155.80 × 0.15 = $23.37
Bill 168604425: $4.84   × 0.15 = $0.73  
Bill 168604426: $6.24   × 0.15 = $0.94
Bill 168604423: $28.69  × 0.15 = $4.30
Bill 168604422: $11.22  × 0.15 = $1.68
Bill 168604421: $32.14  × 0.15 = $4.82
Total penalty_amount: $35.84
```

### **Final Penalty_Due:**
```ruby
penalty_due = total_due + penalty_amount
penalty_due = $535.52 + $35.84 = $571.36
```

---

## 🔍 **CODE LOCATIONS BY FILE**

### **Core Statement Generation:**
- `lib/services/bills/statement_data/deposit_charges.rb:156-162`
- `lib/services/bills/email_manager.rb:253-261`

### **Individual Bill Processing:**
- `lib/bills/bill_calculation_manager.rb:687-691`
- `lib/bill_lib.rb:172-194`
- `app/controllers/customers_controller.rb:855-872`

### **Invoice Processing:**
- `app/jobs/accounting/document_processors/printable_invoice_decorator.rb:23-31`

### **Print Helpers:**
- `lib/print_helper_common.rb:7-16`
- `lib/print_helper.rb`

### **Export Utilities:**
- `lib/single_bill_export_array.rb`
- `lib/view_objects/email/usage_bill_data.rb`

---

## 🚦 **CONFIGURATION FLAGS REFERENCE**

### **Company Level (companies table):**
```sql
penalty_print_total_bills: 0/1
penalty_print_total_balance: 0/1  
penalty_print_percent: decimal(16,6)
```

### **Rate Level (rates table):**
```sql
penalty_percentage: decimal(16,6)  -- Usually 0.15 (15%)
penalty_amount: decimal(16,6)      -- Usually 0.00
use_penalty: 0/1                   -- Enable/disable penalties
include_balance_in_penalty: 0/1    -- Include current balance in penalty calc
```

### **Customer Level (customers table):**
```sql
penalty_waived: 0/1                -- Override to disable penalties
```

### **Bill Level (bills table):**
```sql
penalty_amount: decimal(16,2)      -- Calculated penalty for this bill
penalty_applied: 0/1               -- Whether penalty has been applied
penalty_date: date                 -- When penalty becomes effective
```

---

## 🧪 **TESTING SCENARIOS**

### **Method #3 Test Case:**
```ruby
# Given
customer_balance = 296.59
bill_amounts = [155.80, 4.84, 6.24, 28.69, 11.22, 32.14]
penalty_percentage = 0.15

# Calculate individual penalties
individual_penalties = bill_amounts.map { |amount| amount * penalty_percentage }
total_penalties = individual_penalties.sum  # 35.84

# Calculate penalty_due
total_due = customer_balance + bill_amounts.sum  # 535.52
penalty_due = total_due + total_penalties        # 571.36

# Expected: 571.36
# Actual: 838.29
# Gap: 266.93
```

---

## 🔧 **DEBUGGING TOOLS**

### **Database Queries:**
```sql
-- Check company penalty settings
SELECT penalty_print_total_bills, penalty_print_total_balance, penalty_print_percent 
FROM companies WHERE id = 1720;

-- Check rate penalty settings  
SELECT penalty_percentage, penalty_amount, use_penalty, include_balance_in_penalty
FROM rates WHERE id IN (25428, 25448, 25456, 25436, 25450, 25447);

-- Check customer penalty status
SELECT penalty_waived FROM customers WHERE id = 3178854;

-- Check bill penalties
SELECT id, amount, penalty_amount, penalty_applied 
FROM bills WHERE customer_id = 3178854 AND posted_customer = 0;
```

### **Code Inspection Points:**
1. Add logging to `deposit_charges.rb:156` to capture actual penalty_due calculation
2. Add logging to `email_manager.rb:253` to verify calculate_penalty_due method
3. Check PrintStatementsJob logs for penalty calculation traces
4. Verify statement template penalty field mapping

This reference provides complete technical context for team discussions and debugging efforts.