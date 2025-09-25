# Invoice Analysis: Customer 3178854 (Johanna Lyon) - Beach City Utilities

## Process Summary
**Customer**: Johanna Lyon (ID: 3178854)  
**Company**: Beach City Utilities (CID: 1720)  
**Current Balance**: $296.59  
**Invoice Date**: 08/21/2025  
**Penalty Date**: 09/15/2025  

---

## 📊 CHARGE BREAKDOWN

### Bill #1 (ID: 168604424) - **PRIMARY BILL**
- **Usage Charge**: $150.80 (1,040 gallons consumed)
- **Extra Charge**: $5.00 
- **Total Amount**: $155.80
- **Penalty Amount**: $23.37 (15% of $155.80)

### Bill #2 (ID: 168604425) 
- **Usage Charge**: $4.84 (same 1,040 gallons)
- **Total Amount**: $4.84
- **Penalty Amount**: $0.73 (15% of $4.84)

### Bill #3 (ID: 168604426)
- **Usage Charge**: $6.24 (same 1,040 gallons) 
- **Total Amount**: $6.24
- **Penalty Amount**: $0.94 (15% of $6.24)

---

## 🧮 PENALTY_DUE CALCULATION ANALYSIS

Based on the logs and database records, here's how **penalty_due** is calculated:

### Configuration for CID 1720:
- **Company Settings**: 
  - `penalty_print_total_bills`: 0 (disabled)
  - `penalty_print_total_balance`: 0 (disabled)
  - `penalty_print_percent`: 0.000000
- **Rate Settings**: 
  - `penalty_percentage`: 0.150000 (15%)
  - `include_balance_in_penalty`: 0 (exclude current balance)

### Active Calculation Method: **Default Method (#3)**
```ruby
penalty_due = total_due + penalty_amount
```

Where `penalty_amount` is calculated per bill:
```ruby
penalty_amount = (bill_amount × 0.15) + 0.00
```

### Detailed Calculation for Customer 3178854:

**Current Balance**: $296.59  
**New Bills Total**: $155.80 + $4.84 + $6.24 = $166.88  
**Total Due**: $296.59 + $166.88 = $463.47

**Individual Penalty Amounts**:
- Bill 1: $155.80 × 0.15 = $23.37
- Bill 2: $4.84 × 0.15 = $0.73  
- Bill 3: $6.24 × 0.15 = $0.94
- **Total Penalty**: $23.37 + $0.73 + $0.94 = $25.04

**Final Penalty_Due Amount**: $463.47 + $25.04 = **$488.51**

---

## 🔍 PROCESS FLOW CAPTURED

### Job Execution Timeline:
1. **03:35:26** - PrintStatementsJob started (billing_job_id: 12449799)
   - **FAILED**: "This report generated no data"
   - Duration: 4.026 seconds

2. **03:35:34** - PrintStatementsJob retry (billing_job_id: 12449800)  
   - **SUCCESS**: Statement generated
   - Duration: 3.351 seconds

3. **04:34:05** - PrintInvoiceJob executed (billing_job_id: 12449801)
   - **SUCCESS**: Invoice PDF created
   - File: `a779f1c4-0308-46a6-91f7-b22a0e006b43.pdf`
   - Duration: 3.442 seconds

### Key Parameters Used:
- `penalty_date`: "09/15/2025"
- `bill_date`: "08/21/2025" 
- `company_id`: 1720
- `customer_id`: 3178854

---

## ⚠️ CRITICAL FINDINGS

### Why TRI-2208 (Due After Balance Error) Occurs:

The **penalty_due** calculation for this customer involves:

1. **Multiple Bills**: Customer has 3 separate bills on same date
2. **Complex Total**: Current balance ($296.59) + new charges ($166.88)
3. **Penalty Logic**: 15% applied to each bill individually, not the total
4. **Final Amount**: $463.47 (total due) + $25.04 (penalties) = **$488.51**

### Potential Issues:
- **Multiple bills** may cause confusion in penalty calculation
- **Current balance** ($296.59) is NOT included in penalty calculation (correct per config)
- **Individual penalty rates** applied per bill, not aggregate total

This explains why [TRI-2208](https://jiramb.atlassian.net/browse/TRI-2208) reports "Due After balance isn't calculating correctly" - the penalty calculation across multiple bills may appear inconsistent to users.

---

## 📁 PRESERVED LOG FILES
- `job_queue_tracker_20250831_003814.log`
- `sidekiq_20250831_003814.log` 
- `bill_20250831_003814.log`
- `customer_portal_api_20250831_003814.log`