#!/usr/bin/env python3
"""
Flask Web Application for Ocean Township Address Geocoding System
"""

from flask import Flask, render_template, jsonify, request, send_file
from cache_addresses import AddressCache
from geocode_addresses import AddressGeocoder
from geocoded_examples import GeocodedAnalyzer
import json
import os
import threading
import time
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ocean-township-geocoding-2024'

# Global variables for progress tracking
current_operation = None
operation_progress = {}

class ProgressTracker:
    def __init__(self):
        self.current_operation = None
        self.progress = 0
        self.total = 0
        self.status = "idle"
        self.message = ""
        self.start_time = None
        self.end_time = None
    
    def start(self, operation_name, total=0):
        self.current_operation = operation_name
        self.progress = 0
        self.total = total
        self.status = "running"
        self.message = f"Starting {operation_name}..."
        self.start_time = datetime.now()
        self.end_time = None
    
    def update(self, progress, message=""):
        self.progress = progress
        if message:
            self.message = message
    
    def finish(self, message=""):
        self.status = "completed"
        self.end_time = datetime.now()
        if message:
            self.message = message
        else:
            self.message = f"{self.current_operation} completed successfully"
    
    def error(self, message):
        self.status = "error"
        self.end_time = datetime.now()
        self.message = message
    
    def get_status(self):
        elapsed_time = None
        if self.start_time:
            end_time = self.end_time or datetime.now()
            elapsed_time = (end_time - self.start_time).total_seconds()
        
        return {
            'operation': self.current_operation,
            'progress': self.progress,
            'total': self.total,
            'status': self.status,
            'message': self.message,
            'elapsed_time': elapsed_time
        }

progress_tracker = ProgressTracker()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/addresses')
def get_addresses():
    try:
        cache = AddressCache()
        addresses = cache.load_addresses()
        
        # Add filtering options
        city = request.args.get('city')
        zip_code = request.args.get('zip_code')
        
        if city:
            addresses = [addr for addr in addresses if addr.get('city', '').lower() == city.lower()]
        if zip_code:
            addresses = [addr for addr in addresses if addr.get('zip_code') == zip_code]
        
        return jsonify({
            'success': True,
            'addresses': addresses,
            'total': len(addresses)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/geocoded-addresses')
def get_geocoded_addresses():
    try:
        analyzer = GeocodedAnalyzer()
        addresses = analyzer.load_geocoded_addresses()
        
        # Filter only successfully geocoded addresses
        geocoded = [addr for addr in addresses if addr.get('latitude') and addr.get('longitude')]
        
        return jsonify({
            'success': True,
            'addresses': geocoded,
            'total': len(geocoded)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/statistics')
def get_statistics():
    try:
        cache = AddressCache()
        stats = cache.get_stats()
        
        # Try to get geocoded stats
        geocoded_stats = {}
        try:
            geocoder = AddressGeocoder()
            geocoded_stats = geocoder.get_geocoded_stats()
        except:
            pass
        
        # Try to get analysis stats
        analysis_stats = {}
        try:
            analyzer = GeocodedAnalyzer()
            analysis_stats = analyzer.get_basic_stats()
        except:
            pass
        
        return jsonify({
            'success': True,
            'basic_stats': stats,
            'geocoded_stats': geocoded_stats,
            'analysis_stats': analysis_stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/refresh-cache', methods=['POST'])
def refresh_cache():
    def refresh_task():
        try:
            progress_tracker.start("Address Cache Refresh")
            cache = AddressCache()
            progress_tracker.update(50, "Fetching addresses from website...")
            cache.refresh_cache()
            progress_tracker.finish("Address cache refreshed successfully")
        except Exception as e:
            progress_tracker.error(f"Error refreshing cache: {str(e)}")
    
    # Run in background thread
    thread = threading.Thread(target=refresh_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Cache refresh started'})

@app.route('/api/geocode', methods=['POST'])
def start_geocoding():
    def geocode_task():
        try:
            progress_tracker.start("Geocoding Addresses")
            geocoder = AddressGeocoder()
            
            # Get total count for progress tracking
            cache = AddressCache()
            addresses = cache.load_addresses()
            progress_tracker.total = len(addresses)
            
            # Run geocoding (progress tracking will be handled by monitoring)
            geocoder.geocode_all_addresses()
            progress_tracker.finish("Geocoding completed successfully")
        except Exception as e:
            progress_tracker.error(f"Error during geocoding: {str(e)}")
    
    # Run in background thread
    thread = threading.Thread(target=geocode_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Geocoding started'})

@app.route('/api/progress')
def get_progress():
    return jsonify(progress_tracker.get_status())

@app.route('/api/export/<format>')
def export_data(format):
    try:
        analyzer = GeocodedAnalyzer()
        
        if format == 'csv':
            filename = analyzer.export_for_mapping("ocean_addresses.csv")
            return send_file(filename, as_attachment=True)
        elif format == 'kml':
            filename = analyzer.generate_kml("ocean_addresses.kml")
            return send_file(filename, as_attachment=True)
        elif format == 'json':
            addresses = analyzer.load_geocoded_addresses()
            filename = "ocean_addresses.json"
            with open(filename, 'w') as f:
                json.dump(addresses, f, indent=2)
            return send_file(filename, as_attachment=True)
        else:
            return jsonify({'success': False, 'error': 'Invalid format'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/density-analysis')
def get_density_analysis():
    try:
        analyzer = GeocodedAnalyzer()
        density = analyzer.get_density_analysis()
        return jsonify({
            'success': True,
            'density': density
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/nearby-addresses')
def get_nearby_addresses():
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        radius = float(request.args.get('radius', 0.5))  # Default 0.5 miles
        
        analyzer = GeocodedAnalyzer()
        nearby = analyzer.find_addresses_near_point(lat, lng, radius)
        
        return jsonify({
            'success': True,
            'addresses': nearby,
            'total': len(nearby)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)