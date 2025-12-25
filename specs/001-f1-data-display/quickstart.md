# Quickstart Guide: F1 Data Display System

**Feature**: F1 Data Display System  
**Branch**: `001-f1-data-display`  
**Plan**: [plan.md](plan.md)

## Purpose

Get the F1 Data Display System running on your local machine in under 5 minutes. This guide assumes you have Python 3.12+ installed.

---

## Prerequisites

- **Python**: 3.12 or higher
- **Git**: For cloning the repository
- **Terminal**: Command line access
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

**Check Python version**:
```bash
python3 --version
# Should show Python 3.12.0 or higher
```

---

## Setup Steps

### 1. Clone Repository (if not already done)

```bash
git clone <repository-url> f1-app
cd f1-app
```

### 2. Switch to Feature Branch

```bash
git checkout 001-f1-data-display
```

### 3. Create Virtual Environment

```bash
python3 -m venv .venv
```

### 4. Activate Virtual Environment

**Linux/macOS**:
```bash
source .venv/bin/activate
```

**Windows**:
```bash
.venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output**:
```
Installing collected packages: fastapi, uvicorn, python-multipart, requests, openai, pytest, pytest-asyncio
Successfully installed fastapi-0.115.5 uvicorn-0.32.1 ...
```

### 6. Verify Data Files

Ensure F1 data files exist:
```bash
ls f1data/ | head -5
# Should show: 1984_results.json, 1985_results.json, etc.

ls f1drivers/
# Should show: drivers.json

ls f1constructors/
# Should show: constructors.json
```

**If data files are missing**, run the fetch scripts:
```bash
python3 -m app.fetch_drivers    # Fetch driver data
python3 -m app.fetch_constructors  # Fetch constructor data
python3 -m app.fetch_season --year 2024  # Fetch specific season
```

### 7. Start the Server

```bash
uvicorn app.api_server:app --reload --host 0.0.0.0 --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 8. Open Web Interface

**In your browser**, navigate to:
```
http://localhost:8000
```

You should see the **F1 Stats** web interface with a search box and query suggestions.

---

## Quick Test

### Test 1: Web Interface Query

1. In the web UI, type: **"Who won the 2023 championship?"**
2. Press Enter or click the search icon
3. You should see results for Max Verstappen (Driver) and Red Bull (Constructor)

### Test 2: API Endpoint

**In a new terminal** (keep the server running):
```bash
curl http://localhost:8000/api/drivers/hamilton
```

**Expected response** (truncated):
```json
{
  "driverId": "hamilton",
  "givenName": "Lewis",
  "familyName": "Hamilton",
  "dateOfBirth": "1985-01-07",
  "nationality": "British",
  ...
}
```

### Test 3: API Documentation

Open in browser:
```
http://localhost:8000/docs
```

You should see **Swagger UI** with all API endpoints documented and interactive.

---

## Usage Examples

### Natural Language Queries

Try these queries in the web interface:

**Championship Queries**:
- "Who won the 2010 championship?"
- "2023 champion"
- "championship winner 1984"

**Driver Statistics**:
- "How many wins does Hamilton have?"
- "Verstappen stats"
- "About Michael Schumacher"

**Season Information**:
- "2023 standings"
- "2024 races"
- "Most races 2023"

**Constructor Queries**:
- "About Ferrari"
- "McLaren stats"
- "Red Bull championships"

**Comparisons**:
- "Compare Hamilton and Verstappen"
- "Vettel vs Alonso"

### API Endpoints

**List all drivers**:
```bash
curl http://localhost:8000/api/drivers
```

**Get specific driver**:
```bash
curl http://localhost:8000/api/drivers/hamilton
```

**Get driver statistics**:
```bash
curl http://localhost:8000/api/drivers/hamilton/stats
```

**Get season results**:
```bash
curl http://localhost:8000/api/seasons/2023
```

**Get season standings**:
```bash
curl http://localhost:8000/api/seasons/2023/standings
```

**List all constructors**:
```bash
curl http://localhost:8000/api/constructors
```

**Head-to-head comparison**:
```bash
curl "http://localhost:8000/api/stats/head-to-head?driver1=hamilton&driver2=verstappen"
```

**Natural language query (POST)**:
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Who won the 2010 championship?"}'
```

---

## Project Structure

```
f1-app/
├── app/                      # Backend application
│   ├── api_server.py        # FastAPI app entry point
│   ├── json_loader.py       # Data loading with caching
│   ├── query_parser.py      # Keyword-first query parsing
│   ├── llm_service.py       # Optional LLM fallback
│   ├── config.py            # Configuration management
│   ├── routers/             # API endpoint routers
│   │   ├── drivers.py       # /api/drivers endpoints
│   │   ├── seasons.py       # /api/seasons endpoints
│   │   ├── constructors.py  # /api/constructors endpoints
│   │   ├── analytics.py     # /api/stats endpoints
│   │   └── query.py         # /api/query endpoint
│   └── services/            # Business logic
│       └── f1_service.py    # F1 data service layer
│
├── static/                  # Frontend (zero-build)
│   ├── index.html          # Main query interface
│   ├── drivers.html        # Driver listing
│   ├── results.html        # Season results
│   ├── app.js              # Application logic
│   ├── drivers.css         # Driver styles
│   └── global.css          # Global styles
│
├── f1data/                 # Season results (JSON)
│   ├── 1984_results.json
│   └── ...
│
├── f1drivers/              # Driver database
│   └── drivers.json
│
├── f1constructors/         # Constructor database
│   └── constructors.json
│
├── tests/                  # Test suite
│   ├── conftest.py
│   └── test_f1_service.py
│
├── specs/                  # Feature specifications
│   └── 001-f1-data-display/
│       ├── spec.md         # Feature specification
│       ├── plan.md         # Implementation plan
│       ├── research.md     # Technical research
│       ├── data-model.md   # Entity relationships
│       ├── quickstart.md   # This file
│       └── contracts/      # API contracts
│
├── requirements.txt        # Python dependencies
├── config.json            # LLM configuration (optional)
└── README-SETUP.md        # Setup documentation
```

---

## Configuration (Optional)

### LLM Integration

The LLM service is **optional** - the app works fully without it using keyword-first parsing.

To enable LLM fallback for complex queries:

1. **Copy example config**:
   ```bash
   cp .env.example .env
   ```

2. **For Ollama (local)**:
   ```bash
   # Install Ollama: https://ollama.ai
   ollama pull llama2
   ```
   
   Update `config.json`:
   ```json
   {
     "primary_llm": "ollama",
     "ollama": {
       "model": "llama2",
       "base_url": "http://localhost:11434"
     }
   }
   ```

3. **For Azure OpenAI (cloud)**:
   
   Add to `.env`:
   ```
   AZURE_OPENAI_API_KEY=your-api-key-here
   ```
   
   Update `config.json`:
   ```json
   {
     "primary_llm": "azure",
     "azure": {
       "endpoint": "https://your-resource.openai.azure.com",
       "deployment": "your-deployment-name",
       "api_version": "2024-02-15-preview"
     }
   }
   ```

**Restart the server** after configuration changes.

---

## Development Mode

### Auto-reload on Code Changes

The `--reload` flag enables automatic reloading when Python files change:
```bash
uvicorn app.api_server:app --reload --host 0.0.0.0 --port 8000
```

Edit any Python file in `app/` and the server will automatically restart.

### Frontend Development

**No build process needed!** Edit HTML/CSS/JS files in `static/` and refresh your browser.

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_f1_service.py

# Run with coverage
pytest --cov=app
```

---

## Troubleshooting

### Issue: "Module not found" error

**Solution**: Ensure virtual environment is activated and dependencies installed:
```bash
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: "Port 8000 already in use"

**Solution**: Kill existing process or use different port:
```bash
# Use different port
uvicorn app.api_server:app --reload --port 8001

# Or kill existing process (Linux/macOS)
lsof -ti:8000 | xargs kill -9
```

### Issue: "Data file not found" error

**Solution**: Ensure data files exist:
```bash
ls f1data/ f1drivers/ f1constructors/
```

If missing, run fetch scripts:
```bash
python3 -m app.fetch_drivers
python3 -m app.fetch_constructors
python3 -m app.fetch_season --year 2024
```

### Issue: API returns empty results

**Check logs in terminal** where server is running. Common causes:
- Invalid driver/constructor ID (check spelling)
- Year outside 1984-2024 range
- Data file corrupted (re-fetch data)

### Issue: Web interface not loading

1. **Check server is running**: Terminal should show "Application startup complete"
2. **Check URL**: Should be `http://localhost:8000` (not https)
3. **Check browser console**: Press F12 and look for JavaScript errors
4. **Try different browser**: Chrome/Firefox recommended

---

## Performance Expectations

### Response Times (after initial cache load)

- **Keyword queries**: 1-5ms
- **API endpoints (cached)**: <100ms (95th percentile)
- **API endpoints (first call)**: 200-500ms (file load + cache)
- **LLM fallback (if enabled)**: 1-5s

### Memory Usage

- **Initial**: ~50MB (Python + FastAPI)
- **Fully cached**: ~70-80MB (all drivers + constructors + 5 seasons)
- **Peak**: <150MB under normal load

### Caching Behavior

- **Drivers**: Loaded once, cached permanently (~2MB)
- **Constructors**: Loaded once, cached permanently (~500KB)
- **Seasons**: LRU cache keeps last 5 accessed seasons (~10MB total)

---

## Next Steps

### For Users

1. **Explore the web interface**: Try different query types
2. **Browse API docs**: http://localhost:8000/docs
3. **View alternative docs**: http://localhost:8000/redoc
4. **Check existing pages**: 
   - http://localhost:8000/static/drivers.html
   - http://localhost:8000/static/results.html

### For Developers

1. **Read architecture docs**: See `_docs/keyword-first-architecture.md`
2. **Run tests**: `pytest tests/`
3. **Add new query patterns**: Edit `app/query_parser.py`
4. **Add new endpoints**: Create router in `app/routers/`
5. **Review spec**: See `specs/001-f1-data-display/spec.md`

---

## Support & Resources

- **API Documentation**: http://localhost:8000/docs
- **Feature Specification**: [spec.md](spec.md)
- **Implementation Plan**: [plan.md](plan.md)
- **Data Model**: [data-model.md](data-model.md)
- **API Contracts**: [contracts/openapi.yaml](contracts/openapi.yaml)
- **Constitution**: `.specify/memory/constitution.md`

---

## Success Criteria Verification

After setup, verify the success criteria from the specification:

- ✅ **SC-001**: Driver profile loads in <2 seconds
  ```bash
  time curl http://localhost:8000/api/drivers/hamilton
  ```

- ✅ **SC-009**: API response <100ms after cache warm-up
  ```bash
  # First call (cold): ~200-500ms
  time curl http://localhost:8000/api/drivers/hamilton
  # Second call (cached): <100ms
  time curl http://localhost:8000/api/drivers/hamilton
  ```

- ✅ **SC-004**: Natural language query returns in <5 seconds
  ```bash
  time curl -X POST http://localhost:8000/api/query \
    -H "Content-Type: application/json" \
    -d '{"query": "Who won the 2010 championship?"}'
  ```

All success criteria should pass with the quickstart setup!
