# TriQ Dashboard - POC

A lightweight, on-demand web dashboard for monitoring TriQ ticket validation logs.

## Features

- **Metrics Overview**: Total tickets, average quality score, approval rates
- **Ticket List**: Recent validations with scores, results, and status
- **Auto-Refresh**: Dashboard refreshes every 180 seconds (3 minutes)
- **Minimal Setup**: SQLite database, Flask backend, simple HTML/JS frontend
- **Run On-Demand**: Start when needed, stop when done

## Quick Start

### Prerequisites

- Python 3.7+ (already installed on macOS)
- pip3 (Python package manager)

### Installation (One-Time Setup)

```bash
# Install Flask (only dependency)
pip3 install flask

# That's it! No other dependencies needed.
```

### Usage

#### Step 1: Parse Logs into Database

```bash
cd /Users/munin8/_myprojects/triq-dashboard
python3 triq_db.py
```

**What this does:**
- Reads `/tmp/triq-monitor.log`
- Parses structured log entries
- Stores data in `triq.db` SQLite database
- Shows summary statistics

**Output example:**
```
============================================================
TriQ Log Parser - Converting logs to database
============================================================

🔨 Creating database schema...
✓ Database created: triq.db

📖 Reading log file: /tmp/triq-monitor.log

✓ Parsed 1,234 log entries

📊 Database Statistics:
------------------------------------------------------------
  Total log entries:      1,234
  Unique tickets:         7
  Scored validations:     182
  Average quality score:  3.45/10

  Validation results:
    • PARKING_LOT: 7
    • APPROVED: 0
    • NEEDS_CLARIFICATION: 0

============================================================
✅ Database ready! Run 'python3 dashboard.py' to view
============================================================
```

#### Step 2: Start Dashboard

```bash
python3 dashboard.py
```

**What this does:**
- Starts Flask web server on port 5000
- Serves dashboard at `http://localhost:5000`
- Auto-refreshes UI every 180 seconds

**Output example:**
```
============================================================
🚀 TriQ Dashboard Starting
============================================================

✓ Database loaded: 1,234 log entries
✓ Tracking 7 unique tickets

🌐 Dashboard URL: http://localhost:5000
🔄 Auto-refresh: Every 180 seconds (3 minutes)

Press Ctrl+C to stop
============================================================
```

#### Step 3: Open Dashboard

Open your browser to: **http://localhost:5001**

The dashboard will automatically refresh every 3 minutes to show latest data from the database.

### Updating Data

To refresh data with latest logs:

```bash
# Stop dashboard (Ctrl+C in terminal running dashboard.py)

# Re-parse logs
python3 triq_db.py

# Restart dashboard
python3 dashboard.py
```

**Tip:** You can keep the dashboard running and just re-parse logs in a separate terminal. The dashboard will show updated data on next auto-refresh (max 3 minutes).

## Dashboard Features

### Metrics Cards

- **Total Tickets**: Unique tickets validated
- **Avg Quality Score**: Average validation score (0-10)
- **Approved**: Tickets that passed validation
- **Needs Clarification**: Tickets needing more info
- **Parking Lot**: Tickets below quality threshold (score < 5.0)

### Tickets Table

Columns:
- **Ticket**: Ticket key (e.g., EP-10)
- **Last Validated**: Time since last validation
- **Evals**: Number of evaluation cycles
- **Score**: Quality score (color-coded: green 8+, yellow 5-8, red <5)
- **Result**: Validation outcome (APPROVED, PARKING_LOT, etc.)
- **Priority**: Assigned priority level
- **Urgency/Impact**: Business operations matrix values

### Auto-Refresh

- Dashboard UI refreshes every **180 seconds** (3 minutes)
- Visual indicator shows refresh status
- No page reload - smooth AJAX updates
- To change refresh interval, edit `REFRESH_INTERVAL` in `templates/index.html`

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  /tmp/triq-monitor.log (TriQ monitoring script)    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
           ┌───────────────┐
           │  triq_db.py   │  Parse logs → SQLite
           └───────┬───────┘
                   │
                   ▼
           ┌───────────────┐
           │   triq.db     │  SQLite database
           └───────┬───────┘
                   │
                   ▼
         ┌─────────────────┐
         │  dashboard.py   │  Flask web server
         └────────┬────────┘
                  │
                  ▼
    ┌──────────────────────────┐
    │  http://localhost:5000   │  Web UI (auto-refresh)
    └──────────────────────────┘
```

## File Structure

```
triq-dashboard/
├── triq_db.py              # Log parser script
├── dashboard.py            # Flask web server
├── templates/
│   └── index.html          # Dashboard UI (180s auto-refresh)
├── README.md               # This file
└── triq.db                 # SQLite database (auto-generated)
```

## API Endpoints

The Flask backend provides RESTful API endpoints:

- `GET /` - Dashboard UI
- `GET /api/metrics` - Metrics summary (total tickets, avg score, etc.)
- `GET /api/tickets?limit=50` - Recent ticket validations
- `GET /api/ticket/<key>` - Detailed ticket history
- `GET /api/escalations` - Tickets needing manual intervention (5+ evals)
- `GET /api/health` - Health check / database status

## Customization

### Change Auto-Refresh Interval

Edit `templates/index.html`, line ~360:

```javascript
const REFRESH_INTERVAL = 180000; // milliseconds (180000 = 3 minutes)
```

Change to desired interval:
- 30 seconds: `30000`
- 1 minute: `60000`
- 5 minutes: `300000`

### Change Server Port

Edit `dashboard.py`, line ~18:

```python
PORT = 5000
```

### Increase Ticket Limit

Default shows 50 most recent tickets. To change:

Edit `templates/index.html`, line ~405:

```javascript
const response = await fetch(`${API_BASE}/api/tickets?limit=50`);
```

Change `limit=50` to desired number (e.g., `limit=100`).

## Troubleshooting

### Database Not Found

**Error:** `⚠️ Database not found!`

**Solution:**
```bash
python3 triq_db.py
```

### No Log File

**Error:** `❌ Error: Log file not found at /tmp/triq-monitor.log`

**Solution:** Run the TriQ monitoring script first:
```bash
cd /Users/munin8/_myprojects
./triq-monitor.sh
```

### Port Already in Use

**Error:** `Address already in use`

**Solution:** Either:
1. Stop other process using port 5000
2. Change `PORT` in `dashboard.py` to different number (e.g., 5001)

### Flask Not Installed

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
pip3 install flask
```

### Empty Dashboard

**Symptom:** Dashboard shows "0 tickets" but logs exist

**Solution:**
1. Check that `/tmp/triq-monitor.log` has content:
   ```bash
   wc -l /tmp/triq-monitor.log
   ```

2. Re-parse logs:
   ```bash
   python3 triq_db.py
   ```

3. Check database was created:
   ```bash
   ls -lh triq.db
   ```

## Future Enhancements

This is a POC (Proof of Concept). Planned improvements:

1. **Ticket Detail View**: Click ticket to see full validation history
2. **Filters**: Filter by score range, result type, date
3. **Admin Queue**: Dedicated view for escalated tickets (5+ evals)
4. **Export**: Download data as CSV/JSON
5. **Real-Time Logs**: Live log streaming without re-parsing
6. **Production Dashboard**: Migrate to PostgreSQL + Next.js for full-featured app

## Development

### Dependencies

- Python 3.7+
- Flask 3.x
- SQLite3 (built into Python)

### Running in Development Mode

Flask debug mode is enabled by default in `dashboard.py`:

```python
app.run(debug=True, port=PORT, host='0.0.0.0')
```

This enables:
- Auto-reload on code changes
- Detailed error pages
- Interactive debugger

### Database Schema

See `triq_db.py` for full schema. Key tables:

**`validations`** - Main table
- `id` - Primary key
- `timestamp` - When validation occurred
- `ticket_key` - Ticket identifier (e.g., EP-10)
- `category` - Log category (VALIDATION, SUMMARY, etc.)
- `log_level` - DEBUG, INFO, WARN, ERROR
- `total_score` - Final validation score (0-10)
- `validation_result` - APPROVED, PARKING_LOT, etc.
- `priority` - Assigned priority
- `urgency` / `impact` - Business matrix values
- `evaluation_number` - Validation cycle count

## Support

For issues or questions:

1. Check this README troubleshooting section
2. Review TriQ documentation: `/Users/munin8/_myprojects/TRIQ-TODO.md`
3. Check TriQ monitoring logs: `/tmp/triq-monitor.log`

## License

Internal tool for MuniBilling TriQ system.

---

**Built by:** Claude Code
**Version:** 1.0 POC
**Last Updated:** 2025-10-23
