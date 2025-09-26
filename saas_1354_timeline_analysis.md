# SAAS-1354 Timeline Analysis: "Base amount accepted, convenience fee declined (part2)"

## Main Ticket Status History

### SAAS-1354 - Main Bug
- **Created**: May 22, 2025 at 12:03 PM
- **Current Status**: QA In Progress
- **Status Category Change Date**: September 8, 2025 at 1:19 PM
- **Last Updated**: September 15, 2025 at 4:00 PM
- **Duration in "In Progress" states**: ~115 days (from Sept 8 to current date)
- **Total Age**: ~177 days

## Chronological Timeline of All Related Issues

### December 2024
- **Dec 16, 2024**: TRI-1573 created - Initial service request about Nuvei/Paya payment issues

### January 2025
- **Jan 5, 2025**: TRI-1573 resolved
- **Jan 7, 2025**: SAAS-559 created - Original "Base amount accepted, convenience fee declined" story

### May 2025
- **May 22, 2025**: 
  - SAAS-559 marked as Done
  - **SAAS-1354 created immediately after** (part 2 of the fix)
- **May 29, 2025**: TRI-1998 created - "Paya Payments Stuck in Processing"

### June 2025
- **Jun 3, 2025**: SAAS-559 last updated
- **Jun 4, 2025**: TRI-1998 resolved

### July 2025 - Surge of Related Issues
- **Jul 15**: SAAS-1705 created - Remote charge display issues
- **Jul 15**: SAAS-1706 created (High Priority) - Merchant config errors
- **Jul 17**: SAAS-1725 created (High Priority) - API health check UX issues
- **Jul 22**: SAAS-1751 created - Customer Portal 2 autopay issues
- **Jul 28**: SAAS-1768 created (Critical) - Reproduced base/fee split issue
- **Jul 29**: SAAS-1779 created - Intermittent payment failures
- **Jul 29**: SAAS-1784 created - Paya health check update issues

### August 2025
- **Aug 4**: SAAS-1820 created (Critical) - Gift card payment issues
- **Aug 8**: SAAS-1858 created (Critical) - Fee stuck in "Processing" when base fails
- **Aug 13**: SAAS-1725 moved to Ready for Acceptance
- **Aug 21**: SAAS-1951 created - Failed charges not displaying
- **Aug 21**: SAAS-1952 created - "Online payments not allowed" message issues

### September 2025
- **Sep 8**: 
  - **SAAS-1354 moved to "QA In Progress"** 
  - SAAS-1779 canceled
  - SAAS-2128 created - Rollbar error for IVR button
- **Sep 12**: SAAS-2165 created (Critical) - Heartland ECheck missing fees
- **Sep 15**: Current date - Last update to SAAS-1354 and SAAS-2165

## Key Observations

### Duration Analysis
1. **SAAS-1354 has been in "QA In Progress" for 7 days** (Sept 8 - Sept 15)
2. **Total time since creation**: 177 days (May 22 - Sept 15)
3. **Time from original issue (SAAS-559) to current**: 251 days

### Issue Pattern
- Original issue (SAAS-559) was marked "Done" on May 22
- Part 2 fix (SAAS-1354) was created the same day
- **23 days later**: First related production issue reported (TRI-1998)
- **July surge**: 7 new bugs created in July alone (days 15-29)
- **4 Critical priority issues** still unresolved

### Current State
- **14 linked bugs** with varying priorities:
  - 4 Critical (SAAS-2165, SAAS-1858, SAAS-1820, SAAS-1768)
  - 2 High (SAAS-1725, SAAS-1706)
  - 8 Normal
- **11 issues in "Ready for Acceptance"** status
- **1 in "Ready for QA"** (SAAS-1820)
- **2 in "To Do"** (SAAS-2128, SAAS-2165)
- **1 Canceled** (SAAS-1779)

### Impact Assessment
The original "base amount accepted, convenience fee declined" issue has:
1. Spawned 16 related tickets over 9 months
2. Affected multiple payment gateways (Paya, Heartland)
3. Impacted various payment types (credit cards, eChecks, gift cards)
4. Created customer-facing issues in both Customer Portal 1 and 2
5. Generated critical production issues that remain unresolved

## Recommendations
1. The main ticket has been in development/QA for nearly 6 months
2. New critical issues are still being discovered (SAAS-2165 on Sept 12)
3. Consider comprehensive regression testing across all payment gateways
4. Review the architectural approach to handling split payments (base + fee)