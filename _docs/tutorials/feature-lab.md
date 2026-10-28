# Shared lab 2: make local data limitations visible

Use this brief unchanged for [Path A](./copilot-native.md) and
[Path B](./copilot-spec-kit.md). Budget 75 minutes per path, excluding setup.
Start from the published tutorial baseline, not a repair solution.

## User story

As a learner browsing a season, I want to know what is present in the local
dataset, so that I do not mistake sample-derived statistics for verified
full-season results.

The presence of race records, consecutive rounds, an Ergast `total` field, or
a standings table does **not** establish completeness. Do not fetch a calendar,
invent expected race counts, or silently classify a sample as complete.

## API contract

Add `GET /api/seasons/{year}/coverage` without changing
`GET /api/seasons/{year}` or any stored JSON. For a local dataset with two race
records and no nonempty `StandingsLists`, return HTTP 200:

```json
{
  "season": 2023,
  "raceCount": 2,
  "hasStandings": false,
  "completeness": "unknown",
  "notice": "Local dataset; full-season completeness is not verified."
}
```

Requirements:

- `season` and `raceCount` are integers; count the actual `RaceTable.Races`
  records, not metadata or the highest round number. An empty list counts as 0.
- `hasStandings` is a boolean: true only when
  `MRData.StandingsTable.StandingsLists` is nonempty.
- `completeness` remains `"unknown"` even when standings are present. This
  exercise has no independent authority for a complete season.
- Keep the notice exactly as specified so both paths implement the same contract.
- Missing local season files, including gaps between available years, return
  HTTP 404. Out-of-range missing seasons return 404 too.
- A non-integer path year returns FastAPI's HTTP 422 validation response.
- Use existing loaders and error conventions. Do not mutate their cached
  dictionaries, add network calls, or change existing routes' response shapes.
- Do not hide malformed-data errors behind an empty success response; follow
  existing error handling. The supplied checks focus on valid Ergast fixtures
  and missing files; students should add malformed-data regression coverage.

## UI contract

On the existing [season browser](../../static/results.html) season detail view,
show a visible coverage notice beside the results/standings:

- State the local race count and whether a standings table is present.
- Display the API notice. Do not label calculated standings as verified official
  championship results or claim the dataset is complete.
- Fetch coverage for the selected year through the existing
  [API client](../../static/js/core/api-client.js) and render in the
  [season controller](../../static/js/pages/season-browser.js).
- Update it on year navigation; clear stale information while loading. Prevent
  an older response from overwriting the newly selected season's notice.
- On coverage failure, show an explicit "Coverage information unavailable"
  state; do not silently reuse the previous year's notice. Existing results
  should still be usable if only the coverage request fails.
- Use accessible text, not color alone. Keep the UI build-free.

Update the [API documentation](../readme.md) and add your own backend tests.
Natural-language coverage queries, new datasets, databases, frontend bundlers,
and runtime LLM configuration are out of scope.

## Establish red, then implement

```bash
python -m pytest -q _docs/tutorials/checks/coverage_checks.py
```

**Expected at the tutorial baseline: failures because the endpoint does not
exist.** This is an opt-in exercise contract, not a broken application test.
Do not weaken the checks or add the feature to the baseline before comparing
paths. Follow the selected workflow and obtain approval before implementation.

## API verification

```bash
python -m pytest -q _docs/tutorials/checks/coverage_checks.py
python -m pytest -q tests/contract/test_seasons.py tests/integration/test_season_flow.py
python -m pytest -q tests
git diff
```

The checks patch the season router's loader with empty, race-only, and
standings-containing fixtures; missing files are simulated without changing
the checked-in data. Keep API and UI verification distinct.

## Required browser verification

Use the real browser and local server, not just generated screenshots or
assumptions from the source. Save a short observation or screenshot per case:

| Action | Required observation |
|--------|----------------------|
| Open `/static/results.html?year=2023` | Notice matches `/api/seasons/2023/coverage`; no claim of completeness |
| Navigate to another year | Count and standings status correspond to the new year |
| Throttle the network and change years quickly | No previous-year notice overwrites the final year |
| Block only the coverage request in browser developer tools and reload | Explicit unavailable message; successful race/standings requests still render |
| Navigate using keyboard and inspect text | Notice is readable without relying on color |
| Open other existing pages and submit an existing query | No changed response contract or unrelated UI regression |

If browser automation is unavailable, perform these manually and record that
fact. Passing API checks alone does not complete this lab.

## Reflect

Which assumptions about the data did Copilot make? Did a written contract
prevent a false claim of completeness? How much planning or artifact upkeep
was useful compared with the repair lab? Use [the same rubric](./assessment.md)
for both paths.
