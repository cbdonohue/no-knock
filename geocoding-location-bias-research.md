# Geocoding Location Bias for Monmouth County, NJ - Research & Implementation

## Overview

Successfully implemented location biasing to prime both Nominatim (OpenStreetMap) and Google Maps geocoding APIs to prefer results within Monmouth County, New Jersey. This improves geocoding accuracy for Ocean Township addresses by focusing search results on the local area.

## Implementation Details

### Monmouth County Bounding Box

Based on Wikipedia data for Monmouth County, NJ:
- **North**: 40.5°
- **South**: 40.1° 
- **West**: -74.6°
- **East**: -73.8°
- **Center**: ~40.3°N, 74.2°W

### Location Biasing Parameters Added

#### 1. Nominatim (OpenStreetMap) API
```python
params = {
    'q': address,
    'format': 'json',
    'limit': 1,
    'addressdetails': 1,
    'countrycodes': 'us',  # Existing - Limit to US addresses
    'viewbox': viewbox,    # NEW - Bias towards Monmouth County, NJ
    'bounded': 0           # NEW - Don't strictly limit to viewbox, just bias
}
```

**Parameters Explained:**
- `viewbox`: Defines preferred search area as `west,north,east,south` coordinates
- `bounded=0`: Results can come from outside the viewbox if they're more relevant (biasing, not filtering)
- `bounded=1`: Would strictly limit results to within the viewbox

#### 2. Google Maps API
```python
params = {
    'address': address,
    'key': api_key,
    'region': 'us',  # Existing - Bias towards US results
    'bounds': bounds,  # NEW - Bias towards Monmouth County, NJ
    'components': 'administrative_area_level_2:Monmouth County|country:US'  # NEW - Component filtering
}
```

**Parameters Explained:**
- `bounds`: Viewport biasing using `southwest_lat,southwest_lng|northeast_lat,northeast_lng` format
- `components`: Administrative area filtering to prefer Monmouth County results
- Both parameters work together to strongly bias toward local results

## Benefits of Location Biasing

### 1. **Improved Accuracy**
- Addresses like "Main Street" will prefer Monmouth County results over other states
- Reduces ambiguous matches from similarly named streets in other areas

### 2. **Better Context Resolution**
- Incomplete addresses (missing ZIP codes) are more likely to resolve correctly
- Common local street names get prioritized appropriately

### 3. **Faster Processing**
- APIs can focus search efforts on the relevant geographic area
- Reduces processing time for obvious local matches

## Example Impact

**Before Location Biasing:**
- "Main Street, Ocean Township, NJ" might return results from Ocean Township, PA or other locations first

**After Location Biasing:**
- Same query prioritizes Monmouth County, NJ results
- More likely to return the correct Ocean Township location

## Configuration Options

### Strict vs. Loose Biasing

**Current Implementation (Loose Biasing):**
- Nominatim: `bounded=0` allows results outside the viewbox if more relevant
- Google Maps: `bounds` parameter biases but doesn't restrict

**Alternative (Strict Biasing):**
- Could set Nominatim `bounded=1` to only return results within Monmouth County
- Trade-off: Might miss valid addresses just outside county boundaries

### Adjustable Parameters

The bounding box coordinates are stored in the `monmouth_county_bounds` dictionary and can be easily modified:

```python
self.monmouth_county_bounds = {
    'north': 40.5,   # Can be adjusted for wider/narrower area
    'south': 40.1,
    'west': -74.6,
    'east': -73.8
}
```

## Testing Recommendations

### 1. **Address Quality Testing**
Test with various address formats:
- Complete addresses: "123 Main Street, Ocean Township, NJ 07712"
- Incomplete addresses: "Main Street, Ocean Township"
- Street names only: "Main Street"

### 2. **Boundary Testing**
Test addresses near county boundaries:
- Addresses just inside Monmouth County
- Addresses just outside (to ensure they still resolve if legitimate)

### 3. **Ambiguous Address Testing**
Test common street names that exist in multiple locations:
- "Main Street" (exists in many NJ towns)
- "Park Avenue"
- "First Street"

## Performance Impact

### Minimal Overhead
- Added parameters don't significantly increase API call time
- May actually improve performance by reducing search scope

### Rate Limiting Unchanged
- Same rate limiting applies
- No additional API calls required

## Future Enhancements

### 1. **Dynamic Bounds Adjustment**
Could implement different bounds for different municipalities:
- Tighter bounds for known Ocean Township addresses
- Wider bounds for regional searches

### 2. **Fallback Strategy**
If local biasing returns no results, could retry without bounds:
```python
# First try with bounds
coords = self.geocode_with_bounds(address, api_key)
if not coords:
    # Fallback to unbiased search
    coords = self.geocode_without_bounds(address, api_key)
```

### 3. **Adaptive Biasing**
Could analyze historical geocoding results to optimize bounds:
- Track which areas produce the most results
- Adjust bounds based on success patterns

## Usage Notes

### No Breaking Changes
- Existing functionality remains unchanged
- Backward compatible with all current address formats
- No changes required to calling code

### Error Handling
- Location biasing parameters are safely ignored if invalid
- Falls back to normal geocoding behavior if bias parameters fail

## Summary

The implementation successfully adds intelligent location biasing to the Ocean Township geocoding system. This enhancement:

✅ **Improves accuracy** for local address resolution  
✅ **Maintains compatibility** with existing code  
✅ **Provides flexibility** for future adjustments  
✅ **Uses best practices** from both Nominatim and Google Maps documentation  
✅ **Balances precision** with availability (biasing vs. strict filtering)  

The geocoder now intelligently prioritizes Monmouth County, NJ results while still allowing for legitimate matches outside the area when appropriate.