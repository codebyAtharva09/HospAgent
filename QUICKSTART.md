# 🚀 HospAgent - Quick Start Guide

Get HospAgent up and running in 5 minutes!

## ⚡ Prerequisites Check

Before starting, ensure you have:
- ✅ **Node.js 18+** installed ([Download](https://nodejs.org/))
- ✅ **Python 3.9+** installed ([Download](https://www.python.org/))
- ✅ **Git** installed ([Download](https://git-scm.com/))

**Verify installations:**
```bash
node --version    # Should show v18.x or higher
python --version  # Should show 3.9.x or higher
git --version     # Should show git version
```

## 📥 Step 1: Clone Repository

```bash
git clone https://github.com/codebyAtharva09/HospAgent.git
cd HospAgent-Agentic-AI-
```

## 🔧 Step 2: Backend Setup (5 minutes)

### 2.1 Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2.2 Configure Environment

```bash
# Copy template
copy .env.template .env

# Edit .env file with your credentials
notepad .env  # Windows
# OR
nano .env     # macOS/Linux
```

**Minimum required configuration:**
```env
# Database (Get from supabase.com)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# AI Service (Get from console.groq.com - FREE)
GROQ_API_KEY=gsk_your_groq_api_key

# Authentication (Generate random string)
JWT_SECRET_KEY=your_random_secret_key_here
```

**Quick JWT Secret Generation:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.3 Start Backend Server

```bash
python main.py
```

✅ Backend running at: **http://localhost:8000**  
📚 API Docs: **http://localhost:8000/docs**

## 🎨 Step 3: Frontend Setup (3 minutes)

**Open a new terminal window:**

```bash
cd frontend
npm install
npm run dev
```

✅ Frontend running at: **http://localhost:5173**

## 🎉 Step 4: Access Application

1. **Open browser**: http://localhost:5173
2. **Login with default credentials:**
   - Username: `admin`
   - Password: `admin123`

## 🔑 Default User Accounts

| Username | Password | Role |
|----------|----------|------|
| superadmin | admin123 | SUPER_ADMIN |
| admin | admin123 | ADMIN |
| reception | reception123 | RECEPTION |
| pharmacist | pharma123 | PHARMACIST |

⚠️ **Change these passwords immediately in production!**

## 🛠️ Quick Troubleshooting

### Backend won't start?

```bash
# Check if port 8000 is free
netstat -ano | findstr :8000  # Windows
lsof -ti:8000                 # macOS/Linux

# Kill process if needed
taskkill /PID <PID> /F        # Windows
kill -9 <PID>                 # macOS/Linux
```

### Frontend won't start?

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Can't connect to backend?

1. Check backend is running at http://localhost:8000
2. Check `VITE_API_BASE_URL` in `frontend/.env`
3. Verify CORS settings in backend

### Database connection error?

1. Verify Supabase credentials in `backend/.env`
2. Test connection:
   ```bash
   cd backend
   python test_db_connection.py
   ```

## 📦 Optional: Get API Keys

### Groq (Free - Recommended)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up (free)
3. Create API key
4. Add to `backend/.env`: `GROQ_API_KEY=gsk_...`

### Supabase (Free tier available)
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Go to Settings > API
4. Copy URL and anon key
5. Add to `backend/.env`

### Vapi.ai (Optional - for voice features)
1. Go to [vapi.ai](https://vapi.ai)
2. Create account
3. Create assistant
4. Copy API key and Assistant ID
5. Add to both `backend/.env` and `frontend/.env`

## 🚀 Next Steps

1. **Explore the Dashboard**: Navigate to Command Center
2. **Try Live Data Mode**: Toggle "Live Data" switch
3. **Chat with AI**: Click the chat icon in bottom right
4. **Check Predictions**: Go to Predictive Analytics page
5. **Admin Panel**: Login as superadmin to manage users

## 📚 Learn More

- **Full Documentation**: See main [README.md](./README.md)
- **Backend Guide**: See [backend/README.md](./backend/README.md)
- **Frontend Guide**: See [frontend/README.md](./frontend/README.md)
- **API Documentation**: http://localhost:8000/docs

## 🆘 Need Help?

- 📖 Check the [Troubleshooting](#quick-troubleshooting) section
- 🐛 [Report an Issue](https://github.com/codebyAtharva09/HospAgent/issues)
- 💬 Contact: support@hospagent.com

## 🎯 Development Workflow

### Starting Development

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Making Changes

1. Edit files in `backend/` or `frontend/src/`
2. Changes auto-reload (HMR enabled)
3. Check browser console for errors
4. Test API at http://localhost:8000/docs

### Before Committing

```bash
# Frontend
cd frontend
npm run lint
npm run build  # Ensure it builds

# Backend
cd backend
python -m pytest  # Run tests
```

## 🔒 Security Checklist

Before deploying to production:

- [ ] Change all default passwords
- [ ] Generate strong JWT_SECRET_KEY
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up proper database backups
- [ ] Enable rate limiting
- [ ] Review and update security headers

---

**Happy Coding! 🎉**

For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md)
