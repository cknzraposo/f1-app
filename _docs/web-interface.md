# F1 AI Assistant - Web Interface Documentation

## Overview

The F1 AI Assistant adds a modern web interface with natural language query capabilities to the existing F1 Data API. Users can ask questions like "who won the F1 championship in 2010" and receive conversational responses with rich data visualizations.

## Architecture

### Query Processing Strategy

The system uses a **keyword-first approach** for fast, reliable query processing:

1. **Primary: Keyword Pattern Matching** ([app/query_parser.py](../app/query_parser.py))
   - Fast text-based pattern recognition
   - Extracts years, driver names, team names
   - Matches common question patterns
   - No external dependencies (works offline)
   - ~99% of common queries handled here

2. **Secondary: LLM Fallback** ([app/llm_service.py](../app/llm_service.py))
   - Used only when keyword matching fails
   - Handles complex or unusual phrasing
   - Ollama (local) → Azure OpenAI (cloud) fallback chain

### Components

1. **Keyword Parser** ([app/query_parser.py](../app/query_parser.py)) - NEW
   - Pattern-based query understanding
   - Regex for years, names, entities
   - Zero-latency matching
   - No API keys or services required

2. **Configuration System** ([config.json](../config.json), [app/config.py](../app/config.py))
   - Centralized configuration for LLM endpoints
   - Environment variable overrides for sensitive data
   - Support for both Ollama (local) and Azure OpenAI (cloud)

2. **LLM Service Layer** ([app/llm_service.py](../app/llm_service.py))
   - Unified interface for multiple LLM providers
   - Automatic fallback from Ollama to Azure OpenAI
   - Two-step query processing: (1) parse question → API call, (2) format results as natural language

3. **Chat API Endpoint** ([app/api_server.py](../app/api_server.py))
   - `POST /api/chat` - Accepts natural language questions
   - Executes internal API calls based on LLM parsing
   - Returns enriched responses with structured data

4. **Web Frontend** ([static/index.html](../static/index.html), [static/app.js](../static/app.js))
   - Sleek chat interface built with vanilla HTML and Tailwind CSS
   - Real-time message updates with loading indicators
   - Rich data cards for standings, statistics, and race results
   - Responsive design for mobile and desktop

## Features

### Natural Language Processing

The system uses a **two-tier processing approach**:

**Tier 1: Keyword Matching (Primary - Always First)**
```
User: "Who won the 2010 championship?"
  ↓
QueryParser: Detects "championship" + "2010"
  ↓
Result: {"endpoint": "/api/seasons/2010/standings", "source": "keyword_parser"}
  ↓
API: Returns championship data
  ↓
Simple Summary: Text-based formatting
  ↓
User: "Sebastian Vettel won the 2010 championship..."
```

**Tier 2: LLM Fallback (Secondary - Only if Keywords Fail)**
```
User: "Tell me about the German guy who raced for Red Bull in the early 2010s"
  ↓
QueryParser: No pattern match
  ↓
LLM (Ollama): Interprets complex query
  ↓
Result: {"endpoint": "/api/drivers/search", "params": {"name": "vettel"}}
  ↓
API: Returns driver data
  ↓
LLM Summary: Natural language generation
  ↓
User: Conversational response about Sebastian Vettel
```

### Supported Query Patterns (Keyword Tier)

The keyword parser handles these patterns instantly:

- **"[year] championship"** → `/api/seasons/{year}/standings`
- **"how many wins [driver]"** → Search driver → `/api/drivers/{id}/stats`
- **"[driver] stats"** → Search driver → `/api/drivers/{id}/stats`
- **"about [team]"** → `/api/constructors/{team}/stats`
- **"[year] standings"** → `/api/seasons/{year}/standings`
- **"compare [driver1] and [driver2]"** → `/api/stats/head-to-head`
- **"most races [year]"** → `/api/seasons/{year}/winners`

**Example Flow:**
```
User: "Who won the 2010 championship?"
  ↓
LLM: {"action": "api_call", "endpoint": "/api/seasons/2010/standings", "params": {}}
  ↓
API: Returns championship standings data
  ↓
LLM: Generates natural language summary
  ↓
User: "Sebastian Vettel won the 2010 Formula 1 World Championship..."
```

### Data Visualizations

The frontend automatically formats different data types:

- **Championship Standings**: Ranked tables with driver/constructor positions, points, wins, and podiums
- **Career Statistics**: Grid layouts showing races, wins, podiums, points, pole positions, fastest laps
- **Race Results**: Detailed race information with driver positions and timing data

### LLM Provider Support

#### Primary: Ollama (Local)
- **Endpoint**: `http://localhost:11434`
- **Default Model**: `llama3.2` (configurable)
- **Advantages**: Free, fast, private, no API keys required
- **Setup**: Install Ollama and run `ollama pull llama3.2`

#### Fallback: Azure OpenAI (Cloud)
- **Configuration**: Via [config.json](../config.json) or environment variables
- **Usage**: Automatic fallback when Ollama is unavailable
- **Setup**: Set `azure_openai.enabled = true` and provide credentials

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies:
- `requests` - HTTP client for Ollama API (optional - only for LLM fallback)
- `openai` - Azure OpenAI SDK (optional - only if using Azure)

### 2. Configure Ollama (Optional - For LLM Fallback)

**The app works without Ollama!** Keyword matching handles most queries.

To enable LLM fallback for complex questions:

Install Ollama from [ollama.ai](https://ollama.ai) and pull a model:

```bash
# Install Ollama (Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.2

# Verify it's running
ollama list
```

### 3. Configure Azure OpenAI (Optional)

If you want to use Azure OpenAI as a fallback:

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Azure OpenAI credentials:
   ```
   AZURE_OPENAI_API_KEY=your-key-here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
   ```

3. Enable in [config.json](../config.json):
   ```json
   {
     "llm": {
       "azure_openai": {
         "enabled": true,
         ...
       }
     }
   }
   ```

### 4. Start the Server

```bash
uvicorn app.api_server:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access the Web Interface

Open your browser to:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Info**: http://localhost:8000/api

## Configuration Reference

### config.json Structure

```json
{
  "llm": {
    "primary": "ollama",
    "ollama": {
      "endpoint": "http://localhost:11434",
      "model": "llama3.2",
      "timeout": 30
    },
    "azure_openai": {
      "enabled": false,
      "endpoint": "",
      "api_version": "2024-02-01",
      "deployment_name": "gpt-4"
    }
  },
  "app": {
    "name": "F1 AI Assistant",
    "version": "1.0.0"
  }
}
```

### Environment Variables

- `AZURE_OPENAI_API_KEY` - Azure OpenAI API key (overrides config)
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint URL (overrides config)

## API Reference

### POST /api/chat

**Request:**
```json
{
  "message": "Who won the 2010 championship?"
}
```

**Response:**
```json
{
  "message": "Sebastian Vettel won the 2010 Formula 1 World Championship...",
  "data": {
    "season": 2010,
    "driverStandings": [...],
    "constructorStandings": [...]
  },
  "source": "ollama",
  "endpoint_called": "/api/seasons/2010/standings"
}
```

## Supported Queries

The assistant can answer questions about:

- **Championships**: "Who won the championship in [year]?"
- **Driver Stats**: "How many wins does [driver] have?"
- **Constructor Info**: "Tell me about [team]"
- **Season Data**: "Who won the most races in [year]?"
- **Comparisons**: "Compare Hamilton and Vettel"
- **Race Results**: "What happened in the [year] [race name]?"

## Architecture Decisions

### Why Keyword Matching First?

- **Speed**: Instant response (~1-5ms vs 1-5 seconds for LLM)
- **Reliability**: No dependency on external services
- **Deterministic**: Same query always produces same result
- **Offline**: Works without internet or LLM installation
- **Cost**: Zero API costs or compute requirements
- **Coverage**: Handles 90%+ of typical F1 queries

### When LLM is Used

LLM fallback activates for:
- Ambiguous phrasing: "the fast German driver"
- Complex questions: "who dominated the hybrid era"
- Conversational queries: "how did that season go for McLaren"
- Follow-up context: "what about the next year"

### Why Vanilla HTML/JS?

- **Simplicity**: No build process, bundlers, or complex tooling
- **Performance**: Minimal dependencies, fast page loads
- **Maintainability**: Easy to understand and modify
- **Tailwind CSS**: Modern styling without custom CSS files

### Why LLM as Fallback (Not Primary)?

- **Most queries are simple**: "who won 2010" doesn't need AI
- **Speed matters**: Users expect instant responses
- **Reliability**: LLM might be unavailable or misconfigure
- **Privacy**: Keyword matching keeps data local
- **Cost**: Avoids unnecessary LLM API calls

### Why No Caching?

- **Simplicity**: Leverages existing API caching (drivers, constructors, LRU season cache)
- **Freshness**: Always returns current data
- **Memory**: Avoids duplicating data already cached by the API

## File Structure

```
f1-app/
├── config.json              # Configuration file
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies (updated)
├── static/                  # Frontend files (new)
│   ├── index.html          # Web interface
│   └── app.js              # Frontend JavaScript
├── app/
│   ├── api_server.py       # FastAPI app (extended)
│   ├── query_parser.py     # Keyword parser (new) ⚡ PRIMARY
│   ├── llm_service.py      # LLM integration (new) - fallback
│   ├── config.py           # Config loader (new)
│   └── ...                 # Existing files
└── _docs/
    └── web-interface.md    # This file
```

## Troubleshooting

### Common questions answered via keywords

Most queries work without any LLM setup:
- ✅ "who won 2010 championship"
- ✅ "hamilton wins"
- ✅ "2023 standings"
- ✅ "compare vettel verstappen"
- ✅ "about red bull"

### "LLM service unavailable" (Only for complex queries)

**Problem**: Neither Ollama nor Azure OpenAI is accessible.

**Solutions**:
- Verify Ollama is running: `ollama list`
- Check Ollama endpoint in [config.json](../config.json)
- If using Azure OpenAI, verify credentials in `.env`

### "Failed to parse LLM response as JSON"

**Problem**: LLM returned invalid JSON.

**Solutions**:
- Try a different model: `ollama pull mistral`
- Update model in [config.json](../config.json): `"model": "mistral"`
- Check Ollama logs for errors

### "Module 'openai' not found"

**Problem**: Azure OpenAI SDK not installed.

**Solution**:
```bash
pip install -r requirements.txt
```

### Web interface shows "API not found"

**Problem**: Static files not mounted correctly.

**Solutions**:
- Ensure `static/` directory exists
- Restart the server
- Check FastAPI logs for errors

## Performance Considerations

### LLM Response Time

- **Ollama (local)**: 1-5 seconds (depends on model size and hardware)
- **Azure OpenAI**: 2-10 seconds (depends on network latency and model)

### Optimization Tips

1. **Use smaller models**: `llama3.2:3b` is faster than `llama3.2:8b`
2. **Run Ollama on GPU**: Significantly faster inference
3. **Adjust timeout**: Increase `ollama.timeout` in config for slower systems

## Security Considerations

### API Keys

- **Never commit** `.env` or config files with real API keys
- Use environment variables for production deployments
- Add `.env` and `config.local.json` to `.gitignore`

### CORS

The API currently allows all origins (`allow_origins=["*"]`). For production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Input Validation

- All user input is sanitized before display (XSS prevention)
- LLM responses are parsed and validated before execution
- API endpoints have proper error handling

## Future Enhancements

### Potential Improvements

1. **Conversation History**: Store previous messages for context-aware follow-ups
2. **Multi-turn Reasoning**: "What about 2011?" after asking about 2010
3. **Advanced Visualizations**: Charts/graphs for trends over time
4. **Voice Input**: Speech-to-text for hands-free queries
5. **Export Results**: Download data as CSV/PDF
6. **User Preferences**: Save favorite drivers, teams, or time periods

### LLM Improvements

1. **Function Calling**: Use OpenAI-style function calling for more reliable API routing
2. **RAG Integration**: Embed F1 facts for richer context
3. **Fine-tuning**: Train a specialized F1 model
4. **Streaming Responses**: Show token-by-token generation

## Contributing

When adding new features:

1. Update this documentation
2. Add example queries to the frontend suggestions
3. Test with both Ollama and Azure OpenAI
4. Ensure proper error handling
5. Follow existing code style

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)
- [Tailwind CSS](https://tailwindcss.com)
