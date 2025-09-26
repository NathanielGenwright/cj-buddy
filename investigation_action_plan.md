# PENALTY_DUE INVESTIGATION ACTION PLAN

## 🎯 **IMMEDIATE NEXT STEPS** (Next 1-2 Days)

### **Priority 1: Statement Analysis**
**Owner**: Development Team  
**Timeline**: 24 hours  

**Actions:**
1. **Generate PDF Statement** for customer 3178854
   - Use current data to create statement
   - Compare line-by-line with database values
   - Document where $838.29 appears on statement

2. **Enable Debug Logging**
   ```ruby
   # Add to deposit_charges.rb:156
   Rails.logger.debug "PENALTY DEBUG - Customer #{customer.id}: total_due=#{data.total_due}, penalty_amount=#{data.penalty_amount}, penalty_due=#{data.penalty_due}"
   
   # Add to email_manager.rb:253  
   Rails.logger.debug "EMAIL PENALTY DEBUG - Customer: penalty_due=#{@inner_data.penalty_due}"
   ```

3. **Run PrintStatementsJob** in debug mode for customer 3178854

**Expected Outcome**: Identify exact code path producing $838.29

---

### **Priority 2: Historical Data Deep Dive**
**Owner**: Database/Analytics Team  
**Timeline**: 24 hours

**Actions:**
1. **Complete Transaction Query**
   ```sql
   -- Get ALL transactions for customer
   SELECT 'bill' as type, id, bill_date as trans_date, amount, penalty_amount, penalty_applied, posted_customer
   FROM bills WHERE customer_id = 3178854
   UNION ALL  
   SELECT 'payment' as type, id, payment_date, amount, 0, 0, 1
   FROM payments WHERE customer_id = 3178854
   ORDER BY trans_date DESC, id DESC;
   ```

2. **Penalty Application History**
   ```sql
   -- Check penalty application timeline
   SELECT id, bill_date, penalty_date, penalty_amount, penalty_applied, 
          amount, posted_customer, created_at, updated_at
   FROM bills 
   WHERE customer_id = 3178854 
   AND penalty_amount > 0
   ORDER BY penalty_date, created_at;
   ```

3. **Balance Reconciliation**
   - Manually calculate balance from transaction history
   - Compare with customers.balance_current ($296.59)
   - Identify any discrepancies

**Expected Outcome**: Verify if historical data explains $266.93 gap

---

## 📊 **WEEK 1 INVESTIGATIONS**

### **Code Path Analysis**
**Owner**: Senior Development  
**Timeline**: 3 days

**Tasks:**
1. **Trace Complete Billing Workflow**
   - Document penalty calculation at each step
   - Map data flow from bills → statement generation
   - Identify all penalty modification points

2. **Print Helper Investigation**
   ```ruby
   # Check print_helper_common.rb:7
   def self.get_penalty_b_total(company, usage_bill_data)
     if company.is?(Company::LANSFORD_SEWAGE)
       return nil unless usage_bill_data.penalty_due > 0
       number_to_currency(usage_bill_data.penalty_due + 25)  # ← Lansford specific!
   ```

3. **Statement Template Analysis**
   - Review .erb templates for penalty field display
   - Check for any penalty amount modifications in views
   - Verify penalty_due vs penalty_due_amount usage

### **System Integration Review**
**Owner**: DevOps/Integration Team  
**Timeline**: 5 days

**Tasks:**
1. **Third-Party Integration Check**
   - Review payment gateway penalty handling
   - Check QuickBooks export penalty calculations  
   - Verify no external systems modifying penalties

2. **Caching Investigation**
   - Check for cached penalty calculations
   - Verify statement generation uses fresh data
   - Clear relevant caches and re-test

3. **Environment Differences**
   - Compare penalty calculations dev vs production
   - Check for environment-specific penalty overrides
   - Verify data consistency across environments

---

## 🧪 **TESTING STRATEGY**

### **Regression Testing**
1. **Create test case** with customer 3178854 data
2. **Set up penalty calculation unit tests** for all methods
3. **Add integration test** for complete billing workflow
4. **Validate penalty calculations** across different customer scenarios

### **Edge Case Testing**
1. **Multiple billing cycles** with unpaid penalties
2. **Returned payments** affecting penalty calculations
3. **Rate changes** mid-billing period
4. **Company configuration changes** impact

---

## 🚨 **ESCALATION CRITERIA**

### **Escalate to Senior Management if:**
1. **Customer Impact**: Additional customers affected
2. **Data Integrity**: Database corruption suspected
3. **Financial Impact**: Significant over/under-charging discovered
4. **Timeline**: Investigation extends beyond 1 week

### **Escalate to Vendor if:**
1. **Core System Bug**: Issue in billing engine core
2. **Database Issue**: MySQL-specific penalty calculation problem
3. **Integration Issue**: Third-party system causing penalty errors

---

## 📋 **DOCUMENTATION REQUIREMENTS**

### **During Investigation:**
1. **Log all SQL queries** and results
2. **Document code changes** made for debugging
3. **Record timeline** of investigation steps
4. **Capture screenshots** of statements/interfaces

### **Upon Resolution:**
1. **Root cause analysis** document
2. **Fix implementation** details
3. **Prevention measures** to avoid recurrence
4. **Knowledge base update** for support team

---

## 👥 **TEAM ROLES & RESPONSIBILITIES**

### **Development Team:**
- Code analysis and debugging
- Log analysis and tracing
- Fix implementation
- Unit test creation

### **Database Team:**
- Data integrity verification
- Complex query optimization
- Historical data analysis
- Performance impact assessment

### **QA Team:**
- Test case creation
- Regression testing
- Edge case validation
- User acceptance testing

### **Support Team:**
- Customer communication
- Issue documentation
- Solution validation
- Knowledge base maintenance

---

## 📈 **SUCCESS METRICS**

### **Investigation Success:**
- [ ] Root cause identified within 48 hours
- [ ] $838.29 source code location found
- [ ] Gap explanation documented

### **Resolution Success:**
- [ ] Penalty calculation matches expected $571.36
- [ ] No regression in other customers
- [ ] Automated tests prevent recurrence
- [ ] Customer receives corrected statement

### **Process Success:**
- [ ] Investigation methodology documented
- [ ] Team knowledge enhanced
- [ ] Similar issues preventable
- [ ] Response time improved for future issues

**This action plan provides clear next steps while maintaining investigation momentum and ensuring comprehensive problem resolution.**