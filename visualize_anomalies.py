#!/usr/bin/env python3
"""
Visualize and analyze anomalies found in Ocean Township address data
"""

import json
from pathlib import Path
from collections import Counter
import statistics

def analyze_anomalies():
    """Analyze and visualize the anomalies found"""
    
    # Load anomaly data
    anomaly_file = Path("address_cache/anomalies.json")
    if not anomaly_file.exists():
        print("❌ No anomaly data found. Run anomaly_detection.py first.")
        return
    
    with open(anomaly_file, 'r') as f:
        data = json.load(f)
    
    anomalies = data['anomalies']
    summary = data['summary']
    
    print("🔍 OCEAN TOWNSHIP ANOMALY ANALYSIS")
    print("=" * 50)
    
    # Summary overview
    print(f"\n📊 OVERVIEW:")
    print(f"Total addresses: {summary['total_addresses']:,}")
    print(f"Total anomalies: {summary['total_anomalies']:,}")
    print(f"Anomaly rate: {summary['anomaly_rate']:.1f}%")
    print(f"High severity: {summary['high_severity_count']:,}")
    print(f"Medium severity: {summary['medium_severity_count']:,}")
    
    # Geographic outliers analysis
    geo_outliers = anomalies['geographic_outliers']
    if geo_outliers:
        print(f"\n🌍 GEOGRAPHIC OUTLIERS ({len(geo_outliers)} found):")
        
        distances = [outlier['distance_from_center'] for outlier in geo_outliers]
        print(f"  Average distance from center: {statistics.mean(distances):.1f} miles")
        print(f"  Maximum distance: {max(distances):.1f} miles")
        print(f"  Minimum distance: {min(distances):.1f} miles")
        
        print(f"\n  📍 Furthest outliers:")
        sorted_outliers = sorted(geo_outliers, key=lambda x: x['distance_from_center'], reverse=True)
        for i, outlier in enumerate(sorted_outliers[:5], 1):
            print(f"    {i}. {outlier['address']} ({outlier['distance_from_center']:.1f} miles)")
    
    # Duplicate coordinates analysis
    duplicates = anomalies['duplicate_coordinates']
    if duplicates:
        print(f"\n📍 DUPLICATE COORDINATES ({len(duplicates)} groups):")
        
        total_duplicate_addresses = sum(dup['count'] for dup in duplicates)
        print(f"  Total addresses affected: {total_duplicate_addresses}")
        
        largest_groups = sorted(duplicates, key=lambda x: x['count'], reverse=True)
        print(f"\n  🏆 Largest duplicate groups:")
        for i, dup in enumerate(largest_groups[:5], 1):
            print(f"    {i}. {dup['count']} addresses at same coordinates:")
            for addr in dup['addresses'][:3]:
                print(f"       • {addr}")
            if len(dup['addresses']) > 3:
                print(f"       • ... and {len(dup['addresses']) - 3} more")
    
    # Format anomalies analysis
    format_anomalies = anomalies['format_anomalies']
    if format_anomalies:
        print(f"\n📝 FORMAT ANOMALIES ({len(format_anomalies)} addresses):")
        
        # Count issue types
        issue_counts = Counter()
        for anomaly in format_anomalies:
            for issue in anomaly['issues']:
                issue_counts[issue] += 1
        
        print(f"  📊 Most common issues:")
        for issue, count in issue_counts.most_common(10):
            print(f"    • {issue}: {count:,} addresses")
    
    # Suspicious patterns analysis
    suspicious = anomalies['suspicious_patterns']
    if suspicious:
        print(f"\n🔍 SUSPICIOUS PATTERNS ({len(suspicious)} patterns):")
        for pattern in suspicious:
            print(f"  • {pattern['pattern']}: {pattern.get('count', 'N/A')}")
            if 'street' in pattern:
                print(f"    Street: {pattern['street']}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if geo_outliers:
        print(f"  🌍 Geographic Issues:")
        print(f"    • Review {len(geo_outliers)} addresses outside Ocean Township bounds")
        print(f"    • Verify addresses >20 miles away are legitimate registrations")
        print(f"    • Consider geocoding service accuracy for distant addresses")
    
    if duplicates:
        print(f"  📍 Data Quality:")
        print(f"    • Standardize address formatting to prevent duplicates")
        print(f"    • Implement deduplication process for similar addresses")
        print(f"    • Review {total_duplicate_addresses} potentially duplicate registrations")
    
    if len(format_anomalies) > summary['total_addresses'] * 0.5:
        print(f"  📝 Format Standardization:")
        print(f"    • High format anomaly rate ({len(format_anomalies)/summary['total_addresses']*100:.1f}%)")
        print(f"    • Implement address validation and standardization")
        print(f"    • Update valid city/zip code lists")
    
    print(f"\n🎯 PRIORITY ACTIONS:")
    high_priority = [
        outlier for outlier in geo_outliers 
        if outlier.get('severity') == 'high'
    ]
    if high_priority:
        print(f"  1. Investigate {len(high_priority)} high-severity geographic outliers")
    
    large_duplicates = [
        dup for dup in duplicates 
        if dup['count'] > 2
    ]
    if large_duplicates:
        print(f"  2. Review {len(large_duplicates)} coordinate groups with 3+ addresses")
    
    print(f"  3. Implement address standardization to reduce format anomalies")
    
    # Create simple summary report
    create_summary_report(summary, anomalies)

def create_summary_report(summary, anomalies):
    """Create a simplified summary report"""
    
    report_lines = [
        "# Ocean Township Address Quality Report",
        "",
        f"**Analysis Date:** {summary.get('generated_at', 'Unknown')[:19].replace('T', ' ')}",
        f"**Total Addresses:** {summary['total_addresses']:,}",
        f"**Data Quality Score:** {100 - summary['anomaly_rate']:.1f}/100",
        "",
        "## Issues Found:",
        ""
    ]
    
    for category, count in summary['anomaly_categories'].items():
        if count > 0:
            severity = "🚨" if count > summary['total_addresses'] * 0.1 else "⚠️"
            report_lines.append(f"- {severity} **{category.replace('_', ' ').title()}**: {count:,} issues")
    
    report_lines.extend([
        "",
        "## Recommendations:",
        "",
        "1. **Priority**: Review geographic outliers (addresses >20 miles away)",
        "2. **Data Quality**: Implement address deduplication process", 
        "3. **Standardization**: Create consistent address formatting rules",
        "4. **Validation**: Add geocoding verification for suspicious coordinates",
        "",
        "## Next Steps:",
        "",
        "- Review detailed anomaly report: `address_cache/anomaly_report.txt`",
        "- Investigate high-severity issues first",
        "- Consider implementing address validation in data collection process"
    ])
    
    # Save summary report
    summary_file = Path("address_cache/quality_summary.md")
    with open(summary_file, 'w') as f:
        f.write('\n'.join(report_lines))
    
    print(f"\n📄 Summary report saved: {summary_file}")

if __name__ == "__main__":
    analyze_anomalies() 