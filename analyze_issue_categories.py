#!/usr/bin/env python3

import pandas as pd
from collections import Counter
import os

def analyze_issue_categories():
    """
    Analyze the tri-all-tickets-final.csv file to count Issue_Category values
    and create a filtered version with only the top 20 categories.
    """
    
    # Read the CSV file
    input_file = '/Users/munin8/_myprojects/tri-all-tickets-final.csv'
    
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found!")
        return
    
    print("Reading tri-all-tickets-final.csv...")
    df = pd.read_csv(input_file)
    
    print(f"Total tickets loaded: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Analyze Issue_Category column (Column K)
    issue_category_col = 'Issue_Category'
    
    if issue_category_col not in df.columns:
        print(f"Error: {issue_category_col} column not found!")
        print(f"Available columns: {list(df.columns)}")
        return
    
    # Count Issue_Category values
    category_counts = df[issue_category_col].value_counts()
    
    print(f"\n=== ISSUE CATEGORY ANALYSIS ===")
    print(f"Total unique categories: {len(category_counts)}")
    print(f"Non-null categories: {df[issue_category_col].notna().sum()}")
    print(f"Null/empty categories: {df[issue_category_col].isna().sum()}")
    
    print(f"\n=== ALL CATEGORIES (Ranked by Count) ===")
    for i, (category, count) in enumerate(category_counts.items(), 1):
        percentage = (count / len(df)) * 100
        print(f"{i:2d}. {category:<25} | {count:4d} tickets ({percentage:5.1f}%)")
    
    # Get top 20 categories
    top_20_categories = category_counts.head(20).index.tolist()
    
    print(f"\n=== TOP 20 CATEGORIES ===")
    for i, category in enumerate(top_20_categories, 1):
        count = category_counts[category]
        percentage = (count / len(df)) * 100
        print(f"{i:2d}. {category:<25} | {count:4d} tickets ({percentage:5.1f}%)")
    
    # Filter dataset to include only top 20 categories
    filtered_df = df[df[issue_category_col].isin(top_20_categories)]
    
    print(f"\n=== FILTERING RESULTS ===")
    print(f"Original dataset: {len(df)} tickets")
    print(f"Filtered dataset: {len(filtered_df)} tickets")
    print(f"Coverage: {(len(filtered_df) / len(df)) * 100:.1f}% of original data")
    
    # Save filtered dataset
    output_file = '/Users/munin8/_myprojects/tri-all-tickets-top20-categories.csv'
    filtered_df.to_csv(output_file, index=False)
    
    print(f"\nFiltered dataset saved to: {output_file}")
    
    # Generate summary report
    summary_file = '/Users/munin8/_myprojects/tri-top20-categories-summary.txt'
    with open(summary_file, 'w') as f:
        f.write("TRI TICKETS - TOP 20 ISSUE CATEGORIES ANALYSIS\n")
        f.write("=" * 50 + "\n")
        f.write(f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Original Dataset: {len(df)} tickets\n")
        f.write(f"Filtered Dataset: {len(filtered_df)} tickets\n")
        f.write(f"Coverage: {(len(filtered_df) / len(df)) * 100:.1f}%\n\n")
        
        f.write("TOP 20 ISSUE CATEGORIES:\n")
        f.write("-" * 30 + "\n")
        for i, category in enumerate(top_20_categories, 1):
            count = category_counts[category]
            percentage = (count / len(df)) * 100
            f.write(f"{i:2d}. {category:<25} | {count:4d} tickets ({percentage:5.1f}%)\n")
        
        f.write(f"\nEXCLUDED CATEGORIES:\n")
        f.write("-" * 20 + "\n")
        excluded_categories = category_counts.tail(len(category_counts) - 20)
        for category, count in excluded_categories.items():
            percentage = (count / len(df)) * 100
            f.write(f"    {category:<25} | {count:4d} tickets ({percentage:5.1f}%)\n")
    
    print(f"Summary report saved to: {summary_file}")
    
    return {
        'total_tickets': len(df),
        'filtered_tickets': len(filtered_df),
        'top_20_categories': top_20_categories,
        'coverage_percentage': (len(filtered_df) / len(df)) * 100
    }

if __name__ == "__main__":
    analyze_issue_categories()