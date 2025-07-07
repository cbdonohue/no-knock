#!/usr/bin/env python3
"""
Ocean Township Address Geocoding System - Web UI Startup Script
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import requests
        import beautifulsoup4
        import lxml
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

def create_cache_directory():
    """Create address cache directory if it doesn't exist"""
    cache_dir = Path("address_cache")
    cache_dir.mkdir(exist_ok=True)
    print(f"✅ Cache directory ready: {cache_dir}")

def main():
    """Main startup function"""
    print("🌊 Ocean Township Address Geocoding System - Web UI")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create cache directory
    create_cache_directory()
    
    # Check if we have cached data
    addresses_file = Path("address_cache/addresses.json")
    if addresses_file.exists():
        print("✅ Found cached addresses")
    else:
        print("⚠️  No cached addresses found. You can:")
        print("   1. Use the web UI to refresh the cache")
        print("   2. Run 'python3 cache_addresses.py' first")
    
    # Start the web application
    print("\n🚀 Starting web application...")
    print("📍 Web UI will be available at: http://localhost:5000")
    print("🔗 Or try: http://0.0.0.0:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()