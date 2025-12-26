/**
 * F1 API Client Module
 * Centralized API calls with error handling and caching
 */

// Cache for frequently accessed data
const cache = {
    drivers: null,
    constructors: null,
    seasons: new Map() // LRU-style cache for season data
};

const MAX_SEASON_CACHE_SIZE = 5;

/**
 * Base fetch wrapper with error handling
 */
async function fetchAPI(url, options = {}) {
    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || errorData.error || `HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API Error [${url}]:`, error);
        throw error;
    }
}

/**
 * Get all drivers (cached)
 */
export async function getDrivers() {
    if (cache.drivers) {
        return cache.drivers;
    }
    
    const data = await fetchAPI('/api/drivers');
    cache.drivers = data;
    return data;
}

/**
 * Get specific driver by ID
 */
export async function getDriver(driverId) {
    return await fetchAPI(`/api/drivers/${driverId}`);
}

/**
 * Get driver statistics
 */
export async function getDriverStats(driverId) {
    return await fetchAPI(`/api/drivers/${driverId}/stats`);
}

/**
 * Get all constructors (cached)
 */
export async function getConstructors() {
    if (cache.constructors) {
        return cache.constructors;
    }
    
    const data = await fetchAPI('/api/constructors');
    cache.constructors = data;
    return data;
}

/**
 * Get specific constructor by ID
 */
export async function getConstructor(constructorId) {
    return await fetchAPI(`/api/constructors/${constructorId}`);
}

/**
 * Get constructor statistics
 */
export async function getConstructorStats(constructorId) {
    return await fetchAPI(`/api/constructors/${constructorId}/stats`);
}

/**
 * Get season results (with LRU cache)
 */
export async function getSeasonResults(year) {
    const cacheKey = `season_${year}`;
    
    if (cache.seasons.has(cacheKey)) {
        // Move to end (most recently used)
        const data = cache.seasons.get(cacheKey);
        cache.seasons.delete(cacheKey);
        cache.seasons.set(cacheKey, data);
        return data;
    }
    
    const data = await fetchAPI(`/api/seasons/${year}`);
    
    // Add to cache
    cache.seasons.set(cacheKey, data);
    
    // Enforce cache size limit (remove oldest)
    if (cache.seasons.size > MAX_SEASON_CACHE_SIZE) {
        const firstKey = cache.seasons.keys().next().value;
        cache.seasons.delete(firstKey);
    }
    
    return data;
}

/**
 * Get season standings (drivers and constructors)
 */
export async function getSeasonStandings(year) {
    return await fetchAPI(`/api/seasons/${year}/standings`);
}

/**
 * Get season race winners
 */
export async function getSeasonWinners(year) {
    return await fetchAPI(`/api/seasons/${year}/winners`);
}

/**
 * Execute natural language query
 */
export async function executeQuery(query) {
    return await fetchAPI('/api/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query })
    });
}

/**
 * Get head-to-head comparison statistics
 */
export async function getHeadToHead(driver1Id, driver2Id) {
    return await fetchAPI(`/api/stats/head-to-head?driver1=${driver1Id}&driver2=${driver2Id}`);
}

/**
 * Get available seasons
 */
export async function getAvailableSeasons() {
    // This endpoint doesn't exist yet, but we can infer from 1984-2024
    return Array.from({ length: 2024 - 1984 + 1 }, (_, i) => 1984 + i).reverse();
}

/**
 * Clear all caches
 */
export function clearCache() {
    cache.drivers = null;
    cache.constructors = null;
    cache.seasons.clear();
}

/**
 * Prefetch commonly used data
 */
export async function prefetchCommonData() {
    try {
        await Promise.all([
            getDrivers(),
            getConstructors()
        ]);
    } catch (error) {
        console.warn('Failed to prefetch data:', error);
    }
}
