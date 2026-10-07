# Testing Lessons: Turning Failures into Reproducible Examples

This project is a teaching demo, so test failures should explain the problem as well as signal it. The examples below describe the issues found in the baseline test run, how to trigger the relevant checks, and what each failure teaches.

For step-by-step classroom versions of these lessons, see the [Student Guide](./student-guide.md) and the [Tutor Guide](./tutor-guide.md).

## Run the checks

From the repository root, with the project environment activated:

```bash
python -m pytest -q tests
```

Run one lesson's regression test while investigating:

```bash
python -m pytest -q tests/unit/test_constructor_stats.py
python -m pytest -q tests/integration/test_query_parsing.py::TestQueryParsingWorkflow::test_winners_query_workflow
python -m pytest -q tests/contract/test_constructors.py::TestConstructorEndpointsContract::test_get_constructor_stats_includes_key_metrics
```

The complete suite is expected to pass. On Python 3.14, the current FastAPI/Starlette test stack also emits deprecation warnings about `asyncio.iscoroutinefunction`; these are dependency warnings, not test failures.

## Lesson 1: Cached functions need hashable arguments

`functools.lru_cache` hashes every argument to build its cache key. Passing a list to a cached function raises `TypeError: unhashable type: 'list'` before the function body runs:

```python
from functools import lru_cache

@lru_cache
def calculate(team_id, seasons):
    return len(seasons)

calculate("ferrari", [{"season": 2023}])
```

The constructor endpoint method is cached because it accepts a constructor ID and optional year bounds. Unit tests now exercise `_calculate_constructor_statistics`, the uncached calculation over supplied fixture data; the endpoint method remains responsible for loading and caching data.

## Lesson 2: Give overlapping query patterns explicit precedence

The phrase `who won the most races in 2023` contains `won the`, which also matched the championship parser. With championship parsing first, that race-winner question was routed to season standings. Race-winner recognition now runs first, while championship queries still fall through when they do not ask for race winners.

The integration test reproduces the user-visible path through `POST /api/query`:

```bash
python -m pytest -q tests/integration/test_query_parsing.py::TestQueryParsingWorkflow::test_winners_query_workflow
```

The response should have `dataType == "season_winners"` and a `data.winners` list.

## Lesson 3: Assert the response contract, not an imagined shape

Constructor and driver statistic endpoints return metadata plus a nested `statistics` object. Read a metric at the documented shape:

```python
stats_response = client.get("/api/constructors/ferrari/stats").json()
total_wins = stats_response["statistics"]["totalWins"]
```

Likewise, driver statistics use `wins` and `podiums`, while constructor statistics use `totalWins` and `totalPodiums`. Contract tests now check the response each endpoint actually provides instead of assuming both services use identical metric names or flattening.

## Lesson 4: Compare values using their real types

This assertion raises a `TypeError` because Python does not allow an integer membership check against a string:

```python
2023 in str({"season": 2023})
```

Check the relevant field directly instead:

```python
response_data["season"] == 2023
```

The query integration tests now verify extracted years by checking the returned `season` value.

## Lesson 5: Make test data support the assertion

The fixture seasons contain two races in 2022 and 2023, and one race has only one result. Tests that indexed a second result in every race, expected four podiums, or indexed a fourth constructor in a three-row standings table were asserting facts absent from their fixtures. Tests now derive expectations from the supplied race and standings rows.

The checked-in season files are also samples, not complete historical seasons: they contain five races for 2020, 2022, and 2023, six for 2024, and no `StandingsTable` in those files. Consequently, their constructor career totals cannot support assertions such as “Ferrari has 200+ wins” or “Red Bull was champion.” Integration tests check behavior against available data; unit fixtures separately cover standings and championship calculations.

Inspect the source-data size before adding historical-total assertions:

```bash
python -c "from app.json_loader import load_season_results; print(len(load_season_results(2023)['MRData']['RaceTable']['Races']))"
```

If full historical totals become a learning objective, first add complete, documented data; do not make tests pass by inventing expected totals.

## What changed

- Constructor calculations now have a pure helper that can be tested with supplied season fixtures, and qualifying results are used to count poles when present.
- Race-winner queries no longer get captured by the earlier championship pattern.
- Tests now assert real API shapes, field types, and the data actually available in fixtures.

These examples are intended as regression lessons: the focused commands above should continue passing after future refactors.
