# 🚀 Deployment Checklist

## Before You Start

- [ ] **Download all files** from this Replit to your local computer
- [ ] **Get Mistral API Key** from [console.mistral.ai](https://console.mistral.ai)
- [ ] **Generate secure tokens** using `python generate_tokens.py`
- [ ] **Create GitHub repository** (free account works)

## 📁 Files You Need (Download These)

### Core Application Files:
- [ ] `main.py` - Application entry point
- [ ] `app.py` - Flask application setup
- [ ] `api_routes.py` - API endpoints (now with environment variables)
- [ ] `rag_system.py` - RAG system (now with environment variables)
- [ ] `document_processor.py` - Document processing
- [ ] `vector_store.py` - Vector storage
- [ ] `models.py` - Database models

### Frontend Files:
- [ ] `templates/base.html` - Base template
- [ ] `templates/index.html` - Main page
- [ ] `static/css/custom.css` - Styles
- [ ] `static/js/main.js` - JavaScript (now loads config dynamically)

### Configuration Files:
- [ ] `requirements.txt` - Create this with the dependencies listed in README
- [ ] `runtime.txt` - Python version
- [ ] `render.yaml` - Render deployment config
- [ ] `.env.example` - Environment template
- [ ] `generate_tokens.py` - Token generator script

### Documentation:
- [ ] `README_DEPLOYMENT.md` - Complete deployment guide
- [ ] `DEPLOYMENT_CHECKLIST.md` - This checklist

## 🛠️ Local Setup Steps

1. **Generate Tokens:**
   ```bash
   python generate_tokens.py
   ```

2. **Create Environment File:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

3. **Create requirements.txt:**
   ```txt
   Flask==3.1.1
   Flask-SQLAlchemy==3.1.1
   Werkzeug==3.0.4
   gunicorn==23.0.0
   requests==2.31.0
   PyPDF2==3.0.0
   python-docx==1.1.0
   mistralai==1.0.0
   psycopg2-binary==2.9.10
   email-validator>=2.2.0
   httpx==0.25.0
   ```

4. **Test Locally:**
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

## 🌐 Render Deployment Steps

1. **Push to GitHub:**
   - [ ] Create new repository on GitHub
   - [ ] Upload all files to the repository
   - [ ] Make sure requirements.txt is included

2. **Deploy on Render:**
   - [ ] Go to [render.com](https://render.com)
   - [ ] Create account and connect GitHub
   - [ ] Select "New Web Service"
   - [ ] Choose your repository

3. **Configure Service:**
   - [ ] **Name:** `rag-document-system`
   - [ ] **Build Command:** `pip install -r requirements.txt`
   - [ ] **Start Command:** `gunicorn --bind 0.0.0.0:$PORT main:app`

4. **Set Environment Variables:**
   - [ ] `MISTRAL_API_KEY` = your Mistral API key
   - [ ] `API_BEARER_TOKEN` = token from generate_tokens.py
   - [ ] `SESSION_SECRET` = secret from generate_tokens.py
   - [ ] `FLASK_ENV` = `production`
   - [ ] `DATABASE_URL` = `sqlite:///rag_system.db` (or PostgreSQL)

## ✅ Testing Checklist

After deployment:

- [ ] **Web Interface:** Visit your Render URL and see the upload page
- [ ] **Status Check:** Click "Status" button - should show system ready
- [ ] **Upload Test:** Try uploading a PDF document
- [ ] **Query Test:** Ask a question about the document
- [ ] **API Test:** Use the API testing section on the page

## 🐛 Troubleshooting

If something doesn't work:

1. **Check Render Logs:**
   - Go to Render dashboard → Your service → Logs tab

2. **Common Issues:**
   - [ ] Missing environment variables
   - [ ] Wrong requirements.txt format
   - [ ] Import errors (check file names match exactly)

3. **Test API Endpoints:**
   - [ ] `GET /api/v1/status` - Should return system info
   - [ ] `GET /api/v1/config` - Should return bearer token

## 💡 Tips for Success

- **Double-check file names** - They must match exactly
- **Use the generated tokens** - Don't use the default hardcoded ones
- **Start with Free Tier** - Upgrade if you need more resources
- **Keep environment variables secure** - Never commit them to Git

## 🎉 You're Ready!

Once you complete this checklist, your RAG Document Query System will be:
- ✅ Running locally for development
- ✅ Deployed on Render for production use
- ✅ Secured with proper authentication
- ✅ Ready to process documents and answer questions

---

**Need help?** Check the detailed guide in `README_DEPLOYMENT.md`