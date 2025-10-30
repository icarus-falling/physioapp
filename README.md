# SmartPhysio Web Application

A web-based physiotherapy exercise tracking system with real-time analysis and comprehensive post-session insights.

## 🎯 Features

- **Exercise Tracking**: Track 5 different exercises (Squats, Shoulder Abduction, Elbow Flexion, Hip Flexion, Wrist Extension)
- **Two Session Modes**: 
  - Solo mode with auto-start countdown (15 seconds)
  - Assisted mode with manual start/pause controls
- **Real-time Monitoring**: Live rep counting and scoring
- **SQLite/PostgreSQL Database**: Persistent storage of all session data
- **Post-Session Analysis**: 
  - Detailed session history
  - Performance trends visualization
  - Exercise distribution charts
  - Rep-by-rep breakdown
  - Overall statistics

## 📁 Project Structure

```
smartphysio-web/
├── app.py                        # Flask backend API
├── physio_tracker.db             # SQLite database (auto-created)
├── requirements.txt              # Python dependencies
├── Procfile                      # Render deployment config
├── runtime.txt                   # Python version
├── .gitignore                    # Git ignore rules
├── templates/
│   ├── index.html               # Main exercise tracking page
│   └── analysis.html            # Post-session analysis page
├── soloHelpModes2.py            # Original Python script (reference)
├── physio-web-integration.py   # Modified script with web integration
├── README.md                    # This file
├── DEPLOYMENT.md                # Deployment guide for Render
└── POSTGRES-SETUP.md           # PostgreSQL setup guide
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

The server will start on `http://localhost:5000`

### 3. Access the Web Interface

- **Main Page**: http://localhost:5000/
- **Analysis Page**: http://localhost:5000/analysis
- **Health Check**: http://localhost:5000/api/health

## 📖 Usage Guide

### Starting a Session

1. Open http://localhost:5000/
2. Select exercise type from dropdown:
   - Squats
   - Shoulder Abduction
   - Elbow Flexion
   - Hip Flexion
   - Wrist Extension
3. Choose session mode:
   - **Solo**: Auto-starts after 15-second countdown
   - **Assisted**: Manual control with start/pause buttons
4. Click "Start Session"

### During a Session

- **Solo Mode**: 
  - 15-second countdown, then automatically starts tracking
  - Complete your reps naturally
  
- **Assisted Mode**: 
  - Press "Start" button or press `1` key to begin
  - Press "Pause" button or press `0` key to pause
  - Press `q` key to quit/end session

- **Demo Mode**: Click "Simulate Rep" to test without webcam

### Viewing Analysis

1. Click "View Analysis" button or navigate to `/analysis`
2. View overall statistics dashboard
3. Browse session history
4. Click on any session to see detailed rep breakdown
5. Filter sessions by exercise type

## 🔌 API Endpoints

### Sessions

- `GET /api/sessions` - List all sessions
- `POST /api/sessions` - Create new session
  ```json
  {
    "exercise_type": "squat",
    "session_mode": "solo"
  }
  ```
- `GET /api/sessions/<id>` - Get session details with reps and events
- `PUT /api/sessions/<id>` - Update session
  ```json
  {
    "total_reps": 10,
    "average_score": 87.5,
    "duration_seconds": 180,
    "status": "completed"
  }
  ```
- `DELETE /api/sessions/<id>/delete` - Delete session

### Reps

- `POST /api/reps` - Add new rep to session
  ```json
  {
    "session_id": 1,
    "rep_number": 1,
    "score": 95,
    "perfect_frames": 15,
    "standard_frames": 20,
    "tracked_side": "LEFT",
    "best_angle": 88.5
  }
  ```

### Form Events

- `POST /api/form_events` - Log form feedback event
  ```json
  {
    "session_id": 1,
    "event_type": "form_check",
    "angle": 90.5,
    "form_status": "PERFECT",
    "feedback_message": "Excellent form!"
  }
  ```

### Statistics

- `GET /api/stats` - Get overall statistics
  ```json
  {
    "total_sessions": 25,
    "total_reps": 250,
    "overall_average": 86.7,
    "exercise_breakdown": [...]
  }
  ```

### Health Check

- `GET /api/health` - Check API and database status
  ```json
  {
    "status": "healthy",
    "database": "SQLite",
    "timestamp": "2025-10-30T16:40:00"
  }
  ```

## 🗄️ Database Schema

### Sessions Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER/SERIAL | Primary key |
| exercise_type | TEXT/VARCHAR | Exercise name |
| session_mode | TEXT/VARCHAR | Solo or Assisted |
| start_time | TEXT/TIMESTAMP | Session start time |
| end_time | TEXT/TIMESTAMP | Session end time |
| total_reps | INTEGER | Total repetitions |
| average_score | REAL | Average score (0-100) |
| duration_seconds | INTEGER | Session duration |
| status | TEXT/VARCHAR | active/completed |

### Reps Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER/SERIAL | Primary key |
| session_id | INTEGER | Foreign key to sessions |
| rep_number | INTEGER | Rep sequence number |
| score | REAL | Rep score (0-100) |
| perfect_frames | INTEGER | Perfect form frame count |
| standard_frames | INTEGER | Standard form frame count |
| timestamp | TEXT/TIMESTAMP | Rep timestamp |
| tracked_side | TEXT/VARCHAR | LEFT/RIGHT/NONE |
| best_angle | REAL | Best angle achieved |

### Form Events Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER/SERIAL | Primary key |
| session_id | INTEGER | Foreign key to sessions |
| event_type | TEXT/VARCHAR | Event type |
| timestamp | TEXT/TIMESTAMP | Event timestamp |
| angle | REAL | Joint angle |
| form_status | TEXT/VARCHAR | PERFECT/CORRECT/INCORRECT |
| feedback_message | TEXT | Feedback text |

## 🔗 Integration with Original Python Script

To integrate with the original `soloHelpModes2.py`:

### Option 1: Use the Modified Version

Use `physio-web-integration.py` which has built-in API integration:

```bash
# Start web server first
python app.py

# In another terminal, run the integrated script
python physio-web-integration.py
```

### Option 2: Add API Calls to Your Script

Add these methods to your existing `soloHelpModes2.py`:

```python
import requests

API_URL = 'http://localhost:5000/api'

# Create session
response = requests.post(f'{API_URL}/sessions', json={
    'exercise_type': 'squat',
    'session_mode': 'solo'
})
session_id = response.json()['session_id']

# Log rep after each completion
requests.post(f'{API_URL}/reps', json={
    'session_id': session_id,
    'rep_number': rep_count,
    'score': score,
    'perfect_frames': perfect_frames,
    'standard_frames': standard_frames,
    'tracked_side': tracked_side,
    'best_angle': best_angle
})

# Update session on completion
requests.put(f'{API_URL}/sessions/{session_id}', json={
    'total_reps': total_reps,
    'average_score': avg_score,
    'duration_seconds': duration,
    'status': 'completed'
})
```

## ⌨️ Keyboard Shortcuts

During a session:

- **`1`** - Start session (Assisted mode only)
- **`0`** - Pause session (Assisted mode only)
- **`q`** - Quit/End session
- **`s`** - Switch to Squats
- **`a`** - Switch to Abduction
- **`e`** - Switch to Elbow Flexion
- **`h`** - Switch to Hip Flexion
- **`w`** - Switch to Wrist Extension

## 🎨 Color-Coded Scoring

Reps are color-coded based on performance:

- **🟢 Excellent (95-100)**: Green - Perfect form maintained
- **🔵 Good (85-94)**: Blue - Solid performance
- **🟡 Fair (75-84)**: Yellow - Acceptable form
- **🔴 Poor (<75)**: Red - Needs improvement

## 🚀 Deployment

### Deploy to Render (Free)

See **DEPLOYMENT.md** for detailed instructions.

Quick steps:
1. Push code to GitHub
2. Create account on https://render.com
3. Create new Web Service
4. Connect GitHub repository
5. Configure:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`
6. Add environment variable (optional): `DATABASE_URL` for PostgreSQL

### Use PostgreSQL for Production

See **POSTGRES-SETUP.md** for complete guide.

Benefits:
- ✅ Permanent data storage
- ✅ Automatic backups
- ✅ Better performance
- ✅ Multi-user support

## 🛠️ Troubleshooting

### Database Issues

**Problem**: Database file not found
```bash
# Solution: Delete and restart (creates fresh database)
rm physio_tracker.db
python app.py
```

**Problem**: Database locked error
```bash
# Solution: Use PostgreSQL instead of SQLite for production
# See POSTGRES-SETUP.md
```

### CORS Errors

**Problem**: Frontend can't connect to backend
```bash
# Solution: Ensure Flask-CORS is installed
pip install flask-cors
```

### Connection Refused

**Problem**: Can't connect to http://localhost:5000
```bash
# Solution: Check if server is running
python app.py

# Or check if port is in use
# Windows:
netstat -ano | findstr :5000
# Mac/Linux:
lsof -i :5000
```

## 📊 Performance Optimization

### For Production

1. **Use PostgreSQL** instead of SQLite
2. **Enable caching** for frequent queries
3. **Add database indexes**:
   ```sql
   CREATE INDEX idx_sessions_status ON sessions(status);
   CREATE INDEX idx_reps_session ON reps(session_id);
   ```
4. **Use connection pooling** for database
5. **Enable gzip compression** in Flask

## 🔐 Security Considerations

For production deployment:

1. **Environment Variables**: Store secrets in `.env` file
2. **HTTPS**: Enable SSL (Render does this automatically)
3. **Authentication**: Add user login if handling sensitive health data
4. **Rate Limiting**: Prevent API abuse
5. **Input Validation**: Sanitize all user inputs
6. **CORS**: Configure allowed origins properly

## 📚 Additional Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **Render Documentation**: https://render.com/docs
- **PostgreSQL Guide**: https://www.postgresql.org/docs/
- **MediaPipe Pose**: https://google.github.io/mediapipe/solutions/pose

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🆘 Support

For issues or questions:
1. Check **DEPLOYMENT.md** for deployment issues
2. Check **POSTGRES-SETUP.md** for database issues
3. Review API documentation above
4. Check troubleshooting section

## 🎉 Acknowledgments

- Built with Flask, MediaPipe, and OpenCV
- Designed for physiotherapy and rehabilitation tracking
- Supports both solo practice and assisted therapy sessions

---

**Version**: 1.0.0  
**Last Updated**: October 30, 2025  
**Author**: Your Name  
**Status**: Production Ready ✅
