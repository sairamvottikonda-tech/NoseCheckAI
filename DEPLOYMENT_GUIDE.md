# NoseCheck Web Deployment Guide

## 🚀 Deploy to Render.com (FREE)

This guide will help you deploy NoseCheck as a web application that anyone can access from any device.

### What You'll Get
- ✅ Public URL: `https://nosecheck.onrender.com` (or similar)
- ✅ Works on ANY device (iPhone, Android, computer)
- ✅ No App Store needed
- ✅ FREE hosting (Render free tier)
- ✅ HTTPS (secure) automatically

---

## Step-by-Step Deployment

### **Step 1: Create a Render Account** (2 minutes)

1. Go to: https://render.com
2. Click **Get Started** (top-right)
3. Sign up with:
   - **GitHub** (recommended - easier deployment)
   - OR **Email**
4. Verify your email if needed

---

### **Step 2: Push Code to GitHub** (5 minutes)

If you don't have this code on GitHub yet:

1. **Create a GitHub account** (if you don't have one):
   - Go to: https://github.com
   - Sign up for free

2. **Create a new repository:**
   - Click **+** (top-right) → **New repository**
   - Name: `nosecheck`
   - Make it **Private** (recommended for now)
   - Don't initialize with README (you have one)
   - Click **Create repository**

3. **Push your code** (in Terminal):

```bash
cd /Users/lakshmanvemuru/nosecheck

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit - NoseCheck web app"

# Add GitHub as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/nosecheck.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

### **Step 3: Deploy on Render** (5 minutes)

1. **Go to Render Dashboard:**
   - https://dashboard.render.com

2. **Create New Web Service:**
   - Click **New** (top-right) → **Web Service**

3. **Connect GitHub Repository:**
   - If first time: Click **Connect GitHub** and authorize Render
   - Select your **nosecheck** repository
   - Click **Connect**

4. **Configure the Web Service:**

   **Basic Settings:**
   - **Name**: `nosecheck` (or any name you want)
   - **Region**: Choose closest to you (e.g., Oregon, Frankfurt)
   - **Branch**: `main`
   - **Runtime**: `Python 3`

   **Build & Deploy:**
   - **Build Command**: `pip install -r requirements-production.txt`
   - **Start Command**: `gunicorn -w 1 -b 0.0.0.0:$PORT wsgi:application`

   **Plan:**
   - Select **Free** plan

5. **Click "Create Web Service"**

6. **Wait for deployment** (5-10 minutes):
   - Render will show build logs
   - Watch for "Build successful" and "Deploy live"
   - Green checkmark = deployed! ✅

---

### **Step 4: Test Your App** (2 minutes)

1. **Copy your URL:**
   - At top of Render dashboard: `https://nosecheck.onrender.com`
   - (Your actual URL will be different)

2. **Open in browser:**
   - Click the URL or copy-paste it
   - You should see NoseCheck home page!

3. **Test the flow:**
   - Click "Get Started" or "Upload Photo"
   - Upload a frontal face photo
   - Complete questionnaire
   - View results

---

## 🔗 Sharing with Friends

**Share this link with anyone:**
```
https://your-app-name.onrender.com
```

They can:
- Open it on **any device** (iPhone, Android, computer)
- Use it **immediately** (no installation)
- Works in **any browser** (Safari, Chrome, Firefox)

---

## ⚡ Important Notes

### Free Tier Limitations:
- **Automatic sleep**: App sleeps after 15 min of inactivity
- **Wake-up time**: First request after sleep takes 30-50 seconds
- **Monthly hours**: 750 hours/month (enough for testing)
- **Bandwidth**: Limited but usually sufficient

### Upgrading (Optional):
- **$7/month**: App stays awake 24/7, faster, more resources
- Only needed if you get lots of users

### Custom Domain (Optional):
- Free: `nosecheck.onrender.com`
- Custom: `nosecheck.com` (requires buying domain + $7/mo plan)

---

## 🐛 Troubleshooting

### Build Failed
- Check build logs in Render dashboard
- Most common: Missing dependencies
- Solution: Make sure `requirements-production.txt` is in your repo

### App Crashes
- Check Logs tab in Render dashboard
- Look for Python errors
- Common issue: File paths (use relative paths, not absolute)

### "Could not detect face"
- Same as local: needs clear frontal photos
- Check lighting and photo quality

### Slow First Load
- Normal for free tier (app is waking up)
- Subsequent loads are fast
- Upgrade to paid plan to keep app awake

---

## 📊 Monitor Your App

In Render Dashboard:
- **Logs**: See real-time application logs
- **Metrics**: View CPU, memory, requests
- **Events**: Track deployments and restarts

---

## 🔄 Updating Your App

When you make changes:

```bash
cd /Users/lakshmanvemuru/nosecheck

# Make your changes to code...

# Commit changes
git add .
git commit -m "Description of changes"

# Push to GitHub
git push

# Render automatically redeploys! (takes 2-5 minutes)
```

---

## 🎉 You're Done!

Your app is now live on the internet! Anyone can use it from any device.

**Next steps:**
- Share the URL with friends
- Test on different devices
- Monitor usage in Render dashboard
- Update and improve based on feedback

---

## Alternative: Deploy to Other Platforms

If Render doesn't work, try:
- **Railway.app** - Similar to Render, also free tier
- **PythonAnywhere** - Free tier, easier but slower
- **Heroku** - $5/month minimum (no free tier anymore)
- **Vercel** - Free, but requires serverless adaptation

---

## Need Help?

Common issues and solutions at: https://render.com/docs/troubleshooting

Support:
- Render community: https://community.render.com
- Check logs in Render dashboard first
- Most issues are in build/start commands or dependencies
