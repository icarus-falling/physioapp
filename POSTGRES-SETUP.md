# PostgreSQL Setup Guide for Render

Complete guide to deploy SmartPhysio with **permanent data storage** using PostgreSQL on Render.

## 🎯 Why PostgreSQL?

### SQLite (Default) Problems:
- ❌ Data resets on every deployment
- ❌ Data lost when service sleeps
- ❌ Not suitable for production
- ❌ Single-user limitations

### PostgreSQL Benefits:
- ✅ **Permanent data storage**
- ✅ **Automatic daily backups**
- ✅ **Survives deployments & restarts**
- ✅ **Multi-user support**
- ✅ **Production-ready**
- ✅ **Free tier available** (1GB, 90 days)

---

## 📦 What You Need

1. **app-postgresql.py** - Modified Flask app (already created)
2. **requirements.txt** with `psycopg2-binary`
3. **Render account**
4. **GitHub repository**

---

## 🚀 Step-by-Step Setup

### Step 1: Update Project Files

#### 1.1 Replace app.py

```bash
# Backup original SQLite version
mv app.py app-sqlite-backup.py

# Rename PostgreSQL version to app.py
mv app-postgresql.py app.py
```

#### 1.2 Update requirements.txt

Ensure your `requirements.txt` includes:

```
flask==3.0.0
flask-cors==4.0.0
gunicorn==21.2.0
requests==2.31.0
psycopg2-binary==2.9.9
opencv-python==4.8.1.78
mediapipe==0.10.8
numpy==1.24.3
pyttsx3==2.90
```

**Note:** `psycopg2-binary` is the PostgreSQL database driver.

#### 1.3 Commit Changes

```bash
git add .
git commit -m "Add PostgreSQL support for production"
git push origin main
```

---

### Step 2: Create PostgreSQL Database on Render

#### 2.1 Go to Render Dashboard

1. Log in to https://render.com
2. Click **"New +"** button at top
3. Select **"PostgreSQL"**

#### 2.2 Configure Database

Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `smartphysio-db` |
| **Database** | `physio_tracker` |
| **User** | (auto-generated - leave default) |
| **Region** | **Same as your web service!** |
| **PostgreSQL Version** | 15 or latest |
| **Instance Type** | **Free** |

#### 2.3 Create Database

1. Click **"Create Database"**
2. Wait 1-2 minutes for initialization
3. Status will change to "Available"

#### 2.4 Get Connection String

Once database is ready:

1. Scroll down to **"Connections"** section
2. You'll see two URLs:
   - **Internal Database URL** ← Use this one!
   - External Database URL

3. **Copy the Internal Database URL**

It looks like:
```
postgresql://smartphysio_user:password123@dpg-abc123-a/physio_tracker
```

**Important:** Use **Internal** URL (faster, free internal network)

---

### Step 3: Configure Web Service

#### Option A: Creating New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `smartphysio-web`
   - **Region**: **Same as database**
   - **Runtime**: Python 3
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `gunicorn app:app`
   - **Instance**: Free

4. **Add Environment Variable:**
   - Click "Add Environment Variable"
   - **Key**: `DATABASE_URL`
   - **Value**: (paste Internal Database URL)

5. Click "Create Web Service"

#### Option B: Update Existing Web Service

1. Go to your existing web service
2. Click **"Environment"** in left sidebar
3. Click **"Add Environment Variable"**
4. Enter:
   - **Key**: `DATABASE_URL`
   - **Value**: (paste Internal Database URL)
5. Click "Save Changes"
6. Service will automatically redeploy

---

### Step 4: Verify Deployment

#### 4.1 Watch Build Logs

In your web service dashboard:

```
Installing dependencies...
Successfully installed psycopg2-binary-2.9.9
PostgreSQL database initialized successfully
Starting gunicorn...
Service is live!
```

#### 4.2 Check Database Connection

Visit your app's health endpoint:

```
https://your-app.onrender.com/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "PostgreSQL",
  "timestamp": "2025-10-30T16:40:00"
}
```

**If you see `"database": "PostgreSQL"` - Success!** ✅

**If you see `"database": "SQLite"` - Environment variable not set** ❌

---

### Step 5: Test Data Persistence

#### 5.1 Create Test Session

1. Go to your deployed app
2. Start a new session
3. Simulate a few reps
4. End session
5. Go to Analysis page - note the session

#### 5.2 Trigger Redeploy

```bash
# Make a small change (add comment to app.py)
# Add: # Test deployment

git add .
git commit -m "Test PostgreSQL persistence"
git push origin main
```

#### 5.3 Verify Data Persisted

1. Wait for redeployment (1-2 minutes)
2. Go to Analysis page again
3. **Your previous session should still be there!** ✨

If data is still there = PostgreSQL working correctly!

---

## 🔍 How Environment Detection Works

The modified `app.py` automatically detects the environment:

### Production (Render):
```python
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:  # Environment variable exists
    # Use PostgreSQL
    import psycopg2
    # Connect to PostgreSQL database
    # Data persists permanently ✅
```

### Local Development:
```python
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:  # Not set locally
    # (This block skipped)
else:
    # Use SQLite
    import sqlite3
    # Use local physio_tracker.db file ✅
```

**No code changes needed between environments!**

---

## 🗄️ Database Management

### View Your Data

#### Method 1: Render Dashboard Query Tool

1. Go to your PostgreSQL database dashboard
2. Click **"Query"** tab
3. Run SQL queries:

```sql
-- View all sessions
SELECT * FROM sessions 
ORDER BY start_time DESC 
LIMIT 10;

-- View recent reps
SELECT 
    s.exercise_type,
    r.rep_number,
    r.score,
    r.timestamp
FROM reps r
JOIN sessions s ON r.session_id = s.id
ORDER BY r.timestamp DESC
LIMIT 20;

-- Get exercise statistics
SELECT 
    exercise_type,
    COUNT(*) as total_sessions,
    AVG(average_score) as avg_score,
    SUM(total_reps) as total_reps
FROM sessions
WHERE status = 'completed'
GROUP BY exercise_type;

-- Find top scoring sessions
SELECT 
    exercise_type,
    average_score,
    total_reps,
    start_time
FROM sessions
WHERE status = 'completed'
ORDER BY average_score DESC
LIMIT 5;
```

#### Method 2: Database GUI Client

**Recommended tools (all free):**

- **TablePlus** (Mac/Windows/Linux)
- **DBeaver** (Cross-platform, open-source)
- **pgAdmin** (PostgreSQL official tool)
- **Postico** (Mac only)

**Connection steps:**

1. In Render database dashboard, copy **External Database URL**
2. Open your database client
3. Create new PostgreSQL connection
4. Paste connection string OR enter details:
   - Host: (from URL)
   - Port: 5432
   - Database: physio_tracker
   - User: (from URL)
   - Password: (from URL)
5. Connect!

Now you can browse tables, run queries, export data, etc.

---

## 💾 Backup & Restore

### Automatic Backups

Render provides **daily automatic backups** on free tier!

**View backups:**
1. Go to database dashboard
2. Click **"Backups"** tab
3. See list of automatic backups

**Restore from backup:**
1. Click on a backup
2. Click "Restore"
3. Confirm restoration

### Manual Backup

#### Create Manual Backup

1. Database dashboard → "Backups" tab
2. Click **"Create Backup"**
3. Wait 1-2 minutes
4. Backup appears in list

#### Export Data (via pg_dump)

```bash
# Install PostgreSQL client tools locally
# Then export:

pg_dump "postgresql://user:pass@host:5432/database" > backup.sql

# Or via Render dashboard:
# Backups tab → Download backup
```

#### Import Data

```bash
psql "postgresql://user:pass@host:5432/database" < backup.sql
```

---

## 🔧 Database Maintenance

### View Database Size

```sql
SELECT 
    pg_size_pretty(pg_database_size('physio_tracker')) as database_size;
```

### Optimize Performance

#### Add Indexes for Faster Queries

Add to `init_db()` function in `app.py`:

```python
# Speed up session queries
cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_exercise ON sessions(exercise_type)')

# Speed up rep lookups
cursor.execute('CREATE INDEX IF NOT EXISTS idx_reps_session ON reps(session_id)')

# Speed up form event queries
cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_session ON form_events(session_id)')
```

Then redeploy to create indexes.

#### Check Index Usage

```sql
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

### Clean Old Data

```sql
-- Delete sessions older than 6 months
DELETE FROM sessions 
WHERE start_time < NOW() - INTERVAL '6 months'
AND status = 'completed';

-- Delete incomplete sessions older than 1 day
DELETE FROM sessions 
WHERE status = 'active'
AND start_time < NOW() - INTERVAL '1 day';
```

---

## 💰 Pricing & Limits

### Free Tier (What You Get):

- ✅ **1GB storage**
- ✅ **Daily automatic backups**
- ✅ **Shared CPU/memory**
- ✅ **90-day retention**
- ✅ **SSL/TLS encryption**

**Storage capacity:**
- 1GB = ~10,000 - 100,000 sessions (depending on data)
- Average session = 10-50KB

### After 90 Days:

**Option 1: Upgrade to Paid ($7/month)**
- Unlimited retention
- 10GB storage
- Dedicated resources
- Better performance

**Option 2: Export & Recreate**
```bash
# Before day 90:
1. Export data (pg_dump)
2. Create new free database
3. Import data
4. Update DATABASE_URL
5. Redeploy
```

**Option 3: Alternative Free PostgreSQL**

- **Supabase**: 500MB free, permanent
- **Neon**: 3GB free, permanent
- **ElephantSQL**: 20MB free, permanent
- **Railway**: $5 free credit/month

---

## 🚨 Troubleshooting

### "Failed to connect to database"

**Check:**
1. Is `DATABASE_URL` environment variable set?
   - Web service → Environment → Verify
2. Did you use **Internal** Database URL?
3. Is database status "Available"?

**Fix:**
- Copy Internal Database URL again
- Update environment variable
- Redeploy service

### "psycopg2 installation failed"

**Error:**
```
pg_config executable not found
```

**Fix:**
Already handled! We use `psycopg2-binary` which has pre-compiled binaries.

Ensure `requirements.txt` has:
```
psycopg2-binary==2.9.9
```

NOT:
```
psycopg2==2.9.9  # This requires compilation
```

### "Tables not found"

**Normal behavior!** Tables are created automatically on first run.

**If tables aren't created:**

1. Check logs for errors during `init_db()`
2. Manually create tables via Query tool:

```sql
-- Run the CREATE TABLE statements from app.py
CREATE TABLE IF NOT EXISTS sessions (...);
CREATE TABLE IF NOT EXISTS reps (...);
CREATE TABLE IF NOT EXISTS form_events (...);
```

### "Still using SQLite"

**Check health endpoint:**
```
https://your-app.onrender.com/api/health
```

**If shows "SQLite":**
1. Environment variable `DATABASE_URL` is NOT set
2. Go to web service → Environment
3. Add `DATABASE_URL` with Internal URL
4. Redeploy

### "Database is full"

**Free tier: 1GB limit**

**Check usage:**
```sql
SELECT pg_size_pretty(pg_database_size('physio_tracker'));
```

**Solutions:**
1. Delete old data (see maintenance section)
2. Upgrade to paid tier (10GB)
3. Export and recreate database

---

## 🔐 Security Best Practices

### 1. Never Commit DATABASE_URL

```bash
# .gitignore should have:
.env
.env.local
```

### 2. Use Internal URL

- **Internal URL**: Free, fast, secure within Render network
- **External URL**: For external clients only (charges may apply)

### 3. Rotate Credentials

If database credentials are compromised:

1. Database dashboard → Settings
2. Reset password
3. Update `DATABASE_URL` in web service
4. Redeploy

### 4. Enable SSL (Already Enabled)

PostgreSQL connections are encrypted by default on Render ✅

---

## 📊 Monitoring

### Database Metrics

Database dashboard → **"Metrics"** tab:

- **CPU Usage**
- **Memory Usage**
- **Disk Usage**
- **Active Connections**
- **Query Performance**

### Set Up Alerts

1. Database dashboard → Settings
2. Configure email alerts for:
   - High CPU usage
   - Low disk space
   - Connection errors

---

## 🎯 Production Checklist

Before going live with PostgreSQL:

- [ ] PostgreSQL database created on Render
- [ ] `DATABASE_URL` environment variable set (Internal URL)
- [ ] Using `app-postgresql.py` as `app.py`
- [ ] `psycopg2-binary` in requirements.txt
- [ ] Deployed successfully
- [ ] Health check shows "PostgreSQL"
- [ ] Test session persists after redeploy
- [ ] Backups configured
- [ ] Database indexes added for performance
- [ ] Monitoring enabled

---

## 🎉 Success!

Once everything is set up:

✅ **Permanent data storage**  
✅ **Automatic daily backups**  
✅ **Production-ready database**  
✅ **Free for 90 days** (then $7/month or export)  

Your sessions and reps will persist through:
- Deployments
- Service restarts
- Service sleep/wake cycles
- Server maintenance

**Your data is safe!** 🛡️

---

## 📚 Additional Resources

- **Render PostgreSQL Docs**: https://render.com/docs/databases
- **PostgreSQL Tutorial**: https://www.postgresqltutorial.com/
- **psycopg2 Documentation**: https://www.psycopg.org/docs/

---

**Questions or issues?** Check troubleshooting section or Render community forum!

**Happy coding! 🚀**
