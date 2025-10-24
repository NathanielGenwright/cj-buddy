#!/usr/bin/env python3
"""
TriQ Log Parser - Convert triq-monitor.log to SQLite database

Parses the structured log format from triq-monitor.sh and stores
validation events, scores, and metadata in a SQLite database.

Usage:
    python3 triq_db.py
"""

import sqlite3
import re
import os
from datetime import datetime

# Configuration
LOG_FILE = '/tmp/triq-monitor.log'
DB_FILE = 'triq.db'

def create_database():
    """Create SQLite database with schema for TriQ logs"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Drop existing table to start fresh
    c.execute('DROP TABLE IF EXISTS validations')

    # Create validations table
    c.execute('''
        CREATE TABLE validations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            ticket_key TEXT NOT NULL,
            category TEXT,
            log_level TEXT,
            message TEXT,

            -- Scores
            score REAL,
            total_score REAL,
            max_score REAL,

            -- Results
            validation_result TEXT,
            routing_decision TEXT,

            -- Metadata
            priority TEXT,
            issue_type TEXT,
            urgency TEXT,
            impact TEXT,
            calculated_priority INTEGER,
            assigned_priority INTEGER,
            evaluation_number INTEGER,

            -- Indexing
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create indexes for performance
    c.execute('CREATE INDEX idx_ticket_key ON validations(ticket_key)')
    c.execute('CREATE INDEX idx_timestamp ON validations(timestamp)')
    c.execute('CREATE INDEX idx_total_score ON validations(total_score)')
    c.execute('CREATE INDEX idx_validation_result ON validations(validation_result)')

    conn.commit()
    return conn

def parse_log_file(conn):
    """Parse triq-monitor.log and insert into database"""

    if not os.path.exists(LOG_FILE):
        print(f"❌ Error: Log file not found at {LOG_FILE}")
        print(f"   Please run triq-monitor.sh first to generate logs")
        return 0

    c = conn.cursor()
    parsed_count = 0
    error_count = 0

    print(f"📖 Reading log file: {LOG_FILE}")

    # Current ticket context (for multi-line parsing)
    current_ticket = None
    current_timestamp = None
    current_priority = None
    current_issue_type = None
    current_urgency = None
    current_impact = None
    current_calc_priority = None
    current_assigned_priority = None
    current_eval_number = None

    with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                # Pattern 1: Structured log with ticket, category, level
                # [2025-10-23 15:34:09] [EP-10] [VALIDATION] [INFO] === Starting Validation (Evaluation #1) ===
                match = re.match(
                    r'\[([\d\-: ]+)\] \[([A-Z]+-\d+)\] \[(\w+)\] \[(INFO|DEBUG|WARN|ERROR)\] (.+)',
                    line
                )

                if match:
                    timestamp, ticket, category, level, message = match.groups()
                    current_ticket = ticket
                    current_timestamp = timestamp

                    # Extract metadata from message
                    score = None
                    total_score = None
                    max_score = None
                    validation_result = None
                    routing_decision = None

                    # Parse priority metadata
                    priority_match = re.search(r'Priority: ([^,]+)', message)
                    if priority_match:
                        current_priority = priority_match.group(1).strip()

                    # Parse issue type
                    type_match = re.search(r'Type: (.+)', message)
                    if type_match:
                        current_issue_type = type_match.group(1).strip()

                    # Parse urgency and impact
                    urgency_match = re.search(r'Urgency: (\w+)', message)
                    if urgency_match:
                        current_urgency = urgency_match.group(1)

                    impact_match = re.search(r'Impact: (\w+)', message)
                    if impact_match:
                        current_impact = impact_match.group(1)

                    # Parse calculated priority
                    calc_priority_match = re.search(r'Calculated Priority: (\d+)', message)
                    if calc_priority_match:
                        current_calc_priority = int(calc_priority_match.group(1))

                    # Parse assigned priority
                    assigned_priority_match = re.search(r'Assigned Priority: (\d+)', message)
                    if assigned_priority_match:
                        current_assigned_priority = int(assigned_priority_match.group(1))

                    # Parse evaluation number
                    eval_match = re.search(r'Evaluation #(\d+)', message)
                    if eval_match:
                        current_eval_number = int(eval_match.group(1))

                    # Extract individual scores
                    score_match = re.search(r'Score: ([\d.]+)/([\d.]+)', message)
                    if score_match:
                        score = float(score_match.group(1))
                        max_score = float(score_match.group(2))

                    # Extract weighted scores
                    weighted_match = re.search(r'Weighted: ([\d.]+)/([\d.]+)', message)
                    if weighted_match:
                        # Store weighted score as the main score
                        score = float(weighted_match.group(1))

                    # Extract final validation score
                    final_match = re.search(
                        r'Final Score: ([\d.]+)/([\d.]+) \((\w+)\)',
                        message
                    )
                    if final_match:
                        total_score = float(final_match.group(1))
                        max_score = float(final_match.group(2))
                        validation_result = final_match.group(3)

                    # Extract routing decision
                    routing_match = re.search(r'Decision: ([^(]+)', message)
                    if routing_match:
                        routing_decision = routing_match.group(1).strip()

                    # Insert into database
                    c.execute('''
                        INSERT INTO validations
                        (timestamp, ticket_key, category, log_level, message,
                         score, total_score, max_score,
                         validation_result, routing_decision,
                         priority, issue_type, urgency, impact,
                         calculated_priority, assigned_priority, evaluation_number)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        timestamp, ticket, category, level, message,
                        score, total_score, max_score,
                        validation_result, routing_decision,
                        current_priority, current_issue_type,
                        current_urgency, current_impact,
                        current_calc_priority, current_assigned_priority,
                        current_eval_number
                    ))

                    parsed_count += 1

                else:
                    # Pattern 2: Simple log without structured format
                    # [2025-10-23 15:34:04] Testing JIRA connectivity...
                    simple_match = re.match(r'\[([\d\-: ]+)\] (.+)', line)
                    if simple_match:
                        timestamp, message = simple_match.groups()

                        c.execute('''
                            INSERT INTO validations
                            (timestamp, ticket_key, category, log_level, message)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (timestamp, current_ticket or 'SYSTEM', 'SYSTEM', 'INFO', message))

                        parsed_count += 1

            except Exception as e:
                error_count += 1
                if error_count <= 10:  # Only show first 10 errors
                    print(f"⚠️  Line {line_num}: {str(e)[:100]}")

    conn.commit()
    return parsed_count

def generate_statistics(conn):
    """Generate summary statistics from parsed data"""
    c = conn.cursor()

    # Total entries
    total = c.execute('SELECT COUNT(*) FROM validations').fetchone()[0]

    # Unique tickets
    tickets = c.execute('SELECT COUNT(DISTINCT ticket_key) FROM validations').fetchone()[0]

    # Validations with scores
    scored = c.execute(
        'SELECT COUNT(*) FROM validations WHERE total_score IS NOT NULL'
    ).fetchone()[0]

    # Average score
    avg_score = c.execute(
        'SELECT AVG(total_score) FROM validations WHERE total_score IS NOT NULL'
    ).fetchone()[0]

    # Validation results breakdown
    results = c.execute('''
        SELECT validation_result, COUNT(*) as count
        FROM validations
        WHERE validation_result IS NOT NULL
        GROUP BY validation_result
        ORDER BY count DESC
    ''').fetchall()

    return {
        'total_entries': total,
        'unique_tickets': tickets,
        'scored_validations': scored,
        'avg_score': round(avg_score, 2) if avg_score else 0,
        'results': results
    }

def main():
    """Main execution function"""
    print("=" * 60)
    print("TriQ Log Parser - Converting logs to database")
    print("=" * 60)
    print()

    # Create database
    print("🔨 Creating database schema...")
    conn = create_database()
    print("✓ Database created: triq.db")
    print()

    # Parse logs
    parsed_count = parse_log_file(conn)
    print()
    print(f"✓ Parsed {parsed_count:,} log entries")
    print()

    # Generate statistics
    print("📊 Database Statistics:")
    print("-" * 60)
    stats = generate_statistics(conn)
    print(f"  Total log entries:      {stats['total_entries']:,}")
    print(f"  Unique tickets:         {stats['unique_tickets']:,}")
    print(f"  Scored validations:     {stats['scored_validations']:,}")
    print(f"  Average quality score:  {stats['avg_score']:.2f}/10")
    print()

    if stats['results']:
        print("  Validation results:")
        for result, count in stats['results']:
            print(f"    • {result}: {count}")

    print()
    print("=" * 60)
    print("✅ Database ready! Run 'python3 dashboard.py' to view")
    print("=" * 60)

    conn.close()

if __name__ == '__main__':
    main()
