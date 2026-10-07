# Student Guide: Learning Python Testing and Debugging with the F1 App

This guide uses this F1 app to teach debugging. In each lesson you **break the app on purpose**, read the error, find the cause, and then fix it. Each lesson is based on a real failure from this repository's test suite. The background for each failure is in [Testing Lessons](./testing-lessons.md).

Work through the lessons in order. Each one takes about 15–25 minutes.

---

## What you will learn

After these lessons, you should be able to:

1. Set up a Python project in a virtual environment and run its test suite.
2. Trace a request through the app: **web UI → router → query parser → service → JSON data**.
3. Read a pytest failure and find the line that caused it.
4. Explain five common bugs and how to prevent them:
   - Passing unhashable arguments to cached functions
   - Overlapping patterns that need a defined priority order
   - Asserting the wrong response shape
   - Comparing values of different types
   - Writing tests that depend on data the fixture does not contain
5. Write a regression test that keeps a fixed bug from returning.

## Prerequisites

- Basic Python: functions, dictionaries, lists, classes
- Comfort with a terminal (Linux, macOS, or WSL on Windows)
- Git installed
- Python 3.12 or newer

You do **not** need an LLM, API keys, or a database. The app works fully offline from JSON files.

---

## Part 0: Set up your environment

### Step 1 — Clone the repository and create a virtual environment

```bash
git clone https://github.com/cknzraposo/f1-app.git
cd f1-app
python3 -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
```

> **If `venv` fails with an `ensurepip` error** on Debian/Ubuntu/WSL, install the venv package for your Python version (for example, `sudo apt install python3.12-venv`), then try again.

### Step 2 — Install dependencies

```bash
python -m pip install -r requirements.txt httpx
```

`httpx` is required by FastAPI's `TestClient`, which the API tests use. It is not in `requirements.txt` yet. Spotting missing dependencies like this is part of the exercise.

### Step 3 — Run the tests and record the baseline

```bash
python -m pytest -q tests
```

✅ **Expected:** every test passes. The last line looks like `278 passed`. On newer Python versions you may also see `DeprecationWarning` messages from FastAPI/Starlette. These are dependency warnings, not test failures.

📝 **Record this result.** The baseline is how you'll know later whether a change fixed something or broke it.

### Step 4 — Run the app

```bash
uvicorn app.api_server:app --reload --port 8000
```

Open these pages:

| URL | What you'll see |
|-----|-----------------|
| http://localhost:8000/static/index.html | Web interface |
| http://localhost:8000/docs | Interactive API docs (Swagger UI) |
| http://localhost:8000/api/constructors/ferrari/stats | Raw JSON |

Try typing `who won the most races in 2023` in the web interface. Press `Ctrl+C` in the terminal to stop the server.

---

## Part 1: Tour the architecture

Before breaking anything, follow one question through the code. Open each file and find the named function.

```
"who won the most races in 2023"
        │
        ▼
static/js/…                      Browser sends POST /api/query
        │
        ▼
app/routers/query.py             Receives the query, asks the parser what it means
        │
        ▼
app/query_parser.py              QueryParser.parse() → "/api/seasons/2023/winners"
        │
        ▼
app/services/f1_service.py       Business logic: computes winners, stats, standings
        │
        ▼
app/json_loader.py               Loads f1data/2023_results.json (cached with lru_cache)
```

**Checkpoint questions**

1. Open [query_parser.py](../app/query_parser.py) and find `parse()`. In what order are the patterns tried?
2. Open [json_loader.py](../app/json_loader.py). Which functions use `@lru_cache`, and why might caching help here?
3. The app works without an LLM. Which file handles the fallback, and when is it called?

---

## How every lesson works

Each lesson follows the same five steps:

1. **🎯 Goal**: the concept you're learning.
2. **💥 Break it**: make a small change that reproduces the original bug.
3. **🔍 Investigate**: read the error and find the cause.
4. **🔧 Fix it**: restore or write the correct code.
5. **✅ Verify**: run the regression test and confirm the full suite passes.

> **Reset at any time:** `git restore <file>` undoes your changes to a tracked file. Delete any scratch files you create. If a test still shows the old behavior after you restore a file, see [Troubleshooting](#troubleshooting).

---

## Lesson 1: Cached functions need hashable arguments

### 🎯 Goal
Learn how `functools.lru_cache` builds its cache key, and why you can't pass a list or dictionary to a cached function.

### 💥 Break it
Create a scratch file named `tests/unit/test_scratch_lesson1.py`:

```python
from app.services import F1Service

def test_pass_list_to_cached_method(sample_season_data_2023):
    F1Service().get_constructor_statistics("ferrari", [sample_season_data_2023])
```

Run it:

```bash
python -m pytest -q tests/unit/test_scratch_lesson1.py
```

### 🔍 Investigate
You will see:

```
E       TypeError: unhashable type: 'list'
```

The error happens **before any line of the method body runs**. Why?

1. Open [f1_service.py](../app/services/f1_service.py) and find `get_constructor_statistics`. Look at the decorator above it.
2. Check its signature: `(constructor_id: str, start_year: int | None, end_year: int | None)`. The test passed a list where the method expects a year.
3. `lru_cache` uses all arguments together as a dictionary key. Dictionary keys must be hashable, and lists are not.

Try this in a Python shell:

```python
from functools import lru_cache

@lru_cache
def calculate(team_id, seasons):
    return len(seasons)

calculate("ferrari", [{"season": 2023}])    # TypeError: unhashable type: 'list'
calculate("ferrari", ({"season": 2023},))   # TypeError: unhashable type: 'dict'
```

The second call shows that converting the list to a tuple does not help, because each item inside the tuple must also be hashable.

### 🔧 Fix it
Split the work into two functions:

- **Cached method** (`get_constructor_statistics`): takes simple, hashable inputs (an ID and years), loads the data, and calls the helper.
- **Pure, uncached helper** (`_calculate_constructor_statistics`): takes the loaded season data and performs the calculation.

Unit tests should call the pure helper with fixture data:

```python
stats = F1Service()._calculate_constructor_statistics("ferrari", [sample_season_data_2023])
```

Delete your scratch file.

### ✅ Verify
```bash
rm tests/unit/test_scratch_lesson1.py
python -m pytest -q tests/unit/test_constructor_stats.py
```

### 💬 Reflect
- What else is unhashable? (dict, set, list)
- How would you test a function that is *only* reachable through a cached wrapper?
- What is the risk of caching a function that reads files that might change?

---

## Lesson 2: Give overlapping patterns an explicit priority order

### 🎯 Goal
When several rules can match the same input, the order you check them in decides the result. Learn to recognize this and test for it.

### 💥 Break it
Open [query_parser.py](../app/query_parser.py) and find `parse()`. Swap blocks **1** and **2**, so the championship check runs before the race-winners check:

```python
        # 2. Championship winner ...
        result = self._parse_championship_query(query_lower)
        if result:
            return result

        # 1. Race winners ...
        result = self._parse_race_winners_query(query_lower)
        if result:
            return result
```

Run the regression test:

```bash
python -m pytest -q tests/integration/test_query_parsing.py::TestQueryParsingWorkflow::test_winners_query_workflow
```

### 🔍 Investigate
You will see:

```
E       AssertionError: assert 'championship_standings' == 'season_winners'
```

Note that the HTTP request still **succeeded** with status 200. The app did not crash; it returned the wrong data. That makes this harder to spot than a crash.

Find out why by calling each parser method directly:

```bash
python -c "
from app.query_parser import QueryParser
p = QueryParser()
q = 'who won the most races in 2023'
print('championship:', p._parse_championship_query(q))
print('winners     :', p._parse_race_winners_query(q))
"
```

Both return a match. Look at `CHAMPIONSHIP_KEYWORDS` near the top of the class. Which keyword does `who won the most races` contain?

> Answer: `"won the"`. The championship parser matches too broadly, so whichever parser runs first decides the answer.

### 🔧 Fix it
Put the **more specific** rule first. The race-winners parser requires a year **and** `most`, `all`, or `winners`, so it should run before the broader championship rule:

```bash
git restore app/query_parser.py
```

The same rule applies to the `dataType` checks in [query.py](../app/routers/query.py): `/winners` is checked before `/standings`.

### ✅ Verify
```bash
python -m pytest -q tests/integration/test_query_parsing.py tests/contract/test_query.py
```

Also make sure the championship queries still work:

```bash
python -c "
from app.query_parser import QueryParser
print(QueryParser().parse('who won the 2010 championship'))
"
```

### 💬 Reflect
- Why doesn't status code 200 prove a feature works?
- Would removing `"won the"` from the keywords be a better fix? What might it break?
- Name another place where rule order matters (for example, URL routing, CSS, or `if/elif` chains).

---

## Lesson 3: Assert the real response contract

### 🎯 Goal
Before writing assertions, check the shape the API actually returns.

### 💥 Break it
Run this snippet. It assumes the stats are at the top level of the response:

```bash
python -c "
from fastapi.testclient import TestClient
from app.api_server import app
stats = TestClient(app).get('/api/constructors/ferrari/stats').json()
print(stats['totalWins'])
"
```

### 🔍 Investigate
```
KeyError: 'totalWins'
```

Print the response keys instead of guessing:

```bash
python -c "
from fastapi.testclient import TestClient
from app.api_server import app
c = TestClient(app)
s = c.get('/api/constructors/ferrari/stats').json()
d = c.get('/api/drivers/hamilton/stats').json()
print('constructor:', list(s), '->', list(s['statistics']))
print('driver     :', list(d), '->', list(d['statistics']))
"
```

You can also check the schema at http://localhost:8000/docs.

| Endpoint | Wins field | Podiums field | Poles field |
|----------|-----------|---------------|-------------|
| `/api/constructors/{id}/stats` | `statistics.totalWins` | `statistics.totalPodiums` | `statistics.totalPoles` |
| `/api/drivers/{id}/stats` | `statistics.wins` | `statistics.podiums` | `statistics.polePositions` |

Both endpoints put their metrics under `statistics`, but the field names differ.

### 🔧 Fix it
```python
total_wins = stats["statistics"]["totalWins"]
```

### ✅ Verify
```bash
python -m pytest -q tests/contract/test_constructors.py
```

### 💬 Reflect
- Who depends on this response shape? Open [constructor-profile.js](../static/js/pages/constructor-profile.js) and search for `statistics`.
- Should the API use the same field names for drivers and constructors? What would changing them break?

---

## Lesson 4: Compare values of the same type

### 🎯 Goal
Python does not convert types automatically in comparisons. Check structured fields directly instead of searching text.

### 💥 Break it
```bash
python -c "print(2023 in str({'season': 2023}))"
```

### 🔍 Investigate
```
TypeError: 'in <string>' requires string as left operand, not int
```

- `str(...)` turns the dictionary into a string.
- `2023` is an `int`. The `in` operator on a string requires a string on the left.
- Even `"2023" in str(...)` would be fragile. It would also match `"20230"` or a race named `"2023 Grand Prix"`.

### 🔧 Fix it
Compare the field directly:

```python
assert response_data["season"] == 2023
```

### ✅ Verify
```bash
python -m pytest -q tests/integration/test_query_parsing.py::TestYearExtraction
```

### 💬 Reflect
- When is checking a substring in text an acceptable test?
- How could type hints or a type checker (Pylance, mypy) catch this before you run the code?

---

## Lesson 5: Make sure the test data supports the assertion

### 🎯 Goal
A test can only check facts that exist in its data. Inspect fixtures and data files before writing expected values.

### 💥 Break it
Create `tests/unit/test_scratch_lesson5.py`:

```python
def test_every_race_has_a_second_place(sample_season_data_2023):
    for race in sample_season_data_2023["MRData"]["RaceTable"]["Races"]:
        assert race["Results"][1]["position"] == "2"
```

```bash
python -m pytest -q tests/unit/test_scratch_lesson5.py
```

### 🔍 Investigate
```
E       IndexError: list index out of range
```

Open [conftest.py](../tests/conftest.py) and find `sample_season_data_2023`. Count the races and the results in each race. The second race has only **one** result.

Next, check the real data files:

```bash
python -c "
from app.json_loader import load_season_results
for y in (2020, 2022, 2023, 2024):
    d = load_season_results(y)['MRData']
    print(y, 'races:', len(d['RaceTable']['Races']), '| has standings:', 'StandingsTable' in d)
"
```

The checked-in data is a **sample**: 5–6 races per season and no standings table. A test expecting “Ferrari has 200+ wins” or “Red Bull was champion” cannot pass against this data.

### 🔧 Fix it
Base expected values on the data you have:

```python
races = sample_season_data_2023["MRData"]["RaceTable"]["Races"]
for race in races:
    if len(race["Results"]) > 1:
        assert race["Results"][1]["position"] == "2"
```

Or compare one endpoint against another instead of hard-coding a number:

```python
season = client.get("/api/seasons/2023").json()
expected_races = len(season["MRData"]["RaceTable"]["Races"])
```

Delete your scratch file.

### ✅ Verify
```bash
rm tests/unit/test_scratch_lesson5.py
python -m pytest -q tests/integration/test_constructor_flow.py tests/unit/test_constructor_stats.py
```

### 💬 Reflect
- What's the difference between a **unit fixture** and the **real data files**? When should a test use each?
- If you wanted to test real historical totals, what would you need to add first?

---

## Final check

Run the whole suite. It should match your Part 0 baseline:

```bash
python -m pytest -q tests
git status          # confirm you left no scratch files or unintended changes
```

## Extension challenges

Pick one or more:

1. **Add a keyword pattern.** Support `"fastest laps 2023"` in [query_parser.py](../app/query_parser.py). Add a parser method, place it in the correct position in `parse()`, and write a test. See [Keyword-First Architecture](./keyword-first-architecture.md).
2. **Fix the missing dependency.** Add `httpx` to `requirements.txt`. Should it go in a separate `requirements-dev.txt`? Explain your choice.
3. **Add CI.** Create a GitHub Actions workflow that installs dependencies and runs `python -m pytest -q tests` on every push.
4. **Investigate the warnings.** Run the tests and read the `DeprecationWarning` messages. Which package produces them? Would upgrading FastAPI remove them? Record a new baseline before and after any change.
5. **Write your own break-it lesson.** Find another fragile assumption in the tests, reproduce it, and write it up in the same five-step format.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'app'` | Run commands from the repository root. |
| `ModuleNotFoundError: No module named 'httpx'` | `python -m pip install httpx` |
| `pytest: command not found` | Activate the venv, or use `python -m pytest`. |
| A test still fails after you restored a file | Python may be using stale bytecode. Run `find . -name __pycache__ -prune -exec rm -rf {} +` and test again. |
| Port 8000 already in use | Use `--port 8001`. |

## Related reading

- [Testing Lessons](./testing-lessons.md): a short reference for the five failures
- [Tutor Guide](./tutor-guide.md): session plans and answer notes for instructors
- [Keyword-First Architecture](./keyword-first-architecture.md)
- [API Documentation](./readme.md)
