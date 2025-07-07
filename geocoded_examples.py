#!/usr/bin/env python3
"""
Examples of using geocoded Ocean Township address data
Demonstrates various analysis and visualization capabilities
"""

import json
import pickle
from pathlib import Path
from typing import List, Dict, Tuple
import math

class GeocodedAnalyzer:
    def __init__(self, cache_dir: str = "address_cache"):
        self.cache_dir = Path(cache_dir)
        self.geocoded_file = self.cache_dir / "geocoded_addresses.json"
        self.geocoded_pickle = self.cache_dir / "geocoded_addresses.pkl"
    
    def load_geocoded_addresses(self) -> List[Dict]:
        """Load geocoded addresses"""
        try:
            if self.geocoded_pickle.exists():
                with open(self.geocoded_pickle, 'rb') as f:
                    return pickle.load(f)
            elif self.geocoded_file.exists():
                with open(self.geocoded_file, 'r') as f:
                    return json.load(f)
            else:
                print("❌ No geocoded addresses found. Run geocode_addresses.py first.")
                return []
        except Exception as e:
            print(f"❌ Error loading geocoded addresses: {e}")
            return []
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in miles using Haversine formula"""
        R = 3959  # Earth's radius in miles
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def get_basic_stats(self) -> Dict:
        """Get basic statistics about geocoded addresses"""
        addresses = self.load_geocoded_addresses()
        if not addresses:
            return {}
        
        total = len(addresses)
        geocoded = [a for a in addresses if a.get('latitude') is not None]
        failed = [a for a in addresses if a.get('latitude') is None]
        
        if not geocoded:
            return {
                'total_addresses': total,
                'geocoded_count': 0,
                'failed_count': len(failed),
                'success_rate': 0
            }
        
        # Extract coordinates
        lats = [a['latitude'] for a in geocoded]
        lons = [a['longitude'] for a in geocoded]
        
        # Calculate bounding box
        bbox = {
            'north': max(lats),
            'south': min(lats),
            'east': max(lons),
            'west': min(lons)
        }
        
        # Calculate center point
        center = {
            'latitude': sum(lats) / len(lats),
            'longitude': sum(lons) / len(lons)
        }
        
        # Calculate area dimensions
        width_miles = self.calculate_distance(
            center['latitude'], bbox['west'],
            center['latitude'], bbox['east']
        )
        height_miles = self.calculate_distance(
            bbox['south'], center['longitude'],
            bbox['north'], center['longitude']
        )
        
        return {
            'total_addresses': total,
            'geocoded_count': len(geocoded),
            'failed_count': len(failed),
            'success_rate': len(geocoded) / total * 100,
            'bounding_box': bbox,
            'center_point': center,
            'area_dimensions': {
                'width_miles': width_miles,
                'height_miles': height_miles
            }
        }
    
    def find_addresses_near_point(self, target_lat: float, target_lon: float, 
                                  radius_miles: float = 1.0) -> List[Dict]:
        """Find addresses within a radius of a target point"""
        addresses = self.load_geocoded_addresses()
        nearby = []
        
        for addr in addresses:
            if addr.get('latitude') is None:
                continue
                
            distance = self.calculate_distance(
                target_lat, target_lon,
                addr['latitude'], addr['longitude']
            )
            
            if distance <= radius_miles:
                addr_copy = addr.copy()
                addr_copy['distance_miles'] = distance
                nearby.append(addr_copy)
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance_miles'])
        return nearby
    
    def get_density_analysis(self, grid_size: int = 10) -> Dict:
        """Analyze address density using a grid"""
        addresses = self.load_geocoded_addresses()
        geocoded = [a for a in addresses if a.get('latitude') is not None]
        
        if not geocoded:
            return {}
        
        # Get bounding box
        lats = [a['latitude'] for a in geocoded]
        lons = [a['longitude'] for a in geocoded]
        
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        # Create grid
        lat_step = (max_lat - min_lat) / grid_size
        lon_step = (max_lon - min_lon) / grid_size
        
        grid = {}
        for i in range(grid_size):
            for j in range(grid_size):
                grid[(i, j)] = []
        
        # Assign addresses to grid cells
        for addr in geocoded:
            lat_idx = min(int((addr['latitude'] - min_lat) / lat_step), grid_size - 1)
            lon_idx = min(int((addr['longitude'] - min_lon) / lon_step), grid_size - 1)
            grid[(lat_idx, lon_idx)].append(addr)
        
        # Calculate density stats
        cell_counts = [len(addresses) for addresses in grid.values()]
        max_density = max(cell_counts)
        avg_density = sum(cell_counts) / len(cell_counts)
        
        # Find highest density cell
        max_cell = max(grid.items(), key=lambda x: len(x[1]))
        max_cell_coords = max_cell[0]
        max_cell_lat = min_lat + (max_cell_coords[0] + 0.5) * lat_step
        max_cell_lon = min_lon + (max_cell_coords[1] + 0.5) * lon_step
        
        return {
            'grid_size': grid_size,
            'total_cells': grid_size * grid_size,
            'max_density': max_density,
            'avg_density': avg_density,
            'highest_density_cell': {
                'latitude': max_cell_lat,
                'longitude': max_cell_lon,
                'address_count': len(max_cell[1]),
                'sample_addresses': [a['full_address'] for a in max_cell[1][:3]]
            }
        }
    
    def export_for_mapping(self, output_file: str = "addresses_for_mapping.csv"):
        """Export geocoded addresses in CSV format for mapping tools"""
        addresses = self.load_geocoded_addresses()
        geocoded = [a for a in addresses if a.get('latitude') is not None]
        
        if not geocoded:
            print("❌ No geocoded addresses to export")
            return
        
        try:
            import csv
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'full_address', 'street', 'city', 'state', 'zip_code',
                    'latitude', 'longitude', 'geocoding_service'
                ]
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for addr in geocoded:
                    row = {field: addr.get(field, '') for field in fieldnames}
                    writer.writerow(row)
            
            print(f"📊 Exported {len(geocoded)} geocoded addresses to {output_file}")
            print(f"💡 You can import this CSV into Google Maps, QGIS, or other mapping tools")
            
        except Exception as e:
            print(f"❌ Error exporting CSV: {e}")
    
    def generate_kml(self, output_file: str = "ocean_township_addresses.kml"):
        """Generate KML file for Google Earth/Maps"""
        addresses = self.load_geocoded_addresses()
        geocoded = [a for a in addresses if a.get('latitude') is not None]
        
        if not geocoded:
            print("❌ No geocoded addresses to export")
            return
        
        try:
            kml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Ocean Township No Knock Registry Addresses</name>
    <description>Addresses from the Ocean Township No Knock Registry</description>
    
    <Style id="address-icon">
      <IconStyle>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/shapes/homegardenbusiness.png</href>
        </Icon>
      </IconStyle>
    </Style>
'''
            
            for addr in geocoded:
                lat = addr['latitude']
                lon = addr['longitude']
                address = addr['full_address'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                
                kml_content += f'''
    <Placemark>
      <name>{address}</name>
      <styleUrl>#address-icon</styleUrl>
      <Point>
        <coordinates>{lon},{lat},0</coordinates>
      </Point>
    </Placemark>'''
            
            kml_content += '''
  </Document>
</kml>'''
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(kml_content)
            
            print(f"🗺️  Generated KML file: {output_file}")
            print(f"💡 You can open this in Google Earth or import into Google Maps")
            
        except Exception as e:
            print(f"❌ Error generating KML: {e}")


def main():
    """Demonstrate various geocoded address analysis examples"""
    analyzer = GeocodedAnalyzer()
    
    print("🌍 Ocean Township Geocoded Address Analysis")
    print("=" * 50)
    
    # Basic statistics
    print("\n📊 Basic Statistics:")
    stats = analyzer.get_basic_stats()
    if stats:
        print(f"  Total addresses: {stats['total_addresses']:,}")
        print(f"  Successfully geocoded: {stats['geocoded_count']:,}")
        print(f"  Failed geocoding: {stats['failed_count']:,}")
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        
        if 'center_point' in stats:
            center = stats['center_point']
            print(f"\n📍 Geographic Center:")
            print(f"  Latitude: {center['latitude']:.6f}")
            print(f"  Longitude: {center['longitude']:.6f}")
            
            dimensions = stats['area_dimensions']
            print(f"\n📏 Area Dimensions:")
            print(f"  Width: {dimensions['width_miles']:.1f} miles")
            print(f"  Height: {dimensions['height_miles']:.1f} miles")
    
    # Density analysis
    print("\n🔥 Density Analysis:")
    density = analyzer.get_density_analysis()
    if density:
        print(f"  Grid size: {density['grid_size']}x{density['grid_size']}")
        print(f"  Maximum addresses per cell: {density['max_density']}")
        print(f"  Average addresses per cell: {density['avg_density']:.1f}")
        
        hotspot = density['highest_density_cell']
        print(f"\n🎯 Highest Density Area:")
        print(f"  Location: ({hotspot['latitude']:.6f}, {hotspot['longitude']:.6f})")
        print(f"  Address count: {hotspot['address_count']}")
        print(f"  Sample addresses:")
        for addr in hotspot['sample_addresses']:
            print(f"    • {addr}")
    
    # Example: Find addresses near Ocean Township Municipal Building
    # (approximate coordinates)
    print("\n🏛️  Addresses near Municipal Building:")
    municipal_lat, municipal_lon = 40.2535, -74.0287  # Approximate coordinates
    nearby = analyzer.find_addresses_near_point(municipal_lat, municipal_lon, 0.5)  # Within 0.5 miles
    
    if nearby:
        print(f"  Found {len(nearby)} addresses within 0.5 miles:")
        for addr in nearby[:5]:  # Show first 5
            print(f"    • {addr['full_address']} ({addr['distance_miles']:.2f} miles)")
        if len(nearby) > 5:
            print(f"    ... and {len(nearby) - 5} more")
    else:
        print("  No addresses found near those coordinates")
    
    # Export options
    print("\n💾 Export Options:")
    print("  Generating export files...")
    
    analyzer.export_for_mapping("ocean_township_addresses.csv")
    analyzer.generate_kml("ocean_township_addresses.kml")
    
    print("\n📱 Next Steps:")
    print("  • Import CSV into Google Sheets for analysis")
    print("  • Open KML in Google Earth for 3D visualization")
    print("  • Use coordinates for custom mapping applications")
    print("  • Analyze patterns for urban planning insights")


if __name__ == "__main__":
    main() 