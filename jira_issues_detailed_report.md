# JIRA Issues: "Due After" and "Penalty_Due" - Detailed Analysis

## Executive Summary
**50 JIRA issues** found containing "Due After" or "Penalty_Due" references. Key concerns:
- **6 active issues** requiring immediate attention
- **2 critical/high priority** payment processing problems
- **25 resolved issues** (50% completion rate)

---

## 🚨 CRITICAL & HIGH PRIORITY ISSUES

### [SAAS-1858](https://jiramb.atlassian.net/browse/SAAS-1858) - **CRITICAL**
**Status**: Ready for Acceptance | **Assignee**: Drago Todorov | **Updated**: 2025-08-28
**Issue**: Staging: When Paya Base Charge Fails, the Convenience Fee is stuck in "Processing" Remote Charge Status
**Impact**: Payment processing failures affecting customer experience

### [SAAS-1829](https://jiramb.atlassian.net/browse/SAAS-1829) - **HIGH**
**Status**: Blocked | **Assignee**: Clyde Qasolli | **Updated**: 2025-08-06
**Issue**: CID 662 Autopay failed for the month of August
**Impact**: Automated payment failures

---

## 🔄 ACTIVE ISSUES NEEDING SUPPORT

### [TRI-2208](https://jiramb.atlassian.net/browse/TRI-2208)
**Status**: Waiting for support | **Assignee**: Nathaniel Genwright | **Updated**: 2025-08-28
**Issue**: CID: 1720 - "Due After" balance isn't calculating correctly
**Impact**: Late fee calculation errors

### [TRI-2096](https://jiramb.atlassian.net/browse/TRI-2096)
**Status**: Waiting for support | **Assignee**: Nathaniel Genwright | **Updated**: 2025-08-07
**Issue**: CID: 1120- Due after not calculating as 10% for late fee
**Impact**: Incorrect late fee percentages

### [SAAS-1395](https://jiramb.atlassian.net/browse/SAAS-1395)
**Status**: Dev In Progress | **Assignee**: Nathaniel Genwright | **Updated**: 2025-06-17
**Issue**: PostMortem for 5/29/2025 Paya outages
**Impact**: Payment gateway stability analysis

---

## 📋 RECENTLY RESOLVED ISSUES (2025)

### [TRI-2181](https://jiramb.atlassian.net/browse/TRI-2181) - **CLOSED**
**Resolved**: 2025-08-26 | **Assignee**: Katilyn Wiggins
**Issue**: City of Arcadia: Bill Due Date Incorrect after Posting 0000967448-002862014
**Resolution**: Fixed bill due date calculation after posting process

### [TRI-1932](https://jiramb.atlassian.net/browse/TRI-1932) - **RESOLVED**
**Resolved**: 2025-05-08 | **Assignee**: Bettina Vick
**Issue**: CID 41 Northwest Water - Bill creation error
**Resolution**: Bill generation process fixed

### [TRI-1781](https://jiramb.atlassian.net/browse/TRI-1781) - **RESOLVED**
**Resolved**: 2025-03-14 | **Assignee**: Bettina Vick
**Issue**: CID- 1776 - City of Bowdle Deleting Historical Records off of Current Bills
**Resolution**: Historical record preservation issue fixed

### [TRI-1705](https://jiramb.atlassian.net/browse/TRI-1705) - **RESOLVED**
**Resolved**: 2025-02-26 | **Assignee**: Nathaniel Genwright
**Issue**: CID: 1120 - Invoice Miscalculation – Late Fee and Deposit Issue
**Resolution**: Late fee and deposit calculation corrected

### [TRI-1573](https://jiramb.atlassian.net/browse/TRI-1573) - **RESOLVED**
**Resolved**: 2025-05-27 | **Assignee**: Nathaniel Genwright
**Issue**: CID: 152 - Nuvei/Paya - Back-to-Back Payment Issue Due to Base Charge Success and Fee Fail
**Resolution**: Payment processing sequence fixed

---

## 📊 PENDING WORK

### [SAAS-1533](https://jiramb.atlassian.net/browse/SAAS-1533) - **TO DO**
**Status**: To Do | **Assignee**: Nathaniel Genwright | **Updated**: 2025-06-11
**Issue**: Alpha UI Facelift: Post Bills page > Email Account Bills tile > missing Ebill Penalty Due Date Picker

### [SAAS-1484](https://jiramb.atlassian.net/browse/SAAS-1484) - **TO DO**
**Status**: To Do | **Assignee**: Nathaniel Genwright | **Updated**: 2025-06-11
**Issue**: Alpha UI Facelift: RollBar # not generated - Unable to access Post Bills page after new Bills are created

### [SAAS-145](https://jiramb.atlassian.net/browse/SAAS-145) - **READY FOR QA**
**Status**: Ready For QA | **Assignee**: Caiden Robinson | **Updated**: 2025-08-10
**Issue**: (Bi-County) Make Jobs::PostBillStagesJob stable, prevent failure from DB timeout

---

## 🔍 KEY PATTERNS & THEMES

### Late Fee Calculation Issues
- Multiple tickets (TRI-2208, TRI-2096, TRI-1705) involve "Due After" balance calculations
- Common problem: Incorrect late fee percentages and timing
- Resolution pattern: Code fixes to billing calculation logic

### Payment Processing Problems
- Paya/Nuvei gateway integration issues frequent
- Back-to-back payment failures when base charge succeeds but fees fail
- Convenience fee processing getting stuck in "Processing" status

### Bill Generation & Posting
- Due date calculation errors after bill posting
- Historical record handling during bill operations
- Email bill processing failures

---

## 📈 STATISTICS
- **Total Issues**: 50
- **Resolution Rate**: 60% (30 resolved/closed/done)
- **Active Issues**: 6 (12%)
- **Average Age**: Issues span from 2023-2025
- **Most Affected Areas**: Billing calculations, Payment processing, Due date handling

---

## 🎯 RECOMMENDED ACTIONS
1. **Immediate**: Address SAAS-1858 (Critical Paya processing issue)
2. **High Priority**: Resolve TRI-2208 & TRI-2096 (Due After calculation errors)
3. **Medium Priority**: Complete SAAS-145 QA testing
4. **Long-term**: Review patterns in late fee calculation logic for systemic improvements