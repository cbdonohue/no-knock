#!/usr/bin/env python3
"""
Ocean Township Address Anomaly Detection
Identifies statistical anomalies and potential fraudulent entries in geocoded address data
"""

import json
import pickle
import re
from datetime import datetime
from typing import List, Dict, Set, Tuple, Optional
from pathlib import Path
from collections import defaultdict, Counter
import math
import statistics

class AddressAnomalyDetector:
    def __init__(self, cache_dir: str = "address_cache"):
        self.cache_dir = Path(cache_dir)
        self.geocoded_file = self.cache_dir / "geocoded_addresses.json"
        self.geocoded_pickle = self.cache_dir / "geocoded_addresses.pkl"
        
        # Ocean Township approximate boundaries (expanded for analysis)
        self.ocean_township_bounds = {
            'north': 40.280,   # Northern boundary
            'south': 40.220,   # Southern boundary  
            'east': -74.000,   # Eastern boundary
            'west': -74.080    # Western boundary
        }
        
        # Expected cities for Ocean Township area
        self.valid_cities = {
            'Ocean', 'Oakhurst', 'Wanamassa', 'Allenhurst', 'Elberon', 
            'Deal', 'Wayside', 'Ocean Township', 'Ocean Twp'
        }
        
        # Expected zip codes for Ocean Township area
        self.valid_zip_codes = {'07712', '07755', '07711', '07717', '07721'}
        
        # Anomaly categories
        self.anomalies = {
            'geographic_outliers': [],
            'duplicate_coordinates': [],
            'format_anomalies': [],
            'suspicious_patterns': [],
            'geocoding_failures': [],
            'temporal_anomalies': [],
            'density_anomalies': [],
            'impossible_locations': []
        }
        
        self.stats = {}
    
    def load_geocoded_addresses(self) -> List[Dict]:
        """Load geocoded addresses from cache"""
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
    
    def detect_geographic_outliers(self, addresses: List[Dict]) -> List[Dict]:
        """Detect addresses that are geographically outside expected bounds"""
        outliers = []
        
        for addr in addresses:
            if not addr.get('latitude') or not addr.get('longitude'):
                continue
                
            lat, lon = addr['latitude'], addr['longitude']
            
            # Check if outside Ocean Township bounds
            if (lat > self.ocean_township_bounds['north'] or 
                lat < self.ocean_township_bounds['south'] or
                lon > self.ocean_township_bounds['east'] or
                lon < self.ocean_township_bounds['west']):
                
                # Calculate distance from township center
                center_lat, center_lon = 40.250, -74.040
                distance = self.calculate_distance(lat, lon, center_lat, center_lon)
                
                outliers.append({
                    'address': addr['full_address'],
                    'latitude': lat,
                    'longitude': lon,
                    'distance_from_center': distance,
                    'issue': 'Outside Ocean Township bounds',
                    'severity': 'high' if distance > 20 else 'medium'
                })
        
        return outliers
    
    def detect_duplicate_coordinates(self, addresses: List[Dict]) -> List[Dict]:
        """Detect multiple addresses with identical coordinates"""
        coord_map = defaultdict(list)
        
        for addr in addresses:
            if not addr.get('latitude') or not addr.get('longitude'):
                continue
                
            # Round coordinates to 6 decimal places for comparison
            lat = round(addr['latitude'], 6)
            lon = round(addr['longitude'], 6)
            coord_key = (lat, lon)
            
            coord_map[coord_key].append(addr)
        
        duplicates = []
        for coord, addr_list in coord_map.items():
            if len(addr_list) > 1:
                # Check if addresses are actually different
                unique_addresses = set(addr['full_address'] for addr in addr_list)
                if len(unique_addresses) > 1:
                    duplicates.append({
                        'coordinate': coord,
                        'addresses': [addr['full_address'] for addr in addr_list],
                        'count': len(addr_list),
                        'issue': 'Multiple different addresses at same coordinates',
                        'severity': 'high' if len(addr_list) > 3 else 'medium'
                    })
        
        return duplicates
    
    def detect_format_anomalies(self, addresses: List[Dict]) -> List[Dict]:
        """Detect addresses with formatting anomalies"""
        anomalies = []
        
        for addr in addresses:
            issues = []
            
            # Check for missing components
            if not addr.get('street') or len(addr.get('street', '')) < 3:
                issues.append('Missing or invalid street')
            
            if not addr.get('city') or addr.get('city') not in self.valid_cities:
                issues.append(f'Invalid city: {addr.get("city")}')
            
            if not addr.get('zip_code') or addr.get('zip_code') not in self.valid_zip_codes:
                issues.append(f'Invalid zip code: {addr.get("zip_code")}')
            
            if addr.get('state') != 'NJ':
                issues.append(f'Invalid state: {addr.get("state")}')
            
            # Check for unusual characters
            full_addr = addr.get('full_address', '')
            if re.search(r'[^a-zA-Z0-9\s,.\-#/]', full_addr):
                issues.append('Contains unusual characters')
            
            # Check for very short or very long addresses
            if len(full_addr) < 10:
                issues.append('Address too short')
            elif len(full_addr) > 100:
                issues.append('Address too long')
            
            # Check for repeated words or characters
            words = full_addr.lower().split()
            if len(words) != len(set(words)):
                issues.append('Contains repeated words')
            
            if issues:
                anomalies.append({
                    'address': full_addr,
                    'issues': issues,
                    'severity': 'high' if len(issues) > 2 else 'medium'
                })
        
        return anomalies
    
    def detect_suspicious_patterns(self, addresses: List[Dict]) -> List[Dict]:
        """Detect suspicious patterns in address data"""
        patterns = []
        
        # Group addresses by street name
        street_groups = defaultdict(list)
        for addr in addresses:
            if addr.get('street'):
                # Extract street name (remove house number)
                street_name = re.sub(r'^\d+\s*', '', addr['street'])
                street_groups[street_name.lower()].append(addr)
        
        # Check for streets with unusually many addresses
        for street, addr_list in street_groups.items():
            if len(addr_list) > 20:  # Threshold for suspicious
                patterns.append({
                    'pattern': 'High address count on single street',
                    'street': street,
                    'count': len(addr_list),
                    'addresses': [addr['full_address'] for addr in addr_list[:5]],  # Sample
                    'severity': 'medium'
                })
        
        # Check for sequential house numbers (possible bulk registration)
        for street, addr_list in street_groups.items():
            if len(addr_list) > 5:
                house_numbers = []
                for addr in addr_list:
                    match = re.match(r'^(\d+)', addr.get('street', ''))
                    if match:
                        house_numbers.append(int(match.group(1)))
                
                if len(house_numbers) > 5:
                    house_numbers.sort()
                    consecutive_count = 0
                    max_consecutive = 0
                    
                    for i in range(1, len(house_numbers)):
                        if house_numbers[i] == house_numbers[i-1] + 2:  # Even numbers
                            consecutive_count += 1
                        else:
                            max_consecutive = max(max_consecutive, consecutive_count)
                            consecutive_count = 0
                    
                    max_consecutive = max(max_consecutive, consecutive_count)
                    
                    if max_consecutive > 5:
                        patterns.append({
                            'pattern': 'Sequential house numbers',
                            'street': street,
                            'consecutive_count': max_consecutive,
                            'severity': 'medium'
                        })
        
        return patterns
    
    def detect_geocoding_failures(self, addresses: List[Dict]) -> List[Dict]:
        """Analyze geocoding failures for patterns"""
        failures = []
        
        failed_addresses = [addr for addr in addresses if addr.get('geocoding_status') == 'failed']
        
        if not failed_addresses:
            return failures
        
        # Group failures by reason/pattern
        failure_patterns = defaultdict(list)
        
        for addr in failed_addresses:
            full_addr = addr.get('full_address', '')
            
            # Categorize failure types
            if 'apartment' in full_addr.lower() or 'apt' in full_addr.lower():
                failure_patterns['apartment_addresses'].append(addr)
            elif re.search(r'\d+\s*1/2', full_addr):
                failure_patterns['fractional_addresses'].append(addr)
            elif len(full_addr) < 15:
                failure_patterns['incomplete_addresses'].append(addr)
            elif not re.search(r'^\d+', full_addr):
                failure_patterns['no_house_number'].append(addr)
            else:
                failure_patterns['other_failures'].append(addr)
        
        for pattern, addr_list in failure_patterns.items():
            if len(addr_list) > 5:  # Significant number of failures
                failures.append({
                    'pattern': pattern,
                    'count': len(addr_list),
                    'sample_addresses': [addr['full_address'] for addr in addr_list[:3]],
                    'severity': 'medium'
                })
        
        return failures
    
    def detect_temporal_anomalies(self, addresses: List[Dict]) -> List[Dict]:
        """Detect temporal anomalies in address registration"""
        anomalies = []
        
        # Group addresses by cached date
        date_groups = defaultdict(list)
        for addr in addresses:
            if addr.get('cached_date'):
                # Extract date part only
                date_str = addr['cached_date'][:10]
                date_groups[date_str].append(addr)
        
        # Check for unusually high registration on single day
        for date, addr_list in date_groups.items():
            if len(addr_list) > 100:  # Threshold for suspicious bulk registration
                anomalies.append({
                    'date': date,
                    'count': len(addr_list),
                    'pattern': 'High volume registration on single day',
                    'severity': 'medium'
                })
        
        return anomalies
    
    def detect_density_anomalies(self, addresses: List[Dict]) -> List[Dict]:
        """Detect unusual density patterns"""
        anomalies = []
        
        # Create a simple grid analysis
        valid_addresses = [addr for addr in addresses if addr.get('latitude') and addr.get('longitude')]
        
        if not valid_addresses:
            return anomalies
        
        # Calculate grid bounds
        lats = [addr['latitude'] for addr in valid_addresses]
        lons = [addr['longitude'] for addr in valid_addresses]
        
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        # Create 20x20 grid
        grid_size = 20
        lat_step = (max_lat - min_lat) / grid_size
        lon_step = (max_lon - min_lon) / grid_size
        
        grid = defaultdict(list)
        
        for addr in valid_addresses:
            lat_idx = min(int((addr['latitude'] - min_lat) / lat_step), grid_size - 1)
            lon_idx = min(int((addr['longitude'] - min_lon) / lon_step), grid_size - 1)
            grid[(lat_idx, lon_idx)].append(addr)
        
        # Find cells with unusually high density
        cell_counts = [len(addresses) for addresses in grid.values()]
        if cell_counts:
            mean_count = statistics.mean(cell_counts)
            std_count = statistics.stdev(cell_counts) if len(cell_counts) > 1 else 0
            
            threshold = mean_count + 3 * std_count  # 3 standard deviations
            
            for (lat_idx, lon_idx), addr_list in grid.items():
                if len(addr_list) > threshold and len(addr_list) > 20:
                    cell_lat = min_lat + (lat_idx + 0.5) * lat_step
                    cell_lon = min_lon + (lon_idx + 0.5) * lon_step
                    
                    anomalies.append({
                        'location': (cell_lat, cell_lon),
                        'count': len(addr_list),
                        'expected_count': mean_count,
                        'pattern': 'Unusually high address density',
                        'sample_addresses': [addr['full_address'] for addr in addr_list[:3]],
                        'severity': 'medium'
                    })
        
        return anomalies
    
    def detect_impossible_locations(self, addresses: List[Dict]) -> List[Dict]:
        """Detect addresses in impossible locations (water bodies, etc.)"""
        impossible = []
        
        # Simple check for addresses in water (very rough approximation)
        # This would need more sophisticated GIS data for accuracy
        for addr in addresses:
            if not addr.get('latitude') or not addr.get('longitude'):
                continue
                
            lat, lon = addr['latitude'], addr['longitude']
            
            # Check if coordinates are in Atlantic Ocean (east of -74.0)
            if lon > -74.0 and lat > 40.0 and lat < 40.5:
                impossible.append({
                    'address': addr['full_address'],
                    'latitude': lat,
                    'longitude': lon,
                    'issue': 'Coordinates appear to be in Atlantic Ocean',
                    'severity': 'high'
                })
        
        return impossible
    
    def run_all_detections(self) -> Dict:
        """Run all anomaly detection algorithms"""
        print("🔍 Starting anomaly detection analysis...")
        
        addresses = self.load_geocoded_addresses()
        if not addresses:
            return {}
        
        print(f"📊 Analyzing {len(addresses)} geocoded addresses")
        
        # Run all detection algorithms
        print("  🌍 Detecting geographic outliers...")
        self.anomalies['geographic_outliers'] = self.detect_geographic_outliers(addresses)
        
        print("  📍 Detecting duplicate coordinates...")
        self.anomalies['duplicate_coordinates'] = self.detect_duplicate_coordinates(addresses)
        
        print("  📝 Detecting format anomalies...")
        self.anomalies['format_anomalies'] = self.detect_format_anomalies(addresses)
        
        print("  🔍 Detecting suspicious patterns...")
        self.anomalies['suspicious_patterns'] = self.detect_suspicious_patterns(addresses)
        
        print("  ❌ Analyzing geocoding failures...")
        self.anomalies['geocoding_failures'] = self.detect_geocoding_failures(addresses)
        
        print("  📅 Detecting temporal anomalies...")
        self.anomalies['temporal_anomalies'] = self.detect_temporal_anomalies(addresses)
        
        print("  🗺️ Detecting density anomalies...")
        self.anomalies['density_anomalies'] = self.detect_density_anomalies(addresses)
        
        print("  🌊 Detecting impossible locations...")
        self.anomalies['impossible_locations'] = self.detect_impossible_locations(addresses)
        
        # Calculate summary statistics
        self.calculate_summary_stats(addresses)
        
        return self.anomalies
    
    def calculate_summary_stats(self, addresses: List[Dict]):
        """Calculate summary statistics about anomalies"""
        total_addresses = len(addresses)
        geocoded_addresses = len([addr for addr in addresses if addr.get('latitude')])
        
        # Count anomalies by severity
        high_severity = 0
        medium_severity = 0
        
        for category, anomaly_list in self.anomalies.items():
            for anomaly in anomaly_list:
                if anomaly.get('severity') == 'high':
                    high_severity += 1
                elif anomaly.get('severity') == 'medium':
                    medium_severity += 1
        
        self.stats = {
            'total_addresses': total_addresses,
            'geocoded_addresses': geocoded_addresses,
            'total_anomalies': sum(len(anomalies) for anomalies in self.anomalies.values()),
            'high_severity_count': high_severity,
            'medium_severity_count': medium_severity,
            'anomaly_categories': {cat: len(anomalies) for cat, anomalies in self.anomalies.items()},
            'anomaly_rate': sum(len(anomalies) for anomalies in self.anomalies.values()) / total_addresses * 100
        }
    
    def generate_report(self, save_to_file: bool = True) -> str:
        """Generate a comprehensive anomaly detection report"""
        report = []
        
        report.append("=" * 60)
        report.append("🔍 OCEAN TOWNSHIP ADDRESS ANOMALY DETECTION REPORT")
        report.append("=" * 60)
        
        report.append(f"\n📊 SUMMARY STATISTICS")
        report.append(f"Total addresses analyzed: {self.stats['total_addresses']:,}")
        report.append(f"Successfully geocoded: {self.stats['geocoded_addresses']:,}")
        report.append(f"Total anomalies found: {self.stats['total_anomalies']:,}")
        report.append(f"Anomaly rate: {self.stats['anomaly_rate']:.1f}%")
        report.append(f"High severity issues: {self.stats['high_severity_count']:,}")
        report.append(f"Medium severity issues: {self.stats['medium_severity_count']:,}")
        
        report.append(f"\n🏆 ANOMALY CATEGORIES")
        for category, count in self.stats['anomaly_categories'].items():
            if count > 0:
                report.append(f"  {category.replace('_', ' ').title()}: {count:,}")
        
        # Detailed anomaly reports
        for category, anomalies in self.anomalies.items():
            if not anomalies:
                continue
                
            report.append(f"\n🔍 {category.replace('_', ' ').upper()}")
            report.append("-" * 50)
            
            for i, anomaly in enumerate(anomalies[:10]):  # Show first 10 of each type
                report.append(f"\n{i+1}. Severity: {anomaly.get('severity', 'unknown').upper()}")
                
                if 'address' in anomaly:
                    report.append(f"   Address: {anomaly['address']}")
                
                if 'issue' in anomaly:
                    report.append(f"   Issue: {anomaly['issue']}")
                
                if 'pattern' in anomaly:
                    report.append(f"   Pattern: {anomaly['pattern']}")
                
                if 'count' in anomaly:
                    report.append(f"   Count: {anomaly['count']}")
                
                if 'latitude' in anomaly and 'longitude' in anomaly:
                    report.append(f"   Coordinates: ({anomaly['latitude']:.6f}, {anomaly['longitude']:.6f})")
                
                if 'distance_from_center' in anomaly:
                    report.append(f"   Distance from center: {anomaly['distance_from_center']:.1f} miles")
                
                if 'addresses' in anomaly:
                    report.append(f"   Affected addresses: {len(anomaly['addresses'])}")
                    for addr in anomaly['addresses'][:3]:
                        report.append(f"     • {addr}")
                
                if 'sample_addresses' in anomaly:
                    report.append(f"   Sample addresses:")
                    for addr in anomaly['sample_addresses']:
                        report.append(f"     • {addr}")
            
            if len(anomalies) > 10:
                report.append(f"\n   ... and {len(anomalies) - 10} more anomalies in this category")
        
        report.append(f"\n" + "=" * 60)
        report.append(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"=" * 60)
        
        report_text = "\n".join(report)
        
        if save_to_file:
            report_file = self.cache_dir / "anomaly_report.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"\n📄 Report saved to: {report_file}")
        
        return report_text
    
    def export_anomalies_json(self) -> str:
        """Export anomalies to JSON format"""
        export_data = {
            'summary': self.stats,
            'anomalies': self.anomalies,
            'generated_at': datetime.now().isoformat()
        }
        
        json_file = self.cache_dir / "anomalies.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Anomalies exported to: {json_file}")
        return str(json_file)


def main():
    """Main function to run anomaly detection"""
    detector = AddressAnomalyDetector()
    
    # Run all detections
    anomalies = detector.run_all_detections()
    
    if not anomalies:
        print("❌ No data to analyze. Make sure geocoded addresses exist.")
        return
    
    # Generate and display report
    print("\n" + "=" * 60)
    print("🎯 ANOMALY DETECTION COMPLETE")
    print("=" * 60)
    
    report = detector.generate_report(save_to_file=True)
    detector.export_anomalies_json()
    
    # Print summary
    print(f"\n📊 ANALYSIS SUMMARY:")
    print(f"Total addresses: {detector.stats['total_addresses']:,}")
    print(f"Anomalies found: {detector.stats['total_anomalies']:,}")
    print(f"Anomaly rate: {detector.stats['anomaly_rate']:.1f}%")
    print(f"High severity: {detector.stats['high_severity_count']:,}")
    print(f"Medium severity: {detector.stats['medium_severity_count']:,}")
    
    print(f"\n📁 Files created:")
    print(f"  📄 address_cache/anomaly_report.txt - Detailed report")
    print(f"  📊 address_cache/anomalies.json - Machine-readable data")
    
    print(f"\n🔍 Next steps:")
    print(f"  • Review the detailed report for specific issues")
    print(f"  • Investigate high-severity anomalies first")
    print(f"  • Consider data cleanup or validation improvements")
    print(f"  • Use JSON export for further analysis or visualization")


if __name__ == "__main__":
    main() 