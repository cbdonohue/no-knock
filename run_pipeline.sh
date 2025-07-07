#!/bin/bash

# Ocean Township Address Pipeline Runner
# Simple script to run the pipeline with common configurations

echo "🌊 Ocean Township Address Pipeline Runner"
echo "=========================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if pipeline.py exists
if [ ! -f "pipeline.py" ]; then
    print_error "pipeline.py not found in current directory"
    exit 1
fi

# Show menu
echo
echo "Choose an option:"
echo "1. Run full pipeline (with free geocoding)"
echo "2. Run full pipeline with Google Maps API"
echo "3. Quick analysis of existing data"
echo "4. Run setup and dependency check"
echo "5. Export data only (skip collection/geocoding)"
echo "6. Custom options"
echo "7. Exit"
echo

read -p "Enter your choice (1-7): " choice

case $choice in
    1)
        print_status "Running full pipeline with free geocoding..."
        python3 pipeline.py --full
        ;;
    2)
        read -p "Enter your Google Maps API key: " api_key
        if [ -z "$api_key" ]; then
            print_error "API key cannot be empty"
            exit 1
        fi
        print_status "Running full pipeline with Google Maps API..."
        python3 pipeline.py --full --google-api-key "$api_key"
        ;;
    3)
        print_status "Running quick analysis..."
        python3 pipeline.py --quick-analysis
        ;;
    4)
        print_status "Running setup..."
        python3 setup_pipeline.py
        ;;
    5)
        print_status "Running export only (using cached data)..."
        python3 pipeline.py --full --skip-collection --skip-geocoding
        ;;
    6)
        echo "Available options:"
        echo "  --full                    Run complete pipeline"
        echo "  --quick-analysis          Quick analysis only"
        echo "  --google-api-key KEY      Use Google Maps API"
        echo "  --skip-collection         Skip address collection"
        echo "  --skip-geocoding          Skip geocoding"
        echo "  --export-formats csv kml  Choose export formats"
        echo "  --config CONFIG_FILE      Use custom config file"
        echo "  --log-level INFO          Set logging level"
        echo
        read -p "Enter custom options: " custom_options
        print_status "Running with custom options: $custom_options"
        python3 pipeline.py $custom_options
        ;;
    7)
        print_status "Exiting..."
        exit 0
        ;;
    *)
        print_error "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    print_success "Pipeline completed successfully!"
else
    print_error "Pipeline failed. Check the logs for details."
    exit 1
fi