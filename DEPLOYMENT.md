# Deployment Guide for Render

Complete step-by-step guide to deploy your SmartPhysio web application on Render.

## 📋 Prerequisites

- GitHub account (https://github.com)
- Render account (https://render.com) - Free tier available
- Git installed on your computer
- Your SmartPhysio project ready

---

## 🚀 Deployment Steps

### Step 1: Prepare Your Project

Ensure your project has this structure:

```
smartphysio-web/
├── app.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── .gitignore
├── templates/
│   ├── index.html
│   └── analysis.html
└── README.md
```

**Verify all files are present:**

```bash
ls -la
# Should show: app.py, requirements.txt, Procfile, runtime.txt, .gitignore, templates/
```

---

### Step 2: Initialize Git Repository (If Not Done)

```bash
# Navigate to your project directory
cd smartphysio-web

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: SmartPhysio web application"
```

---

### Step 3: Create GitHub Repository

#### Via GitHub Website:

1. Go to https://github.com/new
2. Fill in:
   - **Repository name**: `smartphysio-web`
   - **Description**: "Physiotherapy exercise tracking web application"
   - **Visibility**: Public (or Private)
   - **DO NOT** initialize with README (you already have one)
3. Click "Create repository"

#### Connect Local Repo to GitHub:

```bash
# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/smartphysio-web.git

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

**Verify**: Visit your GitHub repo URL to confirm files are uploaded.

---

### Step 4: Deploy on Render

#### 4.1 Create Render Account

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (recommended) or email
4. Verify your email

#### 4.2 Create New Web Service

1. In Render Dashboard, click **"New +"** button
2. Select **"Web Service"**
3. Click **"Connect GitHub"** (if not already connected)
4. Authorize Render to access your repositories

#### 4.3 Select Repository

1. Find `smartphysio-web` in the list
2. Click **"Connect"**

#### 4.4 Configure Web Service

Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `smartphysio-web` (or any unique name) |
| **Region** | Choose closest to you (e.g., Oregon, Singapore) |
| **Branch** | `main` |
| **Root Directory** | Leave blank |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Instance Type** | `Free` |

#### 4.5 Environment Variables (Optional)

**For PostgreSQL** (see POSTGRES-SETUP.md):
- Click "Add Environment Variable"
- Key: `DATABASE_URL`
- Value: (PostgreSQL connection string)

**For production**:
- Key: `FLASK_ENV`
- Value: `production`

#### 4.6 Create Web Service

1. Click **"Create Web Service"**
2. Wait for deployment (2-5 minutes first time)

---

### Step 5: Monitor Deployment

#### Watch Build Logs:

In the Render dashboard, you'll see:

```
Building...
Installing dependencies...
Successfully installed flask-3.0.0 flask-cors-4.0.0 ...
Starting gunicorn...
Your service is live!
```

#### Check Status:

- **Green "Live"** = Success! ✅
- **Red "Failed"** = Check logs for errors ❌

---

### Step 6: Access Your Deployed App

Once deployment succeeds:

1. Find your app URL in dashboard:
   ```
   https://smartphysio-web-abc123.onrender.com
   ```

2. Click the URL or visit it in browser

3. Test the application:
   - Main page should load
   - Start a test session
   - View analysis page

---

## 🔄 Auto-Deployment Setup

### How It Works:

Every time you push to GitHub, Render automatically redeploys!

```bash
# Make changes to your code
# Edit app.py or templates

# Commit changes
git add .
git commit -m "Update feature X"

# Push to GitHub
git push origin main

# Render automatically detects push and redeploys (1-3 minutes)
```

### Deployment Triggers:

- ✅ Push to main branch
- ✅ Pull request merged
- ✅ Manual deploy button in dashboard

---

## 🗄️ Database Options

### Option 1: SQLite (Default - Ephemeral Storage)

**What happens:**
- Database file is created on each deployment
- **Data is LOST** when:
  - You deploy new code
  - Service restarts
  - Service sleeps (15 min inactivity on free tier)

**Good for:**
- Testing
- Demo purposes
- Development

**Not good for:**
- Production with real users
- Long-term data storage

### Option 2: PostgreSQL (Recommended - Persistent Storage)

**See POSTGRES-SETUP.md** for complete guide.

**What you get:**
- ✅ Permanent data storage
- ✅ Automatic backups
- ✅ Survives deployments and restarts
- ✅ Production-ready

**Quick steps:**
1. Create PostgreSQL database on Render (free tier)
2. Add `DATABASE_URL` environment variable
3. Use `app-postgresql.py` instead of `app.py`

---

## 💰 Render Free Tier Limits

### What You Get Free:

- ✅ **750 hours/month** of runtime (enough for 1 service 24/7)
- ✅ **Automatic HTTPS/SSL**
- ✅ **Auto-deployments from GitHub**
- ✅ **Custom domains** (paid feature)
- ✅ **Free PostgreSQL** (1GB, 90-day limit)

### Limitations:

- ⏸️ **Service sleeps** after 15 minutes of inactivity
- 🐌 **Cold start**: 30-60 seconds to wake up (first request)
- 💾 **Ephemeral storage**: Files reset on deploy (except database)
- 🌐 **No custom domain** on free tier
- 📊 **Limited bandwidth**

### When Service Sleeps:

**What happens:**
- No visitors for 15 minutes → Service goes to sleep
- Next visitor → Takes 30-60 seconds to wake up
- After wake up → Normal speed

**Solutions:**
- Upgrade to paid tier ($7/month) - no sleep
- Use uptime monitor (e.g., UptimeRobot) to ping every 10 min
- Accept slower first load for free tier

---

## 🛠️ Troubleshooting

### Build Fails

#### Error: "Requirements installation failed"

**Check:**
```bash
# Verify requirements.txt locally
pip install -r requirements.txt
```

**Fix:**
- Ensure all package names are correct
- Check for typos in versions
- Remove packages that aren't needed

#### Error: "Python version not found"

**Check:** `runtime.txt` should contain:
```
python-3.11.0
```

**Supported versions:**
- python-3.11.x
- python-3.10.x
- python-3.9.x

### App Won't Start

#### Error: "Failed to bind to $PORT"

**Fix:** Ensure `app.py` has:
```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
```

#### Error: "Procfile not found"

**Create:** `Procfile` (no extension) with:
```
web: gunicorn app:app
```

### Application Errors

#### Error: "Internal Server Error"

**Check logs:**
1. In Render dashboard, click "Logs" tab
2. Look for Python error messages
3. Common issues:
   - Missing templates folder
   - Database connection issues
   - Import errors

**Fix:**
- Verify `templates/` folder exists
- Check all imports in `app.py`
- Ensure database is properly initialized

#### Error: "Template not found"

**Fix:**
```bash
# Verify folder structure
smartphysio-web/
├── app.py
└── templates/
    ├── index.html
    └── analysis.html
```

### Database Issues

#### Data Keeps Resetting

**Cause:** Using SQLite on Render (ephemeral storage)

**Solution:** 
- Use PostgreSQL (see POSTGRES-SETUP.md)
- Or accept data loss for demo purposes

#### Connection Errors

**For PostgreSQL:**
- Verify `DATABASE_URL` environment variable is set
- Check database status in Render dashboard
- Use **Internal Database URL** (not External)

---

## 📊 Monitoring & Logs

### View Logs:

1. Go to your web service dashboard
2. Click **"Logs"** tab
3. See real-time logs:
   ```
   Starting gunicorn...
   Booting worker with pid: 123
   SQLite database initialized successfully
   ```

### Metrics:

1. Click **"Metrics"** tab
2. View:
   - CPU usage
   - Memory usage
   - Response times
   - Error rates

### Health Checks:

**Endpoint:** `https://your-app.onrender.com/api/health`

**Response:**
```json
{
  "status": "healthy",
  "database": "SQLite",
  "timestamp": "2025-10-30T16:40:00"
}
```

---

## 🔐 Security Best Practices

### 1. Environment Variables

**Never commit secrets to GitHub!**

```bash
# BAD - Don't do this
DATABASE_URL = "postgresql://user:password@host/db"

# GOOD - Use environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')
```

### 2. HTTPS

Render automatically provides HTTPS for all apps ✅

### 3. CORS Configuration

In `app.py`:
```python
from flask_cors import CORS

# Development - allow all
CORS(app)

# Production - restrict origins
CORS(app, origins=['https://your-domain.com'])
```

### 4. Input Validation

Always validate user input:
```python
@app.route('/api/sessions', methods=['POST'])
def sessions():
    data = request.json
    
    # Validate required fields
    if 'exercise_type' not in data:
        return jsonify({'error': 'Missing exercise_type'}), 400
    
    # Validate values
    valid_exercises = ['squat', 'abduction', 'elbow', 'hipflex', 'wristext']
    if data['exercise_type'] not in valid_exercises:
        return jsonify({'error': 'Invalid exercise type'}), 400
```

---

## 🎯 Production Checklist

Before going live:

- [ ] All environment variables set correctly
- [ ] Database configured (PostgreSQL for persistence)
- [ ] CORS configured for production domains
- [ ] Error handling implemented
- [ ] Health check endpoint working
- [ ] Logs reviewed for errors
- [ ] Test all API endpoints
- [ ] Test all web pages
- [ ] Security headers configured
- [ ] Rate limiting implemented (if needed)

---

## 📚 Additional Resources

### Official Documentation:

- **Render Docs**: https://render.com/docs
- **Render Python Guide**: https://render.com/docs/deploy-flask
- **Flask Deployment**: https://flask.palletsprojects.com/en/latest/deploying/

### Community Resources:

- **Render Community**: https://community.render.com
- **Stack Overflow**: Tag `render.com`

---

## 🆘 Getting Help

### 1. Check Logs First

Most issues show up in logs:
- Render Dashboard → Your Service → Logs tab

### 2. Common Error Solutions

See troubleshooting section above

### 3. Render Support

Free tier has community support:
- https://community.render.com

Paid tier has email support

---

## 🎉 Success!

Once deployed successfully:

✅ Your app is live at: `https://your-app.onrender.com`  
✅ Automatic HTTPS enabled  
✅ Auto-deployments from GitHub  
✅ Free hosting (with limitations)  

**Share your app URL with anyone!** They can access it immediately without installation.

---

## 📈 Next Steps

1. **Set up PostgreSQL** for data persistence (POSTGRES-SETUP.md)
2. **Add custom domain** (paid feature)
3. **Upgrade to paid tier** ($7/month) for:
   - No sleep
   - Faster performance
   - More bandwidth
4. **Add monitoring** (UptimeRobot, Pingdom)
5. **Implement analytics** (Google Analytics, Plausible)

---

**Good luck with your deployment! 🚀**

For PostgreSQL setup, see **POSTGRES-SETUP.md**.
