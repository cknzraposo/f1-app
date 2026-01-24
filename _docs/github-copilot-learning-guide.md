# F1 App: GitHub Copilot Learning Guide & WSL Setup

This project demonstrates how the F1 Data API was built using GitHub Copilot using Github Speckit and provides step-by-step instructions for setting up the project on Windows Subsystem for Linux (WSL). Perfect for developers learning GitHub Copilot's capabilities.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [WSL Setup Guide for Beginners](#wsl-setup-guide-for-beginners)
3. [Project Architecture](#project-architecture)
4. [How This App Was Built with GitHub Copilot](#how-this-app-was-built-with-github-copilot)
5. [Learning Exercises](#learning-exercises)

---

## Project Overview

### What is the F1 App?

The **F1 Data API** is a lightweight REST API that provides access to Formula 1 historical data spanning 1984-2024. It demonstrates best practices in API design using a **keyword-first, LLM-optional** architecture.

**Key Characteristics:**
- 🚀 **Zero Database Dependency** - All data stored in JSON files
- ⚡ **Blazingly Fast** - 1-5ms response times for keyword queries
- 🎯 **Keyword-First Processing** - 90%+ of queries handled without AI
- 🤖 **Optional LLM Integration** - Fallback to Ollama/Azure OpenAI for complex queries
- 📊 **Comprehensive Data** - Drivers, constructors, seasons, races (1984-2024)
- 🌐 **Web Interface** - Simple HTML/JS chat interface, no build tools needed

### Use Cases

- Query championship winners by year
- Compare driver statistics
- Analyze team performance
- Get race standings and results
- Retrieve driver and constructor profiles

---

## WSL Setup Guide for Beginners

### Prerequisites

- Windows 10/11
- Administrator access
- 4GB+ RAM available
- ~5GB disk space

### Step 1: Enable WSL on Windows

Open PowerShell **as Administrator** and run:

```powershell
wsl --install
```

This installs WSL2 with Ubuntu by default. Restart your computer when prompted.

### Step 2: Verify WSL Installation

After restart, Ubuntu terminal will open automatically. Set up your Linux username and password.

Verify installation:
```bash
wsl --list --verbose
```

You should see Ubuntu with version 2.

### Step 3: Update Ubuntu Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 4: Install Python and Git

```bash
sudo apt install -y python3 python3-venv python3-pip git
```

Verify installations:
```bash
python3 --version
git --version
```

### Step 5: Clone the F1 App Repository

Choose a working directory (or create one):
```bash
mkdir -p ~/projects
cd ~/projects
```

Clone the repository:
```bash
git clone <repository-url>
cd f1-app
```

### Step 6: Set Up Python Virtual Environment

Create and activate a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

**Note:** Your terminal prompt should now show `(venv)` prefix, indicating the virtual environment is active.

### Step 7: Install Project Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- `fastapi==0.115.5` - Web framework
- `uvicorn==0.32.1` - ASGI server
- `requests>=2.31.0` - HTTP client
- `pytest>=7.4.0` - Testing framework

### Step 8: Start the Development Server

```bash
uvicorn app.api_server:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 9: Access the Application

Open your web browser and navigate to:

- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)

### Step 10: Test the API

In a new terminal (keeping the server running), test an endpoint:

```bash
# Test drivers endpoint
curl http://localhost:8000/api/drivers | head -50

# Test constructor stats
curl http://localhost:8000/api/constructors/red_bull/stats | jq

# Test driver stats
curl http://localhost:8000/api/drivers/max_verstappen/stats | jq
```

### Troubleshooting WSL Setup

**Problem:** `command not found: python3`
- **Solution:** `sudo apt install python3`

**Problem:** Virtual environment won't activate
- **Solution:** Ensure you're in the project directory: `cd ~/projects/f1-app && source venv/bin/activate`

**Problem:** Port 8000 already in use
- **Solution:** Use a different port: `uvicorn app.api_server:app --port 8001`

**Problem:** "ModuleNotFoundError" when running server
- **Solution:** Activate venv first: `source venv/bin/activate`

---

## Project Architecture

### Directory Structure

```
f1-app/
├── app/                          # Main application code
│   ├── api_server.py             # FastAPI application & routes
│   ├── query_parser.py           # Keyword-based query handler (PRIMARY)
│   ├── llm_service.py            # LLM integration (FALLBACK)
│   ├── json_loader.py            # Data loading with caching
│   ├── config.py                 # Configuration management
│   └── routers/                  # API route modules
│       ├── drivers.py
│       ├── constructors.py
│       └── analytics.py
├── f1data/                       # F1 race results (1984-2024)
│   ├── 1984_results.json
│   ├── 1985_results.json
│   └── ...
├── f1drivers/                    # All F1 drivers database
│   └── drivers.json
├── f1constructors/               # All F1 teams database
│   └── constructors.json
├── static/                       # Web interface
│   ├── index.html
│   ├── app.js
│   └── *.css
├── tests/                        # Test suite
├── _docs/                        # Documentation
├── requirements.txt              # Python dependencies
└── config.json                   # Configuration file
```

### Data Flow

```
User Query
    ↓
FastAPI Server
    ↓
QueryParser (Keyword Matching) ← PRIMARY PATH (90%+)
    ↓
    Match Found?
    ├─ YES → Execute API Call → Return Result ⚡ (1-5ms)
    └─ NO → LLMService (Fallback) → Execute API Call → Return Result 🤖 (1-5s)
```

---

## How This App Was Built with GitHub Copilot

This section demonstrates the development process using GitHub Copilot, showing how it accelerates API development, code generation, and architectural decisions.

### Phase 1: Project Initialization & Architecture

**Goal:** Set up FastAPI project structure

**Copilot Prompts Used:**

1. **Initial Project Structure**
```
Prompt: "Create a FastAPI project structure for a Formula 1 data API with 
drivers, constructors, seasons, and race results endpoints"

Response: Generated folder structure, main app file, requirements.txt with 
appropriate dependencies
```

**What Copilot Provided:**
- ✅ Proper FastAPI project layout
- ✅ Initial `requirements.txt` with compatible versions
- ✅ Basic FastAPI app scaffolding
- ✅ CORS middleware configuration

2. **Configuration Management**
```
Prompt: "Create a config.py file that loads settings from config.json 
and environment variables, with fallback defaults for LLM settings"

Response: Complete config.py with:
- JSON config loading
- Environment variable overrides
- Graceful degradation
- Type hints
```

### Phase 2: Data Layer Development

**Goal:** Load F1 data efficiently with caching

**Copilot Prompts Used:**

1. **JSON Loading with LRU Cache**
```
Prompt: "Create a json_loader.py module that loads drivers.json, 
constructors.json, and season results with lru_cache. Drivers and 
constructors should be cached permanently, seasons should use LRU(5)"

Response: Generated:
- load_drivers() with @lru_cache
- load_constructors() with @lru_cache
- load_season_results(year) with @lru_cache(maxsize=5)
- Proper error handling
- Data validation
```

**Key Learning:** Copilot understood caching requirements from natural language and generated proper decorators.

### Phase 3: Core API Endpoints

**Goal:** Build RESTful endpoints for common queries

**Copilot Prompts Used:**

1. **Drivers Endpoints**
```
Prompt: "Add FastAPI routes for:
1. GET /api/drivers - return all drivers
2. GET /api/drivers/{driver_id} - return specific driver
3. GET /api/drivers/{driver_id}/stats - return driver statistics
Make sure to use the cached load_drivers() function"

Response: Generated:
- Three complete endpoints with proper decorators
- Error handling (404 when driver not found)
- Swagger documentation
- Type hints for request/response
```

**Key Learning:** Copilot maintained consistency with existing code patterns and automatically added documentation.

2. **Constructors Endpoints**
```
Prompt: "Create similar endpoints for constructors: 
/api/constructors, /api/constructors/{id}, /api/constructors/{id}/stats
Use the same pattern as drivers endpoints"

Response: Generated parallel endpoints with:
- Consistent naming and structure
- Reusable code patterns
- Proper error handling
```

### Phase 4: Query Parser (Keyword-First Architecture)

**Goal:** Build natural language query parser for pattern matching

**Copilot Prompts Used:**

1. **Query Parser Foundation**
```
Prompt: "Create app/query_parser.py with a QueryParser class that:
- Loads drivers and constructors on init
- Has methods to extract years (1984-2024) using regex
- Has methods to extract driver names using fuzzy matching (difflib)
- Returns a dict with action, endpoint, params, context for matched queries
- Should handle common F1 queries like 'who won 2023 championship' 
  or 'how many wins hamilton'"

Response: Generated:
- QueryParser class with proper initialization
- Regex patterns for year extraction
- Fuzzy matching implementation
- Multiple query pattern methods
```

**Key Learning:** Copilot understood architectural requirements and created a well-structured pattern matcher.

2. **Championship Query Pattern**
```
Prompt: "Add a parse_championship_query method to QueryParser that:
- Detects championship queries (keywords: 'championship', 'champion', 'won')
- Extracts the year from the query
- Returns action='championship', endpoint='/api/seasons/{year}/standings'"

Response: Generated:
- Keyword detection
- Year extraction using existing regex
- Proper return structure
- Docstring explaining the method
```

3. **Driver Stats Pattern**
```
Prompt: "Add parse_driver_stats_query method that:
- Detects stats queries (keywords: 'wins', 'podiums', 'points', 'races')
- Extracts driver name using fuzzy matching
- Returns action='driver_stats', endpoint pointing to /api/drivers/{id}/stats"

Response: Generated:
- Proper keyword and entity extraction
- Integration with existing fuzzy matching
- Consistent return format
```

**Key Learning:** Copilot maintained code patterns and structure when adding new features.

### Phase 5: LLM Fallback Service

**Goal:** Add optional LLM support for complex queries

**Copilot Prompts Used:**

1. **LLM Service Architecture**
```
Prompt: "Create app/llm_service.py that:
- Loads config from app/config.py
- Has a query() method that tries Ollama first, then Azure OpenAI
- Builds F1-specific prompts for query understanding
- Returns action, endpoint, params like QueryParser does
- Gracefully handles missing/unavailable LLM"

Response: Generated:
- LLMService class with proper initialization
- Ollama integration code
- Azure OpenAI fallback
- Error handling for unavailable services
- F1-specific system prompt
```

### Phase 6: Web Interface

**Goal:** Create user-facing chat interface

**Copilot Prompts Used:**

1. **HTML Chat Interface**
```
Prompt: "Create static/index.html with:
- Chat input form
- Messages display area
- Tailwind CSS styling (CDN)
- Responsive design
- Indicator showing which processor handled the query (keyword/ollama/azure)"

Response: Generated:
- Complete HTML structure
- Tailwind CSS styling
- Semantic HTML
- Accessibility features
```

2. **JavaScript Frontend Logic**
```
Prompt: "Create static/app.js that:
- Sends query to /api/query endpoint
- Displays messages in chat interface
- Shows loading indicator
- Displays the 'source' of the response (keyword/ollama/azure)
- Handles errors gracefully"

Response: Generated:
- Fetch API integration
- DOM manipulation
- Error handling
- Loading states
```

### Phase 7: Testing

**Goal:** Add test coverage for API and query parser

**Copilot Prompts Used:**

1. **API Tests**
```
Prompt: "Create tests/test_api.py with pytest that:
- Tests /api/drivers endpoint returns all drivers
- Tests /api/drivers/{id} returns specific driver or 404
- Tests /api/constructors endpoints similarly
- Uses @pytest.mark.asyncio for async tests"

Response: Generated:
- Complete test file with proper fixtures
- All endpoint tests
- Error case handling
- Proper async/await usage
```

2. **Query Parser Tests**
```
Prompt: "Create tests/test_query_parser.py that:
- Tests championship query parsing
- Tests driver stats extraction
- Tests year extraction from various formats
- Tests fuzzy driver name matching"

Response: Generated:
- Test cases for each pattern
- Edge case handling
- Assertion patterns
- Docstrings for tests
```

### Phase 8: Documentation & Configuration

**Goal:** Document API and configuration

**Copilot Prompts Used:**

1. **API Documentation**
```
Prompt: "Create detailed docstrings for all FastAPI endpoints that:
- Describe what the endpoint does
- List all parameters
- Show example responses
- Include usage examples with curl"

Response: Generated:
- Comprehensive docstrings for each endpoint
- Proper formatting for Swagger UI
- Example responses
- Parameter descriptions
```

2. **Configuration Template**
```
Prompt: "Create config.json template with:
- ollama_enabled: boolean
- ollama_model: string
- azure_enabled: boolean
- azure_api_key: string (marked as env var)
- Comments explaining each setting"

Response: Generated:
- Well-structured JSON template
- Helpful comments
- Example values
- Environment variable references
```

---

## Learning Exercises

Use these exercises to practice GitHub Copilot while extending the F1 App.

### Exercise 1: Add a New Endpoint (Beginner)

**Objective:** Add a `/api/drivers/{driver_id}/races` endpoint that returns all races for a specific driver

**Steps:**

1. Open `app/api_server.py`
2. Use Copilot prompt:
```
Prompt: "Add a new endpoint GET /api/drivers/{driver_id}/races that:
- Takes driver_id as path parameter
- Searches all season results for races with that driver
- Returns a list of races with driver's position and points
- Returns 404 if driver not found"
```

3. Copilot will generate the endpoint
4. Test it: `curl http://localhost:8000/api/drivers/max_verstappen/races | jq`

**What You Learn:**
- How Copilot understands endpoint patterns
- Proper error handling in FastAPI
- Data filtering and transformation

---

### Exercise 2: Add a Query Parser Pattern (Intermediate)

**Objective:** Add support for "fastest laps" queries to the parser

**Steps:**

1. Open `app/query_parser.py`
2. Add keywords:
```python
FASTEST_LAP_KEYWORDS = ['fastest lap', 'fastest laps', 'pole position']
```

3. Use Copilot prompt:
```
Prompt: "Add a parse_fastest_lap_query method to QueryParser that:
- Detects fastest lap queries using FASTEST_LAP_KEYWORDS
- Extracts year (default to current year if not specified)
- Extracts driver name if mentioned
- Returns action='fastest_laps', endpoint='/api/fastest-laps/{year}'
- Includes params for driver filter if provided"
```

4. Test it: `curl http://localhost:8000/api/query -X POST -d '{"query": "fastest laps 2023"}'`

**What You Learn:**
- Pattern design with Copilot
- Keyword extraction strategies
- Copilot's code consistency

---

### Exercise 3: Add LLM Prompt Enhancement (Intermediate)

**Objective:** Improve the LLM prompt to better understand F1 domain

**Steps:**

1. Open `app/llm_service.py`
2. Find the `SYSTEM_PROMPT`
3. Use Copilot prompt:
```
Prompt: "Enhance the F1 SYSTEM_PROMPT to include:
- A list of valid F1 actions (championship, driver_stats, constructor_stats, etc.)
- Instructions to always return JSON with action, endpoint, params
- F1 domain knowledge (driver names, team names, championship rules)
- Examples of complex queries and their expected responses"
```

4. Test with a complex query in the web interface

**What You Learn:**
- Prompt engineering with Copilot
- Domain-specific LLM optimization
- JSON response formats

---

### Exercise 4: Create a New Data Endpoint (Advanced)

**Objective:** Add a head-to-head driver comparison endpoint

**Steps:**

1. Create new file `app/routers/analytics.py`
2. Use Copilot prompt:
```
Prompt: "Create app/routers/analytics.py with an endpoint 
GET /api/stats/head-to-head?driver1={id}&driver2={id} that:
- Compares two drivers across all seasons
- Returns total wins, podiums, points, races for each
- Calculates head-to-head record
- Formats results in a comparison structure
- Uses load_season_results() and load_drivers()"
```

3. Include the router in `api_server.py`:
```python
from app.routers import analytics
app.include_router(analytics.router, prefix="/api")
```

4. Test: `curl 'http://localhost:8000/api/stats/head-to-head?driver1=max_verstappen&driver2=lewis_hamilton'`

**What You Learn:**
- Copilot's ability to generate complex data logic
- Data aggregation and comparison
- Router modularization in FastAPI

---

### Exercise 5: Add Unit Tests (Intermediate)

**Objective:** Write tests for the query parser using Copilot

**Steps:**

1. Open `tests/test_query_parser.py`
2. Use Copilot prompt:
```
Prompt: "Add test functions for QueryParser that test:
- parse_championship_query with various year formats
- parse_driver_stats_query with driver name variations
- extract_year method with different year mentions
- Fuzzy driver name matching edge cases
All tests should use pytest and be documented with docstrings"
```

3. Run tests: `pytest tests/test_query_parser.py -v`

**What You Learn:**
- Test generation with Copilot
- Test naming conventions
- pytest patterns and assertions

---

### Exercise 6: Document Your Changes (Beginner)

**Objective:** Use Copilot to auto-generate documentation

**Steps:**

1. After implementing a new feature, select the code
2. Use Copilot prompt:
```
Prompt: "Generate comprehensive docstrings and a markdown section 
explaining how this feature works, including:
- Function/endpoint description
- Parameters and return types
- Example usage with curl
- Edge cases handled"
```

3. Add the generated documentation to `_docs/readme.md`

**What You Learn:**
- Documentation generation with Copilot
- Proper docstring formatting
- Example creation

---

## Key Takeaways: Building with GitHub Copilot

### ✅ Best Practices

1. **Be Specific in Prompts** - Include return types, error handling, and patterns
2. **Maintain Consistency** - Copilot learns from existing code patterns
3. **Leverage Domain Knowledge** - Mention F1 concepts in prompts for better results
4. **Verify Generated Code** - Always test endpoints and run tests
5. **Iterate with Copilot** - Refine prompts based on generated code
6. **Document as You Go** - Use Copilot to generate docstrings and markdown

### 🎯 Copilot's Strengths in This Project

- **Boilerplate Generation** - FastAPI endpoints, config management
- **Pattern Recognition** - Generated consistent query parser methods
- **Data Processing** - Complex filtering and aggregation logic
- **Testing** - Complete test files with proper patterns
- **Documentation** - API docs, docstrings, markdown guides

### ⚠️ What Copilot Needs Your Help With

- **Architecture Decisions** - Overall structure design
- **Edge Cases** - Specific business logic requirements
- **Performance Tuning** - Caching strategies, optimization
- **Security** - Authentication, validation rules
- **Testing Strategy** - What to test and how thoroughly

---

## Next Steps

1. **Explore the API** - Visit http://localhost:8000/docs to see all endpoints
2. **Try the Exercises** - Start with Exercise 1, progress to more complex ones
3. **Extend the App** - Add new features using Copilot
4. **Contribute** - Submit improvements back to the project
5. **Learn More** - Read `_docs/keyword-first-architecture.md` for deeper insights

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [GitHub Copilot Docs](https://github.com/features/copilot)
- [Ergast F1 API](https://api.jolpi.ca/ergast/)
- [Project README](./readme.md)
- [Architecture Deep Dive](./ARCHITECTURE.md)

