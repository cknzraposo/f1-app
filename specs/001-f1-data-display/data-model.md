# Data Model: F1 Data Display System

**Phase**: 1 - Design & Contracts  
**Date**: December 26, 2025  
**Plan**: [plan.md](plan.md) | **Research**: [research.md](research.md)

## Purpose

Define the entity relationships, attributes, and data structures for the F1 Data Display System. This model describes WHAT data exists and HOW entities relate, without specifying implementation details.

---

## Core Entities

### 1. Driver

**Description**: Represents a Formula 1 driver who has competed in at least one race from 1984-2024.

**Attributes**:
- `driverId` (string, unique): Canonical identifier (e.g., "hamilton", "verstappen")
- `givenName` (string): First name(s)
- `familyName` (string): Last name
- `dateOfBirth` (date): Birth date (ISO 8601 format)
- `nationality` (string): Country of citizenship
- `permanentNumber` (string, optional): Permanent racing number (introduced 2014)
- `code` (string, optional): Three-letter abbreviation (e.g., "HAM", "VER")
- `url` (string): Wikipedia reference URL

**Computed Statistics** (derived from race results):
- Total race starts
- Total race wins
- Total podiums (1st, 2nd, 3rd finishes)
- Total pole positions
- Total fastest laps
- World championships won
- Years active (first year - last year)
- Teams driven for

**Relationships**:
- Driver → Race Results (one-to-many): A driver has many race results
- Driver → Constructors (many-to-many): A driver has driven for multiple teams across their career
- Driver → Seasons (many-to-many): A driver has competed in multiple seasons

**Validation Rules**:
- `driverId` must be unique across all drivers
- `dateOfBirth` must be valid date
- `nationality` should match ISO 3166-1 country names
- Driver must have at least one race result to be included

**State Transitions**:
- Active: Currently competing in Formula 1
- Inactive: Previously competed but not in current season
- Retired: Formally announced retirement

---

### 2. Constructor

**Description**: Represents a Formula 1 constructor team (manufacturer) that has entered at least one race from 1984-2024.

**Attributes**:
- `constructorId` (string, unique): Canonical identifier (e.g., "mclaren", "ferrari")
- `name` (string): Official team name
- `nationality` (string): Country of origin
- `url` (string): Wikipedia reference URL

**Computed Statistics** (derived from race results):
- Total race entries
- Total race wins
- Total podiums
- Total pole positions
- Total fastest laps
- Constructors' championships won
- Years active (first year - last year)
- Drivers employed

**Relationships**:
- Constructor → Race Results (one-to-many): A constructor has many race results
- Constructor → Drivers (many-to-many): A constructor employs multiple drivers over time
- Constructor → Seasons (many-to-many): A constructor competes in multiple seasons

**Validation Rules**:
- `constructorId` must be unique across all constructors
- `nationality` should match ISO 3166-1 country names
- Constructor must have at least one race entry to be included

**Name Changes**:
- Constructors may change names over time (e.g., Toro Rosso → AlphaTauri → Racing Bulls)
- Each name change creates a new `constructorId`
- Historical continuity maintained via shared race results

---

### 3. Season

**Description**: Represents a complete Formula 1 championship season (year) containing all races held that year.

**Attributes**:
- `year` (integer, unique): Season year (1984-2024)
- `totalRaces` (integer): Number of races held in the season
- `championDriver` (Driver): Driver who won the championship
- `championConstructor` (Constructor): Constructor who won the championship
- `url` (string): Wikipedia reference URL for the season

**Computed Data**:
- Race schedule (list of races in chronological order)
- Driver championship standings (final)
- Constructor championship standings (final)
- Points system used that year

**Relationships**:
- Season → Races (one-to-many): A season contains multiple races
- Season → Driver Standings (one-to-many): A season has driver championship standings
- Season → Constructor Standings (one-to-many): A season has constructor championship standings

**Validation Rules**:
- `year` must be between 1984 and 2024 (inclusive)
- `totalRaces` must be > 0
- Must have exactly one driver champion
- Must have exactly one constructor champion

**Points System Evolution**:
- 1984-1990: Top 6 scored points (9-6-4-3-2-1)
- 1991-2002: Top 6 scored points (10-6-4-3-2-1)
- 2003-2009: Top 8 scored points (10-8-6-5-4-3-2-1)
- 2010-2018: Top 10 scored points (25-18-15-12-10-8-6-4-2-1)
- 2019-present: Top 10 + fastest lap bonus (25-18-15-12-10-8-6-4-2-1 + 1 for fastest lap if in top 10)

---

### 4. Race

**Description**: Represents a single Grand Prix race event within a season.

**Attributes**:
- `raceId` (string, unique): Canonical identifier (e.g., "2024_monaco")
- `season` (integer): Year the race was held
- `round` (integer): Race number within the season (1-based)
- `raceName` (string): Official name (e.g., "Monaco Grand Prix")
- `circuitId` (string): Identifier for the circuit
- `circuitName` (string): Official circuit name
- `circuitLocation` (string): City/region
- `circuitCountry` (string): Country
- `date` (date): Race date (ISO 8601 format)
- `time` (time, optional): Race start time (UTC)
- `url` (string): Wikipedia reference URL

**Relationships**:
- Race → Season (many-to-one): A race belongs to one season
- Race → Circuit (many-to-one): A race is held at one circuit
- Race → Race Results (one-to-many): A race has multiple results (one per driver)
- Race → Qualifying Results (one-to-many): A race has qualifying results
- Race → Sprint Results (one-to-many, optional): Some races have sprint race results

**Validation Rules**:
- `season` must match parent season year
- `round` must be unique within season
- `date` must be valid date
- Race must have at least one race result

**Race Types**:
- Standard Race: Qualifying + Race
- Sprint Weekend: Sprint Qualifying + Sprint Race + Qualifying + Race (introduced 2021)

---

### 5. Race Result

**Description**: Represents a single driver's result in a specific race.

**Attributes**:
- `driver` (Driver): Reference to driver
- `constructor` (Constructor): Reference to constructor/team
- `position` (integer): Final finishing position (1-based, null if DNF)
- `positionText` (string): Position display text (e.g., "1", "R" for retired, "D" for disqualified)
- `points` (float): Championship points earned
- `grid` (integer): Starting grid position
- `laps` (integer): Number of laps completed
- `status` (string): Finishing status (e.g., "Finished", "Collision", "Engine", "+1 Lap")
- `time` (duration, optional): Total race time (if finished)
- `fastestLapTime` (duration, optional): Driver's fastest lap time
- `fastestLapSpeed` (float, optional): Driver's fastest lap average speed (km/h)
- `fastestLapRank` (integer, optional): Rank of driver's fastest lap (1 = fastest overall)

**Relationships**:
- Race Result → Race (many-to-one): A result belongs to one race
- Race Result → Driver (many-to-one): A result is for one driver
- Race Result → Constructor (many-to-one): A result is for one constructor

**Validation Rules**:
- Each driver can have only one result per race
- `position` must be between 1 and number of starters (or null for DNF)
- `points` must match the points system for that season
- `grid` must be > 0
- `laps` must be ≤ total race laps

**Derived Data**:
- DNF (Did Not Finish): position is null or positionText contains "R", "D", etc.
- Points finish: position is within points-scoring range for that season
- Podium: position is 1, 2, or 3
- Win: position is 1

---

### 6. Championship Standing

**Description**: Represents a driver's or constructor's position in the championship at a specific point in the season.

**Driver Standing Attributes**:
- `driver` (Driver): Reference to driver
- `position` (integer): Championship position (1-based)
- `points` (float): Total championship points
- `wins` (integer): Number of race wins

**Constructor Standing Attributes**:
- `constructor` (Constructor): Reference to constructor
- `position` (integer): Championship position (1-based)
- `points` (float): Total championship points
- `wins` (integer): Number of race wins

**Relationships**:
- Standing → Season (many-to-one): Standings belong to one season
- Standing → Driver or Constructor (many-to-one): Each standing is for one entity

**Validation Rules**:
- `position` must be unique within season standings
- `points` must be non-negative
- `wins` must be ≤ total races in season
- Standings ordered by points (descending), then wins (descending)

**Standing Types**:
- Final Season Standing: Position at end of season
- After Round N Standing: Position after specific race

---

### 7. Circuit

**Description**: Represents a racing circuit that has hosted Formula 1 races.

**Attributes**:
- `circuitId` (string, unique): Canonical identifier (e.g., "monaco", "silverstone")
- `circuitName` (string): Official circuit name
- `location` (string): City or region
- `country` (string): Country
- `lat` (float): Latitude coordinate
- `long` (float): Longitude coordinate
- `url` (string): Wikipedia reference URL

**Relationships**:
- Circuit → Races (one-to-many): A circuit hosts multiple races over the years

**Validation Rules**:
- `circuitId` must be unique
- `lat` must be between -90 and 90
- `long` must be between -180 and 180

**Circuit Changes**:
- Circuits may be modified over time (layout changes)
- Major changes may result in new `circuitId` (e.g., Hockenheim modifications)

---

## Entity Relationships Diagram

```
┌──────────────┐
│   Season     │
│ (1984-2024)  │
└──────┬───────┘
       │ 1:N
       ↓
┌──────────────┐      1:N     ┌──────────────┐
│     Race     │─────────────→│ Race Result  │
│              │               │              │
└──────┬───────┘               └────┬─────┬───┘
       │                            │     │
       │ N:1                     N:1│     │N:1
       ↓                            ↓     ↓
┌──────────────┐               ┌─────┴────┴───┐      ┌──────────────┐
│   Circuit    │               │    Driver    │      │ Constructor  │
│              │               │              │←────→│              │
└──────────────┘               └──────┬───────┘ N:M  └──────┬───────┘
                                      │                      │
                                      │ 1:N                  │ 1:N
                                      ↓                      ↓
                              ┌───────────────┐      ┌──────────────┐
                              │Driver Standing│      │Constructor   │
                              │               │      │Standing      │
                              └───────────────┘      └──────────────┘
```

---

## Data Flow

### Query → Response Flow

```
1. User Query
   ↓
2. Query Parser extracts entities (driver, constructor, year)
   ↓
3. API Router routes to appropriate endpoint
   ↓
4. Service Layer retrieves data via JSON Loader
   ↓
5. JSON Loader checks LRU cache
   ↓ (cache miss)
6. JSON Loader reads file from disk
   ↓
7. JSON Loader caches data and returns
   ↓
8. Service Layer formats response (preserves Ergast format)
   ↓
9. API Layer returns JSON response
   ↓
10. Frontend JavaScript renders data
```

### Statistics Computation

Driver and Constructor statistics are **computed on-demand** from race results, not stored separately:

```python
# Example: Calculate driver total wins
def get_driver_wins(driver_id: str) -> int:
    wins = 0
    for year in available_seasons():
        season_data = load_season_results(year)
        for race in season_data['races']:
            for result in race['results']:
                if result['driver']['driverId'] == driver_id and result['position'] == 1:
                    wins += 1
    return wins
```

This approach:
- ✅ Eliminates data duplication
- ✅ Ensures statistics always match source data
- ✅ Leverages LRU cache for performance
- ✅ Simplifies data management (no update synchronization)

---

## Data Immutability

**Historical data is immutable** - race results never change after the fact:
- No UPDATE operations needed
- No data synchronization required
- No cache invalidation logic needed
- Cache entries valid indefinitely

**Exceptions** (rare):
- Post-race penalties or disqualifications may modify results
- These are reflected in official Ergast API data
- Manual data refresh via fetch scripts updates JSON files

---

## Data Validation

### Input Validation

```python
# Year range validation
if not (1984 <= year <= 2024):
    raise ValueError(f"Year {year} outside valid range")

# Driver ID format validation  
if not re.match(r'^[a-z_]+$', driver_id):
    raise ValueError(f"Invalid driver ID format: {driver_id}")

# Position validation
if position < 1:
    raise ValueError(f"Position must be positive: {position}")
```

### Data Integrity Checks

```python
# Ensure race has results
if not race.get('results'):
    logger.warning(f"Race {race_id} has no results")

# Verify points match position
expected_points = POINTS_SYSTEM[year][position]
if result['points'] != expected_points:
    logger.error(f"Points mismatch for {driver_id} in {race_id}")

# Check standings consistency
if sum(driver_points) != season_total_points:
    logger.error(f"Standings point total mismatch for {year}")
```

---

## Conclusion

This data model:
- ✅ Captures all entities from feature specification
- ✅ Defines clear relationships between entities
- ✅ Specifies validation rules and constraints
- ✅ Supports computed statistics without data duplication
- ✅ Leverages immutability for simplified data management
- ✅ Aligns with Ergast API format (Constitution Principle IV)

**Ready for contract generation** (OpenAPI specification).
