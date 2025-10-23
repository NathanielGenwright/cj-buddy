# JIRA Feedback Templates for Engineering Portal
## Standardized Responses for TriQ Validation

### Overview
These templates provide consistent, helpful feedback for ticket submitters based on validation results. Each template includes specific guidance and examples to improve ticket quality.

---

## Template Categories

### 1. APPROVAL Templates

#### Template A1: Full Approval
```
**✅ VALIDATION PASSED - APPROVED FOR ENGINEERING**

Your ticket has been validated and meets all quality standards. It has been added to the engineering backlog.

**Quality Score**: {score}/10
**Estimated Response Time**: {timeline}
**Assigned Team**: {team}

Thank you for the clear and detailed submission!
```

#### Template A2: Approval with Minor Notes
```
**✅ VALIDATION PASSED - APPROVED WITH NOTES**

Your ticket has been approved for engineering work. The following minor clarifications may help with faster resolution:

**Quality Score**: {score}/10

**Optional Improvements**:
{specific_suggestions}

**Next Steps**: This ticket is now in the engineering backlog.
```

---

### 2. CLARIFICATION REQUEST Templates

#### Template C1: Missing Environment Details
```
**⚠️ CLARIFICATION NEEDED - ENVIRONMENT INFORMATION**

Your ticket is well-documented but needs technical environment details for effective troubleshooting.

**Quality Score**: {score}/10

**Please provide**:
- **Browser**: Which browser and version? (Chrome 120, Safari 17, etc.)
- **Operating System**: Windows, Mac, iOS, Android, etc.
- **Device Type**: Desktop, mobile phone, tablet
- **Network**: Corporate WiFi, home internet, mobile data

**Example**:
"Using Chrome 120 on Windows 11 desktop via corporate WiFi"

**How to find this info**:
- Browser version: Usually in Help > About menu
- OS version: System Settings > About
- Device: What you're using to access the system

Once you add this information, your ticket will be immediately approved for engineering work.
```

#### Template C2: Missing Error Details
```
**⚠️ CLARIFICATION NEEDED - ERROR MESSAGE SPECIFICS**

Your ticket describes the problem well but needs specific error messages for troubleshooting.

**Quality Score**: {score}/10

**Please provide**:
- **Exact error message**: Copy the text exactly as shown, or take a screenshot
- **Error timing**: When does the error appear? (during login, after clicking submit, etc.)
- **Error codes**: Any numbers or codes shown with the error

**Example**:
"Error message: 'Authentication failed - invalid credentials (Error Code: AUTH_401)'"
"This appears immediately after clicking 'Login' button"

**Screenshots help!** If possible, include a screenshot showing:
- The error message
- What you were trying to do when it happened
- The browser address bar (to confirm which page)

Adding these details will move your ticket directly to engineering.
```

#### Template C3: Missing Business Impact
```
**⚠️ CLARIFICATION NEEDED - BUSINESS IMPACT**

Your ticket has good technical details but needs business context for proper prioritization.

**Quality Score**: {score}/10

**Please provide**:
- **Who is affected**: Just you, your team, all customers, specific user group?
- **Business impact**: What work/process is blocked or disrupted?
- **Urgency**: How quickly does this need resolution?
- **Workarounds**: Is there any temporary way to accomplish the task?

**Example**:
"Affects all 25 customer service staff. Cannot process payments, blocking daily billing operations. Need resolution by EOD to avoid revenue impact. No workaround available."

This helps engineering prioritize your issue appropriately.
```

#### Template C4: Missing Reproduction Steps
```
**⚠️ CLARIFICATION NEEDED - REPRODUCTION STEPS**

Your ticket describes the issue but needs clear steps to reproduce the problem.

**Quality Score**: {score}/10

**Please provide step-by-step instructions**:
1. Start from a specific page or state
2. List each action taken (click, type, navigate)
3. Include what you expected to happen
4. Describe what actually happened instead

**Example**:
1. Navigate to Customer Portal login page
2. Enter username: user@company.com
3. Enter password: (correct password)
4. Click "Login" button
5. Expected: Dashboard should load
6. Actual: "Unauthorized access" error appears

**Additional helpful info**:
- Does this happen every time or only sometimes?
- Does it work on different browsers/devices?
- When did you first notice this problem?

Clear reproduction steps help engineering fix the issue faster.
```

---

### 3. REVISION REQUEST Templates

#### Template R1: Major Restructuring Needed
```
**❌ REVISION REQUIRED - INCOMPLETE INFORMATION**

Your ticket needs significant additional information before engineering can investigate.

**Quality Score**: {score}/10

**Required improvements**:
{specific_requirements_list}

**Template for resubmission**:
```
**Problem Summary**: [Specific issue in 1-2 sentences]

**Environment**:
- Browser: [Browser name and version]
- Operating System: [Windows/Mac/etc. version]
- Device: [Desktop/mobile/tablet]

**Issue Details**:
- What you were trying to do: [Goal/task]
- What happened instead: [Specific error or problem]
- Error message (exact text): "[Copy error text here]"

**Business Impact**:
- Who is affected: [Number of users/teams]
- Work blocked: [What can't be done]
- Urgency: [Timeline needs]

**Troubleshooting Tried**:
- [List what you've already attempted]
```

**Examples of well-documented tickets**: [Link to examples]

Please restructure your ticket using this template for faster processing.
```

#### Template R2: Generic Summary and Description
```
**❌ REVISION REQUIRED - SUMMARY TOO GENERIC**

Your ticket title and description need to be more specific for proper routing and prioritization.

**Quality Score**: {score}/10

**Current Issues**:
- Summary: "{current_summary}" is too generic
- Description lacks specific problem details

**Improvement needed**:

**Better Summary Examples**:
- Instead of: "Login Help"
- Use: "Users getting 'unauthorized' error during Customer Portal login"

- Instead of: "Payment Issue"  
- Use: "Credit card payments failing with timeout error in billing system"

**Better Description Structure**:
1. **Specific problem**: What exactly isn't working?
2. **Impact**: Who/what is affected?
3. **Error details**: Exact messages or symptoms
4. **Environment**: What system/browser/device?

**Before resubmitting**, ask yourself:
- Would someone else understand the problem from my title alone?
- Have I explained what I was trying to do?
- Have I included specific error messages or symptoms?
- Is it clear what business impact this has?

Please revise with these improvements.
```

#### Template R3: Authentication Issues - Special Handling
```
**❌ REVISION REQUIRED - AUTHENTICATION ISSUE NEEDS SECURITY REVIEW**

Your ticket involves authentication/security and requires additional information before engineering review.

**Quality Score**: {score}/10

**⚠️ Security Considerations**:
This issue involves login/authentication systems and may require security team review.

**Required Information**:
- **Account identifier**: Username or account number (you can anonymize: user***@domain.com)
- **Company/Organization**: Which organization's account?
- **User role**: Admin, regular user, guest, etc.?
- **System access level**: What parts of the system should you have access to?
- **Recent changes**: Any password changes, permission updates, new devices?

**Security Guidelines**:
- ❌ Do NOT include actual passwords in tickets
- ❌ Do NOT share account credentials  
- ✅ DO include anonymized usernames
- ✅ DO describe permission levels and expected access

**Next Steps**:
1. Revise ticket with required information
2. Security team will review for sensitive issues
3. Engineering will handle technical troubleshooting

**Escalation**: If this is urgent business disruption, contact IT support directly at [contact info]
```

---

### 4. ROUTING Templates

#### Template RT1: Route to Customer Support
```
**↗️ ROUTING RECOMMENDATION - CUSTOMER SUPPORT**

Your request appears to be a customer support issue rather than an engineering problem.

**Quality Score**: {score}/10 (for engineering context)

**Recommended routing**: Customer Service & Support (CSS1)

**Why this routing**:
- Issue appears to be account-specific rather than system-wide
- May require customer account access/changes
- Likely resolvable through standard support procedures

**For faster resolution**:
1. Contact Customer Support at: [contact info]
2. Reference this ticket: {ticket_key}
3. They can escalate to engineering if needed

**When to use Engineering Portal**:
- System-wide problems affecting multiple users
- Technical bugs requiring code changes
- New feature requests for development
- Infrastructure/performance issues

Thank you for using our support system!
```

#### Template RT2: Route to DevOps/Infrastructure
```
**↗️ ROUTING RECOMMENDATION - INFRASTRUCTURE TEAM**

Your ticket describes an infrastructure or system performance issue.

**Quality Score**: {score}/10

**Recommended routing**: DevOps/Infrastructure Team

**Why this routing**:
{specific_infrastructure_indicators}

**Your ticket will be transferred with this information**:
- Original ticket details
- Validation assessment
- Recommended priority level

**Infrastructure team will**:
1. Investigate system performance/availability
2. Check server logs and monitoring
3. Coordinate any necessary maintenance
4. Provide updates on resolution

**Expected response time**: Infrastructure issues typically receive response within {sla_time}

No action needed from you - the infrastructure team will take over from here.
```

---

### 5. SPECIAL SITUATION Templates

#### Template S1: Emergency/Production Down
```
**🚨 EMERGENCY ESCALATION - PRODUCTION ISSUE**

Your ticket indicates a critical production problem.

**IMMEDIATE ACTIONS**:
1. ✅ Escalated to on-call engineering team
2. ✅ Infrastructure team notified
3. ✅ Management alerted

**Response Timeline**: 
- Initial response: Within 15 minutes
- Status updates: Every 30 minutes
- Resolution target: 2-4 hours depending on scope

**Contact Information**:
- Emergency hotline: [phone number]
- Real-time updates: [status page]
- Direct escalation: [manager contact]

**Your ticket quality**: {score}/10
Note: Emergency issues bypass normal validation requirements

**What happens next**:
1. Engineering team will contact you directly
2. They may need additional information quickly
3. Please remain available for rapid response

Thank you for the urgent alert!
```

#### Template S2: Feature Request Guidance
```
**💡 FEATURE REQUEST IDENTIFIED**

Your submission appears to be a feature request rather than a bug report.

**Quality Score**: {score}/10 (for bug context)

**Feature Request Process**:
1. **Product Planning**: Feature requests go through product review
2. **Business Case**: Need justification and user impact analysis  
3. **Planning Cycle**: Features are evaluated for upcoming releases
4. **Timeline**: Feature delivery typically takes 1-3 months minimum

**To improve your feature request**:
- **Business justification**: Why is this needed? What problem does it solve?
- **User impact**: How many users would benefit?
- **Current workarounds**: How are users handling this today?
- **Success criteria**: How would you measure successful implementation?

**Next Steps**:
1. Your request will be reviewed by the product team
2. You'll receive updates on planning decisions
3. If approved, it enters the development backlog

**Note**: Critical bug fixes take priority over feature requests.
```

---

## Template Usage Guidelines

### Selection Logic
```bash
IF score >= 9: Use Template A1
ELIF score >= 7: Use Template A2  
ELIF score >= 5: Use appropriate Template C* based on missing elements
ELIF score >= 3: Use appropriate Template R* based on major gaps
ELSE: Use appropriate Template RT* for routing

# Special cases override normal scoring
IF emergency_keywords: Use Template S1
IF feature_request_indicators: Use Template S2
IF security_keywords: Use Template R3
```

### Customization Variables
- `{score}`: Calculated quality score
- `{specific_suggestions}`: Targeted improvement items
- `{timeline}`: Estimated response time
- `{team}`: Assigned engineering team
- `{ticket_key}`: JIRA ticket identifier
- `{current_summary}`: Original ticket summary
- `{specific_requirements_list}`: Itemized missing elements

### Follow-up Actions
- **Approved tickets**: Assign to appropriate team queue
- **Clarification requests**: Set ticket status to "Waiting for customer"
- **Revision requests**: Add "needs_revision" label
- **Routed tickets**: Transfer to appropriate project
- **Emergency escalations**: Trigger immediate notification workflow

### Quality Monitoring
- Track template effectiveness by response rates
- Monitor time-to-resolution after feedback provided
- Survey submitters on feedback helpfulness
- Adjust templates based on common patterns and user feedback