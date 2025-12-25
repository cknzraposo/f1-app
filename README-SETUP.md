# F1 AI Assistant - Quick Start Guide

## 🏁 What's New?

A sleek web interface with **intelligent keyword matching** and optional AI fallback for complex queries.

**Ask questions like:**
- "Who won the F1 championship in 2010?"
- "How many wins does Lewis Hamilton have?"
- "Tell me about Red Bull Racing"
- "Compare Verstappen and Hamilton"

## ⚡ Query Processing

1. **Primary: Keyword Matching** (instant, always works)
   - Pattern recognition for common queries
   - No LLM required for 90%+ of questions
   - Zero latency, works offline

2. **Fallback: LLM** (only for complex queries)
   - Handles unusual phrasing
   - Ollama (local) or Azure OpenAI (cloud)
   - Optional - app works fine without it

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
uvicorn app.api_server:app --reload --host 0.0.0.0 --port 8000
```

### 3. Open Your Browser

🌐 **Web Interface**: http://localhost:8000
📚 **API Docs**: http://localhost:8000/docs

**That's it!** The app works immediately with keyword matching.

## 🔧 Optional: Enable LLM Fallback

Only needed for complex/unusual queries:

### Install Ollama (Local)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.2

# Verify it's running
ollama list
```

### Or Configure Azure OpenAI

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials
3. Enable in `config.json`

## 🎯 Features

✅ **Fast Keyword Matching** - Instant responses for common queries (~1-5ms)  
✅ **Smart Pattern Recognition** - Extracts years, drivers, teams automatically  
✅ **Works Offline** - No LLM needed for 90%+ of queries  
✅ **LLM Fallback** - Handles complex questions when needed  
✅ **Rich Data Visualizations** - Championship tables, driver stats, race results  
✅ **Modern UI** - Sleek design with Tailwind CSS  
✅ **Zero Build Process** - Vanilla HTML/JS, no bundlers

## 🏎️ Query Examples

**Handled by Keywords (instant):**
- "who won 2010 championship" ⚡
- "hamilton stats" ⚡
- "2023 standings" ⚡
- "compare vettel verstappen" ⚡
- "about ferrari" ⚡

**Handled by LLM Fallback (if configured):**
- "tell me about the german driver who dominated in 2010s" 🤖
- "who was the best in the hybrid era" 🤖

## 📖 Full Documentation

See [_docs/web-interface.md](_docs/web-interface.md) for:
- Architecture overview
- API reference
- Configuration options
- Troubleshooting guide
- Security considerations
- Future enhancements

## 🔧 Troubleshooting

**Most queries work immediately!** No setup needed for:
- Championship winners by year
- Driver statistics and records
- Team/constructor information
- Season standings
- Driver comparisons

**"LLM service unavailable"** (only for complex queries)
- Most queries work via keywords anyway
- Optional: Install Ollama for LLM fallback

**"Module not found"**
- Run: `pip install -r requirements.txt`

**Web interface not loading**
- Ensure `static/` directory exists
- Restart the server

## 🎨 Architecture

```
User Question → Keyword Parser (Primary) → Internal API → Fast Response
                     ↓ (if no match)
                LLM Service (Fallback)
                     ↓
            Ollama (local) → Azure OpenAI (cloud)
```

**Speed Comparison:**
- Keyword Match: ~1-5ms ⚡
- LLM (Ollama): ~1-5 seconds 🤖
- LLM (Azure): ~2-10 seconds ☁️

## 📁 New Files

- `config.json` - LLM configuration (optional)
- `.env.example` - Environment variable template
- `app/query_parser.py` - **Keyword parser (PRIMARY)**
- `app/llm_service.py` - LLM integration (fallback)
- `app/config.py` - Configuration loader
- `static/index.html` - Web interface
- `static/app.js` - Frontend JavaScript
- `_docs/web-interface.md` - Comprehensive documentation

## 🤝 Contributing

Contributions welcome! See [_docs/web-interface.md](_docs/web-interface.md) for guidelines.

---

**Built with:** FastAPI • Pattern Matching • Ollama (optional) • Tailwind CSS • Vanilla JavaScript
