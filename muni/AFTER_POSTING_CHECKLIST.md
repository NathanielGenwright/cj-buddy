# After Invoice 5782219 Posting Completes - Immediate Checklist

## What to Check Immediately

Run this query to see the final state:

```sql
SELECT
  i.id,
  i.invoice_number,
  i.total_due,
  i.total_billed,
  i.previous_balance,
  i.payments_received,
  i.post_billing_job_id,
  -- Check bills
  COUNT(b.id) as bills_linked,
  SUM(b.amount) as sum_of_bills,
  -- What it should be
  (i.previous_balance + IFNULL(SUM(b.amount), 0) - i.payments_received) as should_be,
  -- Discrepancy
  (i.previous_balance + IFNULL(SUM(b.amount), 0) - i.payments_received) - i.total_due as discrepancy
FROM invoices i
LEFT JOIN bills b ON b.invoice_id = i.id
WHERE i.id = 5782219
GROUP BY i.id;
```

## Expected Scenarios

### Scenario A: It Worked Correctly ✅
```
total_due = $103.34 (previous $50.81 + bills $52.53)
bills_linked = 2
discrepancy = $0.00
```
**Action:** None needed - document this as a successful case!

### Scenario B: Same Problem - $0.00 total_due ❌
```
total_due = $0.00 or $50.81
bills_linked = 2 or 0
discrepancy = $103.34 or $52.53
```
**Action:** Need to fix with one of these options:

#### Quick Fix SQL:
```sql
UPDATE invoices
SET total_due = 103.34
WHERE id = 5782219;
```

#### Or Re-post the invoice:
```ruby
# In Rails console
Invoices::InvoicesPost.for_customers(customer_ids: [3279710]).call
```

## Root Cause Summary

If total_due is wrong, it means:
- Bills were NOT linked to invoice when `sp_post_invoices` calculated `total_due`
- The stored procedure saw $0 in bills and calculated accordingly
- Bills got linked AFTER the calculation

## What to Tell the User

If the invoice shows $0.00 or $50.81 instead of $103.34:

"The invoice was generated with an incorrect total due to a timing issue in the posting process. The bills ($52.53) were added after the total was calculated. We need to either:
1. Re-post the invoice to recalculate the total
2. Manually update the total_due to the correct amount ($103.34)"

---

**Expected Correct Values:**
- previous_balance: $50.81
- new bills: $52.53 ($33.56 + $18.97)
- payments: $0.00
- **CORRECT total_due: $103.34**
