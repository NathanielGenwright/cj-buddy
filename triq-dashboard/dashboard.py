#!/usr/bin/env python3
"""
TriQ Dashboard - Flask web application for monitoring TriQ validation logs

Provides a clean web interface to view validation metrics, ticket scores,
and system activity from the TriQ triage automation system.

Usage:
    python3 dashboard.py

Then open: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuration
DB_FILE = 'triq.db'
PORT = 5001

def get_db():
    """Get database connection with row factory for dict-like access"""
    if not os.path.exists(DB_FILE):
        return None

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    return dict(zip(row.keys(), row)) if row else None

# ============================================================================
# WEB ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/metrics')
def get_metrics():
    """
    Get high-level metrics for dashboard cards

    Returns:
        {
            "total_tickets": int,
            "avg_score": float,
            "parking_lot": int,
            "approved": int,
            "needs_clarification": int
        }
    """
    db = get_db()
    if not db:
        return jsonify({
            'error': 'Database not found. Run triq_db.py first.',
            'total_tickets': 0,
            'avg_score': 0,
            'parking_lot': 0,
            'approved': 0,
            'needs_clarification': 0
        }), 404

    try:
        # Total unique tickets
        total = db.execute(
            'SELECT COUNT(DISTINCT ticket_key) FROM validations WHERE ticket_key != "SYSTEM"'
        ).fetchone()[0]

        # Average score from final validations
        avg_score_result = db.execute('''
            SELECT AVG(total_score)
            FROM validations
            WHERE total_score IS NOT NULL
        ''').fetchone()[0]
        avg_score = round(avg_score_result, 2) if avg_score_result else 0

        # Count by validation result (get latest per ticket)
        parking_lot = db.execute('''
            SELECT COUNT(DISTINCT ticket_key)
            FROM validations v1
            WHERE validation_result = 'PARKING_LOT'
              AND timestamp = (
                  SELECT MAX(timestamp)
                  FROM validations v2
                  WHERE v2.ticket_key = v1.ticket_key
                    AND v2.validation_result IS NOT NULL
              )
        ''').fetchone()[0]

        approved = db.execute('''
            SELECT COUNT(DISTINCT ticket_key)
            FROM validations v1
            WHERE validation_result IN ('APPROVED', 'APPROVED_WITH_NOTES')
              AND timestamp = (
                  SELECT MAX(timestamp)
                  FROM validations v2
                  WHERE v2.ticket_key = v1.ticket_key
                    AND v2.validation_result IS NOT NULL
              )
        ''').fetchone()[0]

        needs_clarification = db.execute('''
            SELECT COUNT(DISTINCT ticket_key)
            FROM validations v1
            WHERE validation_result = 'NEEDS_CLARIFICATION'
              AND timestamp = (
                  SELECT MAX(timestamp)
                  FROM validations v2
                  WHERE v2.ticket_key = v1.ticket_key
                    AND v2.validation_result IS NOT NULL
              )
        ''').fetchone()[0]

        db.close()

        return jsonify({
            'total_tickets': total,
            'avg_score': avg_score,
            'parking_lot': parking_lot,
            'approved': approved,
            'needs_clarification': needs_clarification
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tickets')
def get_tickets():
    """
    Get list of tickets with their latest validation results

    Query params:
        limit: Maximum number of tickets to return (default: 50)

    Returns:
        [{
            "ticket_key": str,
            "last_validated": str,
            "total_score": float,
            "validation_result": str,
            "routing_decision": str,
            "evaluation_count": int,
            "priority": str,
            "urgency": str,
            "impact": str
        }]
    """
    db = get_db()
    if not db:
        return jsonify({'error': 'Database not found'}), 404

    limit = request.args.get('limit', 50, type=int)

    try:
        # Get latest validation for each ticket
        tickets = db.execute('''
            SELECT
                v1.ticket_key,
                v1.timestamp as last_validated,
                v1.total_score,
                v1.validation_result,
                v1.routing_decision,
                v1.priority,
                v1.urgency,
                v1.impact,
                v1.evaluation_number as evaluation_count
            FROM validations v1
            INNER JOIN (
                SELECT ticket_key, MAX(timestamp) as max_timestamp
                FROM validations
                WHERE validation_result IS NOT NULL
                  AND ticket_key != 'SYSTEM'
                GROUP BY ticket_key
            ) v2 ON v1.ticket_key = v2.ticket_key
                AND v1.timestamp = v2.max_timestamp
            ORDER BY v1.timestamp DESC
            LIMIT ?
        ''', (limit,)).fetchall()

        result = [dict_from_row(t) for t in tickets]
        db.close()

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ticket/<ticket_key>')
def get_ticket_detail(ticket_key):
    """
    Get detailed validation history for a specific ticket

    Returns:
        {
            "ticket_key": str,
            "total_validations": int,
            "latest_score": float,
            "latest_result": str,
            "history": [{...}]
        }
    """
    db = get_db()
    if not db:
        return jsonify({'error': 'Database not found'}), 404

    try:
        # Get all validation events for this ticket
        events = db.execute('''
            SELECT *
            FROM validations
            WHERE ticket_key = ?
            ORDER BY timestamp ASC
        ''', (ticket_key,)).fetchall()

        if not events:
            db.close()
            return jsonify({'error': 'Ticket not found'}), 404

        # Get summary
        summary = db.execute('''
            SELECT
                COUNT(*) as total_validations,
                MAX(total_score) as latest_score,
                (SELECT validation_result
                 FROM validations
                 WHERE ticket_key = ?
                   AND validation_result IS NOT NULL
                 ORDER BY timestamp DESC
                 LIMIT 1) as latest_result
            FROM validations
            WHERE ticket_key = ?
        ''', (ticket_key, ticket_key)).fetchone()

        db.close()

        return jsonify({
            'ticket_key': ticket_key,
            'total_validations': summary[0],
            'latest_score': summary[1],
            'latest_result': summary[2],
            'history': [dict_from_row(e) for e in events]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/escalations')
def get_escalations():
    """
    Get tickets requiring manual intervention (5+ evaluations)

    Returns:
        [{
            "ticket_key": str,
            "evaluation_count": int,
            "latest_score": float,
            "latest_result": str,
            "first_seen": str,
            "last_seen": str
        }]
    """
    db = get_db()
    if not db:
        return jsonify({'error': 'Database not found'}), 404

    try:
        escalations = db.execute('''
            SELECT
                ticket_key,
                MAX(evaluation_number) as evaluation_count,
                (SELECT total_score
                 FROM validations v2
                 WHERE v2.ticket_key = v1.ticket_key
                   AND total_score IS NOT NULL
                 ORDER BY timestamp DESC
                 LIMIT 1) as latest_score,
                (SELECT validation_result
                 FROM validations v2
                 WHERE v2.ticket_key = v1.ticket_key
                   AND validation_result IS NOT NULL
                 ORDER BY timestamp DESC
                 LIMIT 1) as latest_result,
                MIN(timestamp) as first_seen,
                MAX(timestamp) as last_seen
            FROM validations v1
            WHERE ticket_key != 'SYSTEM'
            GROUP BY ticket_key
            HAVING MAX(evaluation_number) >= 5
            ORDER BY evaluation_count DESC, last_seen DESC
        ''').fetchall()

        result = [dict_from_row(e) for e in escalations]
        db.close()

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    db_exists = os.path.exists(DB_FILE)

    if not db_exists:
        return jsonify({
            'status': 'error',
            'database': 'not_found',
            'message': 'Run triq_db.py to create database'
        }), 503

    db = get_db()
    try:
        count = db.execute('SELECT COUNT(*) FROM validations').fetchone()[0]
        db.close()

        return jsonify({
            'status': 'ok',
            'database': 'connected',
            'total_records': count
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'database': 'error',
            'message': str(e)
        }), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 TriQ Dashboard Starting")
    print("=" * 60)
    print()

    # Check if database exists
    if not os.path.exists(DB_FILE):
        print("⚠️  Database not found!")
        print("   Please run: python3 triq_db.py")
        print()
        print("   The dashboard will start, but data won't be available")
        print("   until you parse the logs.")
        print()
    else:
        # Show quick stats
        db = get_db()
        if db:
            count = db.execute('SELECT COUNT(*) FROM validations').fetchone()[0]
            tickets = db.execute(
                'SELECT COUNT(DISTINCT ticket_key) FROM validations WHERE ticket_key != "SYSTEM"'
            ).fetchone()[0]
            db.close()

            print(f"✓ Database loaded: {count:,} log entries")
            print(f"✓ Tracking {tickets} unique tickets")
            print()

    print(f"🌐 Dashboard URL: http://localhost:{PORT}")
    print(f"🔄 Auto-refresh: Every 180 seconds (3 minutes)")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    app.run(debug=True, port=PORT, host='0.0.0.0')
