# Understanding Meter Rollover - Staff Guide

**Document Type:** End-User Knowledgebase
**Target Audience:** Customer Service, Billing Staff, Field Operations
**Last Updated:** January 2026

---

## Table of Contents

1. [What is Meter Rollover?](#what-is-meter-rollover)
2. [How the System Handles Rollover](#how-the-system-handles-rollover)
3. [Recognizing Rollover Situations](#recognizing-rollover-situations)
4. [Common Customer Questions](#common-customer-questions)
5. [Troubleshooting Common Issues](#troubleshooting-common-issues)
6. [When to Escalate](#when-to-escalate)
7. [Quick Reference Card](#quick-reference-card)

---

## What is Meter Rollover?

### Simple Explanation

Think of a water meter like the odometer in a car. When a car odometer reaches 999,999 miles, it "rolls over" to 000,000. Water meters work the same way.

**Example:** A 5-digit meter showing 99,999 will display 00,000 after the next unit of water is used.

### Why This Matters for Billing

When a meter rolls over, the new reading appears to be **lower** than the previous reading:
- Last month's reading: 98,500
- This month's reading: 1,200

Without rollover handling, the system might think the customer used **negative** water (which is impossible!). Our billing system automatically detects this situation and calculates the correct usage.

### Visual Example

```
BEFORE ROLLOVER:              AFTER ROLLOVER:
┌─────────────────┐          ┌─────────────────┐
│ [9][8][5][0][0] │    →     │ [0][1][2][0][0] │
└─────────────────┘          └─────────────────┘
     98,500                        1,200

Actual water used: 2,700 gallons
(500 to reach 99,999, then 1,200 more after rolling to 00,000)
```

---

## How the System Handles Rollover

### Automatic Detection

The billing system automatically detects rollover when:
1. The current reading is **less than** the previous reading
2. The meter is configured with a maximum reading value

### The Math (Simplified)

When rollover is detected:
```
Usage = (Maximum meter value) - (Previous reading) + (Current reading)
```

**Real Example:**
- Meter maximum: 100,000
- Previous reading: 98,500
- Current reading: 1,200
- **Calculated usage:** 100,000 - 98,500 + 1,200 = **2,700 gallons**

### What You'll See in the System

When a rollover is correctly processed, you'll see:
- Previous Reading: 98,500
- Current Reading: 1,200
- **Consumption: 2,700** (positive number, correctly calculated)

---

## Recognizing Rollover Situations

### Signs That Rollover Occurred

| What You See | What It Means |
|--------------|---------------|
| Current reading much lower than previous | Likely rollover |
| Large consumption amount with low current reading | Rollover was detected and handled |
| Customer says "my meter reset" | Rollover (or meter replacement) |

### Normal Rollover vs. Problems

**Normal Rollover (No Action Needed):**
- Previous: 98,500 → Current: 1,200 → Consumption: 2,700
- The consumption amount makes sense for the customer's typical usage
- No warning flags on the account

**Potential Problem (May Need Review):**
- Previous: 50,000 → Current: 200 → Consumption: 50,200
- Consumption seems unusually high
- Customer disputes the reading
- Warning flags appear on the reading

---

## Common Customer Questions

### "Why is my reading lower than last month?"

**Suggested Response:**
> "Your meter has reached its maximum display capacity and rolled over to zero, similar to a car odometer. This is completely normal and happens to all meters eventually. Our system automatically calculates your actual usage correctly. Your bill shows [X] gallons used this period, which is [similar to/higher than/lower than] your typical usage."

### "Did my meter reset? Will I be charged for all that water?"

**Suggested Response:**
> "Your meter didn't reset - it rolled over, which is normal. You're only being charged for the water you actually used. The system calculated [X] gallons based on where your meter was before it rolled over and where it is now."

### "How do I know the reading is correct?"

**Suggested Response:**
> "I can walk you through the calculation:
> - Your previous reading was [X]
> - Your current reading is [Y]
> - Your meter holds up to [Z] before rolling over
> - So your usage is: [Z] - [X] + [Y] = [Result] gallons
>
> Does that usage amount seem reasonable based on your household?"

### "This happened before - is something wrong with my meter?"

**Suggested Response:**
> "No, this is normal. Meters only roll over when they reach their maximum display value, which typically happens every [X] years depending on your usage. High-usage customers may see this more frequently than low-usage customers."

---

## Troubleshooting Common Issues

### Issue 1: Zero or Negative Consumption Showing

**What You See:** Consumption shows as 0 or a negative number

**Possible Causes:**
1. Meter rollover not being detected (configuration issue)
2. Reading entered incorrectly
3. Readings entered in wrong order

**What To Do:**
1. Verify the readings are entered correctly
2. Check if the consumption amount makes sense
3. If consumption should be positive but shows 0, escalate to supervisor

### Issue 2: Consumption Seems Too High After Rollover

**What You See:** Very large consumption amount after rollover

**Possible Causes:**
1. Meter was not read for several months
2. Multiple rollovers occurred (rare)
3. Incorrect meter maximum configured

**What To Do:**
1. Check the billing history - how long since last reading?
2. Compare to customer's typical usage
3. If the amount seems unreasonable, escalate for review

### Issue 3: Customer Disputes Rollover Bill

**What You See:** Customer believes bill is wrong after rollover

**Steps to Resolve:**
1. Pull up the reading history
2. Explain the rollover calculation (see customer questions above)
3. Compare usage to previous periods
4. If customer still disputes, offer to have meter tested
5. Document the conversation in account notes

### Issue 4: Warning Flag on Reading

**What You See:** Orange or red warning indicator on the meter reading

**Common Warning Types:**

| Warning | Meaning | Action |
|---------|---------|--------|
| "No Consumption" | Zero or negative usage calculated | Review reading accuracy |
| "High Variance" | Usage differs significantly from history | Verify reading, check for leaks |
| "No Customer" | Reading not linked to customer account | Escalate to billing |

---

## When to Escalate

### Escalate to Supervisor When:

- Customer remains unsatisfied after explanation
- Consumption amount seems impossible (e.g., 500,000 gallons for residential)
- Multiple warning flags on the same reading
- Suspected meter malfunction
- Reading cannot be verified

### Escalate to Technical Support When:

- Rollover not being detected (keeps showing negative)
- Meter configuration appears incorrect
- System calculation doesn't match manual calculation
- Pattern of issues with specific meter size/type

### Information to Include in Escalation:

1. Account number
2. Meter number
3. Previous and current readings
4. Date of readings
5. Calculated vs. expected consumption
6. Customer's typical usage pattern
7. Any error messages or warning flags

---

## Quick Reference Card

### Rollover at a Glance

```
┌────────────────────────────────────────────────────────────┐
│                    METER ROLLOVER                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  WHAT IT IS:                                               │
│  Meter reaches max value (like 99999) and resets to 0      │
│                                                            │
│  HOW TO SPOT IT:                                           │
│  Current reading LOWER than previous reading               │
│                                                            │
│  THE FORMULA:                                              │
│  Usage = Max Value - Previous + Current                    │
│                                                            │
│  EXAMPLE:                                                  │
│  Max: 100,000 | Previous: 98,500 | Current: 1,200         │
│  Usage = 100,000 - 98,500 + 1,200 = 2,700 gallons         │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Common Meter Maximum Values

| Meter Display | Maximum Value | Typical Use |
|---------------|---------------|-------------|
| 4 digits (0000-9999) | 10,000 | Small/older meters |
| 5 digits (00000-99999) | 100,000 | Standard residential |
| 6 digits (000000-999999) | 1,000,000 | Commercial/large |

### Quick Calculation Examples

**4-Digit Meter (Max 10,000):**
- Previous: 9,500 → Current: 300
- Usage: 10,000 - 9,500 + 300 = **800**

**5-Digit Meter (Max 100,000):**
- Previous: 98,500 → Current: 1,200
- Usage: 100,000 - 98,500 + 1,200 = **2,700**

**6-Digit Meter (Max 1,000,000):**
- Previous: 995,000 → Current: 8,000
- Usage: 1,000,000 - 995,000 + 8,000 = **13,000**

### Response Templates

**For Phone Calls:**
> "I see your meter recently rolled over from [X] to [Y]. This is normal - it's like a car odometer reaching its maximum and starting over. Your actual usage of [Z] gallons was calculated correctly."

**For Written Correspondence:**
> "Your meter reading of [current] is lower than your previous reading of [previous] because your meter has completed a full cycle and rolled over. This is a normal occurrence. Your usage of [consumption] has been calculated as: [max] - [previous] + [current] = [consumption] gallons."

**For Escalation Notes:**
> "Customer inquiry RE: meter rollover. Account [#], Meter [#]. Previous reading [X], Current reading [Y], Consumption calculated [Z]. Customer concern: [describe]. Action taken: [describe]. Resolution needed: [describe]."

---

## Frequently Asked Questions (Internal)

### Q: How often do meters roll over?

**A:** It depends on usage. A typical residential customer using 5,000 gallons/month on a 5-digit meter (max 100,000) would see rollover approximately every 20 months. High-usage customers see it more often.

### Q: Can a meter roll over more than once between readings?

**A:** Technically yes, but this is rare and usually only happens if readings were missed for a very long period. The system can only detect one rollover per reading cycle. If multiple rollovers are suspected, escalate for manual review.

### Q: What if the meter was replaced and didn't actually roll over?

**A:** Meter replacements should be documented separately. If a new meter was installed, there should be:
- A final reading on the old meter
- An initial reading on the new meter
- These should be separate line items, not treated as rollover

### Q: Why do some meters not support rollover?

**A:** Some specialty meters or very old meters are configured with rollover disabled. In these cases, if the reading appears to go backward, it may indicate a problem. Check with your supervisor if you encounter this.

### Q: What's the difference between rollover and a meter reset?

**A:**
- **Rollover:** Normal operation - meter counts up to maximum, then continues from zero
- **Reset:** Unusual - meter was physically reset or replaced (should be documented)

Rollover is automatic and expected. A reset usually requires investigation.

---

## Additional Resources

- **Technical Documentation:** `Meter_Rollover_Logic_Technical_Setup.md` (for IT/Engineering)
- **Meter Reading Training:** [Link to training materials]
- **Customer Service Scripts:** [Link to call center scripts]
- **Billing System Help:** Press F1 in the meter reading screen

---

*Questions about this guide? Contact your supervisor or the billing department.*

*For technical issues, submit a support ticket to IT.*
