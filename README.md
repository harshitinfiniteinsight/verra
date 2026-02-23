# Verra VCU Interactive Data Chatbot

An AI-powered interactive chatbot for analyzing Verra carbon credit data using OpenAI GPT-5.2, Vanna AI for text-to-SQL, and SQLite. Ask questions in natural language and get intelligent analysis with interactive charts and tables.

## Features

- **Natural Language Q&A**: Ask questions like "Which projects are heating up?" or "Show emerging opportunities"
- **Momentum & Velocity Analytics**: Automatically computed per-project metrics based on retirement patterns
- **2x2 Quadrant Classification**: Projects classified as Hot, Emerging, Stable, or Dormant
- **Interactive Charts**: Auto-generated Plotly visualizations with zoom, pan, and hover tooltips
- **Intermediary Intelligence**: Track who is retiring credits and identify market patterns
- **Multi-turn Conversation**: Chat history maintained for context-aware follow-ups
- **Real-time SQL Display**: See the SQL generated for each query

## Architecture

```
Frontend (Next.js 14)        Backend (FastAPI)           Data (SQLite)
- React Components           - Vanna AI Framework        - Raw VCU Data
- Plotly Charts              - Text-to-SQL Engine        - Computed Metrics
- Chat Interface             - OpenAI GPT-5.2            - Intermediary Analysis
                              - REST API
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- OpenAI API key (for GPT-5.2)
- ~50MB disk space for database

### 1. Clone and Setup Backend

```bash
cd verra/backend

# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env
```

Add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-5.2
```

### 2. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
# This loads vcus.csv and creates computed metrics tables
python init_db.py
```

This will:
- Load ~22K rows from vcus.csv into SQLite
- Clean numeric columns (remove commas)
- Parse date columns
- Create indexes for performance
- Compute Momentum, Velocity, and quadrant classification
- Generate retirement beneficiary analysis

### 4. Start Backend

```bash
# From verra/backend/
python main.py

# Backend will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 5. Setup Frontend

In a new terminal:

```bash
cd verra/frontend

# Install dependencies (if not already done)
npm install

# Frontend will automatically use http://localhost:8000 for API
```

### 6. Start Frontend

```bash
npm run dev

# Frontend available at http://localhost:3000
```

## Usage

1. Open http://localhost:3000 in your browser
2. Browse suggested questions in the left sidebar, organized by category:
   - **Momentum**: "Which projects are heating up?"
   - **Supply**: "Show hot projects to warehouse"
   - **Market Intelligence**: "Who are the top intermediaries?"
   - **Analytics**: "Compare average momentum by country"
3. Or type your own natural language question
4. Results include:
   - Natural language response
   - SQL query executed
   - Data table (first 5 rows)
   - Interactive chart (if applicable)

## Key Computed Metrics

### Momentum (delta_z)
- **Definition**: Z-score of change in retirement activity between 180-day windows
- **Positive**: Project activity is rising (heating up)
- **Negative**: Project activity is falling (slowing down)
- **Near Zero**: Stable activity levels

### Velocity
- **Definition**: `(recent_90_retirements / total_quantity_issued) * 10,000`
- **Use**: Normalize activity across different project sizes
- **High**: Intensive recent trading activity
- **Low**: Lower trading intensity

### Quadrant Classification

| Momentum | Velocity | Quadrant | Meaning |
|----------|----------|----------|---------|
| Rising | High | **Hot** | Immediate trading opportunity |
| Rising | Low | **Emerging** | Pre-trade positioning, early interest |
| Stable | High | **Stable** | Predictable supply, watch for changes |
| Falling | Low | **Dormant** | Low near-term opportunity |

## Database Schema

### Primary Tables

**vcus**: Raw carbon credit data
- Issuance details (date, quantity, vintage period)
- Project info (ID, name, country, type, methodology)
- Retirement data (date, beneficiary, reason, details)
- Certifications (CORSIA, Article 6, etc.)

**project_summary**: Per-project aggregations
- Total issuances and retirements
- Cumulative quantities
- Unique beneficiary counts
- Date ranges

**project_metrics**: Computed metrics
- `recent_90d_count`: Retirement events in last 90 days
- `prior_90d_count`: Retirement events in prior 90-day period
- `recent_90z`: Z-score of recent activity
- `delta_z`: Momentum (z-score of change)
- `velocity`: Normalized activity intensity
- `quadrant`: Classification (Hot/Emerging/Stable/Dormant)

**retirement_beneficiaries**: Intermediary analysis
- Who is retiring credits for each project
- Retirement frequency
- Quantities retired

## API Endpoints

### Chat
`POST /api/chat`
```json
{
  "message": "Which projects are heating up?",
  "history": []
}
```

Response:
```json
{
  "text": "Found 5 hot projects...",
  "sql": "SELECT ...",
  "data": [...],
  "chart_spec": {...}
}
```

### Data Summary
`GET /api/data/summary`

Returns dataset overview with metrics distribution

### Suggested Questions
`GET /api/data/suggestions`

Returns categorized suggested questions

### Hot Projects
`GET /api/data/hot-projects?limit=10`

### Emerging Projects
`GET /api/data/emerging-projects?limit=10`

### Slowing Projects
`GET /api/data/slowing-projects?limit=10`

## Environment Variables

### Backend (.env)
```
OPENAI_API_KEY=sk-your-api-key
LLM_MODEL=gpt-5.2
BACKEND_HOST=localhost
BACKEND_PORT=8000
DATABASE_PATH=verra.db
DATA_PATH=../vcus.csv
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting

### Database initialization fails
- Ensure `vcus.csv` exists in the `verra/` directory
- Check file permissions
- Verify ~50MB free disk space

### Backend won't start
- Check OpenAI API key is valid
- Ensure port 8000 is not in use: `lsof -i :8000`
- Check Python dependencies: `pip list | grep vanna`

### Frontend can't reach backend
- Ensure backend is running: http://localhost:8000/health
- Check CORS headers in browser console
- Verify API URL in `.env.local`

### Vanna training fails
- Network issue with OpenAI API
- Invalid API key
- Rate limiting (wait and retry)

## Performance Tips

1. **Indexes**: Database created with indexes on frequently queried columns
2. **Pagination**: Tables show first 5 rows; use SQL LIMIT for large results
3. **Caching**: Suggested questions loaded once on sidebar init
4. **Streaming**: Charts render lazily with dynamic import

## Development

### Adding new suggested questions
Edit `backend/training_data.py`:
```python
CHATBOT_QUESTIONS = [
    "Your new question here?",
    # ...
]
```

### Updating Vanna training data
Edit `backend/training_data.py` and restart backend to retrain.

### Adding new API endpoints
Edit `backend/main.py` and add new route:
```python
@app.get("/api/my-endpoint")
async def my_endpoint():
    return {"data": "value"}
```

## Production Deployment

For production deployment:

1. **Backend**:
   - Use Gunicorn: `gunicorn -w 4 -b 0.0.0.0:8000 main:app`
   - Set up reverse proxy (nginx)
   - Use environment variables for secrets

2. **Frontend**:
   - Build: `npm run build`
   - Deploy to Vercel, Netlify, or your server
   - Update API URL in `.env.local`

3. **Database**:
   - Use production SQLite tools for backup
   - Or migrate to PostgreSQL for scale

## Support

For issues:
1. Check logs in terminal where server is running
2. Check browser console for frontend errors
3. Review API docs at `/docs` endpoint
4. Check Vanna documentation: https://github.com/vanna-ai/vanna

## License

MIT License - See LICENSE file for details

## Credits

Built with:
- [Vanna AI](https://github.com/vanna-ai/vanna) - Text-to-SQL framework
- [OpenAI GPT-5.2](https://platform.openai.com/docs/models/gpt-5.2) - Language model
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [Next.js](https://nextjs.org/) - Frontend framework
- [Plotly](https://plotly.com/) - Interactive charts
- [Tailwind CSS](https://tailwindcss.com/) - Styling
