# Driver Profile Pages

## Overview
Driver names in search result tables are now clickable links that open dedicated driver profile pages with comprehensive career statistics and season-by-season history.

## Features

### 1. **Clickable Driver Names**
- All driver names in search result tables are automatically converted to clickable links
- Links styled in blue (#60a5fa) with hover effects
- Detected columns: `name`, `fullName`, `driver`, `driver.name`, `Driver.givenName`, `Driver.familyName`

### 2. **Driver Profile Page** (`/static/drivers.html`)
The profile page displays three main sections:

#### Driver Information Card
- Full name with large prominent display
- Nationality with flag icon
- Date of birth
- Permanent race number
- Driver code (e.g., ALO, HAM, VER)

#### Career Statistics
Grid of 7 key metrics displayed as cards:
- **Total Races**: Number of race entries
- **Wins**: Number of victories
- **Podiums**: Number of top-3 finishes
- **Pole Positions**: Number of qualifying P1s
- **Fastest Laps**: Number of fastest race laps
- **Total Points**: Career points accumulated
- **DNFs**: Did Not Finish count

#### Season-by-Season History
Table showing year-by-year performance:
- **Season**: Year
- **Team**: Primary constructor (most races)
- **Races**: Number of races entered
- **Wins**: Wins in that season
- **Podiums**: Podium finishes
- **Points**: Total points scored

### 3. **Data Sources**
The driver profile page fetches data from three API endpoints:
- `/api/drivers/{driver_id}` - Basic driver information
- `/api/drivers/{driver_id}/stats` - Career statistics
- `/api/drivers/{driver_id}/seasons/{year}` - Season results (checked for 1984-2024)

## Technical Implementation

### Frontend Changes (`static/app.js`)

#### Helper Functions Added:

```javascript
// Create clickable driver link
function createDriverLink(driverName, driverId)
```
Generates HTML anchor tag with styling for driver names.

```javascript
// Check if column contains driver data
function isDriverColumn(columnKey)
```
Detects if a table column should have clickable driver links.

```javascript
// Extract driver ID from row data
function getDriverId(row, columnKey)
```
Extracts driver ID from various possible data structures, with fallback to matching against global drivers list.

#### Table Rendering Enhancement
Modified the table cell rendering in `renderDataTable()` to:
1. Check if column contains driver information
2. Extract driver ID from the row data
3. Convert plain text driver name to clickable link

### New Page (`static/drivers.html`)

**Features:**
- Glass-morphism design matching main app aesthetic
- Responsive grid layout for statistics cards
- Async data loading with loading spinners
- Error handling for missing data
- Back button to return to search results
- Season history aggregation logic

**Styling:**
- Purple gradient background
- Glass-card effects with backdrop blur
- Hover animations on stat cards
- Responsive design (mobile-friendly)
- Tailwind CSS via CDN

## Usage Examples

### Example 1: Championship Standings
```
Query: "2023 championship"
Result: Table with driver names
Action: Click "Max Verstappen"
Opens: drivers.html?id=max_verstappen
```

### Example 2: Driver Search
```
Query: "tell me about alonso"
Result: Driver information card
Action: Click "Fernando Alonso"
Opens: drivers.html?id=alonso
```

### Example 3: Season Winners
```
Query: "who won most races 2022"
Result: Table of race winners
Action: Click any driver name
Opens: Corresponding driver profile page
```

## URL Structure

Driver profile pages use query parameter format:
```
/static/drivers.html?id={driverId}
```

Examples:
- `/static/drivers.html?id=alonso`
- `/static/drivers.html?id=hamilton`
- `/static/drivers.html?id=max_verstappen`
- `/static/drivers.html?id=leclerc`

## Edge Cases Handled

1. **Driver in standings but not in drivers.json**
   - Uses driverId from standings data directly
   - Falls back to global drivers list matching

2. **Driver with no race data (1984-2024)**
   - Career stats show note: "No race data available..."
   - Season history shows: "No season history available..."

3. **Driver not found**
   - Shows error message: "Driver not found"
   - Back button still functional

4. **Missing driver ID in data**
   - Attempts fuzzy matching against loaded drivers list
   - Falls back to non-linked plain text if no match

## Performance Considerations

1. **Driver List Pre-loading**
   - `allDrivers` array loaded on page initialization
   - Used for driver ID lookup and fuzzy matching

2. **Season History Loading**
   - Parallel API calls for all years (1984-2024)
   - Failed requests silently ignored
   - Only successful seasons displayed

3. **Link Generation**
   - Links generated during table render
   - No additional API calls needed for linking
   - Minimal performance impact

## Future Enhancements

Potential improvements:
1. Add constructor/team links similar to driver links
2. Include race-by-race results with expandable accordion
3. Add career timeline visualization
4. Display career win/podium charts
5. Compare drivers side-by-side from profile page
6. Add photo/avatar support if image data available
7. Show career highlights and achievements
8. Add social media links if available in data

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- JavaScript ES6+ features used
- Tailwind CSS v3 via CDN
- No build process required
- Works offline after initial page load (except API calls)
