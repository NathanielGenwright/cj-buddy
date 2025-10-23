# JIRA Triage Quality Validation Rubric
## Engineering Portal (EP) Project

### Overview
This rubric provides standardized criteria for evaluating Engineering Portal tickets before they enter the engineering workflow. It ensures tickets contain sufficient information for effective troubleshooting and resolution.

---

## Quality Scoring Matrix

### Score Ranges
- **9.5-10**: **APPROVE** - Perfect quality, ready for engineering backlog
- **9.0-9.4**: **APPROVE** - Excellent quality, ready for engineering backlog
- **8.5-8.9**: **APPROVE_WITH_NOTES** - Very good quality, minor clarifications helpful
- **8.0-8.4**: **APPROVE_WITH_NOTES** - Good quality, minor clarifications helpful  
- **7.5-7.9**: **APPROVE_WITH_NOTES** - Acceptable quality, some clarifications helpful
- **7.0-7.4**: **APPROVE_WITH_NOTES** - Marginal quality, clarifications recommended
- **5-6**: **NEEDS_CLARIFICATION** - Specific items requested
- **3-4**: **REQUEST_REVISION** - Major restructuring needed
- **1-2**: **ROUTE_ELSEWHERE** - May belong in different queue

---

## Evaluation Criteria

### Tier 1: Critical Required Fields (40 points total)

#### 1. Summary Quality (10 points)
- **10 points**: Descriptive, specific summary that clearly indicates the problem
- **9.5 points**: Very descriptive and specific, minor refinement possible
- **9.0 points**: Clear and specific with good problem indication
- **8.5 points**: Generally clear and specific with minor gaps
- **8.0 points**: Clear but could be more specific
- **7.5 points**: Reasonably clear but lacks some specificity
- **7.0 points**: Generally clear but could be more specific
- **4 points**: Vague but indicates problem area
- **1 point**: Generic or unclear (e.g., "Tech Help", "Issue")
- **0 points**: Missing or meaningless

#### 2. Problem Description Structure (10 points)
- **10 points**: Well-structured with clear sections (Problem, Environment, Steps, Impact)
- **9.5 points**: Very well-structured with nearly all key sections present
- **9.0 points**: Well-structured with most key sections clear
- **8.5 points**: Good structure with most key sections, minor gaps
- **8.0 points**: Good structure with most key sections
- **7.5 points**: Reasonable structure with some key sections
- **7.0 points**: Basic good structure but missing some key sections
- **4 points**: Basic structure but missing key elements
- **1 point**: Unstructured but contains useful information
- **0 points**: Missing or incoherent

#### 3. Error Messages/Evidence (10 points)
- **10 points**: Exact error messages with screenshots or verbatim text
- **9.5 points**: Very detailed error messages with good supporting evidence
- **9.0 points**: Specific error messages with some supporting evidence
- **8.5 points**: Specific error descriptions with minor accuracy issues
- **8.0 points**: Specific error descriptions, mostly accurate
- **7.5 points**: Good error descriptions with reasonable accuracy
- **7.0 points**: Basic specific error descriptions
- **4 points**: General error descriptions but unclear
- **1 point**: Mentions errors but no specifics
- **0 points**: No error information provided

#### 4. Business Impact Assessment (10 points)
- **10 points**: Clear impact, affected users count, urgency indicators
- **9.5 points**: Very clear impact with most metrics and good urgency assessment
- **9.0 points**: Clear impact with good metrics and urgency indicators
- **8.5 points**: Good impact description with most metrics
- **8.0 points**: Good impact description with some metrics
- **7.5 points**: Reasonable impact description with basic metrics
- **7.0 points**: Basic good impact description
- **4 points**: Basic impact statement without structured assessment
- **1 point**: Mentions impact but lacks MuniBilling assessment criteria
- **0 points**: No business impact described

**MuniBilling Impact Assessment Criteria:**
- Number of users affected (specific count preferred)
- Criticality of affected workflows (billing, payment, customer service)
- Financial implications (revenue loss, transaction impacts)
- Disruption to billing process (timeline, dependencies)
- Legal or regulatory compliance risks

### Tier 2: Important for Efficiency (30 points total)

#### 5. Environment Details (10 points)
- **10 points**: Browser, OS, device, network context all provided
- **7 points**: Most environment details provided
- **4 points**: Some environment context
- **1 point**: Minimal environment information
- **0 points**: No environment details

#### 6. Reproduction Steps (10 points)
- **10 points**: Clear step-by-step reproduction sequence
- **7 points**: Good reproduction steps with minor gaps
- **4 points**: Basic steps provided
- **1 point**: Mentions process but unclear
- **0 points**: No reproduction information

#### 7. Troubleshooting Attempted (10 points)
- **10 points**: Detailed list of troubleshooting already performed
- **7 points**: Good troubleshooting summary
- **4 points**: Some troubleshooting mentioned
- **1 point**: Basic mention of attempts
- **0 points**: No troubleshooting information

### Tier 3: Helpful for Prioritization (30 points total)

#### 8. Account/System Context (10 points)
- **10 points**: Clear system identification, user role, company context
- **7 points**: Good context with minor gaps
- **4 points**: Basic system/user information
- **1 point**: Minimal context provided
- **0 points**: No context given

#### 9. Timing Information (10 points)
- **10 points**: Clear timeline of when issue started, frequency patterns
- **7 points**: Good timing information
- **4 points**: Basic timing details
- **1 point**: Vague timing references
- **0 points**: No timing information

#### 10. Supporting Documentation (10 points)
- **10 points**: Screenshots, logs, or detailed supporting evidence
- **7 points**: Good supporting information
- **4 points**: Some supporting details
- **1 point**: Minimal supporting information
- **0 points**: No supporting documentation

---

## Validation Actions by Score Range

### 9.5-10 Points: APPROVE ✅
- **Action**: Move to engineering backlog immediately
- **Routing**: Assign to appropriate team based on component
- **Timeline**: Ready for immediate planning/sprint inclusion
- **Quality**: Perfect documentation standard

### 9.0-9.4 Points: APPROVE ✅
- **Action**: Move to engineering backlog
- **Routing**: Assign to appropriate team based on component
- **Timeline**: Ready for immediate planning/sprint inclusion
- **Quality**: Excellent documentation standard

### 8.5-8.9 Points: APPROVE_WITH_NOTES ✅
- **Action**: Move to backlog with very minor clarification suggestions
- **Routing**: Assign with optional clarification items noted
- **Timeline**: No delays, clarifications can be gathered during development
- **Quality**: Very good documentation standard

### 8.0-8.4 Points: APPROVE_WITH_NOTES ✅
- **Action**: Move to backlog with minor clarification requests
- **Routing**: Assign with specific clarification items noted
- **Timeline**: Minor delays acceptable for quick clarifications
- **Quality**: Good documentation standard

### 7.5-7.9 Points: APPROVE_WITH_NOTES ✅
- **Action**: Move to backlog with clarification requests
- **Routing**: Assign with multiple clarification items noted
- **Timeline**: Some delays expected for clarifications
- **Quality**: Acceptable documentation standard

### 7.0-7.4 Points: APPROVE_WITH_NOTES ⚠️
- **Action**: Move to backlog with significant clarification requests
- **Routing**: Assign with detailed clarification requirements
- **Timeline**: Delays expected for substantial clarifications
- **Quality**: Marginal documentation standard

### 5-6 Points: NEEDS_CLARIFICATION ⚠️
- **Action**: Request specific missing information
- **Routing**: Return to reporter with checklist of needed items
- **Timeline**: Block progression until clarifications provided
- **Template**: Use standardized clarification request templates

### 3-4 Points: REQUEST_REVISION ❌
- **Action**: Major restructuring required
- **Routing**: May route to Customer Success (CSS1) for information gathering
- **Timeline**: Significant delay expected
- **Template**: Provide structure template and examples

### 1-2 Points: ROUTE_ELSEWHERE ↗️
- **Action**: Evaluate if ticket belongs in Engineering Portal
- **Routing**: Consider Customer Service, Sales, or other projects
- **Timeline**: Remove from engineering queue
- **Template**: Provide guidance on proper routing

---

## Special Routing Rules

### By Issue Type
- **Authentication/Security**: Flag for security team review if score ≥ 6
- **Infrastructure**: Route to DevOps if system-wide impact
- **Integration Issues**: Route to Backend team if API-related
- **UI/UX Problems**: Route to Frontend team if interface-related

### By Priority Indicators
- **Production Down**: Emergency routing regardless of documentation quality
- **Security Incident**: Immediate escalation with parallel documentation improvement
- **Multiple Users Affected**: Higher priority even with documentation gaps

### By Reporter Type
- **Internal Staff**: More lenient scoring, faster clarification turnaround
- **Customer Users**: Standard scoring, provide clear guidance templates
- **External Partners**: Strict scoring, ensure proper communication channels

---

## Implementation Guidelines

### Automated Checks
- Summary length and specificity analysis
- Description structure validation
- Error message pattern detection
- Environment detail completeness

### Manual Review Triggers
- Scores 4-6 require human validation
- Security-related keywords trigger manual review
- High-priority items bypass some automation

### Feedback Templates
- Standardized responses for each score range
- Specific checklists for common missing elements
- Examples of well-documented tickets for reference

### Monitoring Metrics
- Average ticket quality scores over time
- Time-to-clarification for tickets needing revision
- Re-submission success rates after feedback
- Engineering team satisfaction with ticket quality

---

## Quality Improvement Process

### For Reporters
1. **Self-Assessment**: Provide rubric for self-evaluation before submission
2. **Templates**: Offer structured templates for common issue types
3. **Training**: Regular sessions on effective ticket documentation

### For Triage Team
1. **Consistency**: Regular calibration sessions using this rubric
2. **Feedback**: Track which clarifications are most effective
3. **Iteration**: Monthly rubric updates based on patterns and feedback

### Success Criteria
- **Target Score**: 80% of tickets scoring 7+ within 90 days
- **Revision Rate**: <20% of tickets requiring major revision
- **Engineering Satisfaction**: >90% satisfaction with ticket quality
- **Time Efficiency**: Average triage time <5 minutes per ticket