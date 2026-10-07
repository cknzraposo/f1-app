# Tutor Guide: Teaching Debugging and Testing with the F1 App

This guide supports the [Student Guide](./student-guide.md). Students follow the step-by-step instructions there. This guide covers what tutors need to run the sessions: timing, setup checks, answer notes, common misconceptions, and assessment ideas.

The five lessons come from real failures in this repository's test suite (30 failing tests in the original baseline). The background for each is in [Testing Lessons](./testing-lessons.md).

---

## Course at a glance

| Item | Detail |
|------|--------|
| Audience | Beginner–intermediate Python developers |
| Total time | About 2.5–3 hours, or two 90-minute sessions |
| Format | Live demo, then pairs work through break → investigate → fix → verify |
| Requirements | Python 3.12+, Git, terminal. **No LLM, API keys, or database.** |
| Core skill | Reading failures, finding the cause, and verifying fixes with tests |

### Learning outcomes

Students should be able to:

1. Set up a virtual environment and run a test suite.
2. Trace a request across the router, parser, service, and data layers.
3. Read a pytest traceback and find the line that caused the failure.
4. Explain and prevent five common bugs.
5. Write a regression test, and explain why it keeps the bug from returning.

### Suggested schedule

| Block | Minutes | Content |
|-------|---------|---------|
| Setup and baseline | 20 | Student Guide Part 0 |
| Architecture tour | 15 | Part 1 plus checkpoint questions |
| Lesson 1 – `lru_cache` | 20 | Caching, hashability, pure helpers |
| Lesson 2 – Pattern order | 25 | **Key lesson:** a 200 response with wrong data |
| *Break* | 10 | |
| Lesson 3 – Response contract | 15 | Inspect the response before asserting |
| Lesson 4 – Type comparisons | 10 | Short; works well as a warm-up |
| Lesson 5 – Test data | 20 | Fixtures compared with real data |
| Wrap-up and extensions | 15 | Final check, reflection, assign an extension |

For a **60-minute** session, run setup, the tour, and Lessons 2 and 5. These two have the most impact. Assign Lessons 1, 3, and 4 as homework.

---

## Before the session

Do this the day before on the same kind of machine the students will use:

```bash
git clone https://github.com/cknzraposo/f1-app.git && cd f1-app
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt httpx
python -m pytest -q tests                 # expect: 278 passed
uvicorn app.api_server:app --port 8000    # open /static/index.html, then Ctrl+C
```

Checklist:

- [ ] The test suite passes on a clean clone.
- [ ] `httpx` is installed. It is **not** in `requirements.txt`, and API tests fail to import without it. Either mention this up front or let students find it (see Extension 2).
- [ ] On Debian/Ubuntu/WSL, `python3 -m venv` may fail without the `python3.X-venv` package. Install it beforehand.
- [ ] On Python 3.14 you will see many `DeprecationWarning` lines from FastAPI/Starlette. Tell students in advance that these are warnings, not failures.
- [ ] Decide whether students fork the repository or work on a local branch. A branch makes it easy to `git restore` files.

---

## Teaching approach

Every lesson uses the same five steps: **🎯 Goal → 💥 Break → 🔍 Investigate → 🔧 Fix → ✅ Verify**.

- **Demo the first lesson live**, including any mistakes you make. Then let pairs drive the remaining lessons.
- **Ask students to predict** the error before they run the break step. A wrong prediction is useful because it shows what they misunderstood.
- **Insist on reading the full traceback.** Ask: “What is the last line that comes from *our* code?”
- **Verify with the narrowest test first**, then run the full suite. Explain why both steps matter.
- **Run `git status` at the end** of every lesson so no scratch files or unintended changes remain.

---

## Lesson notes and answer key

### Lesson 1 — Cached functions need hashable arguments

**Expected error:** `TypeError: unhashable type: 'list'`

**Key point:** The error is raised by `lru_cache` *before* the function body runs. It builds the cache key from all arguments together, and that key must be hashable.

**Common misconceptions**

| Student says | Clarify |
|--------------|---------|
| “Convert the list to a tuple.” | A tuple of **dicts** is still unhashable (`unhashable type: 'dict'`). Have them try it. |
| “Remove `@lru_cache`.” | That fixes the error but loses performance for every API call. Separating the work is the better design. |
| “The method body has a bug.” | Ask them to set a breakpoint inside the body. It is never reached. |

**Design takeaway:** Put caching around an **I/O boundary** that takes simple keys (an ID and years). Keep the calculation in a **pure function** that unit tests can call directly with fixtures.

**Checkpoint answers:** `lists`, `dicts`, and `sets` are unhashable. Caching file reads is risky if the files change while the server is running, because the cache returns stale data until the process restarts.

### Lesson 2 — Give overlapping patterns an explicit priority order ⭐

**Expected failure:** `AssertionError: assert 'championship_standings' == 'season_winners'`

**Key point:** The HTTP status is **200**. Nothing crashes, but the user gets standings instead of race winners. This kind of bug passes a quick manual check and is only caught by a test that checks the content of the response.

**Root cause:** `CHAMPIONSHIP_KEYWORDS` includes `"won the"` and `"winner"`, so `who won the most races in 2023` matches the championship parser. Whichever parser runs first decides the result.

**Fix:** Run the more specific rule first. Race winners require a year **and** `most`, `all`, or `winners`. The same ordering rule applies to the `dataType` checks in `app/routers/query.py`, where `/winners` is checked before `/standings`.

**Discussion prompt:** “Should we remove `won the` from the championship keywords?” Good answers note that this would break `who won the 2010 championship`. Ask students to show this with the parser one-liner. There is no single correct answer; what matters is the reasoning.

**Stretch:** Ask students to write a test that fails if anyone reorders `parse()` again. The existing integration test already does this. Show them that it does.

### Lesson 3 — Assert the real response contract

**Expected error:** `KeyError: 'totalWins'`

**Key point:** Inspect the actual response, using `print(list(resp))` or `/docs`, before writing assertions.

| Endpoint | Wins | Podiums | Poles |
|----------|------|---------|-------|
| Constructors | `statistics.totalWins` | `statistics.totalPodiums` | `statistics.totalPoles` |
| Drivers | `statistics.wins` | `statistics.podiums` | `statistics.polePositions` |

**Common misconception:** “Change the API to match the test.” The frontend (`static/js/pages/constructor-profile.js`) already reads `statistics.*`, so changing the API would break the UI. Use this to introduce **contract tests**: they protect every consumer of the API, not only the code under test.

### Lesson 4 — Compare values of the same type

**Expected error:** `TypeError: 'in <string>' requires string as left operand, not int`

**Key point:** `"2023" in str(data)` would run without error but is still fragile. It matches `20230`, race names, and dates. Assert on the specific field instead: `data["season"] == 2023`.

**Quick extension:** Ask how a type checker such as Pylance or mypy could flag this before the code runs.

### Lesson 5 — Make sure the test data supports the assertion

**Expected error:** `IndexError: list index out of range`

**Facts to have ready**

- The `sample_season_data_2023` fixture has 2 races. The second has only **one** result.
- The checked-in season files are **samples**: 5 races for 2020, 2022, and 2023; 6 for 2024; and **no `StandingsTable`** in any season file.
- So, through the API, every constructor has `totalChampionships == 0` and `bestSeasonPosition is None`. Championship calculations are covered by the unit fixtures, which do include standings.

**Key point:** Never make a test pass by inventing an expected number. Either compute the expected value from the data (for example, by counting races from `/api/seasons/{year}`) or add complete, documented data first.

**Common misconception:** “The data is wrong, so let's change the data to match the test.” Discuss who owns the data, how it is refreshed (`app/fetch_season.py`), and why test expectations should follow the data rather than drive it.

---

## Common pitfalls during the session

| Problem | Cause | Fix |
|---------|-------|-----|
| Tests still fail after `git restore` | Stale `.pyc` bytecode. Python checks modification time and file size, so a quick swap and restore within one second can go undetected. | `find . -name __pycache__ -prune -exec rm -rf {} +` |
| `No module named 'app'` | Running from the wrong directory | `cd` to the repository root |
| `No module named 'httpx'` | Not in `requirements.txt` | `python -m pip install httpx` |
| Many warnings hide the result | FastAPI/Starlette deprecations on Python 3.14 | Read the final summary line, or add `-p no:warnings` during demos |
| Scratch test files left in `tests/` | Student forgot to clean up | Run `git status` at the end of every lesson |

> The stale-bytecode issue happened while this guide was being written. It is worth demonstrating on purpose, because it shows students that the code Python runs can differ from the code they see in the editor.

---

## Assessment ideas

### Quick checks (formative)

1. *Why does `lru_cache` reject a list argument before the function body runs?*
2. *The API returned 200. Name two reasons that doesn't prove the feature works.*
3. *What would you check before asserting `totalWins >= 200`?*
4. *Rewrite `assert 2023 in str(resp)` correctly.*

### Practical task (summative)

Give students a deliberately broken branch, such as one with the parser blocks swapped and an assertion that indexes a missing result. Ask them to:

1. Run the suite and list the failures.
2. Classify each failure by lesson number.
3. Fix each one with a short explanation.
4. Show the full suite passing, and `git status` showing only intended changes.

### Rubric

| Criterion | Developing | Proficient | Advanced |
|-----------|-----------|------------|----------|
| Reading failures | Needs help finding the failing line | Finds the cause in the traceback independently | Predicts the error before running the code |
| Fix quality | Deletes or weakens the assertion | Fixes the cause | Fixes the cause and explains the design trade-off |
| Verification | Runs one test | Runs the focused test, then the full suite | Adds a regression test for a new case |
| Communication | Describes the symptom | Explains cause and fix | Writes it up as a new five-step lesson |

---

## Extension activities

These match the Student Guide's extension challenges:

1. **New keyword pattern.** Reinforces Lesson 2: students must choose where the new rule goes in `parse()`.
2. **Missing `httpx` dependency.** Leads to a discussion of runtime and development dependencies (`requirements-dev.txt`).
3. **Continuous integration.** A GitHub Actions workflow that runs the suite. Discuss why CI catches problems like Lesson 2 that manual testing misses.
4. **Dependency upgrade.** Record the warnings, upgrade FastAPI/Starlette on a branch, and compare against the baseline. This is good practice in making small, reviewable changes.
5. **Student-authored lesson.** The best evidence of mastery is writing a new break-it lesson for the next group.

---

## Keep the material accurate

When the codebase changes, re-run every “break it” step from the Student Guide and update the expected error text and test counts. If you add complete historical data, update Lesson 5 and the facts in this guide.
