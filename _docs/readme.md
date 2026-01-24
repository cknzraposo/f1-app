# F1 Data API Documentation

A lightweight REST API for querying Formula 1 historical data (1984-2024). Built with FastAPI, this API provides efficient access to driver information, race results, constructor data, and analytics without requiring a database backend.
The main data source is https://api.jolpi.ca/ergast/ - which generates a set of .json files which then is used by this app.

## Features

- ✅ **Zero Database Dependency** - All data loaded from JSON files on-demand
- ✅ **Efficient Caching** - LRU caching for frequently accessed data
- ✅ **Original Data Structure** - API returns unmodified Ergast API JSON format
- ✅ **Comprehensive Endpoints** - Drivers, constructors, seasons, races, and analytics
- ✅ **Auto-Generated Documentation** - Interactive Swagger UI at `/docs`
- ✅ **CORS Enabled** - Ready for web frontend integration
- ✅ **Fast Performance** - Async FastAPI with lazy-loading strategy
- ✅ **Pure REST API** - No dependencies on external services or LLMs

## Quick Start

### Installation

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the API

```bash
# Activate the virtual environment (if not already active)
source venv/bin/activate

# Start the development server
uvicorn app.api_server:app --reload --host 0.0.0.0 --port 8000

# Or for production
uvicorn app.api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API Base URL**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Information

#### `GET /`
Get API information and available endpoint categories.

**Response:**
```json
{
  "name": "F1 Data API",
  "version": "1.0.0",
  "description": "REST API for querying Formula 1 historical data (1984-2024)",
  "documentation": "/docs",
  "endpoints": {
    "drivers": "/api/drivers",
    "constructors": "/api/constructors",
    "seasons": "/api/seasons"
  }
}
```

#### `GET /health`
Health check endpoint.

---

### Drivers

#### `GET /api/drivers`
Get all F1 drivers (874 drivers total).

**Response:** Returns complete `drivers.json` structure with MRData wrapper.

**Example:**
```bash
curl http://localhost:8000/api/drivers
```

---

#### `GET /api/drivers/{driver_id}`
Get specific driver by driverId.

**Parameters:**
- `driver_id` (path) - Driver's unique identifier (e.g., `max_verstappen`, `hamilton`)

**Example:**
```bash
curl http://localhost:8000/api/drivers/max_verstappen
```

**Response:**
```json
{
  "MRData": {
    "DriverTable": {
      "Drivers": [
        {
          "driverId": "max_verstappen",
          "permanentNumber": "33",
          "code": "VER",
          "url": "http://en.wikipedia.org/wiki/Max_Verstappen",
          "givenName": "Max",
          "familyName": "Verstappen",
          "dateOfBirth": "1997-09-30",
          "nationality": "Dutch"
        }
      ]
    }
  }
}
```

---

#### `GET /api/drivers/search`
Search drivers by name or nationality.

**Query Parameters:**
- `name` (optional) - Search by driver name (case-insensitive)
- `nationality` (optional) - Filter by nationality

**Examples:**
```bash
# Search by name
curl "http://localhost:8000/api/drivers/search?name=hamilton"

# Filter by nationality
curl "http://localhost:8000/api/drivers/search?nationality=British"

# Combine filters
curl "http://localhost:8000/api/drivers/search?name=michael&nationality=German"
```

---

#### `GET /api/drivers/{driver_id}/seasons/{year}`
Get all race results for a specific driver in a specific season.

**Parameters:**
- `driver_id` (path) - Driver's unique identifier
- `year` (path) - Season year (1984-2024)

**Example:**
```bash
curl http://localhost:8000/api/drivers/max_verstappen/seasons/2024
```

**Response:** Returns races with only the specified driver's results.

---

#### `GET /api/drivers/{driver_id}/stats`
Get career statistics for a driver.

**Parameters:**
- `driver_id` (path) - Driver's unique identifier
- `start_year` (query, optional) - Start year for stats calculation
- `end_year` (query, optional) - End year for stats calculation

**Example:**
```bash
curl http://localhost:8000/api/drivers/max_verstappen/stats

# Stats for specific period
curl "http://localhost:8000/api/drivers/max_verstappen/stats?start_year=2021&end_year=2024"
```

**Response:**
```json
{
  "driverId": "max_verstappen",
  "statistics": {
    "totalRaces": 187,
    "wins": 61,
    "podiums": 106,
    "totalPoints": 2846.5,
    "polePositions": 39,
    "fastestLaps": 32,
    "dnfs": 21,
    "teams": ["Red Bull", "Toro Rosso"],
    "firstRace": {
      "date": "2015-03-15",
      "raceName": "Australian Grand Prix",
      "season": 2015
    },
    "lastRace": {
      "date": "2024-12-08",
      "raceName": "Abu Dhabi Grand Prix",
      "season": 2024
    },
    "seasons": [
      {
        "season": 2024,
        "races": 24,
        "wins": 9,
        "podiums": 17,
        "points": 437.0
      }
    ]
  }
}
```

---

### Seasons

#### `GET /api/seasons`
Get list of available seasons (1984-2024).

**Example:**
```bash
curl http://localhost:8000/api/seasons
```

**Response:**
```json
{
  "seasons": [1984, 1985, ..., 2024],
  "count": 41,
  "firstSeason": 1984,
  "lastSeason": 2024
}
```

---

#### `GET /api/seasons/{year}`
Get all race data for a specific season.

**Parameters:**
- `year` (path) - Season year (1984-2024)

**Example:**
```bash
curl http://localhost:8000/api/seasons/2024
```

**Response:** Returns complete season JSON with all races and results.

---

#### `GET /api/seasons/{year}/races/{round}`
Get results for a specific race in a season.

**Parameters:**
- `year` (path) - Season year
- `round` (path) - Race round number (1-based)

**Example:**
```bash
curl http://localhost:8000/api/seasons/2024/races/1
```

---

#### `GET /api/seasons/{year}/standings`
Calculate driver and constructor championship standings for a season.

**Parameters:**
- `year` (path) - Season year

**Example:**
```bash
curl http://localhost:8000/api/seasons/2024/standings
```

**Response:**
```json
{
  "season": 2024,
  "driverStandings": [
    {
      "position": 1,
      "driverId": "max_verstappen",
      "name": "Max Verstappen",
      "nationality": "Dutch",
      "points": 437.0,
      "wins": 9,
      "podiums": 17
    }
  ],
  "constructorStandings": [
    {
      "position": 1,
      "constructorId": "mclaren",
      "name": "McLaren",
      "nationality": "British",
      "points": 666.0,
      "wins": 6
    }
  ]
}
```

---

#### `GET /api/seasons/{year}/winners`
Get list of race winners for a season.

**Parameters:**
- `year` (path) - Season year

**Example:**
```bash
curl http://localhost:8000/api/seasons/2024/winners
```

**Response:**
```json
{
  "season": 2024,
  "winners": [
    {
      "round": "1",
      "raceName": "Bahrain Grand Prix",
      "circuit": "Bahrain International Circuit",
      "date": "2024-03-02",
      "driver": {
        "driverId": "max_verstappen",
        "name": "Max Verstappen",
        "nationality": "Dutch"
      },
      "constructor": {
        "constructorId": "red_bull",
        "name": "Red Bull"
      },
      "grid": "1",
      "time": "1:31:44.742"
    }
  ],
  "count": 24
}
```

---

### Constructors

#### `GET /api/constructors`
Get all F1 constructors (214 constructors total).

**Response:** Returns complete `constructors.json` structure.

**Example:**
```bash
curl http://localhost:8000/api/constructors
```

---

#### `GET /api/constructors/{constructor_id}`
Get specific constructor by constructorId.

**Parameters:**
- `constructor_id` (path) - Constructor's unique identifier (e.g., `red_bull`, `mclaren`)

**Example:**
```bash
curl http://localhost:8000/api/constructors/red_bull
```

---

#### `GET /api/constructors/{constructor_id}/seasons/{year}`
Get all race results for a specific constructor in a specific season.

**Parameters:**
- `constructor_id` (path) - Constructor's unique identifier
- `year` (path) - Season year (1984-2024)

**Example:**
```bash
curl http://localhost:8000/api/constructors/red_bull/seasons/2024
```

**Response:** Returns races with all results for the specified constructor's drivers.

---

#### `GET /api/constructors/{constructor_id}/stats`
Get career statistics for a constructor.

**Parameters:**
- `constructor_id` (path) - Constructor's unique identifier
- `start_year` (query, optional) - Start year for stats calculation
- `end_year` (query, optional) - End year for stats calculation

**Example:**
```bash
curl http://localhost:8000/api/constructors/red_bull/stats

# Stats for specific period
curl "http://localhost:8000/api/constructors/red_bull/stats?start_year=2020&end_year=2024"
```

**Response:**
```json
{
  "constructorId": "red_bull",
  "statistics": {
    "totalRaces": 389,
    "wins": 121,
    "podiums": 254,
    "totalPoints": 6897.5,
    "polePositions": 93,
    "fastestLaps": 94,
    "drivers": ["coulthard", "verstappen", "webber", ...],
    "firstRace": {
      "date": "2005-03-06",
      "raceName": "Australian Grand Prix",
      "season": 2005
    },
    "lastRace": {
      "date": "2024-12-08",
      "raceName": "Abu Dhabi Grand Prix",
      "season": 2024
    },
    "seasons": [
      {
        "season": 2024,
        "races": 24,
        "wins": 14,
        "podiums": 35,
        "points": 589.0
      }
    ]
  }
}
```

---

### Analytics

#### `GET /api/stats/head-to-head`
Compare two drivers head-to-head.

**Query Parameters:**
- `driver1` (required) - First driver ID
- `driver2` (required) - Second driver ID
- `start_year` (optional) - Start year for comparison
- `end_year` (optional) - End year for comparison

**Example:**
```bash
curl "http://localhost:8000/api/stats/head-to-head?driver1=max_verstappen&driver2=hamilton"

# With date range
curl "http://localhost:8000/api/stats/head-to-head?driver1=max_verstappen&driver2=hamilton&start_year=2021&end_year=2024"
```

**Response:**
```json
{
  "driver1": {
    "driverId": "max_verstappen",
    "statistics": { ... }
  },
  "driver2": {
    "driverId": "hamilton",
    "statistics": { ... }
  },
  "headToHead": {
    "racesTogetherCount": 95,
    "driver1Better": 58,
    "driver2Better": 37,
    "races": [
      {
        "season": 2024,
        "round": "1",
        "raceName": "Bahrain Grand Prix",
        "date": "2024-03-02",
        "driver1Position": "1",
        "driver2Position": "7",
        "better": "max_verstappen"
      }
    ]
  }
}
```

---

#### `GET /api/stats/fastest-laps/{year}`
Get fastest laps for a season.

**Parameters:**
- `year` (path) - Season year
- `limit` (query, optional, default: 20) - Number of results to return

**Example:**
```bash
curl http://localhost:8000/api/stats/fastest-laps/2024

# With limit
curl "http://localhost:8000/api/stats/fastest-laps/2024?limit=10"
```

**Response:**
```json
{
  "season": 2024,
  "fastestLaps": [
    {
      "round": "1",
      "raceName": "Bahrain Grand Prix",
      "circuit": "Bahrain International Circuit",
      "driver": {
        "driverId": "max_verstappen",
        "name": "Max Verstappen"
      },
      "constructor": "Red Bull",
      "lap": "56",
      "time": "1:33.244",
      "rank": "1",
      "averageSpeed": {
        "value": "208.934",
        "units": "kph"
      }
    }
  ],
  "count": 24
}
```

---

## Data Structure

The API preserves the original Ergast API JSON structure:

```json
{
  "MRData": {
    "xmlns": "http://ergast.com/mrd/1.5",
    "series": "f1",
    "url": "...",
    "limit": "...",
    "offset": "...",
    "total": "...",
    "DriverTable": { ... },
    "ConstructorTable": { ... },
    "RaceTable": { ... }
  }
}
```

## Architecture

### Lazy Loading Strategy

- **Static Data (Cached)**: Drivers and constructors loaded once on first request
- **Dynamic Data (Lazy)**: Season results loaded on-demand with LRU cache (keeps last 5 seasons)
- **On-Demand Computation**: Statistics and analytics calculated in real-time

### File Structure

```
app/
├── json_loader.py       # JSON loading utilities with caching
├── api_server.py        # FastAPI application with all endpoints
├── f1_constructors.py   # Constructor data fetcher
├── f1_drivers.py        # Driver data fetcher
├── f1_results.py        # Results data fetcher
├── fetch_*.py           # Execution scripts
f1drivers/
├── drivers.json         # All driver data (~15-20 KB)
f1constructors/
├── constructors.json    # All constructor data (~10-12 KB)
f1data/
├── 1984_results.json    # Season results
├── ...
├── 2024_results.json    # (~6-8 MB total for all seasons)
```

### Performance Characteristics

- **Cold Start**: ~50ms (loading drivers/constructors)
- **Cached Request**: ~5-10ms
- **Season Data**: ~20-30ms (first request), ~5ms (cached)
- **Statistics Calculation**: ~100-500ms (depends on career length)
- **Memory Usage**: ~50MB (with 5 seasons cached)

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK` - Successful request
- `404 Not Found` - Resource not found (season, driver, constructor, race)
- `422 Unprocessable Entity` - Invalid query parameters
- `500 Internal Server Error` - Server error

**Error Response Format:**
```json
{
  "detail": "Driver 'invalid_driver' not found"
}
```

## CORS Configuration

CORS is enabled for all origins (`*`). For production, update the `allow_origins` in [app/api_server.py](../app/api_server.py):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

## Web Frontend Integration

Example JavaScript fetch:

```javascript
// Get all drivers
const drivers = await fetch('http://localhost:8000/api/drivers')
  .then(res => res.json());

// Get driver stats
const stats = await fetch('http://localhost:8000/api/drivers/max_verstappen/stats')
  .then(res => res.json());

// Search drivers
const search = await fetch('http://localhost:8000/api/drivers/search?name=hamilton')
  .then(res => res.json());

// Get season standings
const standings = await fetch('http://localhost:8000/api/seasons/2024/standings')
  .then(res => res.json());

// Head-to-head comparison
const h2h = await fetch('http://localhost:8000/api/stats/head-to-head?driver1=max_verstappen&driver2=hamilton')
  .then(res => res.json());
```

## Development

### Running in Development Mode

```bash
uvicorn app.api_server:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag enables auto-reload on code changes.

### Adding New Endpoints

1. Add endpoint function to [app/api_server.py](../app/api_server.py)
2. Use appropriate tags for organization
3. Add proper type hints and docstrings
4. Test with `/docs` interactive UI
5. Update this documentation

### Testing Endpoints

Use the interactive Swagger UI at `http://localhost:8000/docs` to test all endpoints with built-in request/response examples.

## Production Deployment

### Using Uvicorn

```bash
# Single worker
uvicorn app.api_server:app --host 0.0.0.0 --port 8000

# Multiple workers (recommended)
uvicorn app.api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Gunicorn + Uvicorn Workers

```bash
pip install gunicorn

gunicorn app.api_server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.api_server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## Future Enhancements

Potential additions:
- Race calendar endpoint with upcoming races
- Weather data integration
- Lap-by-lap race analysis
- Qualifying results endpoints
- Pit stop statistics
- Team radio transcripts (if data available)
- Driver rivalry detection algorithms
- Prediction models for race outcomes
- WebSocket support for real-time updates
- GraphQL endpoint as alternative to REST
- Rate limiting for public API deployment
- Authentication/API keys for premium features

## Data Source

Data collected from the Ergast F1 API (via jolpi.ca mirror):
- Base API: `https://api.jolpi.ca/ergast/f1`
- Coverage: 1984-2024 (41 seasons)
- Update frequency: Manual refresh using fetch scripts

To update data:
```bash
python app/fetch_drivers.py
python app/fetch_constructors.py
python app/fetch_season.py
```

## License

This API provides access to Formula 1 historical data. All F1 trademarks and copyrights are property of Formula One Licensing BV.

## Support

For issues or questions:
- Check interactive docs at `/docs`
- Review error responses for troubleshooting
- Examine JSON data files for structure reference

---

**API Version:** 1.0.0  
**Last Updated:** December 25, 2025  
**Data Coverage:** 1984-2024 (41 seasons, 874 drivers, 214 constructors)
