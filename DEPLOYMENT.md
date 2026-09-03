# Quick Start - All Deployment Options

## 🚀 Fastest Way (2 minutes)

### Option 1: Local Installation

```bash
# Clone repository
git clone https://github.com/brandsconnet-byte/video-rag-engine.git
cd video-rag-engine

# Run installation script
python install.py

# Choose option 1 (Local)
```

Then visit: **http://localhost:5000**

---

## ☁️ Instant Cloud Access (No Deployment!)

### Option 2: ngrok (Access from anywhere)

```bash
# 1. Start app locally
python app.py

# 2. In another terminal, run quick-share
bash quick-share.sh

# You'll get a URL like: https://abc123.ngrok.io
```

Share that URL with anyone! ✅

**Pros:**
- ✅ No server setup
- ✅ No deployments
- ✅ Share URL instantly
- ✅ SSL/HTTPS included

**Cons:**
- ❌ App must run on your computer
- ❌ URL changes on restart
- ❌ Free plan has limits

---

## 🐳 Docker (Professional)

### Option 3: Docker & Docker Compose

```bash
# Install Docker first: https://docker.com

# Build image
docker build -t video-rag-engine .

# Run container
docker run -p 5000:5000 video-rag-engine

# Or with docker-compose
docker-compose up
```

Then visit: **http://localhost:5000**

---

## ⚡ Heroku (Easy Cloud Deployment)

### Option 4: Deploy to Heroku (FREE TIER)

```bash
# 1. Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Run deployment script
bash deploy-heroku.sh

# Enter app name when prompted
```

Your app will be live at: **https://your-app-name.herokuapp.com**

**Pros:**
- ✅ Free tier available
- ✅ Automatic SSL/HTTPS
- ✅ Easy to scale
- ✅ Always running

**Cons:**
- ❌ Free tier sleeps after 30 min inactivity
- ❌ Limited to 512MB RAM
- ❌ Limited video processing time

---

## 🚀 AWS (Most Powerful)

### Option 5: Deploy to AWS Elastic Beanstalk

```bash
# 1. Install AWS & EB CLI
pip install awsebcli

# 2. Configure AWS
aws configure
# Enter your AWS Access Key ID & Secret

# 3. Run deployment
bash deploy-aws.sh
```

Your app will be live at: **https://video-rag-engine.elasticbeanstalk.com**

**Pros:**
- ✅ Highly scalable
- ✅ Auto-scaling support
- ✅ Unlimited video processing
- ✅ Always running
- ✅ Full control

**Cons:**
- ❌ More complex setup
- ❌ Requires AWS account
- ❌ Pay as you go (but cheap)

---

## 📊 Comparison Table

| Feature | Local | ngrok | Docker | Heroku | AWS |
|---------|-------|-------|--------|--------|-----|
| Setup Time | 5 min | 2 min | 10 min | 10 min | 15 min |
| Cost | $0 | Free | $0 | Free | $5-50/mo |
| Always Running | ❌ | ❌ | ✅* | ✅ | ✅ |
| Video Size | Unlimited | Unlimited | Unlimited | 500MB limit | Unlimited |
| Processing Time | Unlimited | Unlimited | Unlimited | 30 min limit | Unlimited |
| Public URL | ❌ | ✅ | ✅ (manual) | ✅ | ✅ |
| SSL/HTTPS | ❌ | ✅ | ❌ | ✅ | ✅ |
| Scalability | Low | None | Medium | High | Very High |

*Docker requires running on server

---

## 🎯 Recommended Setup by Use Case

### "I just want to test it"
→ **Option 1: Local Installation**
- Quick, simple, free
- Visit http://localhost:5000

### "I want to share with a friend right now"
→ **Option 2: ngrok**
- 2-minute setup
- Share URL instantly
- No server setup

### "I want production deployment"
→ **Option 4: Heroku** (start) → **Option 5: AWS** (scale)
- Heroku for free testing
- AWS for production

---

## 🔐 Security Considerations

### Local (http://localhost:5000)
```bash
# Only accessible from your computer
# No encryption
# For testing only
```

### ngrok (https://xyz123.ngrok.io)
```bash
# Anyone with URL can access
# SSL/HTTPS included
# Revoke URL anytime
```

### Heroku (https://your-app.herokuapp.com)
```bash
# Public HTTPS
# Add authentication in settings
# Environment variables for secrets
```

### AWS (https://your-app.elasticbeanstalk.com)
```bash
# Private VPC available
# SSL/HTTPS included
# IAM security
# Firewall rules
```

---

## 🆘 Troubleshooting

### Port 5000 already in use
```bash
# Kill process using port 5000
kill $(lsof -t -i :5000)  # macOS/Linux
netstat -ano | findstr :5000  # Windows
```

### "pip not found"
```bash
# Use python3 instead
python3 -m pip install -r requirements.txt
```

### Docker image too large
```bash
# Use lightweight Python image
# Already configured in Dockerfile
```

### Upload fails
```bash
# Increase upload size limit in app.py
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 * 1024
```

---

## ✅ Quick Checklist

- [ ] Python 3.8+ installed
- [ ] 8GB+ RAM available
- [ ] 5GB+ disk space
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] AI models downloaded
- [ ] App runs locally
- [ ] Can access http://localhost:5000
- [ ] Can upload test video
- [ ] Can search scenes
- [ ] Can extract clips

---

**🎉 Pick an option above and get started!**
