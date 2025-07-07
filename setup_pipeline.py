#!/usr/bin/env python3
"""
Setup script for Ocean Township Address Pipeline
Checks dependencies and prepares the environment
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def check_python_version():
    """Check if Python version is supported"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 6):
        print("❌ Python 3.6+ is required. Current version:", sys.version)
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} is supported")
    return True


def check_dependencies():
    """Check if all required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'requests',
        'beautifulsoup4',
        'lxml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    return missing_packages


def install_dependencies(packages):
    """Install missing dependencies"""
    if not packages:
        return True
    
    print(f"📥 Installing missing packages: {', '.join(packages)}")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade"
        ] + packages)
        print("✅ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def check_modules():
    """Check if the required modules are available"""
    print("🔍 Checking required modules...")
    
    required_modules = [
        'cache_addresses',
        'geocode_addresses',
        'geocoded_examples'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}.py is available")
        except ImportError:
            print(f"❌ {module}.py is missing")
            missing_modules.append(module)
    
    return missing_modules


def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        'address_cache',
        'exports',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created/verified directory: {directory}")


def create_sample_config():
    """Create a sample configuration file if it doesn't exist"""
    print("⚙️  Setting up configuration...")
    
    config_file = "pipeline_config.json"
    
    if not os.path.exists(config_file):
        sample_config = {
            "log_level": "INFO",
            "use_cached_addresses": True,
            "resume_geocoding": True,
            "export_formats": ["csv", "kml"]
        }
        
        with open(config_file, 'w') as f:
            json.dump(sample_config, f, indent=2)
        
        print(f"✅ Created sample configuration: {config_file}")
    else:
        print(f"✅ Configuration file already exists: {config_file}")


def run_test():
    """Run a quick test to verify everything works"""
    print("🧪 Running quick test...")
    
    try:
        # Test imports
        from cache_addresses import AddressCache
        from geocode_addresses import AddressGeocoder
        from geocoded_examples import GeocodedAnalyzer
        
        # Test basic functionality
        cache = AddressCache()
        geocoder = AddressGeocoder()
        analyzer = GeocodedAnalyzer()
        
        print("✅ All modules imported successfully")
        print("✅ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main setup function"""
    print("🌊 Ocean Township Address Pipeline Setup")
    print("=" * 50)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Check and install dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        if not install_dependencies(missing_deps):
            success = False
    
    # Check required modules
    missing_modules = check_modules()
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        print("Make sure all Python files are in the same directory.")
        success = False
    
    # Create directories
    create_directories()
    
    # Create sample configuration
    create_sample_config()
    
    # Run test
    if success:
        success = run_test()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run the full pipeline: python pipeline.py --full")
        print("2. Or run quick analysis: python pipeline.py --quick-analysis")
        print("3. For help: python pipeline.py --help")
    else:
        print("❌ Setup failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()