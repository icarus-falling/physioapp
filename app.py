from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

# Database configuration - supports both PostgreSQL and SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # PostgreSQL for production (Render)
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from urllib.parse import urlparse
    
    # Parse database URL
    url = urlparse(DATABASE_URL)
    
    def get_db_connection():
        """Create PostgreSQL connection"""
        return psycopg2.connect(
            host=url.hostname,
            port=url.port,
            user=url.username,
            password=url.password,
            database=url.path[1:]
        )
    
    def init_db():
        """Initialize PostgreSQL database with required tables"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id SERIAL PRIMARY KEY,
                exercise_type VARCHAR(50) NOT NULL,
                session_mode VARCHAR(20) NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                total_reps INTEGER DEFAULT 0,
                average_score REAL DEFAULT 0.0,
                duration_seconds INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'active'
            )
        ''')
        
        # Reps table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reps (
                id SERIAL PRIMARY KEY,
                session_id INTEGER NOT NULL,
                rep_number INTEGER NOT NULL,
                score REAL NOT NULL,
                perfect_frames INTEGER DEFAULT 0,
                standard_frames INTEGER DEFAULT 0,
                timestamp TIMESTAMP NOT NULL,
                tracked_side VARCHAR(10),
                best_angle REAL,
                FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
            )
        ''')
        
        # Form feedback events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS form_events (
                id SERIAL PRIMARY KEY,
                session_id INTEGER NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                angle REAL,
                form_status VARCHAR(20),
                feedback_message TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("PostgreSQL database initialized successfully")
    
else:
    # SQLite for local development
    import sqlite3
    
    DATABASE = 'physio_tracker.db'
    
    def get_db_connection():
        """Create SQLite connection"""
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db():
        """Initialize SQLite database with required tables"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercise_type TEXT NOT NULL,
                session_mode TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                total_reps INTEGER DEFAULT 0,
                average_score REAL DEFAULT 0.0,
                duration_seconds INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Reps table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                rep_number INTEGER NOT NULL,
                score REAL NOT NULL,
                perfect_frames INTEGER DEFAULT 0,
                standard_frames INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL,
                tracked_side TEXT,
                best_angle REAL,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # Form feedback events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS form_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                angle REAL,
                form_status TEXT,
                feedback_message TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("SQLite database initialized successfully")

# Initialize database on startup
init_db()

@app.route('/')
def index():
    """Main exercise tracking page"""
    return render_template('index.html')

@app.route('/analysis')
def analysis():
    """Post-session analysis page"""
    return render_template('analysis.html')

@app.route('/api/sessions', methods=['GET', 'POST'])
def sessions():
    """Handle session creation and retrieval"""
    if request.method == 'POST':
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if DATABASE_URL:
            # PostgreSQL
            cursor.execute('''
                INSERT INTO sessions (exercise_type, session_mode, start_time, status)
                VALUES (%s, %s, %s, 'active')
                RETURNING id
            ''', (data['exercise_type'], data['session_mode'], datetime.now()))
            session_id = cursor.fetchone()[0]
        else:
            # SQLite
            cursor.execute('''
                INSERT INTO sessions (exercise_type, session_mode, start_time, status)
                VALUES (?, ?, ?, 'active')
            ''', (data['exercise_type'], data['session_mode'], datetime.now().isoformat()))
            session_id = cursor.lastrowid
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'session_id': session_id, 'status': 'success'})
    
    else:  # GET
        conn = get_db_connection()
        
        if DATABASE_URL:
            # PostgreSQL
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM sessions ORDER BY start_time DESC')
            sessions = [dict(row) for row in cursor.fetchall()]
            # Convert datetime objects to ISO format strings
            for session in sessions:
                if session['start_time']:
                    session['start_time'] = session['start_time'].isoformat()
                if session['end_time']:
                    session['end_time'] = session['end_time'].isoformat()
        else:
            # SQLite
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sessions ORDER BY start_time DESC')
            sessions = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({'sessions': sessions})

@app.route('/api/sessions/<int:session_id>', methods=['GET', 'PUT'])
def session_detail(session_id):
    """Get or update a specific session"""
    conn = get_db_connection()
    
    if request.method == 'PUT':
        data = request.json
        cursor = conn.cursor()
        
        if DATABASE_URL:
            # PostgreSQL
            cursor.execute('''
                UPDATE sessions
                SET end_time = %s,
                    total_reps = %s,
                    average_score = %s,
                    duration_seconds = %s,
                    status = %s
                WHERE id = %s
            ''', (
                data.get('end_time', datetime.now()),
                data.get('total_reps', 0),
                data.get('average_score', 0.0),
                data.get('duration_seconds', 0),
                data.get('status', 'completed'),
                session_id
            ))
        else:
            # SQLite
            cursor.execute('''
                UPDATE sessions
                SET end_time = ?,
                    total_reps = ?,
                    average_score = ?,
                    duration_seconds = ?,
                    status = ?
                WHERE id = ?
            ''', (
                data.get('end_time', datetime.now().isoformat()),
                data.get('total_reps', 0),
                data.get('average_score', 0.0),
                data.get('duration_seconds', 0),
                data.get('status', 'completed'),
                session_id
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success'})
    
    else:  # GET
        if DATABASE_URL:
            # PostgreSQL
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM sessions WHERE id = %s', (session_id,))
            session = cursor.fetchone()
            
            if not session:
                cursor.close()
                conn.close()
                return jsonify({'error': 'Session not found'}), 404
            
            session_data = dict(session)
            # Convert datetime objects
            if session_data['start_time']:
                session_data['start_time'] = session_data['start_time'].isoformat()
            if session_data['end_time']:
                session_data['end_time'] = session_data['end_time'].isoformat()
            
            # Get all reps for this session
            cursor.execute('''
                SELECT * FROM reps 
                WHERE session_id = %s 
                ORDER BY rep_number
            ''', (session_id,))
            reps = [dict(row) for row in cursor.fetchall()]
            for rep in reps:
                if rep['timestamp']:
                    rep['timestamp'] = rep['timestamp'].isoformat()
            
            # Get form events
            cursor.execute('''
                SELECT * FROM form_events 
                WHERE session_id = %s 
                ORDER BY timestamp
            ''', (session_id,))
            events = [dict(row) for row in cursor.fetchall()]
            for event in events:
                if event['timestamp']:
                    event['timestamp'] = event['timestamp'].isoformat()
        else:
            # SQLite
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
            session = cursor.fetchone()
            
            if not session:
                cursor.close()
                conn.close()
                return jsonify({'error': 'Session not found'}), 404
            
            session_data = dict(session)
            
            # Get all reps
            cursor.execute('''
                SELECT * FROM reps 
                WHERE session_id = ? 
                ORDER BY rep_number
            ''', (session_id,))
            reps = [dict(row) for row in cursor.fetchall()]
            
            # Get form events
            cursor.execute('''
                SELECT * FROM form_events 
                WHERE session_id = ? 
                ORDER BY timestamp
            ''', (session_id,))
            events = [dict(row) for row in cursor.fetchall()]
        
        session_data['reps'] = reps
        session_data['events'] = events
        
        cursor.close()
        conn.close()
        
        return jsonify(session_data)

@app.route('/api/reps', methods=['POST'])
def add_rep():
    """Add a new rep to a session"""
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if DATABASE_URL:
        # PostgreSQL
        cursor.execute('''
            INSERT INTO reps (session_id, rep_number, score, perfect_frames, 
                             standard_frames, timestamp, tracked_side, best_angle)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data['session_id'],
            data['rep_number'],
            data['score'],
            data.get('perfect_frames', 0),
            data.get('standard_frames', 0),
            datetime.now(),
            data.get('tracked_side', 'NONE'),
            data.get('best_angle', 0.0)
        ))
    else:
        # SQLite
        cursor.execute('''
            INSERT INTO reps (session_id, rep_number, score, perfect_frames, 
                             standard_frames, timestamp, tracked_side, best_angle)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['session_id'],
            data['rep_number'],
            data['score'],
            data.get('perfect_frames', 0),
            data.get('standard_frames', 0),
            datetime.now().isoformat(),
            data.get('tracked_side', 'NONE'),
            data.get('best_angle', 0.0)
        ))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'status': 'success'})

@app.route('/api/form_events', methods=['POST'])
def add_form_event():
    """Log form feedback events"""
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if DATABASE_URL:
        # PostgreSQL
        cursor.execute('''
            INSERT INTO form_events (session_id, event_type, timestamp, angle, 
                                    form_status, feedback_message)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            data['session_id'],
            data['event_type'],
            datetime.now(),
            data.get('angle', 0.0),
            data.get('form_status', 'NONE'),
            data.get('feedback_message', '')
        ))
    else:
        # SQLite
        cursor.execute('''
            INSERT INTO form_events (session_id, event_type, timestamp, angle, 
                                    form_status, feedback_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['session_id'],
            data['event_type'],
            datetime.now().isoformat(),
            data.get('angle', 0.0),
            data.get('form_status', 'NONE'),
            data.get('feedback_message', '')
        ))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'status': 'success'})

@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    conn = get_db_connection()
    
    if DATABASE_URL:
        # PostgreSQL
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Total sessions
        cursor.execute("SELECT COUNT(*) as count FROM sessions WHERE status = 'completed'")
        total_sessions = cursor.fetchone()['count']
        
        # Total reps
        cursor.execute("SELECT SUM(total_reps) as total FROM sessions WHERE status = 'completed'")
        result = cursor.fetchone()
        total_reps = result['total'] if result['total'] else 0
        
        # Average score
        cursor.execute("SELECT AVG(average_score) as avg FROM sessions WHERE status = 'completed'")
        result = cursor.fetchone()
        overall_avg = result['avg'] if result['avg'] else 0
        
        # Exercise breakdown
        cursor.execute('''
            SELECT exercise_type, 
                   COUNT(*) as session_count,
                   SUM(total_reps) as total_reps,
                   AVG(average_score) as avg_score
            FROM sessions 
            WHERE status = 'completed'
            GROUP BY exercise_type
        ''')
        exercise_breakdown = [dict(row) for row in cursor.fetchall()]
    else:
        # SQLite
        cursor = conn.cursor()
        
        # Total sessions
        cursor.execute("SELECT COUNT(*) as count FROM sessions WHERE status = 'completed'")
        total_sessions = cursor.fetchone()['count']
        
        # Total reps
        cursor.execute("SELECT SUM(total_reps) as total FROM sessions WHERE status = 'completed'")
        result = cursor.fetchone()
        total_reps = result['total'] if result['total'] else 0
        
        # Average score
        cursor.execute("SELECT AVG(average_score) as avg FROM sessions WHERE status = 'completed'")
        result = cursor.fetchone()
        overall_avg = result['avg'] if result['avg'] else 0
        
        # Exercise breakdown
        cursor.execute('''
            SELECT exercise_type, 
                   COUNT(*) as session_count,
                   SUM(total_reps) as total_reps,
                   AVG(average_score) as avg_score
            FROM sessions 
            WHERE status = 'completed'
            GROUP BY exercise_type
        ''')
        exercise_breakdown = [dict(row) for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'total_sessions': total_sessions,
        'total_reps': total_reps,
        'overall_average': round(overall_avg, 2),
        'exercise_breakdown': exercise_breakdown
    })

@app.route('/api/sessions/<int:session_id>/delete', methods=['DELETE'])
def delete_session(session_id):
    """Delete a session and all related data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if DATABASE_URL:
        # PostgreSQL (CASCADE will auto-delete related records)
        cursor.execute('DELETE FROM sessions WHERE id = %s', (session_id,))
    else:
        # SQLite (manual deletion)
        cursor.execute('DELETE FROM reps WHERE session_id = ?', (session_id,))
        cursor.execute('DELETE FROM form_events WHERE session_id = ?', (session_id,))
        cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'status': 'success'})

@app.route('/api/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if DATABASE_URL:
            cursor.execute('SELECT 1')
        else:
            cursor.execute('SELECT 1')
        
        cursor.close()
        conn.close()
        
        db_type = 'PostgreSQL' if DATABASE_URL else 'SQLite'
        
        return jsonify({
            'status': 'healthy',
            'database': db_type,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
