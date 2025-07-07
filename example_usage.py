#!/usr/bin/env python3
"""
Example usage of the Ocean Township Address Cache
"""

from cache_addresses import AddressCache

def main():
    # Initialize the cache
    cache = AddressCache()
    
    # Load all addresses
    print("Loading all addresses...")
    addresses = cache.load_addresses()
    print(f"Loaded {len(addresses)} addresses\n")
    
    # Example 1: Get addresses by city
    print("=== Addresses in Ocean ===")
    ocean_addresses = cache.get_addresses_by_city('Ocean')
    for addr in ocean_addresses[:5]:  # Show first 5
        print(f"  {addr['full_address']}")
    print(f"  ... and {len(ocean_addresses) - 5} more Ocean addresses\n")
    
    # Example 2: Get addresses by zip code
    print("=== Addresses in 07755 (Oakhurst area) ===")
    zip_07755 = cache.get_addresses_by_zip('07755')
    for addr in zip_07755[:5]:  # Show first 5
        print(f"  {addr['full_address']}")
    print(f"  ... and {len(zip_07755) - 5} more 07755 addresses\n")
    
    # Example 3: Get statistics
    print("=== Statistics ===")
    stats = cache.get_stats()
    print(f"Total addresses: {stats['total_addresses']}")
    print(f"Unique cities: {stats['unique_cities']}")
    print(f"Unique zip codes: {stats['unique_zip_codes']}")
    
    # Example 4: Find specific street names
    print("\n=== Search for specific streets ===")
    abbey_lane = [addr for addr in addresses if 'Abbey Lane' in addr['full_address']]
    print(f"Found {len(abbey_lane)} addresses on Abbey Lane:")
    for addr in abbey_lane:
        print(f"  {addr['full_address']}")
    
    # Example 5: Group by zip code
    print("\n=== Top 5 zip codes by address count ===")
    zip_counts = {}
    for addr in addresses:
        zip_code = addr['zip_code']
        if zip_code:  # Only count non-empty zip codes
            zip_counts[zip_code] = zip_counts.get(zip_code, 0) + 1
    
    for zip_code, count in sorted(zip_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {zip_code}: {count} addresses")
    
    # Example 6: Export filtered data
    print("\n=== Export example ===")
    export_file = "ocean_addresses_07712.json"
    ocean_07712 = cache.get_addresses_by_zip('07712')
    
    import json
    with open(export_file, 'w') as f:
        json.dump(ocean_07712, f, indent=2)
    
    print(f"Exported {len(ocean_07712)} addresses with zip code 07712 to {export_file}")


if __name__ == "__main__":
    main() 