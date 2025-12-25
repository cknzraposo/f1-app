# F1 AI Assistant - Quick Start Guide

## 🏁 What's New?

A sleek web interface with **intelligent keyword matching** to retrieve F1 data via an API.

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

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
uvicorn app.api_server:app --reload --host 0.0.0.0 --port 8000
```

### 2. Open Your Browser

🌐 **Web Interface**: http://localhost:8000
📚 **API Docs**: http://localhost:8000/docs

**That's it!** The app works immediately with keyword matching.


## 🎯 Features

✅ **Fast Keyword Matching** - Instant responses for common queries (~1-5ms)  
✅ **Smart Pattern Recognition** - Extracts years, drivers, teams automatically  
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

**"Module not found"**
- Run: `pip install -r requirements.txt`

**Web interface not loading**
- Ensure `static/` directory exists
- Restart the server

## 📁 Key Files

- `.env.example` - Environment variable template
- `app/query_parser.py` - **Keyword parser (PRIMARY)**
- `app/config.py` - Configuration loader
- `static/index.html` - Web interface
- `static/app.js` - Frontend JavaScript
- `_docs/web-interface.md` - Comprehensive documentation