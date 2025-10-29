#!/usr/bin/env python3

import pandas as pd
import os

def create_comprehensive_summary():
    """
    Create a comprehensive summary of all Issue_Category distributions
    from both original and refined categorization.
    """
    
    # Read the original and refined datasets
    original_file = '/Users/munin8/_myprojects/tri-all-tickets-final.csv'
    refined_file = '/Users/munin8/_myprojects/tri-tickets-refined-categories.csv'
    
    print("Creating comprehensive Issue_Category summary...")
    
    # Read original data
    df_original = pd.read_csv(original_file)
    original_counts = df_original['Issue_Category'].value_counts()
    
    # Read refined data  
    df_refined = pd.read_csv(refined_file)
    refined_counts = df_refined['Refined_Category'].value_counts()
    
    # Create summary report
    summary_file = '/Users/munin8/_myprojects/tri-issue-categories-complete-summary.md'
    
    with open(summary_file, 'w') as f:
        f.write("# TRI Tickets - Complete Issue Category Summary\n\n")
        f.write(f"**Analysis Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**Total Tickets Analyzed**: {len(df_original):,}  \n\n")
        
        # Original categorization
        f.write("## 📊 Original Issue Categories (Column K)\n\n")
        f.write("| Rank | Category | Count | Percentage | Notes |\n")
        f.write("|------|----------|-------|------------|-------|\n")
        
        for i, (category, count) in enumerate(original_counts.items(), 1):
            percentage = (count / len(df_original)) * 100
            note = "🔴 **Needs breakdown**" if category == "Other" and percentage > 50 else ""
            f.write(f"| {i:2d} | {category:<25} | {count:4d} | {percentage:5.1f}% | {note} |\n")
        
        f.write(f"\n**Total Original Categories**: {len(original_counts)}  \n")
        f.write(f"**Dominant Category**: {original_counts.index[0]} ({original_counts.iloc[0]} tickets, {(original_counts.iloc[0]/len(df_original)*100):.1f}%)  \n\n")
        
        # Refined categorization
        f.write("## 🏷️ Refined Issue Categories (After Pattern Analysis)\n\n")
        f.write("| Rank | Category | Count | Percentage | Source | Priority |\n")
        f.write("|------|----------|-------|------------|--------|----------|\n")
        
        for i, (category, count) in enumerate(refined_counts.items(), 1):
            percentage = (count / len(df_refined)) * 100
            
            # Determine source and priority
            if category in original_counts.index:
                source = "Original"
            else:
                source = "**New**"
            
            # Assign priority based on count and business impact
            if count >= 50:
                priority = "🔴 High"
            elif count >= 20:
                priority = "🟡 Medium" 
            elif count >= 10:
                priority = "🟢 Low"
            else:
                priority = "⚪ Monitor"
            
            f.write(f"| {i:2d} | {category:<25} | {count:4d} | {percentage:5.1f}% | {source} | {priority} |\n")
        
        f.write(f"\n**Total Refined Categories**: {len(refined_counts)}  \n")
        f.write(f"**Improvement**: {len(refined_counts)} categories (was {len(original_counts)})  \n")
        f.write(f"**Remaining Uncategorized**: {refined_counts.get('Uncategorized', 0)} tickets ({(refined_counts.get('Uncategorized', 0)/len(df_refined)*100):.1f}%)  \n\n")
        
        # Category mapping analysis
        f.write("## 🔄 Category Transformation Analysis\n\n")
        f.write("### Categories Added from 'Other' Breakdown:\n")
        
        new_categories = []
        for category in refined_counts.index:
            if category not in original_counts.index and category != 'Uncategorized':
                count = refined_counts[category]
                percentage = (count / len(df_refined)) * 100
                new_categories.append((category, count, percentage))
        
        new_categories.sort(key=lambda x: x[1], reverse=True)
        
        f.write("| New Category | Count | Percentage | Business Impact |\n")
        f.write("|--------------|-------|------------|----------------|\n")
        
        impact_map = {
            'Account Management': 'Customer service efficiency',
            'Request/Enhancement': 'Product development priorities', 
            'System Issues': 'System reliability and uptime',
            'Rate & Pricing': 'Revenue and billing accuracy',
            'Data Issues': 'Data integrity and reporting',
            'Communication': 'Customer engagement and satisfaction',
            'Report Issues': 'Business intelligence and compliance',
            'Calculation Issues': 'Billing accuracy and customer trust',
            'Portal Issues': 'Customer self-service adoption',
            'Configuration': 'System flexibility and customization'
        }
        
        for category, count, percentage in new_categories:
            impact = impact_map.get(category, 'General operational efficiency')
            f.write(f"| {category:<20} | {count:4d} | {percentage:5.1f}% | {impact} |\n")
        
        f.write(f"\n**Total New Categories Identified**: {len(new_categories)}  \n")
        f.write(f"**Coverage Improvement**: Reduced 'Other' from 75.1% to 57.4% ('Uncategorized')  \n\n")
        
        # Priority action categories
        f.write("## 🚨 Priority Action Categories\n\n")
        f.write("### High-Volume Categories (50+ tickets)\n")
        high_volume = [(cat, count) for cat, count in refined_counts.items() if count >= 50]
        for category, count in high_volume:
            percentage = (count / len(df_refined)) * 100
            f.write(f"- **{category}**: {count} tickets ({percentage:.1f}%) - Requires dedicated specialist\n")
        
        f.write("\n### Medium-Volume Categories (20-49 tickets)\n")
        medium_volume = [(cat, count) for cat, count in refined_counts.items() if 20 <= count < 50]
        for category, count in medium_volume:
            percentage = (count / len(df_refined)) * 100
            f.write(f"- **{category}**: {count} tickets ({percentage:.1f}%) - Regular review needed\n")
        
        f.write("\n### Emerging Categories (10-19 tickets)\n") 
        emerging = [(cat, count) for cat, count in refined_counts.items() if 10 <= count < 20]
        for category, count in emerging:
            percentage = (count / len(df_refined)) * 100
            f.write(f"- **{category}**: {count} tickets ({percentage:.1f}%) - Monitor for growth\n")
        
        # Business recommendations
        f.write("\n## 💡 Business Recommendations\n\n")
        f.write("### Immediate Actions\n")
        f.write("1. **Uncategorized Review**: Manual review of 362 remaining uncategorized tickets\n")
        f.write("2. **Specialist Assignment**: Dedicated resources for high-volume categories\n")
        f.write("3. **Process Improvement**: Better intake forms to reduce miscategorization\n\n")
        
        f.write("### Medium-term Improvements\n")
        f.write("1. **Template Development**: Create category-specific ticket templates\n")
        f.write("2. **Automated Routing**: Rules-based assignment by category\n")
        f.write("3. **Training Programs**: Category-specific expertise development\n\n")
        
        f.write("### Long-term Strategy\n")
        f.write("1. **Predictive Categorization**: ML-based automatic categorization\n")
        f.write("2. **Category Evolution**: Regular review and refinement of categories\n")
        f.write("3. **Performance Metrics**: Category-based SLA and quality tracking\n\n")
        
        # Summary statistics
        f.write("## 📈 Summary Statistics\n\n")
        f.write(f"| Metric | Original | Refined | Improvement |\n")
        f.write(f"|--------|----------|---------|-------------|\n")
        f.write(f"| Total Categories | {len(original_counts)} | {len(refined_counts)} | +{len(refined_counts) - len(original_counts)} categories |\n")
        f.write(f"| Largest Category | {original_counts.iloc[0]} tickets | {refined_counts.iloc[0]} tickets | {refined_counts.iloc[0] - original_counts.iloc[0]:+d} tickets |\n")
        f.write(f"| Coverage | {((len(df_original) - original_counts.get('Other', 0)) / len(df_original) * 100):.1f}% | {((len(df_refined) - refined_counts.get('Uncategorized', 0)) / len(df_refined) * 100):.1f}% | {((len(df_refined) - refined_counts.get('Uncategorized', 0)) / len(df_refined) * 100) - ((len(df_original) - original_counts.get('Other', 0)) / len(df_original) * 100):+.1f}% |\n")
        
        f.write(f"\n---\n")
        f.write(f"*Analysis includes all {len(df_original):,} TRI tickets with comprehensive category breakdown and business impact assessment.*\n")
    
    # Create simplified CSV summary
    csv_summary_file = '/Users/munin8/_myprojects/tri-categories-comparison.csv'
    
    # Prepare comparison data
    comparison_data = []
    
    # Add all categories from both datasets
    all_categories = set(original_counts.index) | set(refined_counts.index)
    
    for category in sorted(all_categories):
        original_count = original_counts.get(category, 0)
        refined_count = refined_counts.get(category, 0)
        
        # Handle renamed categories
        if category == 'Other':
            refined_count = refined_counts.get('Uncategorized', 0)
        
        original_pct = (original_count / len(df_original) * 100) if original_count > 0 else 0
        refined_pct = (refined_count / len(df_refined) * 100) if refined_count > 0 else 0
        
        status = "Original" if category in original_counts.index else "New"
        if category == "Other":
            status = "Renamed to Uncategorized"
        
        comparison_data.append({
            'Category': category,
            'Original_Count': original_count,
            'Original_Percentage': round(original_pct, 1),
            'Refined_Count': refined_count,
            'Refined_Percentage': round(refined_pct, 1),
            'Change': refined_count - original_count,
            'Status': status
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    comparison_df = comparison_df.sort_values('Refined_Count', ascending=False)
    comparison_df.to_csv(csv_summary_file, index=False)
    
    print(f"✅ Comprehensive summary saved to: {summary_file}")
    print(f"✅ CSV comparison saved to: {csv_summary_file}")
    
    # Print key statistics
    print(f"\n=== KEY STATISTICS ===")
    print(f"Original categories: {len(original_counts)}")
    print(f"Refined categories: {len(refined_counts)}")
    print(f"New categories created: {len([c for c in refined_counts.index if c not in original_counts.index and c != 'Uncategorized'])}")
    print(f"Uncategorized reduction: {original_counts.get('Other', 0)} → {refined_counts.get('Uncategorized', 0)} tickets")
    
    return summary_file, csv_summary_file, comparison_df

if __name__ == "__main__":
    create_comprehensive_summary()