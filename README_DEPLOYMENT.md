# RAG Document Query System - Deployment Guide

## 📋 Prerequisites

Before deploying, make sure you have:
- **Mistral AI API Key** - Get one from [console.mistral.ai](https://console.mistral.ai)
- **Bearer Token** - Generate a secure random string for API authentication
- **Database** (optional) - PostgreSQL for production (SQLite is used by default)

## 🔧 Required Dependencies (requirements.txt)

Create a `requirements.txt` file with these dependencies:

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

## 🖥️ Local Development Setup

### 1. Clone and Setup

```bash
# Clone the repository (download all files)
# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your actual values:
# MISTRAL_API_KEY=your-mistral-api-key-here
# API_BEARER_TOKEN=your-secure-bearer-token-here
# SESSION_SECRET=your-random-session-secret
```

### 3. Run Locally

```bash
# Option 1: Using Flask development server
python main.py

# Option 2: Using Gunicorn (production-like)
gunicorn --bind 0.0.0.0:5000 --reload main:app
```

The application will be available at `http://localhost:5000`

## 🚀 Render Deployment

### Method 1: Using GitHub Repository

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to [render.com](https://render.com) and sign up/login
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name:** `rag-document-system`
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT main:app`
     - **Instance Type:** Free or paid tier

3. **Environment Variables:**
   Set these in your Render dashboard:
   ```
   MISTRAL_API_KEY=your-mistral-api-key-here
   API_BEARER_TOKEN=your-secure-bearer-token-here
   SESSION_SECRET=your-random-session-secret
   DATABASE_URL=sqlite:///rag_system.db (or PostgreSQL URL)
   FLASK_ENV=production
   ```

### Method 2: Using render.yaml (Infrastructure as Code)

The included `render.yaml` file will automatically configure your deployment:

1. Push to GitHub as above
2. On Render, select "Deploy using render.yaml"
3. Set the environment variables in the Render dashboard

## 🗄️ Database Configuration

### SQLite (Default - Good for testing)
```env
DATABASE_URL=sqlite:///rag_system.db
```

### PostgreSQL (Recommended for production)
```env
DATABASE_URL=postgresql://username:password@hostname:port/database_name
```

For Render, you can add a PostgreSQL database:
1. Go to your Render dashboard
2. Click "New +" → "PostgreSQL"
3. Copy the connection URL to your environment variables

## 🔐 Security Configuration

### Generate Secure Tokens

```python
# Generate a secure bearer token
import secrets
bearer_token = secrets.token_hex(32)
print(f"API_BEARER_TOKEN={bearer_token}")

# Generate a session secret
session_secret = secrets.token_hex(16)
print(f"SESSION_SECRET={session_secret}")
```

### Production Security Checklist

- ✅ Use strong, unique bearer tokens
- ✅ Set `FLASK_ENV=production`
- ✅ Use PostgreSQL for production database
- ✅ Keep API keys secure and never commit them to code
- ✅ Use HTTPS in production (Render provides this automatically)

## 🧪 Testing Your Deployment

1. **Check System Status:**
   ```bash
   curl https://your-app.onrender.com/api/v1/status
   ```

2. **Test Document Upload:**
   ```bash
   curl -X POST https://your-app.onrender.com/api/v1/hackrx/run \
     -H "Authorization: Bearer YOUR_BEARER_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "documents": "https://example.com/sample.pdf",
       "questions": ["What is this document about?"]
     }'
   ```

3. **Access Web Interface:**
   Visit `https://your-app.onrender.com` in your browser

## 🏗️ File Structure for Deployment

Your deployment should include these files:

```
rag-document-system/
├── main.py                 # Application entry point
├── app.py                  # Flask application setup
├── api_routes.py           # API endpoints
├── rag_system.py           # Core RAG functionality
├── document_processor.py   # Document processing
├── vector_store.py         # Vector storage and search
├── models.py               # Database models
├── templates/
│   ├── base.html
│   └── index.html
├── static/
│   ├── css/custom.css
│   └── js/main.js
├── requirements.txt        # Python dependencies
├── runtime.txt            # Python version
├── render.yaml            # Render configuration
├── .env.example           # Environment template
└── README_DEPLOYMENT.md   # This file
```

## 🐛 Troubleshooting

### Common Issues:

1. **Import Errors:**
   - Ensure all Python files are in the root directory
   - Check that requirements.txt includes all dependencies

2. **Database Issues:**
   - Verify DATABASE_URL is correctly set
   - For PostgreSQL, ensure the database exists

3. **API Authentication:**
   - Check that API_BEARER_TOKEN matches between server and client
   - Verify the /api/v1/config endpoint returns the correct token

4. **Memory/Performance:**
   - Render free tier has limitations
   - Consider upgrading to a paid tier for production use

### Logs and Debugging:

On Render, you can view logs in the dashboard under "Logs" tab.

For local debugging:
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python main.py
```

## 📞 Support

If you encounter issues:
1. Check the logs in your Render dashboard
2. Verify all environment variables are set correctly
3. Test the API endpoints individually
4. Ensure your bearer token is properly configured

---

**Ready to deploy!** 🚀 Your RAG Document Query System is now configured for both local development and production deployment on Render.