# PENALTY_DUE INVESTIGATION - EVIDENCE LOG

## 📋 **INVESTIGATION METADATA**

**Investigation Date**: August 31, 2025  
**Investigator**: AI Assistant (Claude)  
**Customer**: Johanna Lyon (ID: 3178854)  
**Company**: Beach City Utilities (ID: 1720)  
**Issue**: Penalty_due discrepancy $571.36 vs $838.29

---

## 🔍 **EVIDENCE COLLECTION LOG**

### **Evidence #1: Database Ground Truth**
**Source**: MySQL billingdb  
**Method**: Direct SQL queries  
**Timestamp**: 2025-08-31

```sql
-- Customer balance verification
SELECT balance_current FROM customers WHERE id = 3178854;
Result: $296.59

-- Unposted bills verification  
SELECT id, amount, penalty_amount FROM bills WHERE customer_id = 3178854 AND posted_customer = 0;
Results: 6 bills totaling $238.93 with penalties $35.84
```

**Status**: ✅ VERIFIED

---

### **Evidence #2: Company Configuration**
**Source**: companies table  
**Method**: Direct SQL query  
**Timestamp**: 2025-08-31

```sql
SELECT penalty_print_total_bills, penalty_print_total_balance, penalty_print_percent 
FROM companies WHERE id = 1720;

Results:
- penalty_print_total_bills: 0
- penalty_print_total_balance: 0  
- penalty_print_percent: 0.000000
```

**Conclusion**: Should use Method #3 (default penalty calculation)  
**Status**: ✅ VERIFIED

---

### **Evidence #3: Rate Configuration**
**Source**: rates table  
**Method**: JOIN query with bills  
**Timestamp**: 2025-08-31

```sql
SELECT DISTINCT r.penalty_percentage, r.penalty_amount, r.use_penalty, r.include_balance_in_penalty
FROM bills b JOIN rates r ON b.rate_id = r.id 
WHERE b.customer_id = 3178854 AND b.posted_customer = 0;

Results: All rates have:
- penalty_percentage: 0.150000 (15%)
- penalty_amount: 0.000000
- use_penalty: 1
- include_balance_in_penalty: 0
```

**Conclusion**: Individual bill penalties calculated correctly  
**Status**: ✅ VERIFIED

---

### **Evidence #4: Individual Penalty Calculations**
**Source**: bills table penalty_amount field  
**Method**: Mathematical verification  
**Timestamp**: 2025-08-31

| Bill ID | Amount | Expected (15%) | Actual DB | Status |
|---------|--------|----------------|-----------|---------|
| 168604424 | $155.80 | $23.37 | $23.37 | ✅ MATCH |
| 168604425 | $4.84 | $0.73 | $0.73 | ✅ MATCH |
| 168604426 | $6.24 | $0.94 | $0.94 | ✅ MATCH |
| 168604423 | $28.69 | $4.30 | $4.30 | ✅ MATCH |
| 168604422 | $11.22 | $1.68 | $1.68 | ✅ MATCH |
| 168604421 | $32.14 | $4.82 | $4.82 | ✅ MATCH |

**Conclusion**: Database penalty amounts are mathematically correct  
**Status**: ✅ VERIFIED

---

### **Evidence #5: Method #3 Calculation Logic**
**Source**: `lib/services/bills/statement_data/deposit_charges.rb:161`  
**Method**: Code analysis  
**Timestamp**: 2025-08-31

```ruby
data.penalty_due = if company.penalty_print_total_bills
                     data.total_due + (penalty_bill_total * company.penalty_print_percent).round(2)
                   elsif company.penalty_print_total_balance
                     data.total_due + (data.total_due * company.penalty_print_percent).round(2)
                   else
                     data.total_due + data.penalty_amount  # ← This path should execute
                   end
```

**Expected Calculation**:
```
penalty_due = total_due + penalty_amount
penalty_due = ($296.59 + $238.93) + $35.84
penalty_due = $535.52 + $35.84 = $571.36
```

**Status**: ✅ LOGIC VERIFIED

---

### **Evidence #6: Alternative Penalty Methods**
**Source**: Multiple code files  
**Method**: Code analysis  
**Timestamp**: 2025-08-31

| Method | Location | Result for Customer | Notes |
|--------|----------|-------------------|-------|
| PrintableInvoiceDecorator | printable_invoice_decorator.rb:23 | $0 | Company flags disabled |
| Bill calculation | bill_lib.rb:177 | $35.84 | Individual penalties only |
| Email manager | email_manager.rb:253 | $571.36 | Same as Method #3 |
| Customer controller | customers_controller.rb:868 | $35.84 | Individual penalties only |

**Conclusion**: No alternative method produces $838.29  
**Status**: ✅ VERIFIED

---

### **Evidence #7: Historical Penalty Data**
**Source**: bills table (posted bills)  
**Method**: SQL aggregation  
**Timestamp**: 2025-08-31

```sql
-- Historical accrued penalties
SELECT SUM(penalty_amount) as total_accrued_penalties 
FROM bills WHERE customer_id = 3178854 AND posted_customer = 1;
Result: $236.85

-- Historical balance
SELECT SUM(amount) as total_posted_balance 
FROM bills WHERE customer_id = 3178854 AND posted_customer = 1 AND open_balance > 0;
Result: $296.59 (matches customers.balance_current)
```

**Historical Total Theory**:
$296.59 + $238.93 + $35.84 + $236.85 = $808.21 (still $30 short of $838.29)

**Status**: ❌ PARTIAL EXPLANATION

---

### **Evidence #8: Document Analysis Discrepancies**
**Source**: Investigation documents from previous day  
**Method**: Document comparison  
**Timestamp**: 2025-08-31

**Document 1 (penalty_due_calculation_838_29.md)**:
- Claims new bills total: $238.93 ✅
- Expected penalty_due: $571.36 ✅  
- Actual reported: $838.29 ❌

**Document 2 (customer_3178854_invoice_analysis.md)**:
- Claims new bills total: $166.88 ❌ (only counted 3 bills)
- Expected penalty_due: $488.51 ❌ (wrong baseline)
- Same actual: $838.29 ❌

**Conclusion**: Document 2 had calculation errors, Document 1 is accurate  
**Status**: ✅ RECONCILED

---

### **Evidence #9: Penalty Field Inventory**
**Source**: Database schema analysis  
**Method**: INFORMATION_SCHEMA queries  
**Timestamp**: 2025-08-31

**Found penalty_* fields**:
- customers.penalty_waived: 0 (penalties enabled)
- bills.penalty_amount: Individual amounts (verified correct)
- bills.penalty_applied: 0 (not yet applied)
- bills.penalty_date: 2025-09-15 (future date)
- companies.penalty_print_*: Various settings (verified)
- rates.penalty_percentage: 0.15 (15% - verified)

**Conclusion**: No additional penalty fields explain $838.29  
**Status**: ✅ COMPREHENSIVE

---

## 📊 **EVIDENCE SUMMARY**

### **✅ CONFIRMED FACTS:**
1. Database penalty amounts are mathematically correct ($35.84)
2. Company configuration correctly points to Method #3
3. Method #3 calculation should produce $571.36
4. Individual bill penalties are accurately calculated at 15%
5. No alternative penalty method produces $838.29
6. Customer penalty settings are normal (not waived)

### **❌ UNEXPLAINED EVIDENCE:**
1. **$838.29 figure source**: Unknown code location
2. **$266.93 gap**: No evidence explains this difference
3. **Statement generation**: Not yet traced

### **🔍 INVESTIGATIVE GAPS:**
1. **Actual PDF statement**: Not yet generated/analyzed
2. **PrintStatementsJob logs**: Not yet examined  
3. **Complete transaction history**: Partially analyzed
4. **Print helper calculations**: Not yet traced

---

## 🎯 **EVIDENCE-BASED CONCLUSIONS**

### **High Confidence (95%+):**
- Core penalty calculation logic is working correctly
- Database contains accurate penalty amounts
- Configuration is properly set for Method #3

### **Medium Confidence (70-95%):**
- Bug exists in statement generation or display layer
- $838.29 is not produced by standard penalty calculation methods
- Historical data accumulation does not fully explain the gap

### **Low Confidence (<70%):**
- Specific code location producing $838.29
- Whether other customers are affected
- Timeline for when bug was introduced

---

## 📋 **CHAIN OF CUSTODY**

**Evidence Collection**: Direct from production database  
**Data Integrity**: Verified through multiple query methods  
**Code Analysis**: Direct from source code repository  
**Documentation**: All queries and results logged  
**Reproducibility**: All evidence can be independently verified

---

## 🔒 **EVIDENCE PRESERVATION**

**Files Created**:
- `/Users/munin8/_myprojects/penalty_due_analysis_final.md`
- `/Users/munin8/_myprojects/penalty_due_amount_analysis.md`
- All investigation documents with timestamps

**Database Snapshots**: Queries documented for reproduction  
**Code References**: Line-by-line analysis preserved  
**Investigation Timeline**: Complete log of actions taken

**This evidence log provides complete traceability and supports reproducible investigation results.**