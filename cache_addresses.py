#!/usr/bin/env python3
"""
Ocean Township No Knock Registry Address Cache
Extracts and caches addresses from the registry for future processing
"""

import json
import pickle
import re
import requests
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from bs4 import BeautifulSoup


class AddressCache:
    def __init__(self, cache_dir: str = "address_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.json_file = self.cache_dir / "addresses.json"
        self.pickle_file = self.cache_dir / "addresses.pkl"
        
    def fetch_live_addresses(self) -> List[Dict[str, str]]:
        """Fetch live addresses from the Ocean Township No Knock Registry website"""
        url = "https://webgeo.co/prod1/portal/portal.jsp?c=3668658&p=557207238&g=557207303"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            print(f"Fetching live data from: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find addresses in the page content
            addresses = []
            raw_addresses = self._extract_addresses_from_html(soup)
            
            print(f"Found {len(raw_addresses)} raw addresses from website")
            
            # Parse each address
            for addr in raw_addresses:
                parsed = self._parse_single_address(addr)
                if parsed:
                    addresses.append(parsed)
            
            return addresses
            
        except requests.RequestException as e:
            print(f"Error fetching data from website: {e}")
            print("Falling back to cached data if available...")
            return self.load_addresses() if self.json_file.exists() else []
        except Exception as e:
            print(f"Error parsing website data: {e}")
            print("Falling back to cached data if available...")
            return self.load_addresses() if self.json_file.exists() else []
    
    def _extract_addresses_from_html(self, soup: BeautifulSoup) -> List[str]:
        """Extract addresses from the HTML content"""
        addresses = []
        
        # The webpage contains addresses in a large text block
        # First, try to find the main content area
        page_text = soup.get_text()
        
        # Look for the section with addresses after "Street AdressCity, State Zip"
        if "Street AdressCity, State Zip" in page_text:
            # Split by this header and take the content after it
            parts = page_text.split("Street AdressCity, State Zip", 1)
            if len(parts) > 1:
                address_content = parts[1]
            else:
                address_content = page_text
        else:
            address_content = page_text
        
        # Extract address patterns using regex
        # Look for patterns like: number + street name + city + state + zip
        address_patterns = [
            # Pattern: "123 Street Name City, ST 12345"
            r'(\d+(?:\s+\d+/\d+)?\s+[A-Za-z\s\.,\-\']+(?:Ocean|Oakhurst|Wanamassa|Allenhurst|Elberon|Deal|Wayside)[^,\n]*,?\s*(?:N\.?J\.?|New Jersey)\s*\d{5}(?:-\d{4})?)',
            # Pattern: "123 Street Name City ST 12345" (without comma)
            r'(\d+(?:\s+\d+/\d+)?\s+[A-Za-z\s\.,\-\']+(?:Ocean|Oakhurst|Wanamassa|Allenhurst|Elberon|Deal|Wayside)[^,\n]*\s+(?:N\.?J\.?|New Jersey)\s+\d{5}(?:-\d{4})?)',
        ]
        
        for pattern in address_patterns:
            matches = re.findall(pattern, address_content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                addr = match.strip()
                # Clean up the address
                addr = re.sub(r'\s+', ' ', addr)  # Replace multiple spaces with single space
                addr = re.sub(r'\n', ' ', addr)   # Replace newlines with spaces
                
                if addr and self._looks_like_address(addr) and len(addr) < 200:  # Reasonable length limit
                    addresses.append(addr)
        
        # If still no addresses, try a different approach - split by lines and filter
        if not addresses:
            lines = address_content.split('\n')
            for line in lines:
                line = line.strip()
                if line and self._looks_like_address(line) and len(line) < 200:
                    addresses.append(line)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_addresses = []
        for addr in addresses:
            normalized_addr = re.sub(r'\s+', ' ', addr.strip())  # Normalize whitespace
            if normalized_addr not in seen and len(normalized_addr) > 15:  # Minimum length filter
                seen.add(normalized_addr)
                unique_addresses.append(normalized_addr)
        
        return unique_addresses
    
    def _looks_like_address(self, text: str) -> bool:
        """Check if text looks like a valid address"""
        # Basic checks for address format
        if len(text) < 15:  # Too short to be a full address
            return False
        
        if len(text) > 150:  # Too long, probably not a single address
            return False
        
        # Should contain numbers (house number)
        if not re.search(r'^\d+', text.strip()):  # Should start with a number
            return False
        
        # Should contain one of the known cities
        cities = ['Ocean', 'Oakhurst', 'Wanamassa', 'Allenhurst', 'Elberon', 'Deal', 'Wayside']
        if not any(city.lower() in text.lower() for city in cities):
            return False
        
        # Should contain NJ and zip code
        if not re.search(r'N\.?J\.?|New Jersey', text, re.IGNORECASE):
            return False
        
        if not re.search(r'0[0-9]{4}(?:-[0-9]{4})?', text):  # Zip code pattern
            return False
        
        # Exclude headers and non-address content
        exclude_patterns = [
            'Street AdressCity',
            'New No Knock Registration',
            'Ocean Township',
            'No Knock Registry'
        ]
        
        for pattern in exclude_patterns:
            if pattern.lower() in text.lower():
                return False
        
        return True
    
    def _parse_single_address(self, address: str) -> Optional[Dict[str, str]]:
        """Parse a single address string into components"""
        # Clean up the address
        address = address.strip()
        if not address:
            return None
        
        # Try to extract components using regex
        # Pattern: Street Address, City, State ZIP
        pattern = r'^(.+?)\s+([A-Za-z\s]+),?\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)?$'
        match = re.match(pattern, address)
        
        if match:
            street, city, state, zip_code = match.groups()
            return {
                'full_address': address,
                'street': street.strip(),
                'city': city.strip(),
                'state': state.strip(),
                'zip_code': zip_code.strip() if zip_code else '',
                'cached_date': datetime.now().isoformat()
            }
        else:
            # If regex fails, return basic structure
            return {
                'full_address': address,
                'street': '',
                'city': '',
                'state': '',
                'zip_code': '',
                'cached_date': datetime.now().isoformat()
            }
    
    def cache_addresses(self, addresses: List[Dict[str, str]]) -> None:
        """Cache addresses to both JSON and pickle formats"""
        # Save as JSON
        with open(self.json_file, 'w') as f:
            json.dump(addresses, f, indent=2)
        
        # Save as pickle for faster loading
        with open(self.pickle_file, 'wb') as f:
            pickle.dump(addresses, f)
        
        print(f"Cached {len(addresses)} addresses to {self.cache_dir}")
    
    def load_addresses(self, use_pickle: bool = True) -> List[Dict[str, str]]:
        """Load cached addresses"""
        if use_pickle and self.pickle_file.exists():
            with open(self.pickle_file, 'rb') as f:
                return pickle.load(f)
        elif self.json_file.exists():
            with open(self.json_file, 'r') as f:
                return json.load(f)
        else:
            return []
    
    def get_addresses_by_city(self, city: str) -> List[Dict[str, str]]:
        """Get addresses filtered by city"""
        addresses = self.load_addresses()
        return [addr for addr in addresses if city.lower() in addr['city'].lower()]
    
    def get_addresses_by_zip(self, zip_code: str) -> List[Dict[str, str]]:
        """Get addresses filtered by zip code"""
        addresses = self.load_addresses()
        return [addr for addr in addresses if zip_code in addr['zip_code']]
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about cached addresses"""
        addresses = self.load_addresses()
        cities = {}
        zip_codes = {}
        
        for addr in addresses:
            city = addr['city']
            zip_code = addr['zip_code']
            
            cities[city] = cities.get(city, 0) + 1
            zip_codes[zip_code] = zip_codes.get(zip_code, 0) + 1
        
        return {
            'total_addresses': len(addresses),
            'unique_cities': len(cities),
            'unique_zip_codes': len(zip_codes),
            'city_counts': cities,
            'zip_code_counts': zip_codes
        }
    
    def refresh_cache(self) -> bool:
        """Refresh the cache with live data from the website"""
        print("Refreshing cache with live data...")
        addresses = self.fetch_live_addresses()
        
        if addresses:
            self.cache_addresses(addresses)
            return True
        else:
            print("Failed to refresh cache - no addresses found")
            return False


def main():
    """Main function to cache addresses"""
    cache = AddressCache()
    
    # Fetch live addresses from the website
    addresses = cache.fetch_live_addresses()
    
    # Cache the addresses
    if addresses:
        cache.cache_addresses(addresses)
    else:
        print("No addresses found or error occurred.")
    
    # Display statistics
    stats = cache.get_stats()
    print("\nAddress Cache Statistics:")
    print(f"Total addresses: {stats['total_addresses']}")
    print(f"Unique cities: {stats['unique_cities']}")
    print(f"Unique zip codes: {stats['unique_zip_codes']}")
    
    print("\nTop cities by address count:")
    for city, count in sorted(stats['city_counts'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {city}: {count}")
    
    print("\nTop zip codes by address count:")
    for zip_code, count in sorted(stats['zip_code_counts'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {zip_code}: {count}")
    
    # Example usage
    print("\nExample usage:")
    print("Load all addresses: cache.load_addresses()")
    print("Get Ocean addresses: cache.get_addresses_by_city('Ocean')")
    print("Get 07712 addresses: cache.get_addresses_by_zip('07712')")


if __name__ == "__main__":
    main() 