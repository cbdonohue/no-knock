# Ocean Township Address Geocoding - Web UI Guide

## 🚀 Quick Start

### Option 1: Using the Startup Script (Recommended)
```bash
python3 start_web_ui.py
```

### Option 2: Direct Launch
```bash
# Install dependencies first
pip install --break-system-packages -r requirements.txt

# Run the application
python3 app.py
```

## 📍 Access the Web UI

Once started, the web application will be available at:
- **Primary URL**: http://localhost:5000
- **Network URL**: http://0.0.0.0:5000

## 🌟 Features

### 1. **Interactive Map View**
- View all geocoded addresses on an interactive map
- Click markers to see address details and coordinates
- Search and filter addresses directly on the map
- Zoom and pan to explore different areas

### 2. **Address Management**
- **Refresh Cache**: Fetch latest addresses from Ocean Township website
- **Start Geocoding**: Convert addresses to latitude/longitude coordinates
- **Real-time Progress**: Track geocoding progress with live updates

### 3. **Data Export**
- **CSV Format**: For spreadsheets and GIS applications
- **KML Format**: For Google Earth and Google Maps
- **JSON Format**: For custom applications and analysis

### 4. **Address List View**
- Browse all addresses in a searchable list
- Filter by city or zip code
- See geocoding status for each address
- View caching timestamps

### 5. **Analytics Dashboard**
- View statistics: total addresses, geocoded count, success rate
- Geographic distribution analysis
- City and zip code breakdown

## 🎯 How to Use

### First-Time Setup
1. **Start the Web UI**: Run `python3 start_web_ui.py`
2. **Load Addresses**: Click "Refresh Cache" to fetch current addresses
3. **Geocode Addresses**: Click "Start Geocoding" to add coordinates
4. **View Results**: Switch to "Map View" to see addresses on the map

### Daily Operations
- **Check for Updates**: Use "Refresh Cache" to get latest addresses
- **Export Data**: Use the "Export Data" dropdown for different formats
- **Search Addresses**: Use the search boxes to find specific addresses
- **Filter Results**: Use city/zip filters to narrow down results

## 🛠️ Technical Details

### API Endpoints
- `GET /api/addresses` - Get all cached addresses
- `GET /api/geocoded-addresses` - Get geocoded addresses
- `GET /api/statistics` - Get system statistics
- `POST /api/refresh-cache` - Refresh address cache
- `POST /api/geocode` - Start geocoding process
- `GET /api/progress` - Get operation progress
- `GET /api/export/{format}` - Export data in specified format

### Data Storage
- **Address Cache**: `address_cache/addresses.json`
- **Geocoded Data**: `address_cache/geocoded_addresses.json`
- **Failed Geocoding**: `address_cache/failed_geocoding.json`

### Dependencies
- **Flask**: Web framework
- **Requests**: HTTP client for web scraping
- **BeautifulSoup4**: HTML parsing
- **LXML**: XML/HTML processing
- **Leaflet**: Interactive maps (loaded via CDN)
- **Chart.js**: Data visualization (loaded via CDN)

## 🔧 Configuration

### Geocoding Services
- **Default**: Free Nominatim service (OpenStreetMap)
- **Premium**: Google Maps API (requires API key)

### Rate Limiting
- **Nominatim**: 1 request per second (respectful to free service)
- **Google Maps**: Higher rate limits (configurable)

## 📊 Understanding the Data

### Address Data Structure
```json
{
  "full_address": "64 Cold Indian Springs Road Ocean, NJ 07712",
  "street": "64 Cold Indian Springs Road",
  "city": "Ocean",
  "state": "NJ",
  "zip_code": "07712",
  "cached_date": "2025-01-07T10:30:00.123456",
  "latitude": 40.254123,
  "longitude": -74.028456,
  "geocoded_date": "2025-01-07T11:45:00.789012",
  "geocoding_service": "nominatim",
  "geocoding_status": "success"
}
```

### Success Rates
- **Typical Success Rate**: 85-95% depending on geocoding service
- **Factors**: Address formatting, geocoding service accuracy
- **Retry Logic**: Failed addresses can be reprocessed

## 🚨 Troubleshooting

### Common Issues
1. **Web UI won't start**: Check if dependencies are installed
2. **No addresses visible**: Click "Refresh Cache" to load data
3. **Geocoding fails**: Check internet connection and service availability
4. **Map not loading**: Verify internet connection for map tiles

### Error Messages
- **"No cached addresses found"**: Run cache refresh first
- **"Geocoding failed"**: Check network connectivity
- **"Export failed"**: Ensure geocoded data exists

## 🔄 Update Process

### Regular Updates
1. **Weekly**: Refresh address cache for new entries
2. **Monthly**: Re-geocode failed addresses
3. **Quarterly**: Export data for archival

### Data Refresh
- **Manual**: Use web UI "Refresh Cache" button
- **Automatic**: Can be scheduled via cron jobs

## 📈 Performance

### Typical Performance
- **~1,500 addresses** from Ocean Township registry
- **30-60 minutes** for full geocoding process
- **File sizes**: CSV (50KB), KML (300KB), JSON (500KB)

### Optimization Tips
- Use Google Maps API for better accuracy and speed
- Run geocoding during off-peak hours
- Export data in batches for large datasets

## 🌐 Browser Compatibility

### Supported Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Mobile Support
- Responsive design works on tablets and phones
- Touch-friendly interface
- Optimized for mobile viewing

---

**Built for Ocean Township, NJ** 🏢  
**Powered by Flask, Leaflet, and modern web technologies** 🚀