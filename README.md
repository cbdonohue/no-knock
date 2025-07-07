# Ocean Township No Knock Registry Address Cache

A Python script that caches addresses from the Ocean Township No Knock Registry for future processing.

## Features

- **Live Data Fetching**: Automatically fetches current addresses from the Ocean Township No Knock Registry website
- **Address Parsing**: Extracts and parses addresses from the live registry data
- **Geocoding**: Convert addresses to latitude/longitude coordinates using free or premium services
- **Dual Storage**: Saves addresses in both JSON and pickle formats for flexibility
- **Search & Filter**: Find addresses by city, zip code, or proximity to coordinates
- **Statistics**: Get detailed statistics about the cached addresses
- **Structured Data**: Each address is parsed into components (street, city, state, zip)
- **Mapping Export**: Export data for use in Google Maps, Google Earth, QGIS, and other mapping tools
- **Fallback Protection**: Falls back to cached data if website is unavailable

## Usage

### Basic Usage

```bash
python cache_addresses.py
```

This will:
1. Fetch live addresses from the Ocean Township No Knock Registry website
2. Cache them to `address_cache/addresses.json` and `address_cache/addresses.pkl`
3. Display statistics about the cached addresses

### Programmatic Usage

```python
from cache_addresses import AddressCache

# Initialize the cache
cache = AddressCache()

# Load all addresses
addresses = cache.load_addresses()

# Get addresses by city
ocean_addresses = cache.get_addresses_by_city('Ocean')
oakhurst_addresses = cache.get_addresses_by_city('Oakhurst')

# Get addresses by zip code
zip_07712 = cache.get_addresses_by_zip('07712')
zip_07755 = cache.get_addresses_by_zip('07755')

# Refresh cache with live data
cache.refresh_cache()

# Get statistics
stats = cache.get_stats()
print(f"Total addresses: {stats['total_addresses']}")
```

### Geocoding Addresses

Add latitude/longitude coordinates to addresses:

```bash
# Using free Nominatim service (OpenStreetMap)
python geocode_addresses.py

# Using Google Maps API (more accurate, requires API key)
python geocode_addresses.py --google-api-key YOUR_API_KEY

# Resume interrupted geocoding
python geocode_addresses.py --resume

# Start fresh (ignore existing geocoded data)
python geocode_addresses.py --no-resume

# Show statistics only
python geocode_addresses.py --stats-only
```

### Using Geocoded Data

```python
from geocoded_examples import GeocodedAnalyzer

analyzer = GeocodedAnalyzer()

# Get basic statistics
stats = analyzer.get_basic_stats()
print(f"Success rate: {stats['success_rate']:.1f}%")

# Find addresses near a point (latitude, longitude, radius in miles)
nearby = analyzer.find_addresses_near_point(40.2535, -74.0287, 0.5)

# Export for mapping tools
analyzer.export_for_mapping("addresses.csv")  # For spreadsheets/GIS
analyzer.generate_kml("addresses.kml")        # For Google Earth
```

## Data Structure

### Basic Address Data

Each address is stored as a dictionary with the following structure:

```python
{
    'full_address': '64 Cold Indian Springs Road Ocean, NJ 07712',
    'street': '64 Cold Indian Springs Road',
    'city': 'Ocean',
    'state': 'NJ',
    'zip_code': '07712',
    'cached_date': '2024-01-15T10:30:00.123456'
}
```

### Geocoded Address Data

After geocoding, addresses include additional coordinate information:

```python
{
    'full_address': '64 Cold Indian Springs Road Ocean, NJ 07712',
    'street': '64 Cold Indian Springs Road',
    'city': 'Ocean',
    'state': 'NJ',
    'zip_code': '07712',
    'cached_date': '2024-01-15T10:30:00.123456',
    'latitude': 40.254123,
    'longitude': -74.028456,
    'geocoded_date': '2024-01-15T11:45:00.789012',
    'geocoding_service': 'nominatim',  # or 'google_maps'
    'geocoding_status': 'success'      # or 'failed'
}
```

## Files Created

### Address Cache Files
- `address_cache/addresses.json` - Human-readable JSON format
- `address_cache/addresses.pkl` - Binary pickle format (faster loading)

### Geocoded Files (after running geocode_addresses.py)
- `address_cache/geocoded_addresses.json` - Addresses with coordinates (JSON)
- `address_cache/geocoded_addresses.pkl` - Addresses with coordinates (pickle)
- `address_cache/failed_geocoding.json` - Addresses that failed geocoding

### Export Files (after running geocoded_examples.py)
- `ocean_township_addresses.csv` - CSV format for spreadsheets/GIS
- `ocean_township_addresses.kml` - KML format for Google Earth/Maps

## Data Source

The addresses are sourced from the Ocean Township No Knock Registry:
https://webgeo.co/prod1/portal/portal.jsp?c=3668658&p=557207238&g=557207303

## Requirements

- Python 3.6+
- requests (for web scraping)
- beautifulsoup4 (for HTML parsing)
- lxml (for HTML parsing)

Install dependencies with:
```bash
pip install -r requirements.txt
```

## License

This script is provided as-is for educational and administrative purposes. 