"""
Simple keyword-based query parser for F1 questions.
Attempts to match patterns and extract entities before falling back to LLM.
"""
import re
import json
from pathlib import Path
from difflib import get_close_matches
from typing import Dict, Any, Optional, List


class QueryParser:
    """Parse natural language F1 queries using keyword matching and patterns."""
    
    # Year patterns
    YEAR_PATTERN = r'\b(19\d{2}|20\d{2})\b'
    
    # Common keywords
    CHAMPIONSHIP_KEYWORDS = ['championship', 'champion', 'title', 'won the', 'winner']
    WINS_KEYWORDS = ['wins', 'victories', 'won', 'win count']
    STATS_KEYWORDS = ['stats', 'statistics', 'career', 'record', 'about']
    RACE_KEYWORDS = ['race', 'grand prix', 'gp']
    STANDINGS_KEYWORDS = ['standings', 'points', 'table', 'leaderboard']
    FASTEST_KEYWORDS = ['fastest lap', 'fastest laps', 'speed']
    COMPARE_KEYWORDS = ['compare', 'vs', 'versus', 'against']
    
    def __init__(self):
        """Initialize parser and load driver database."""
        self.known_drivers = self._load_driver_database()
        self.driver_fullnames = self._load_driver_fullnames()
    
    def _load_driver_database(self) -> Dict[str, str]:
        """Load all drivers from f1drivers/drivers.json."""
        try:
            drivers_file = Path(__file__).parent.parent / "f1drivers" / "drivers.json"
            with open(drivers_file, 'r') as f:
                data = json.load(f)
                drivers = data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])
                
                # Create mapping of surname (lowercase) -> driverId
                # Priority: surname mapping only, given names excluded to avoid conflicts
                driver_map = {}
                for driver in drivers:
                    surname = driver.get("familyName", "").lower()
                    driver_id = driver.get("driverId", "")
                    
                    # Map surname to driver ID (prefer existing to avoid overwriting)
                    if surname and driver_id:
                        if surname not in driver_map:
                            driver_map[surname] = driver_id
                
                print(f"Loaded {len(driver_map)} driver surnames")
                return driver_map
        except Exception as e:
            print(f"Warning: Could not load driver database: {e}")
            return {}
    
    def _load_driver_fullnames(self) -> Dict[str, str]:
        """Load full names for multi-word matching."""
        try:
            drivers_file = Path(__file__).parent.parent / "f1drivers" / "drivers.json"
            with open(drivers_file, 'r') as f:
                data = json.load(f)
                drivers = data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])
                
                # Create mapping of full name (lowercase) -> driverId
                fullname_map = {}
                for driver in drivers:
                    given = driver.get("givenName", "")
                    family = driver.get("familyName", "")
                    driver_id = driver.get("driverId", "")
                    
                    if given and family and driver_id:
                        fullname = f"{given} {family}".lower()
                        fullname_map[fullname] = driver_id
                
                return fullname_map
        except Exception as e:
            return {}
    
    def parse(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Parse a user query and return API call information.
        
        Args:
            query: User's natural language question
            
        Returns:
            Dict with endpoint, params, and context, or None if no match
        """
        query_lower = query.lower().strip()
        
        # Try different patterns in order of specificity
        
        # 1. Championship winner (e.g., "who won the 2010 championship")
        result = self._parse_championship_query(query_lower)
        if result:
            return result
        
        # 2. Driver statistics (e.g., "how many wins does hamilton have")
        result = self._parse_driver_stats_query(query_lower)
        if result:
            return result
        
        # 3. Team/Constructor info (e.g., "tell me about red bull")
        result = self._parse_constructor_query(query_lower)
        if result:
            return result
        
        # 4. Season standings (e.g., "2023 standings")
        result = self._parse_standings_query(query_lower)
        if result:
            return result
        
        # 5. Driver comparison (e.g., "compare hamilton and verstappen")
        result = self._parse_comparison_query(query_lower)
        if result:
            return result
        
        # 6. Race winners in a season (e.g., "who won the most races in 2023")
        result = self._parse_race_winners_query(query_lower)
        if result:
            return result
        
        # 7. General driver search (e.g., "find hamilton")
        result = self._parse_driver_search_query(query_lower)
        if result:
            return result
        
        # No pattern matched
        return None
    
    def _extract_year(self, text: str) -> Optional[int]:
        """Extract a year from text (1984-2024)."""
        match = re.search(self.YEAR_PATTERN, text)
        if match:
            year = int(match.group(1))
            if 1984 <= year <= 2024:
                return year
        return None
    
    def _extract_driver_name(self, text: str, exclude_words: List[str] = None) -> Optional[str]:
        """
        Extract potential driver name from text with fuzzy matching.
        Searches against full driver database loaded from JSON.
        Returns driverId if found.
        """
        exclude_words = exclude_words or []
        exclude_lower = [w.lower() for w in exclude_words]
        
        # Remove common question words
        text_lower = text.lower()
        for word in exclude_lower:
            text_lower = text_lower.replace(word, ' ')
        
        # Strategy 1: Check for full name match (e.g., "lewis hamilton")
        # This has highest priority to disambiguate common surnames
        for fullname, driver_id in self.driver_fullnames.items():
            if fullname in text_lower:
                return driver_id
        
        # Strategy 2: Exact match against known driver surnames
        # Now we prioritize modern drivers by checking driverId format
        words = text_lower.split()
        for word in words:
            cleaned = re.sub(r'[^\w]', '', word)
            if cleaned in self.known_drivers and len(cleaned) > 2:
                driver_id = self.known_drivers[cleaned]
                # Prefer drivers with underscores (modern format: "lewis_hamilton")
                # over old format (single names like "abate")
                if '_' in driver_id:
                    return driver_id
                # Store as fallback but keep looking
                fallback_driver = driver_id
        
        # Return fallback driver if we found one
        if 'fallback_driver' in locals():
            return fallback_driver
        
        # Strategy 3: Fuzzy match against all known driver surnames
        for word in words:
            cleaned = re.sub(r'[^\w]', '', word)
            if len(cleaned) > 3:  # Only fuzzy match words with 4+ chars
                matches = get_close_matches(
                    cleaned, 
                    self.known_drivers.keys(), 
                    n=1, 
                    cutoff=0.85  # 85% similarity threshold
                )
                if matches and matches[0] not in exclude_lower:
                    return self.known_drivers[matches[0]]
        
        # Strategy 4: Extract capitalized words as fallback
        original_words = text.split()
        for word in original_words:
            cleaned = re.sub(r'[^\w]', '', word)
            if (len(cleaned) > 2 and 
                cleaned[0].isupper() and 
                cleaned.lower() not in exclude_lower and
                not cleaned.isdigit()):
                # Try fuzzy match on this capitalized word
                matches = get_close_matches(
                    cleaned.lower(), 
                    self.known_drivers.keys(), 
                    n=1, 
                    cutoff=0.80
                )
                if matches:
                    return self.known_drivers[matches[0]]
        
        return None
    
    def _extract_constructor_name(self, text: str) -> Optional[str]:
        """Extract potential constructor/team name from text."""
        # Known team names/keywords
        teams = {
            'red bull': 'red_bull',
            'redbull': 'red_bull',
            'ferrari': 'ferrari',
            'mercedes': 'mercedes',
            'mclaren': 'mclaren',
            'alpine': 'alpine',
            'aston martin': 'aston_martin',
            'williams': 'williams',
            'alfa romeo': 'alfa',
            'alphatauri': 'alphatauri',
            'haas': 'haas',
            'racing point': 'racing_point',
            'force india': 'force_india',
            'renault': 'renault',
            'lotus': 'lotus',
            'brawn': 'brawn',
            'toyota': 'toyota',
            'bmw': 'bmw',
            'honda': 'honda',
            'sauber': 'sauber'
        }
        
        for team_name, team_id in teams.items():
            if team_name in text:
                return team_id
        
        return None
    
    def _parse_championship_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Parse championship winner queries."""
        if not any(kw in query for kw in self.CHAMPIONSHIP_KEYWORDS):
            return None
        
        year = self._extract_year(query)
        if year:
            return {
                "action": "api_call",
                "endpoint": f"/api/seasons/{year}/standings",
                "params": {},
                "context": f"Championship standings for {year}",
                "source": "keyword_parser"
            }
        
        return None
    
    def _parse_driver_stats_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Parse driver statistics queries."""
        # Check for stats keywords
        has_stats_keyword = (
            any(kw in query for kw in self.STATS_KEYWORDS) or
            any(kw in query for kw in self.WINS_KEYWORDS)
        )
        
        if not has_stats_keyword:
            return None
        
        # Extract driver name (returns driverId if found)
        exclude = ['who', 'does', 'have', 'many', 'wins', 'stats', 'about', 'tell', 'me']
        driver_id = self._extract_driver_name(query, exclude)
        
        if driver_id:
            # Directly get stats using the driver ID
            return {
                "action": "api_call",
                "endpoint": f"/api/drivers/{driver_id}/stats",
                "params": {},
                "context": f"Get statistics for driver '{driver_id}'",
                "source": "keyword_parser"
            }
        
        return None
    
    def _parse_constructor_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Parse constructor/team queries."""
        if not any(kw in query for kw in self.STATS_KEYWORDS):
            return None
        
        team_id = self._extract_constructor_name(query)
        if team_id:
            return {
                "action": "api_call",
                "endpoint": f"/api/constructors/{team_id}/stats",
                "params": {},
                "context": f"Statistics for constructor '{team_id}'",
                "source": "keyword_parser"
            }
        
        return None
    
    def _parse_standings_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Parse standings queries."""
        if not any(kw in query for kw in self.STANDINGS_KEYWORDS):
            return None
        
        year = self._extract_year(query)
        if year:
            return {
                "action": "api_call",
                "endpoint": f"/api/seasons/{year}/standings",
                "params": {},
                "context": f"Standings for {year}",
                "source": "keyword_parser"
            }
        
        return None
    
    def _parse_comparison_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Parse driver comparison queries."""
        if not any(kw in query for kw in self.COMPARE_KEYWORDS):
            return None
        
        # Extract two driver IDs
        # Split on comparison keywords
        parts = re.split(r'\b(vs|versus|and|against)\b', query)
        
        driver_ids = []
        for part in parts:
            driver_id = self._extract_driver_name(part, ['compare', 'who', 'better'])
            if driver_id and driver_id not in driver_ids:
                driver_ids.append(driver_id)
        
        if len(driver_ids) >= 2:
            return {
                "action": "api_call",
                "endpoint": "/api/stats/head-to-head",
                "params": {"driver1": driver_ids[0], "driver2": driver_ids[1]},
                "context": f"Compare {driver_ids[0]} vs {driver_ids[1]}",
                "source": "keyword_parser"
            }
        
        return None
    
    def _parse_race_winners_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Parse race winners queries."""
        has_race_keyword = any(kw in query for kw in self.RACE_KEYWORDS + ['won', 'winner'])
        
        if not has_race_keyword:
            return None
        
        year = self._extract_year(query)
        if year and ('most' in query or 'all' in query or 'winners' in query):
            return {
                "action": "api_call",
                "endpoint": f"/api/seasons/{year}/winners",
                "params": {},
                "context": f"Race winners for {year}",
                "source": "keyword_parser"
            }
        
        return None
    
    def _parse_driver_search_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Parse general driver search queries."""
        if 'driver' not in query and 'find' not in query:
            return None
        
        driver_id = self._extract_driver_name(query, ['driver', 'find', 'search', 'who', 'is'])
        if driver_id:
            return {
                "action": "api_call",
                "endpoint": f"/api/drivers/{driver_id}",
                "params": {},
                "context": f"Get information for driver '{driver_id}'",
                "source": "keyword_parser"
            }
        
        return None
