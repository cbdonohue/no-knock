# Ocean Township Address Pipeline - Workflow Guide

## 🌊 Overview

The Ocean Township Address Pipeline is a simplified, automated workflow that combines all the geocoding steps into a single streamlined process. Instead of running multiple scripts manually, you can now execute the entire pipeline with just one command.

## 🚀 What the Pipeline Does

### **Before (Manual Process)**
1. Run `python cache_addresses.py` to collect addresses
2. Run `python geocode_addresses.py` to add coordinates  
3. Run `python geocoded_examples.py` to analyze and export
4. Manually manage configurations and error handling

### **After (Automated Pipeline)**
1. Run `python pipeline.py --full` and you're done! 🎉

The pipeline automatically:
- ✅ Collects addresses from the Ocean Township website
- ✅ Geocodes them with coordinates (free or premium API)  
- ✅ Performs geographic analysis and statistics
- ✅ Exports data in multiple formats (CSV, KML, JSON)
- ✅ Generates comprehensive summary reports
- ✅ Handles errors gracefully with detailed logging
- ✅ Supports resume capability for interrupted runs

## 📦 Quick Start

### **1. Setup (One-time)**
```bash
# Check dependencies and setup environment
python3 setup_pipeline.py
```

### **2. Run the Pipeline**
```bash
# Complete pipeline with free geocoding
python3 pipeline.py --full

# Or use the interactive menu
./run_pipeline.sh
```

### **3. View Results**
The pipeline generates:
- `ocean_township_addresses.csv` - Spreadsheet/GIS format
- `ocean_township_addresses.kml` - Google Earth/Maps format  
- `pipeline_summary_YYYYMMDD_HHMMSS.json` - Detailed report
- `pipeline.log` - Execution log

## 🔧 Command Options

### **Basic Commands**
```bash
# Run complete pipeline
python3 pipeline.py --full

# Quick analysis of existing data
python3 pipeline.py --quick-analysis

# Show help
python3 pipeline.py --help
```

### **Advanced Options**
```bash
# Use Google Maps API for better accuracy
python3 pipeline.py --full --google-api-key YOUR_API_KEY

# Skip address collection (use cached data)
python3 pipeline.py --full --skip-collection

# Skip geocoding (export only)
python3 pipeline.py --full --skip-collection --skip-geocoding

# Choose export formats
python3 pipeline.py --full --export-formats csv kml json

# Use custom configuration
python3 pipeline.py --full --config my_config.json

# Set logging level
python3 pipeline.py --full --log-level DEBUG
```

## 📊 Pipeline Steps

### **Step 1: Address Collection**
- Fetches current addresses from Ocean Township website
- Caches data locally for faster subsequent runs
- Parses and structures address information

### **Step 2: Geocoding**
- Converts addresses to latitude/longitude coordinates
- Uses Nominatim (free) or Google Maps API (premium)
- Implements smart retry logic and rate limiting
- Supports resume capability for interrupted runs

### **Step 3: Analysis & Export**
- Generates geographic statistics and insights
- Performs density analysis and proximity calculations
- Exports data in multiple formats for different use cases

### **Step 4: Summary Report**
- Creates comprehensive execution summary
- Includes performance metrics and recommendations
- Provides actionable insights for future runs

## 🎯 Use Cases

### **For Administrators**
```bash
# Weekly data refresh
python3 pipeline.py --full --skip-collection  # Use cached addresses

# Monthly comprehensive update
python3 pipeline.py --full  # Fresh data collection
```

### **For Analysts**
```bash
# Quick stats check
python3 pipeline.py --quick-analysis

# Detailed analysis with all formats
python3 pipeline.py --full --export-formats csv kml json
```

### **For GIS Users**
```bash
# Export for mapping software
python3 pipeline.py --full --export-formats csv

# Export for Google Earth
python3 pipeline.py --full --export-formats kml
```

## ⚙️ Configuration

### **Default Configuration**
The pipeline uses sensible defaults, but you can customize behavior:

```json
{
  "log_level": "INFO",
  "use_cached_addresses": true,
  "resume_geocoding": true,
  "export_formats": ["csv", "kml"]
}
```

### **Advanced Configuration**
Edit `pipeline_config.json` for detailed customization:

```json
{
  "log_level": "INFO",
  "use_cached_addresses": true,
  "resume_geocoding": true,
  "request_delay": 1.0,
  "max_retries": 3,
  "export_settings": {
    "csv_delimiter": ",",
    "include_failed_addresses": false,
    "coordinate_precision": 6
  },
  "geocoding_preferences": {
    "prefer_google_maps": false,
    "nominatim_timeout": 30,
    "google_maps_timeout": 30
  }
}
```

## 🛠️ Interactive Runner

Use the interactive script for a menu-driven experience:

```bash
./run_pipeline.sh
```

This provides a user-friendly menu with options for:
1. Full pipeline with free geocoding
2. Full pipeline with Google Maps API
3. Quick analysis only
4. Setup and dependency check
5. Export data only
6. Custom options
7. Exit

## 📈 Performance & Monitoring

### **Logging**
- All operations are logged to `pipeline.log`
- Real-time progress updates with emojis
- Detailed error reporting and troubleshooting info

### **Progress Tracking**
- Step-by-step execution with clear status
- ETA estimates for long-running operations
- Resume capability for interrupted runs

### **Summary Reports**
Each run generates a timestamped summary with:
- Execution statistics
- Data quality metrics
- Performance indicators
- Recommendations for improvements

## 🔍 Troubleshooting

### **Common Issues**

**❌ "Module not found" errors**
```bash
# Run setup to check dependencies
python3 setup_pipeline.py
```

**❌ "No addresses found" errors**
```bash
# Check internet connection and try again
python3 pipeline.py --full
```

**❌ Low geocoding success rate**
```bash
# Try Google Maps API for better accuracy
python3 pipeline.py --full --google-api-key YOUR_API_KEY
```

**❌ Pipeline interrupted**
```bash
# Resume from where it left off
python3 pipeline.py --full  # Automatically resumes
```

### **Debug Mode**
For detailed troubleshooting:
```bash
python3 pipeline.py --full --log-level DEBUG
```

## 🎉 Benefits

### **Simplicity**
- One command instead of multiple scripts
- Automatic error handling and recovery
- Interactive menu for easy use

### **Reliability**
- Comprehensive logging and monitoring
- Resume capability for interrupted runs
- Graceful error handling with detailed messages

### **Flexibility**
- Multiple export formats
- Configurable options
- Support for both free and premium geocoding

### **Insights**
- Automatic analysis and statistics
- Summary reports with recommendations
- Performance metrics and optimization tips

## 📞 Support

For questions or issues:
1. Check the `pipeline.log` file for detailed error messages
2. Run with `--log-level DEBUG` for verbose output
3. Use `python3 setup_pipeline.py` to verify setup
4. Review the generated summary reports for insights

## 🔄 Migration from Manual Process

If you're upgrading from the manual process:

1. **Backup your data**: Your existing cache files will be preserved
2. **Run setup**: `python3 setup_pipeline.py`
3. **Test the pipeline**: `python3 pipeline.py --quick-analysis`
4. **Full run**: `python3 pipeline.py --full`

The pipeline is fully backward compatible and will use your existing cached data.

---

**Happy geocoding! 🗺️**