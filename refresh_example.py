#!/usr/bin/env python3
"""
Example demonstrating the refresh functionality of the Ocean Township Address Cache
"""

from cache_addresses import AddressCache
import time

def main():
    # Initialize the cache
    cache = AddressCache()
    
    print("=== Ocean Township No Knock Registry - Live Data Demo ===\n")
    
    # Show current cached data
    current_addresses = cache.load_addresses()
    print(f"Currently cached addresses: {len(current_addresses)}")
    
    if current_addresses:
        first_addr = current_addresses[0]
        print(f"Sample address: {first_addr['full_address']}")
        print(f"Last cached: {first_addr['cached_date'][:19].replace('T', ' ')}")
    
    print("\n" + "="*50)
    print("Refreshing with live data from website...")
    print("="*50)
    
    # Refresh the cache with live data
    success = cache.refresh_cache()
    
    if success:
        # Show updated data
        new_addresses = cache.load_addresses()
        print(f"\n✅ Successfully refreshed!")
        print(f"Total addresses now: {len(new_addresses)}")
        
        # Show statistics
        stats = cache.get_stats()
        print(f"\nLive Data Statistics:")
        print(f"• Total addresses: {stats['total_addresses']:,}")
        print(f"• Unique cities: {stats['unique_cities']}")
        print(f"• Unique zip codes: {stats['unique_zip_codes']}")
        
        print(f"\nTop 3 zip codes:")
        zip_counts = [(zip_code, count) for zip_code, count in stats['zip_code_counts'].items() if zip_code]
        for zip_code, count in sorted(zip_counts, key=lambda x: x[1], reverse=True)[:3]:
            print(f"  • {zip_code}: {count:,} addresses")
        
        print(f"\nSample of newest data:")
        for i, addr in enumerate(new_addresses[:3]):
            print(f"  {i+1}. {addr['full_address']}")
        
        print(f"\n💾 Data saved to:")
        print(f"  • JSON: {cache.json_file}")
        print(f"  • Pickle: {cache.pickle_file}")
        
    else:
        print("❌ Failed to refresh cache")
    
    print(f"\n🌐 Data source: https://webgeo.co/prod1/portal/portal.jsp?c=3668658&p=557207238&g=557207303")
    print(f"📅 This data is always current from the Ocean Township No Knock Registry")


if __name__ == "__main__":
    main() 