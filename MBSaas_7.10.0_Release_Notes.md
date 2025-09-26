# MBSaas 7.10.0 Release Notes
*Release Date: TBD*

## Executive Summary

MBSaas 7.10.0 represents a significant advancement in payment processing reliability and customer portal functionality. This release introduces a comprehensive overhaul of our payment architecture, delivering enhanced transaction stability, proactive error handling, and an improved customer experience across all portal versions.

**Key Highlights:**
- ✅ **Payment System Modernization**: New unified payment processing architecture with enhanced reliability for split transactions
- ✅ **Proactive Gateway Monitoring**: Real-time health checks for Paya and Heartland payment processors
- ✅ **Intelligent Customer Portal Management**: Automatic version routing and enhanced control options
- ✅ **Enhanced User Experience**: Improved error messaging and streamlined interfaces

---

## 🔧 Payment Processing Excellence

### Major Payment System Overhaul
**Core Enhancement (SAAS-1354)**
This release introduces a revolutionary new payment processing architecture built around "Purchasers" - a unified business logic framework that dramatically improves the handling of complex payment scenarios.

**Key Improvements:**
- ✅ **Resolved Split Transaction Issues**: Fixed critical problems where convenience fees were declined while base amounts were accepted
- ✅ **Enhanced Gateway Health Monitoring**: Added comprehensive health status indicators for Paya payment gateways (joining existing Heartland monitoring)
- ✅ **Intelligent Payment Button Management**: Payment buttons automatically hide when gateway issues are detected and reappear when resolved
- ✅ **Optimized Performance**: Streamlined data handling with 90-day Remote Charges view and 18-month payment history display
- ✅ **Hourly Health Updates**: Automatic gateway status refresh ensures real-time payment system visibility

### Payment Reliability Enhancements
**Resolved Critical Issues:**
- **SAAS-1768**: Fixed edge cases in Paya payment processing for transactions over $100 with non-absorb gateway profiles
- **SAAS-1706**: Resolved merchant configuration errors that prevented convenience fee calculations in specific environments
- **SAAS-1858**: Fixed convenience fees getting stuck in "Processing" status when base charges fail
- **SAAS-2165**: Restored missing convenience fees in Heartland eCheck transactions

### Improved Error Handling
**SAAS-1725**: Enhanced Customer Portal Experience
- ✅ **User-Friendly Messages**: When payment gateways are temporarily unavailable, customers now see clear, helpful messages instead of technical errors
- ✅ **Automatic Button Management**: Payment options are intelligently hidden during service interruptions to prevent failed attempts
- ✅ **Better Communication**: Informative status messages help customers understand when to retry their payments

---

## 🖥️ Customer Portal Enhancements

### Intelligent Portal Version Management
**SAAS-536**: Smart Version Redirects
- ✅ **Automatic Routing**: Customers are seamlessly redirected to their designated portal version
- ✅ **Bookmark Protection**: Eliminates confusion from accessing incorrect portal versions
- ✅ **Zero Manual Intervention**: No customer action required for proper portal access

**SAAS-1193**: Complete Portal Control
- ✅ **"Disabled" Option**: Companies can now completely turn off customer portal access
- ✅ **Clear Messaging**: Customers see friendly messages when portal access is disabled
- ✅ **Easy Re-activation**: Portal access can be restored instantly by selecting any version

### Portal Display & Functionality Fixes
**SAAS-1751**: AutoPay Options Visibility
- ✅ **Consistent Access**: AutoPay management options remain visible regardless of payment settings
- ✅ **Improved User Experience**: Customers can reliably manage automatic payment preferences

**SAAS-1705 & SAAS-1951**: Payment History Accuracy
- ✅ **Corrected Display**: Failed charges no longer incorrectly appear as successful in customer history
- ✅ **Complete History**: Fixed missing failed charges in payment history displays

### Administrative Interface Improvements
**SAAS-571**: Multifamily Rate Management
- ✅ **Streamlined Interface**: Enhanced rate copying process in System Info → Rates
- ✅ **Context-Aware Controls**: "Copy Rate to Companies" button only appears when relevant
- ✅ **Error Prevention**: Redesigned workflow reduces confusion and copying mistakes

---

## 🛠️ Technical Improvements

### New Administrative Tools
- **Charge Explorer**: New admin diagnostic tool for Level 2+ administrators to troubleshoot payment issues (DevOps use only)
- **Enhanced Gateway Profiles**: Real-time health status indicators on payment gateway configuration screens

### Performance Optimizations
- **Streamlined Data Views**: 90-day limit on Remote Charges Needing Attention for improved performance
- **Optimized History**: 18-month limit on online payment history with option to request historical data from Analytics team

### Architecture Enhancements
- **Unified Payment Logic**: New "Purchasers" framework consolidates payment processing business rules
- **Merchant-Specific Health Checks**: Paya gateway monitoring validates individual merchant connectivity
- **Proactive Error Prevention**: System-wide improvements to detect and handle payment gateway issues before they impact customers

---

## 🧪 Quality Assurance

### Comprehensive Testing
- **SAAS-1810, 1811**: Extensive staging environment validation
- **Full Regression Testing**: Payment Gateway Profile (PGP) complete regression suite
- **Multi-Environment Validation**: Testing across various company configurations and payment scenarios

---

## 📊 Resolved Issues Summary

| Category | Issues Resolved | Key Benefits |
|----------|----------------|--------------|
| **Payment Processing** | 8 critical fixes | Enhanced transaction reliability, better error handling |
| **Customer Portal** | 6 improvements | Improved user experience, better access control |
| **Administrative Tools** | 3 enhancements | Better troubleshooting, streamlined workflows |
| **Performance** | 2 optimizations | Faster page loads, improved system responsiveness |

---

## 🚀 Looking Forward

This release establishes a solid foundation for future payment processing enhancements and customer portal innovations. The new "Purchasers" architecture enables rapid development of additional payment features, while the enhanced monitoring capabilities ensure continued system reliability.

**Next Steps:**
- Monitor payment processing performance metrics
- Gather customer feedback on portal experience improvements
- Analyze gateway health monitoring data for optimization opportunities

---

## 📞 Support Information

For technical questions about this release, please contact:
- **Engineering Team**: For payment processing or gateway issues
- **Analytics Team**: For historical payment data requests (beyond current 18-month display limit)
- **DevOps Team**: For gateway health monitoring or system status questions

---

*This release represents the collaborative effort of our Engineering, QA, and DevOps teams to deliver enhanced payment reliability and improved customer experience across the MBSaas platform.*