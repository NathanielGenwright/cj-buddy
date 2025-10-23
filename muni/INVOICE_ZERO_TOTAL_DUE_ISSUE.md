# Invoice $0.00 Total Due Issue - Customer 3279710

## Issue Summary
New customer accounts are being created with invoices showing `total_due = $0.00` despite having bills with actual amounts.

**Affected Customer:** 3279710 (Sahuarita Wastewater Utility, Company ID: 203)
**Invoice:** #10586892 (ID: 5774775)
**Expected Total:** $56.27
**Actual Total:** $0.00

## Root Cause Analysis

### The Problem: Timing Issue in Invoice Posting

The stored procedure `sp_post_invoices` calculates `total_due` at the moment of posting:

```sql
-- From sp_post_invoices
SET i.total_due = CASE
    WHEN co.is_collection_site = true
    THEN i.previous_balance + IFNULL(bills_a.amount, 0) - IFNULL(payments_a.amount, 0)
    ELSE IFNULL(bills_a.amount, 0)
END
```

For **collection sites** like Sahuarita (`is_collection_site = 1`), the formula is:
```
total_due = previous_balance + bills_amount - payments_amount
```

### Timeline of Events

| Time | Event | Bills Linked? | total_due Calculated? |
|------|-------|---------------|----------------------|
| Oct 7-8 | Bills created ($56.27 total) | ❌ No | ❌ No |
| Oct 9, 8:59 PM | Invoice created (ID: 5774775) | ❌ No | ❌ No |
| Oct 10, 2:51 AM | **Invoice POSTED** | ❌ **NO** | ✅ **YES - Calculated as $0.00** |
| After posting | Bills linked to invoice | ✅ Yes | ❌ Never recalculated |

**At the critical moment (2:51 AM posting):**
- `previous_balance` = $0.00
- `bills_amount` = $0.00 ← **Bills not yet linked to invoice!**
- `payments_amount` = $0.00
- **Result:** `total_due = $0.00 + $0.00 - $0.00 = $0.00` ❌

### Database Evidence

```sql
-- Current state (WRONG)
invoice.total_due = 0.00
invoice.total_billed = 56.27
invoice.post_billing_job_id = 12577210 (posted)

-- Bills linked to invoice
bill_171282000: $27.30 (SEW-R)
bill_171282004: $18.97 (AdminFeesR)
bill_171200396: $10.00 (Account Setup Fee)
TOTAL: $56.27

-- Correct calculation should be:
total_due = $0.00 + $56.27 - $0.00 = $56.27 ✅
```

## Why This Happens

The issue occurs when:
1. **New customer accounts** are created
2. **Bills are generated** but not immediately linked to an invoice
3. **Invoice creation and posting happen quickly** (within hours)
4. The posting process sees **no bills linked** yet and calculates `total_due = $0.00`
5. Bills get linked to the invoice **after** posting
6. `total_due` is **never recalculated** after bill linkage

## Verification Queries

```sql
-- Check if total_due is wrong
SELECT
  i.id,
  i.invoice_number,
  i.total_due as stored_total_due,
  i.previous_balance + SUM(b.amount) - i.payments_received as correct_total_due,
  (i.previous_balance + SUM(b.amount) - i.payments_received) - i.total_due as discrepancy
FROM invoices i
LEFT JOIN bills b ON b.invoice_id = i.id
WHERE i.customer_id = 3279710
GROUP BY i.id;
```

## Fix Options

### Option 1: Re-post the Invoice (Safest)
Re-run the posting process to recalculate `total_due` with bills now linked:

```ruby
# In Rails console
invoice = Invoice.find(5774775)
Invoices::InvoicesPost.for_customers(customer_ids: [3279710]).call
```

### Option 2: Direct SQL Update (Quick Fix)
```sql
UPDATE invoices
SET total_due = 56.27
WHERE id = 5774775;
```

### Option 3: Batch Fix for All Affected Invoices
```sql
UPDATE invoices i
JOIN (
  SELECT
    i.id,
    i.previous_balance + IFNULL(SUM(b.amount), 0) - i.payments_received as correct_total_due
  FROM invoices i
  LEFT JOIN bills b ON b.invoice_id = i.id
  WHERE i.customer_id = 3279710
  GROUP BY i.id
) calc ON calc.id = i.id
SET i.total_due = calc.correct_total_due
WHERE i.customer_id = 3279710
  AND i.total_due != calc.correct_total_due;
```

## Prevention: Long-Term Fix

### Root Cause in Process Flow
The issue stems from a race condition between:
- Bill → Invoice linkage
- Invoice posting (which calculates `total_due`)

### Proposed Solutions

#### Solution A: Ensure Bills Are Linked Before Posting
Modify the posting workflow to verify all bills are linked before calculating `total_due`.

**Location:** [/Users/munin8/_myprojects/muni/muni-billing/legacy/lib/invoices/invoices_post.rb](muni-billing/legacy/lib/invoices/invoices_post.rb)

```ruby
# In process_invoices method, add:
def process_invoices(customer_id:)
  # Ensure all bills are linked first
  ensure_bills_linked(customer_id: customer_id)

  # Then update invoice with recalculated total_due
  recalculate_total_due(customer_id: customer_id)

  unposted_invoices.where(customer_id: customer_id)
    .update_all(post_billing_job_id: post_batch.id)
end
```

#### Solution B: Trigger-Based Recalculation
Add a database trigger to recalculate `total_due` whenever bills are linked:

```sql
CREATE TRIGGER bills_after_update_recalc_invoice_total
AFTER UPDATE ON bills
FOR EACH ROW
BEGIN
  IF NEW.invoice_id IS NOT NULL AND OLD.invoice_id IS NULL THEN
    UPDATE invoices i
    SET i.total_due = (
      SELECT
        i.previous_balance + IFNULL(SUM(b.amount), 0) - i.payments_received
      FROM bills b
      WHERE b.invoice_id = NEW.invoice_id
    )
    WHERE i.id = NEW.invoice_id
      AND EXISTS (
        SELECT 1 FROM customers c
        JOIN companies co ON c.company_id = co.id
        WHERE c.id = i.customer_id
          AND co.is_collection_site = 1
      );
  END IF;
END;
```

#### Solution C: Post-Posting Validation
Add a validation step after posting to verify `total_due` matches bill totals:

```ruby
# Add to Invoices::InvoicesPost
def validate_total_due(customer_id:)
  invoice = unposted_invoices.find_by(customer_id: customer_id)
  calculated = invoice.bills.sum(:amount) + invoice.previous_balance - invoice.payments_received

  if invoice.total_due != calculated
    Rails.logger.warn("Invoice #{invoice.id} total_due mismatch: #{invoice.total_due} vs #{calculated}")
    invoice.update_columns(total_due: calculated)
  end
end
```

## Monitoring Setup

I've created monitoring queries in: [monitor_customer_3279710.sql](monitor_customer_3279710.sql)

### Usage:
```bash
# Run monitoring queries
mysql -u billingdbuser -p billingdb < monitor_customer_3279710.sql

# Or in Rails console
File.read('monitor_customer_3279710.sql').split(';').each do |query|
  next if query.strip.empty? || query.strip.start_with?('--')
  puts ActiveRecord::Base.connection.execute(query).to_a
end
```

## Related Code References

- **Stored Procedure:** `sp_post_invoices` in [db/structure.sql:31619](muni-billing/legacy/db/structure.sql#L31619)
- **Invoice Posting (Ruby):** [lib/invoices/invoices_post.rb](muni-billing/legacy/lib/invoices/invoices_post.rb)
- **Invoice Model:** [app/models/invoice.rb](muni-billing/legacy/app/models/invoice.rb)
- **Invoice Creation:** [lib/invoices/invoice_creation.rb](muni-billing/legacy/lib/invoices/invoice_creation.rb)

## Impact Assessment

### Affected Scenarios
- ✅ **New customer accounts** (like 3279710)
- ✅ **Collection site companies** (`is_collection_site = 1`)
- ✅ **Quick bill → invoice → posting cycles** (within hours)
- ❌ Not affected: Regular billing cycles with proper timing
- ❌ Not affected: Non-collection-site companies

### Business Impact
- **Customer confusion:** Invoices show $0.00 but customers are charged actual amounts
- **Payment processing issues:** Payment portals may not display correct amount due
- **Accounting discrepancies:** Reported totals don't match actual bills
- **Customer service burden:** Support teams must explain discrepancies

## Testing Checklist

- [ ] Verify current invoice state for customer 3279710
- [ ] Run monitoring queries before creating new bills
- [ ] Create bills and track when they're linked to invoice
- [ ] Watch invoice posting process timing
- [ ] Verify `total_due` calculation after posting
- [ ] Test fix option (re-post or direct update)
- [ ] Validate invoice prints with correct total

## Questions to Answer

1. **How many invoices are affected?**
   ```sql
   SELECT COUNT(*)
   FROM invoices i
   LEFT JOIN bills b ON b.invoice_id = i.id
   JOIN customers c ON i.customer_id = c.id
   JOIN companies co ON c.company_id = co.id
   WHERE co.is_collection_site = 1
     AND i.post_billing_job_id IS NOT NULL
     AND i.total_due = 0
     AND EXISTS (SELECT 1 FROM bills WHERE invoice_id = i.id AND amount > 0);
   ```

2. **Is this specific to Sahuarita or all collection sites?**
3. **What triggers the quick posting cycle for new accounts?**
4. **Should we delay posting until bills are confirmed linked?**

## Next Steps

1. **Immediate:** Fix customer 3279710's invoice using Option 1 or 2
2. **Short-term:** Identify all affected invoices and batch fix
3. **Medium-term:** Implement Solution A or B to prevent recurrence
4. **Long-term:** Add monitoring/alerting for `total_due = $0.00` with non-zero bills

---

**Created:** 2025-10-15
**Last Updated:** 2025-10-15
**Status:** Root cause identified, fix options documented
