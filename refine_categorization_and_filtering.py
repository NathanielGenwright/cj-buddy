#!/usr/bin/env python3

import pandas as pd
import re
from collections import Counter
import os

def analyze_other_category_patterns():
    """
    Analyze the 'Other' category tickets to identify patterns for better categorization.
    Also create urgency and quality-based filtering.
    """
    
    # Read the CSV file
    input_file = '/Users/munin8/_myprojects/tri-all-tickets-final.csv'
    
    print("Reading tri-all-tickets-final.csv...")
    df = pd.read_csv(input_file)
    
    print(f"Total tickets loaded: {len(df)}")
    
    # Filter for 'Other' category tickets
    other_tickets = df[df['Issue_Category'] == 'Other']
    print(f"'Other' category tickets: {len(other_tickets)}")
    
    # Analyze summaries for patterns
    print(f"\n=== ANALYZING 'OTHER' CATEGORY PATTERNS ===")
    
    # Extract keywords from summaries
    all_summaries = ' '.join(other_tickets['Summary'].fillna('').str.lower())
    
    # Define refined categorization patterns
    categorization_patterns = {
        'Account Management': [
            'account', 'customer', 'user', 'contact', 'admin', 'permission', 'access',
            'login', 'password', 'authentication'
        ],
        'Report Issues': [
            'report', 'statement', 'invoice', 'receipt', 'export', 'pdf', 'print'
        ],
        'Rate & Pricing': [
            'rate', 'pricing', 'charge', 'fee', 'tier', 'surcharge', 'discount', 'tax'
        ],
        'Communication': [
            'email', 'notice', 'notification', 'mail', 'communication', 'reminder',
            'alert', 'message'
        ],
        'Configuration': [
            'config', 'setup', 'setting', 'template', 'format', 'layout', 'display',
            'customize', 'global'
        ],
        'Data Issues': [
            'import', 'export', 'transfer', 'sync', 'data', 'file', 'update',
            'duplicate', 'missing'
        ],
        'System Issues': [
            'error', 'bug', 'issue', 'problem', 'fix', 'broken', 'not working',
            'failure', 'crash', 'slow'
        ],
        'Calculation Issues': [
            'calculation', 'calculating', 'calculate', 'reads', 'reading', 'meter',
            'usage', 'consumption', 'billing'
        ],
        'Portal Issues': [
            'portal', 'website', 'online', 'web', 'browser', 'mobile', 'app'
        ],
        'Request/Enhancement': [
            'request', 'enhance', 'improve', 'add', 'create', 'new', 'feature',
            'modification', 'change'
        ]
    }
    
    # Apply refined categorization
    def refined_categorize(summary):
        summary_lower = str(summary).lower()
        
        # Score each category based on keyword matches
        category_scores = {}
        for category, keywords in categorization_patterns.items():
            score = sum(1 for keyword in keywords if keyword in summary_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return the category with highest score, or 'Uncategorized' if no matches
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        else:
            return 'Uncategorized'
    
    # Apply refined categorization to all tickets
    df['Refined_Category'] = df['Summary'].apply(refined_categorize)
    
    # For tickets that were already properly categorized, keep original
    mask = df['Issue_Category'] != 'Other'
    df.loc[mask, 'Refined_Category'] = df.loc[mask, 'Issue_Category']
    
    # Analyze refined categorization results
    print(f"\n=== REFINED CATEGORIZATION RESULTS ===")
    refined_counts = df['Refined_Category'].value_counts()
    
    for i, (category, count) in enumerate(refined_counts.items(), 1):
        percentage = (count / len(df)) * 100
        print(f"{i:2d}. {category:<25} | {count:4d} tickets ({percentage:5.1f}%)")
    
    return df, refined_counts

def create_urgency_quality_filters(df):
    """
    Create different filtering approaches based on urgency and quality scores.
    """
    
    print(f"\n=== CREATING URGENCY & QUALITY FILTERS ===")
    
    # Filter 1: Critical and High Urgency tickets
    urgent_tickets = df[df['Urgency'].isin(['Critical', 'High'])]
    print(f"Critical/High urgency tickets: {len(urgent_tickets)}")
    
    # Filter 2: Low quality tickets (TriQ Score < 5.0)
    low_quality_tickets = df[df['TriQ_Score'] < 5.0]
    print(f"Low quality tickets (TriQ < 5.0): {len(low_quality_tickets)}")
    
    # Filter 3: Very low quality tickets (TriQ Score < 4.0)
    very_low_quality_tickets = df[df['TriQ_Score'] < 4.0]
    print(f"Very low quality tickets (TriQ < 4.0): {len(very_low_quality_tickets)}")
    
    # Filter 4: High urgency AND low quality (double trouble)
    urgent_and_poor_quality = df[
        (df['Urgency'].isin(['Critical', 'High'])) & 
        (df['TriQ_Score'] < 5.0)
    ]
    print(f"Urgent + Low Quality tickets: {len(urgent_and_poor_quality)}")
    
    # Filter 5: Unassigned tickets (need immediate attention)
    unassigned_tickets = df[df['Assignee'].isna() | (df['Assignee'] == '')]
    print(f"Unassigned tickets: {len(unassigned_tickets)}")
    
    # Filter 6: SLA Risk tickets (Critical unassigned or urgent waiting)
    sla_risk_tickets = df[
        ((df['Urgency'] == 'Critical') & (df['Assignee'].isna() | (df['Assignee'] == ''))) |
        ((df['Urgency'] == 'High') & df['Status'].isin(['Waiting for customer', 'Waiting for support']))
    ]
    print(f"SLA Risk tickets: {len(sla_risk_tickets)}")
    
    # Filter 7: High-quality templates (TriQ Score >= 8.0)
    template_tickets = df[df['TriQ_Score'] >= 8.0]
    print(f"High-quality template tickets (TriQ >= 8.0): {len(template_tickets)}")
    
    # Filter 8: Action Required - Immediate (based on Action_Required field)
    immediate_action_tickets = df[df['Action_Required'].str.contains('URGENT|IMMEDIATELY', case=False, na=False)]
    print(f"Immediate action required tickets: {len(immediate_action_tickets)}")
    
    return {
        'urgent_tickets': urgent_tickets,
        'low_quality_tickets': low_quality_tickets,
        'very_low_quality_tickets': very_low_quality_tickets,
        'urgent_and_poor_quality': urgent_and_poor_quality,
        'unassigned_tickets': unassigned_tickets,
        'sla_risk_tickets': sla_risk_tickets,
        'template_tickets': template_tickets,
        'immediate_action_tickets': immediate_action_tickets
    }

def save_filtered_datasets(df, filters, refined_counts):
    """
    Save various filtered datasets to CSV files.
    """
    
    print(f"\n=== SAVING FILTERED DATASETS ===")
    
    # Save refined categorization dataset
    refined_file = '/Users/munin8/_myprojects/tri-tickets-refined-categories.csv'
    df.to_csv(refined_file, index=False)
    print(f"Refined categorization saved to: {refined_file}")
    
    # Save urgency/quality filtered datasets
    filter_files = {
        'urgent_tickets': '/Users/munin8/_myprojects/tri-tickets-urgent-priority.csv',
        'low_quality_tickets': '/Users/munin8/_myprojects/tri-tickets-low-quality.csv',
        'very_low_quality_tickets': '/Users/munin8/_myprojects/tri-tickets-very-low-quality.csv',
        'urgent_and_poor_quality': '/Users/munin8/_myprojects/tri-tickets-urgent-poor-quality.csv',
        'unassigned_tickets': '/Users/munin8/_myprojects/tri-tickets-unassigned.csv',
        'sla_risk_tickets': '/Users/munin8/_myprojects/tri-tickets-sla-risk.csv',
        'template_tickets': '/Users/munin8/_myprojects/tri-tickets-high-quality-templates.csv',
        'immediate_action_tickets': '/Users/munin8/_myprojects/tri-tickets-immediate-action.csv'
    }
    
    for filter_name, filename in filter_files.items():
        filter_df = filters[filter_name]
        filter_df.to_csv(filename, index=False)
        print(f"{filter_name:<25} ({len(filter_df):3d} tickets) -> {filename}")
    
    # Create comprehensive summary report
    summary_file = '/Users/munin8/_myprojects/tri-refined-analysis-summary.md'
    with open(summary_file, 'w') as f:
        f.write("# TRI Tickets - Refined Categorization & Filtering Analysis\n\n")
        f.write(f"**Analysis Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**Total Tickets**: {len(df)}  \n\n")
        
        f.write("## 🏷️ Refined Category Distribution\n\n")
        f.write("| Rank | Category | Count | Percentage |\n")
        f.write("|------|----------|-------|------------|\n")
        
        for i, (category, count) in enumerate(refined_counts.items(), 1):
            percentage = (count / len(df)) * 100
            f.write(f"| {i:2d} | {category:<20} | {count:4d} | {percentage:5.1f}% |\n")
        
        f.write("\n## 🎯 Priority Filtering Results\n\n")
        f.write("| Filter Type | Count | Description |\n")
        f.write("|-------------|-------|-------------|\n")
        
        filter_descriptions = {
            'urgent_tickets': 'Critical/High urgency tickets requiring immediate attention',
            'low_quality_tickets': 'TriQ Score < 5.0 - Need quality improvement',
            'very_low_quality_tickets': 'TriQ Score < 4.0 - Critical quality issues',
            'urgent_and_poor_quality': 'High urgency + Low quality - Double trouble',
            'unassigned_tickets': 'No assignee - Need immediate assignment',
            'sla_risk_tickets': 'Risk of SLA breach - Critical/urgent unassigned',
            'template_tickets': 'TriQ Score ≥ 8.0 - Use as quality templates',
            'immediate_action_tickets': 'Flagged for immediate action in system'
        }
        
        for filter_name in filters.keys():
            count = len(filters[filter_name])
            description = filter_descriptions.get(filter_name, 'No description')
            f.write(f"| {filter_name.replace('_', ' ').title()} | {count:3d} | {description} |\n")
        
        f.write("\n## 📁 Generated Files\n\n")
        f.write("### Main Dataset\n")
        f.write("- `tri-tickets-refined-categories.csv` - Complete dataset with refined categorization\n\n")
        
        f.write("### Priority Filters\n")
        for filter_name, filename in filter_files.items():
            count = len(filters[filter_name])
            f.write(f"- `{os.path.basename(filename)}` - {count} tickets\n")
        
        f.write("\n## 🚨 Immediate Action Required\n\n")
        if len(filters['sla_risk_tickets']) > 0:
            f.write("### SLA Risk Tickets (Assign Immediately)\n")
            for _, ticket in filters['sla_risk_tickets'].head(10).iterrows():
                f.write(f"- **{ticket['Ticket_Key']}**: {ticket['Summary']} (Urgency: {ticket['Urgency']})\n")
        
        if len(filters['very_low_quality_tickets']) > 0:
            f.write("\n### Very Low Quality Tickets (Request Revision)\n")
            for _, ticket in filters['very_low_quality_tickets'].head(10).iterrows():
                f.write(f"- **{ticket['Ticket_Key']}**: TriQ {ticket['TriQ_Score']} - {ticket['Quality_Issues']}\n")
    
    print(f"Comprehensive summary saved to: {summary_file}")
    
    return {
        'refined_file': refined_file,
        'filter_files': filter_files,
        'summary_file': summary_file
    }

def main():
    """
    Main execution function.
    """
    print("=== TRI TICKETS REFINED CATEGORIZATION & FILTERING ===")
    
    # Step 1: Analyze and refine categorization
    df, refined_counts = analyze_other_category_patterns()
    
    # Step 2: Create urgency and quality filters
    filters = create_urgency_quality_filters(df)
    
    # Step 3: Save all filtered datasets
    files = save_filtered_datasets(df, filters, refined_counts)
    
    print(f"\n=== ANALYSIS COMPLETE ===")
    print(f"✅ Refined categorization applied to all {len(df)} tickets")
    print(f"✅ {len(files['filter_files'])} filtered datasets created")
    print(f"✅ Comprehensive analysis report generated")
    
    return df, filters, files

if __name__ == "__main__":
    main()