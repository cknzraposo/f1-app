# Data Provider Fallback Note

_Last updated: 2026-03-02_

## Why this note exists
Jolpi/Ergast-compatible endpoint may lag for some seasons (observed with 2025 showing only rounds 1-5), so we need a documented fallback path.

## Verified findings
- **Primary source (current app):** `https://api.jolpi.ca/ergast/f1/{year}/results.json`
  - On check date, 2025 returned rounds **1-5** only.
- **OpenF1:** `https://api.openf1.org/v1`
  - Useful for meetings/sessions (calendar-level coverage), including full 2025 schedule.
  - Direct race classification endpoints were not available (`/results` and `/classification` returned `404` in tests).
- **FIA official documents:** `https://www.fia.com/system/files/decision-document/...`
  - Final race classification PDFs are reachable and suitable as authoritative fallback for missing rounds.

## Recommended fallback order
1. Jolpi (fast, Ergast-compatible JSON)
2. FIA final race classification PDFs (authoritative fallback when Jolpi is incomplete)

## Implementation note for future work
If/when needed, add an importer that:
- Detects missing rounds for a season.
- Fetches corresponding FIA final classification PDFs.
- Parses/normalizes results into existing Ergast-style JSON structure used by this project.
- Merges data incrementally without changing existing API response format.
