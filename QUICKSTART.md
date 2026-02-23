# Quick Start Guide

## One-Command Setup

```bash
cd /Users/harshitagarwal/Desktop/verra
bash setup.sh
```

This will:
1. Check Python and Node installation
2. Install all Python dependencies
3. Install all Node dependencies
4. Initialize the SQLite database from vcus.csv
5. Create necessary .env files

## Manual Setup (if preferred)

### Backend Setup
```bash
cd backend

# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env
# Add: OPENAI_API_KEY=sk-your-api-key-here

# Install Python dependencies
pip install -r requirements.txt

# Initialize database (creates verra.db)
python3 init_db.py
```

### Frontend Setup
```bash
cd frontend

# Install Node dependencies
npm install

# Already configured for http://localhost:8000
```

## Start the Application

### Terminal 1 - Backend (Port 8000)
```bash
cd /Users/harshitagarwal/Desktop/verra/backend
python3 main.py
```

Expected output:
```
Startup: Checking database...
Setting up Vanna AI...
Vanna ready!
Started server process [PID]
Application startup complete [http://0.0.0.0:8000]
```

### Terminal 2 - Frontend (Port 3000)
```bash
cd /Users/harshitagarwal/Desktop/verra/frontend
npm run dev
```

Expected output:
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
```

## Access the Application

Open your browser: **http://localhost:3000**

You should see:
- Left sidebar with dataset stats and suggested questions
- Main chat area with welcome message
- Chat input at the bottom

## Try These Questions

1. **"Which projects are heating up?"**
   - Shows Hot quadrant projects with highest velocity

2. **"Show emerging opportunities in energy projects"**
   - Shows Emerging quadrant with rising momentum

3. **"Who are the top intermediaries?"**
   - Displays retirement beneficiaries and activity

4. **"Compare average momentum by country"**
   - Aggregated analysis by geography

## Verify Everything Works

### Backend Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}
```

### API Docs
Visit: **http://localhost:8000/docs**
- Interactive API documentation
- Try endpoints directly
- See request/response formats

### Frontend Console
Open browser DevTools (F12)
- Console: Should show API calls and no errors
- Network: Should see successful requests to http://localhost:8000

## Troubleshooting

**"Connection refused" on http://localhost:8000**
- Make sure backend is running in Terminal 1
- Check port 8000 is available: `lsof -i :8000`

**"Module not found" in backend**
- Ensure you're in the `verra/backend` directory
- Run `pip install -r requirements.txt`

**Frontend won't load**
- Make sure backend is running first
- Check .env.local has correct API URL

**Database initialization fails**
- Verify `vcus.csv` exists in `verra/` directory
- Check file permissions and available disk space (~50MB)
- Run: `python3 init_db.py --verbose`

**API returns "Vanna not initialized"**
- Backend is still starting - wait 10-15 seconds
- Check OpenAI API key in .env is correct
- Try restarting backend

## File Locations

```
Data:
/Users/harshitagarwal/Desktop/verra/vcus.csv
/Users/harshitagarwal/Desktop/verra/verra.db (created)

Backend:
/Users/harshitagarwal/Desktop/verra/backend/

Frontend:
/Users/harshitagarwal/Desktop/verra/frontend/

Logs:
Terminal 1: Backend logs
Terminal 2: Frontend logs
Browser Console: Frontend errors
```

## Next Steps

1. **Explore data** using suggested questions in sidebar
2. **Read the README** for detailed documentation
3. **Check IMPLEMENTATION_SUMMARY** for full technical details
4. **Review training_data.py** to add custom questions
5. **Deploy to production** - see README for deployment guide

## Support Files

- `README.md` - Full documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical implementation details
- `backend/training_data.py` - Vanna training data and business context
- `.env.example` - Environment variables template
- `setup.sh` - Automated setup script

## Environment Variables

### Backend (.env)
```
OPENAI_API_KEY=sk-your-key         # Required: OpenAI API key
LLM_MODEL=gpt-5.2                   # GPT model to use
BACKEND_HOST=0.0.0.0                # Bind address
BACKEND_PORT=8000                   # Port number
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend URL
```

## Performance Notes

- **First load**: 15-30 seconds (Vanna training on startup)
- **Typical query**: 2-5 seconds (OpenAI + database)
- **Chart generation**: Automatic, included in query response
- **Database size**: ~50MB (includes computed metrics)

Enjoy! 🚀
