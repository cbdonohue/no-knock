#!/usr/bin/env python3
"""
Geocode Ocean Township No Knock Registry Addresses
Adds latitude and longitude coordinates to cached addresses
"""

import json
import pickle
import time
import requests
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import sys

class AddressGeocoder:
    def __init__(self, cache_dir: str = "address_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Input files
        self.addresses_file = self.cache_dir / "addresses.json"
        self.addresses_pickle = self.cache_dir / "addresses.pkl"
        
        # Output files
        self.geocoded_file = self.cache_dir / "geocoded_addresses.json"
        self.geocoded_pickle = self.cache_dir / "geocoded_addresses.pkl"
        self.failed_file = self.cache_dir / "failed_geocoding.json"
        
        # Rate limiting
        self.request_delay = 1.0  # Seconds between requests (be respectful to free services)
        
        # Progress tracking
        self.processed_count = 0
        self.success_count = 0
        self.failed_count = 0
        
    def load_addresses(self) -> List[Dict]:
        """Load addresses from cache"""
        try:
            if self.addresses_pickle.exists():
                with open(self.addresses_pickle, 'rb') as f:
                    return pickle.load(f)
            elif self.addresses_file.exists():
                with open(self.addresses_file, 'r') as f:
                    return json.load(f)
            else:
                print("❌ No cached addresses found. Run cache_addresses.py first.")
                return []
        except Exception as e:
            print(f"❌ Error loading addresses: {e}")
            return []
    
    def load_existing_geocoded(self) -> Dict[str, Dict]:
        """Load existing geocoded addresses to avoid re-processing"""
        existing = {}
        try:
            if self.geocoded_file.exists():
                with open(self.geocoded_file, 'r') as f:
                    data = json.load(f)
                    for addr in data:
                        if 'full_address' in addr:
                            existing[addr['full_address']] = addr
        except Exception as e:
            print(f"⚠️  Could not load existing geocoded data: {e}")
        
        return existing
    
    def geocode_with_nominatim(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Geocode address using Nominatim (OpenStreetMap) - Free but rate limited
        Returns (latitude, longitude) or None if failed
        """
        try:
            # Nominatim API endpoint
            url = "https://nominatim.openstreetmap.org/search"
            
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1,
                'countrycodes': 'us'  # Limit to US addresses
            }
            
            headers = {
                'User-Agent': 'Ocean Township Address Geocoder (Educational Use)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return (lat, lon)
            
            return None
            
        except Exception as e:
            print(f"  ❌ Nominatim error for '{address}': {e}")
            return None
    
    def geocode_with_google(self, address: str, api_key: str) -> Optional[Tuple[float, float]]:
        """
        Geocode address using Google Maps API - More accurate but requires API key
        Returns (latitude, longitude) or None if failed
        """
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            
            params = {
                'address': address,
                'key': api_key,
                'region': 'us'  # Bias towards US results
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                location = data['results'][0]['geometry']['location']
                lat = float(location['lat'])
                lng = float(location['lng'])
                return (lat, lng)
            
            return None
            
        except Exception as e:
            print(f"  ❌ Google Maps error for '{address}': {e}")
            return None
    
    def geocode_address(self, address_data: Dict, google_api_key: Optional[str] = None) -> Dict:
        """Geocode a single address and return updated data"""
        address = address_data['full_address']
        
        # Try Google Maps first if API key provided
        if google_api_key:
            coords = self.geocode_with_google(address, google_api_key)
            geocoding_service = 'google_maps'
        else:
            coords = self.geocode_with_nominatim(address)
            geocoding_service = 'nominatim'
        
        # Update the address data
        geocoded_data = address_data.copy()
        
        if coords:
            geocoded_data.update({
                'latitude': coords[0],
                'longitude': coords[1],
                'geocoded_date': datetime.now().isoformat(),
                'geocoding_service': geocoding_service,
                'geocoding_status': 'success'
            })
            self.success_count += 1
            print(f"  ✅ {address} → ({coords[0]:.6f}, {coords[1]:.6f})")
        else:
            geocoded_data.update({
                'latitude': None,
                'longitude': None,
                'geocoded_date': datetime.now().isoformat(),
                'geocoding_service': geocoding_service,
                'geocoding_status': 'failed'
            })
            self.failed_count += 1
            print(f"  ❌ Failed: {address}")
        
        self.processed_count += 1
        return geocoded_data
    
    def save_progress(self, geocoded_addresses: List[Dict], failed_addresses: List[Dict]):
        """Save current progress"""
        try:
            # Save geocoded addresses
            with open(self.geocoded_file, 'w') as f:
                json.dump(geocoded_addresses, f, indent=2)
            
            with open(self.geocoded_pickle, 'wb') as f:
                pickle.dump(geocoded_addresses, f)
            
            # Save failed addresses
            if failed_addresses:
                with open(self.failed_file, 'w') as f:
                    json.dump(failed_addresses, f, indent=2)
            
            print(f"💾 Progress saved: {len(geocoded_addresses)} addresses")
            
        except Exception as e:
            print(f"❌ Error saving progress: {e}")
    
    def geocode_all_addresses(self, google_api_key: Optional[str] = None, resume: bool = True):
        """Geocode all addresses from the cache"""
        print("🌍 Starting address geocoding...")
        print(f"📡 Using: {'Google Maps API' if google_api_key else 'Nominatim (OpenStreetMap)'}")
        
        # Load addresses
        addresses = self.load_addresses()
        if not addresses:
            return
        
        print(f"📍 Found {len(addresses)} addresses to process")
        
        # Load existing geocoded data if resuming
        existing_geocoded = {}
        geocoded_addresses = []
        failed_addresses = []
        
        if resume:
            existing_geocoded = self.load_existing_geocoded()
            geocoded_addresses = list(existing_geocoded.values())
            print(f"🔄 Resuming: {len(existing_geocoded)} already processed")
        
        # Process addresses
        start_time = time.time()
        
        try:
            for i, addr_data in enumerate(addresses, 1):
                address = addr_data['full_address']
                
                # Skip if already processed and resuming
                if resume and address in existing_geocoded:
                    continue
                
                print(f"\n[{i}/{len(addresses)}] Processing: {address[:60]}...")
                
                # Geocode the address
                geocoded_data = self.geocode_address(addr_data, google_api_key)
                
                if geocoded_data['geocoding_status'] == 'success':
                    geocoded_addresses.append(geocoded_data)
                else:
                    failed_addresses.append(geocoded_data)
                
                # Rate limiting - be respectful to free services
                if not google_api_key:  # More conservative with free services
                    time.sleep(self.request_delay)
                else:
                    time.sleep(0.1)  # Google allows higher rates
                
                # Save progress every 50 addresses
                if self.processed_count % 50 == 0:
                    self.save_progress(geocoded_addresses, failed_addresses)
                    
                    # Show progress
                    elapsed = time.time() - start_time
                    rate = self.processed_count / elapsed
                    remaining = len(addresses) - i
                    eta = remaining / rate if rate > 0 else 0
                    
                    print(f"\n📊 Progress: {self.processed_count} processed, "
                          f"{self.success_count} success, {self.failed_count} failed")
                    print(f"⏱️  Rate: {rate:.1f} addr/sec, ETA: {eta/60:.1f} minutes")
        
        except KeyboardInterrupt:
            print("\n⏸️  Interrupted by user. Saving progress...")
            self.save_progress(geocoded_addresses, failed_addresses)
            return
        
        # Final save
        self.save_progress(geocoded_addresses, failed_addresses)
        
        # Summary
        elapsed = time.time() - start_time
        print(f"\n🎉 Geocoding complete!")
        print(f"⏱️  Total time: {elapsed/60:.1f} minutes")
        print(f"📊 Results:")
        print(f"  ✅ Successful: {self.success_count}")
        print(f"  ❌ Failed: {self.failed_count}")
        print(f"  📈 Success rate: {self.success_count/(self.success_count+self.failed_count)*100:.1f}%")
        
        print(f"\n💾 Files created:")
        print(f"  📍 Geocoded addresses: {self.geocoded_file}")
        print(f"  📍 Geocoded addresses (pickle): {self.geocoded_pickle}")
        if failed_addresses:
            print(f"  ❌ Failed addresses: {self.failed_file}")
    
    def get_geocoded_stats(self) -> Dict:
        """Get statistics about geocoded addresses"""
        try:
            if self.geocoded_file.exists():
                with open(self.geocoded_file, 'r') as f:
                    addresses = json.load(f)
                
                total = len(addresses)
                successful = len([a for a in addresses if a.get('latitude') is not None])
                failed = total - successful
                
                # Get bounding box
                lats = [a['latitude'] for a in addresses if a.get('latitude') is not None]
                lons = [a['longitude'] for a in addresses if a.get('longitude') is not None]
                
                bbox = None
                if lats and lons:
                    bbox = {
                        'north': max(lats),
                        'south': min(lats),
                        'east': max(lons),
                        'west': min(lons)
                    }
                
                return {
                    'total_addresses': total,
                    'successful_geocoding': successful,
                    'failed_geocoding': failed,
                    'success_rate': successful / total * 100 if total > 0 else 0,
                    'bounding_box': bbox
                }
            else:
                return {'error': 'No geocoded data found'}
                
        except Exception as e:
            return {'error': str(e)}


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Geocode Ocean Township addresses')
    parser.add_argument('--google-api-key', help='Google Maps API key for better accuracy')
    parser.add_argument('--no-resume', action='store_true', help='Start fresh (ignore existing geocoded data)')
    parser.add_argument('--stats-only', action='store_true', help='Only show statistics of existing geocoded data')
    
    args = parser.parse_args()
    
    geocoder = AddressGeocoder()
    
    if args.stats_only:
        stats = geocoder.get_geocoded_stats()
        print("📊 Geocoded Address Statistics:")
        print(json.dumps(stats, indent=2))
        return
    
    # Check if using Google API
    if args.google_api_key:
        print("🗺️  Using Google Maps API for higher accuracy")
        print("⚠️  Note: Google Maps API usage may incur charges")
    else:
        print("🆓 Using free Nominatim service (OpenStreetMap)")
        print("⚠️  Note: Free service has rate limits and may be less accurate")
    
    # Start geocoding
    geocoder.geocode_all_addresses(
        google_api_key=args.google_api_key,
        resume=not args.no_resume
    )


if __name__ == "__main__":
    main() 