# Fortress Sync Billing Data Analysis

## Overview
Analysis of the "Sync billing data from MuniBilling to Fortress" feature, focusing on the method behavior, date parameters, and meter reading inclusion logic.

## Primary Method Location
**Method**: `Jobs::Fortress::SyncBillsToFortress#process_job`  
**File**: `app/business_logic/jobs/fortress/sync_bills_to_fortress.rb:9`  
**Supporting Class**: `ApiConsumer::Fortress::Bill` (handles API communication)  

## What This Method Does (End-User Terms)

This method sends billing information from your MuniBilling system to an external system called "Fortress" (likely a property management or HOA system). Think of it as automatically sharing your utility bills with a third-party system that manages the properties where your customers live.

## Date Parameters and Their Impact

### **Bill Date** (Required Parameter)
- **What it is**: The specific date that appears on the bills you want to send
- **Format**: Must be in MM/DD/YYYY format (e.g., "12/15/2023")
- **Impact**: Only bills with this exact date will be sent to Fortress
- **Critical**: The job will fail if no bill date is provided - it shows "Bill Date must be defined" error

### **Date Processing Logic**
The system converts date strings into proper date objects for several date fields:
- `bill_date` - The primary bill date filter
- `start_date` - Beginning of billing period
- `end_date` - End of billing period  
- `statement_date` - When the statement was generated

**Code Reference**: `app/business_logic/jobs/fortress/common.rb:30-35`

## Bill Selection Criteria

**Only sends bills that match ALL these criteria:**
1. **Date Match**: Bills with the exact `bill_date` you specify
2. **Unposted**: Only bills that haven't been posted to customer accounts yet (`posted_customer = false`)
3. **Not Previously Sent**: Excludes bills already synchronized to Fortress
4. **Valid Mappings**: Only bills where both the customer and property exist in Fortress
5. **Company Match**: Bills belonging to the specified company
6. **Excludes Fortress Bills**: Bills with notes starting with "Fortress Bill -" are excluded

**Code Reference**: `lib/api_consumer/fortress/bill.rb:168-177`

## The Sync Process

1. **Validation**: Checks that bill date is provided and in correct format
2. **Bill Selection**: Finds all qualifying bills for the specified date using `bills_from_mb_to_fortress` method
3. **Data Packaging**: Groups bills by customer/property and formats them for Fortress
4. **Transmission**: Sends bill data to Fortress with the bill date as metadata
5. **Tracking**: Records which bills were successfully sent via `ExternalApiKey` to prevent duplicates

## Meter Reading Bills and Date Ranges

### Key Finding: Meter Reading Dates Are NOT Considered for Bill Selection

**Question**: Does it include meter reading bills created with reading dates that may be outside of the billing period?

**Answer**: **YES** - The sync method is **strictly filtered by `bill_date` only** and does **NOT** consider meter reading dates that may fall outside the billing period.

### How the Filtering Works

**Primary Filter**: The query uses `.unposted_customer` scope which filters on:
- `bills.posted_customer = false`

**No Reading Date Filtering**: The `bills_from_mb_to_fortress` method does **not** include any WHERE clauses for:
- `start_reading_date` 
- `end_reading_date`
- `actual_reading` dates

### Practical Examples

**If you have a bill dated December 15, 2023 that includes:**
- Meter readings from November 20, 2023 to December 10, 2023 ✅ **INCLUDED**
- Meter readings from December 1, 2023 to January 5, 2024 ✅ **INCLUDED**  
- Any other reading date combination ✅ **INCLUDED**

**The sync only cares about:**
1. **Bill Date**: Must match exactly (December 15, 2023)
2. **Posted Status**: Must be unposted (`posted_customer = false`)
3. **Company**: Must belong to the specified company
4. **Not Previously Sent**: No existing external API key for Fortress

### Reading Dates Are Metadata Only

When bills are sent to Fortress, the reading information (`start_reading_date`, `end_reading_date`, `consumption`) becomes part of the bill record but doesn't affect **which bills get selected** for sync.

The bill creation process sets these values, but they're just stored as metadata:
```ruby
# From bill_opts method (lines 386-409)
start_reading_date: start_date,
end_reading_date: end_date,
actual_reading: nil,
start_reading: 0,
end_reading: 0,
consumption: 0
```

## Bill Data Sent to Fortress

Each bill sent includes:
- `referenceId`: Comma-separated bill IDs (converted to dash-separated)
- `comment`: Bill notes
- `fortressUnitId`: External parcel/unit ID
- `fortressHouseholdId`: External customer/household ID  
- `fortressTransactionCode`: Billing type code mapping
- `amount`: Bill amount (rounded to 2 decimals)

**Code Reference**: `lib/api_consumer/fortress/bill.rb:196-207`

## Practical Impact

**If you specify December 15, 2023 as the bill date:**
- Only bills dated exactly December 15, 2023 will be sent
- Bills from December 14th or December 16th will be ignored
- The Fortress system receives these bills tagged with the December 15, 2023 date
- **All bills with that date are included regardless of their meter reading period dates**

## Bottom Line

A bill created for meter readings taken entirely outside the billing period will still be included as long as:
1. Its `bill_date` matches your sync parameter
2. It meets all other selection criteria (unposted, valid mappings, etc.)

This date-centric approach ensures you can control exactly which billing cycle gets shared with Fortress, preventing accidental transmission of wrong billing periods, but it does not filter based on when the actual meter readings were taken.

---

**Analysis Date**: September 2, 2025  
**Codebase**: MuniBilling Legacy System  
**Primary Files Analyzed**:
- `app/business_logic/jobs/fortress/sync_bills_to_fortress.rb`
- `lib/api_consumer/fortress/bill.rb`
- `app/business_logic/jobs/fortress/common.rb`
- `lib/presenters/fortress/job_item.rb`