#!/usr/bin/env python3
"""
Ocean Township Address Pipeline - Simplified Workflow
A comprehensive pipeline to automate the entire process of collecting, geocoding, analyzing, and exporting addresses.
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Import the existing modules
try:
    from cache_addresses import AddressCache
    from geocode_addresses import AddressGeocoder
    from geocoded_examples import GeocodedAnalyzer
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all the required modules are in the same directory.")
    sys.exit(1)


class AddressPipeline:
    """Main pipeline class that orchestrates the entire workflow"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the pipeline with configuration options"""
        self.config = config or {}
        self.setup_logging()
        self.cache = AddressCache()
        self.geocoder = AddressGeocoder()
        self.analyzer = GeocodedAnalyzer()
        
        # Pipeline state tracking
        self.pipeline_state = {
            'started_at': datetime.now().isoformat(),
            'steps_completed': [],
            'current_step': None,
            'errors': []
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = self.config.get('log_level', 'INFO')
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('pipeline.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log_step(self, step_name: str, status: str = "started"):
        """Log pipeline step progress"""
        if status == "started":
            self.pipeline_state['current_step'] = step_name
            self.logger.info(f"🚀 Starting step: {step_name}")
        elif status == "completed":
            self.pipeline_state['steps_completed'].append(step_name)
            self.pipeline_state['current_step'] = None
            self.logger.info(f"✅ Completed step: {step_name}")
        elif status == "failed":
            self.pipeline_state['errors'].append(f"Failed step: {step_name}")
            self.logger.error(f"❌ Failed step: {step_name}")
    
    def run_full_pipeline(self, google_api_key: Optional[str] = None, 
                         skip_collection: bool = False,
                         skip_geocoding: bool = False,
                         export_formats: Optional[List[str]] = None) -> Dict:
        """Run the complete pipeline from start to finish"""
        
        self.logger.info("🌊 Starting Ocean Township Address Pipeline")
        self.logger.info("=" * 60)
        
        results = {
            'success': True,
            'steps_completed': [],
            'total_addresses': 0,
            'geocoded_addresses': 0,
            'export_files': [],
            'errors': []
        }
        
        try:
            # Step 1: Address Collection
            if not skip_collection:
                collection_result = self.run_address_collection()
                results['steps_completed'].append('collection')
                results['total_addresses'] = collection_result['total_addresses']
            
            # Step 2: Geocoding
            if not skip_geocoding:
                geocoding_result = self.run_geocoding(google_api_key)
                results['steps_completed'].append('geocoding')
                results['geocoded_addresses'] = geocoding_result['geocoded_count']
            
            # Step 3: Analysis and Export
            export_result = self.run_analysis_and_export(export_formats or ['csv', 'kml'])
            results['steps_completed'].append('analysis_export')
            results['export_files'] = export_result['export_files']
            
            # Step 4: Generate Summary Report
            summary_result = self.generate_summary_report()
            results['steps_completed'].append('summary_report')
            results['summary_file'] = summary_result['summary_file']
            
            self.logger.info("🎉 Pipeline completed successfully!")
            
        except Exception as e:
            results['success'] = False
            results['errors'].append(str(e))
            self.logger.error(f"❌ Pipeline failed: {e}")
            raise
        
        return results
    
    def run_address_collection(self) -> Dict:
        """Step 1: Collect addresses from the website"""
        self.log_step("Address Collection")
        
        try:
            # Check if we already have recent data
            if self.config.get('use_cached_addresses', True):
                addresses = self.cache.load_addresses()
                if addresses:
                    self.logger.info(f"📁 Using cached addresses: {len(addresses)} found")
                    self.log_step("Address Collection", "completed")
                    return {'total_addresses': len(addresses)}
            
            # Fetch fresh data from website
            self.logger.info("🌐 Fetching addresses from Ocean Township website...")
            self.cache.refresh_cache()
            addresses = self.cache.load_addresses()
            
            self.logger.info(f"📊 Collected {len(addresses)} addresses")
            self.log_step("Address Collection", "completed")
            
            return {'total_addresses': len(addresses)}
            
        except Exception as e:
            self.log_step("Address Collection", "failed")
            raise Exception(f"Address collection failed: {e}")
    
    def run_geocoding(self, google_api_key: Optional[str] = None) -> Dict:
        """Step 2: Geocode addresses to get coordinates"""
        self.log_step("Geocoding")
        
        try:
            # Configure geocoding service
            service_name = "Google Maps" if google_api_key else "Nominatim (OpenStreetMap)"
            self.logger.info(f"🗺️  Using {service_name} for geocoding")
            
            # Check if we should resume existing geocoding
            if self.config.get('resume_geocoding', True):
                stats = self.geocoder.get_geocoded_stats()
                if stats and stats['geocoded_count'] > 0:
                    self.logger.info(f"📍 Resuming geocoding from {stats['geocoded_count']} existing coordinates")
            
            # Run geocoding
            if google_api_key:
                self.geocoder.geocode_all_addresses(google_api_key=google_api_key)
            else:
                self.geocoder.geocode_all_addresses()
            
            # Get final statistics
            final_stats = self.geocoder.get_geocoded_stats()
            self.logger.info(f"🎯 Geocoding complete: {final_stats['geocoded_count']} addresses")
            self.logger.info(f"📈 Success rate: {final_stats['success_rate']:.1f}%")
            
            self.log_step("Geocoding", "completed")
            
            return {
                'geocoded_count': final_stats['geocoded_count'],
                'success_rate': final_stats['success_rate']
            }
            
        except Exception as e:
            self.log_step("Geocoding", "failed")
            raise Exception(f"Geocoding failed: {e}")
    
    def run_analysis_and_export(self, export_formats: List[str]) -> Dict:
        """Step 3: Analyze data and export in requested formats"""
        self.log_step("Analysis and Export")
        
        try:
            export_files = []
            
            # Generate basic analysis
            self.logger.info("📊 Generating geographic analysis...")
            stats = self.analyzer.get_basic_stats()
            
            self.logger.info(f"🏠 Total addresses: {stats['total_addresses']:,}")
            self.logger.info(f"🎯 Geographic center: {stats['center_point']}")
            self.logger.info(f"📏 Coverage area: {stats['area_dimensions']['width_miles']:.1f} × {stats['area_dimensions']['height_miles']:.1f} miles")
            
            # Export in requested formats
            for format_type in export_formats:
                try:
                    if format_type.lower() == 'csv':
                        filename = "ocean_township_addresses.csv"
                        self.analyzer.export_for_mapping(filename)
                        export_files.append(filename)
                        self.logger.info(f"📄 Exported CSV: {filename}")
                    
                    elif format_type.lower() == 'kml':
                        filename = "ocean_township_addresses.kml"
                        self.analyzer.generate_kml(filename)
                        export_files.append(filename)
                        self.logger.info(f"🌍 Exported KML: {filename}")
                    
                    elif format_type.lower() == 'json':
                        filename = "ocean_township_addresses_analysis.json"
                        analysis_data = {
                            'statistics': stats,
                            'density_analysis': self.analyzer.get_density_analysis(),
                            'generated_at': datetime.now().isoformat()
                        }
                        with open(filename, 'w') as f:
                            json.dump(analysis_data, f, indent=2)
                        export_files.append(filename)
                        self.logger.info(f"📋 Exported JSON analysis: {filename}")
                        
                except Exception as e:
                    self.logger.warning(f"⚠️  Failed to export {format_type}: {e}")
            
            self.log_step("Analysis and Export", "completed")
            
            return {'export_files': export_files}
            
        except Exception as e:
            self.log_step("Analysis and Export", "failed")
            raise Exception(f"Analysis and export failed: {e}")
    
    def generate_summary_report(self) -> Dict:
        """Step 4: Generate a comprehensive summary report"""
        self.log_step("Summary Report Generation")
        
        try:
            # Collect all pipeline information
            stats = self.analyzer.get_basic_stats()
            geocoding_stats = self.geocoder.get_geocoded_stats()
            cache_stats = self.cache.get_stats()
            
            # Create summary report
            summary = {
                'pipeline_execution': {
                    'started_at': self.pipeline_state['started_at'],
                    'completed_at': datetime.now().isoformat(),
                    'steps_completed': self.pipeline_state['steps_completed'],
                    'errors': self.pipeline_state['errors']
                },
                'address_collection': {
                    'total_addresses': cache_stats['total_addresses'],
                    'unique_cities': cache_stats['unique_cities'],
                    'unique_zip_codes': cache_stats['unique_zip_codes']
                },
                'geocoding_results': {
                    'geocoded_count': geocoding_stats['geocoded_count'],
                    'success_rate': geocoding_stats['success_rate'],
                    'service_used': geocoding_stats.get('service_used', 'nominatim')
                },
                'geographic_analysis': {
                    'center_point': stats['center_point'],
                    'area_dimensions': stats['area_dimensions'],
                    'bounding_box': stats['bounding_box']
                },
                'recommendations': self.generate_recommendations(stats, geocoding_stats)
            }
            
            # Save summary report
            summary_file = f"pipeline_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            self.logger.info(f"📋 Generated summary report: {summary_file}")
            self.log_step("Summary Report Generation", "completed")
            
            return {'summary_file': summary_file}
            
        except Exception as e:
            self.log_step("Summary Report Generation", "failed")
            raise Exception(f"Summary report generation failed: {e}")
    
    def generate_recommendations(self, stats: Dict, geocoding_stats: Dict) -> List[str]:
        """Generate recommendations based on pipeline results"""
        recommendations = []
        
        # Geocoding success rate recommendations
        success_rate = geocoding_stats.get('success_rate', 0)
        if success_rate < 85:
            recommendations.append("Consider using Google Maps API for better geocoding accuracy")
        
        # Data freshness recommendations
        recommendations.append("Run pipeline weekly to keep data current")
        
        # Export format recommendations
        recommendations.append("Use CSV exports for GIS software like QGIS")
        recommendations.append("Use KML exports for Google Earth visualization")
        
        return recommendations
    
    def run_quick_analysis(self) -> Dict:
        """Run a quick analysis without full pipeline"""
        self.logger.info("🔍 Running quick analysis...")
        
        try:
            # Load existing data
            addresses = self.cache.load_addresses()
            if not addresses:
                raise Exception("No addresses found. Run full pipeline first.")
            
            stats = self.analyzer.get_basic_stats()
            geocoding_stats = self.geocoder.get_geocoded_stats()
            
            # Display key metrics
            self.logger.info(f"📊 Quick Analysis Results:")
            self.logger.info(f"   Total addresses: {len(addresses):,}")
            self.logger.info(f"   Geocoded: {geocoding_stats['geocoded_count']:,}")
            self.logger.info(f"   Success rate: {geocoding_stats['success_rate']:.1f}%")
            self.logger.info(f"   Geographic center: {stats['center_point']}")
            
            return {
                'total_addresses': len(addresses),
                'geocoded_count': geocoding_stats['geocoded_count'],
                'success_rate': geocoding_stats['success_rate']
            }
            
        except Exception as e:
            self.logger.error(f"Quick analysis failed: {e}")
            raise


def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(
        description="Ocean Township Address Pipeline - Simplified Workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline with free geocoding
  python pipeline.py --full

  # Run with Google Maps API for better accuracy
  python pipeline.py --full --google-api-key YOUR_API_KEY

  # Skip address collection (use cached data)
  python pipeline.py --full --skip-collection

  # Export only specific formats
  python pipeline.py --full --export-formats csv kml

  # Quick analysis of existing data
  python pipeline.py --quick-analysis

  # Run with custom configuration
  python pipeline.py --full --config pipeline_config.json
        """
    )
    
    # Main commands
    parser.add_argument('--full', action='store_true',
                       help='Run the complete pipeline')
    parser.add_argument('--quick-analysis', action='store_true',
                       help='Run quick analysis of existing data')
    
    # Pipeline options
    parser.add_argument('--google-api-key', type=str,
                       help='Google Maps API key for enhanced geocoding')
    parser.add_argument('--skip-collection', action='store_true',
                       help='Skip address collection (use cached data)')
    parser.add_argument('--skip-geocoding', action='store_true',
                       help='Skip geocoding step')
    parser.add_argument('--export-formats', nargs='+', 
                       choices=['csv', 'kml', 'json'], default=['csv', 'kml'],
                       help='Export formats to generate')
    
    # Configuration
    parser.add_argument('--config', type=str,
                       help='Path to JSON configuration file')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {'log_level': args.log_level}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config.update(json.load(f))
    
    # Initialize pipeline
    pipeline = AddressPipeline(config)
    
    try:
        if args.full:
            # Run complete pipeline
            results = pipeline.run_full_pipeline(
                google_api_key=args.google_api_key,
                skip_collection=args.skip_collection,
                skip_geocoding=args.skip_geocoding,
                export_formats=args.export_formats
            )
            
            print("\n" + "="*60)
            print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"📊 Total addresses: {results['total_addresses']:,}")
            print(f"📍 Geocoded addresses: {results['geocoded_addresses']:,}")
            print(f"📁 Export files: {', '.join(results['export_files'])}")
            print(f"📋 Steps completed: {', '.join(results['steps_completed'])}")
            
        elif args.quick_analysis:
            # Run quick analysis
            results = pipeline.run_quick_analysis()
            
        else:
            parser.print_help()
            return
            
    except KeyboardInterrupt:
        pipeline.logger.info("⏹️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        pipeline.logger.error(f"❌ Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()