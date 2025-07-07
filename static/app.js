// Ocean Township Address Geocoding System - JavaScript

class OceanTownshipApp {
    constructor() {
        this.map = null;
        this.markers = [];
        this.currentAddresses = [];
        this.currentGeocodedAddresses = [];
        this.progressInterval = null;
        
        this.init();
    }

    init() {
        this.initializeMap();
        this.setupEventListeners();
        this.loadInitialData();
    }

    // Initialize Leaflet map
    initializeMap() {
        // Initialize map centered on Ocean Township, NJ
        this.map = L.map('map').setView([40.2535, -74.0287], 12);

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
    }

    // Setup event listeners
    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Action buttons
        document.getElementById('refreshCacheBtn').addEventListener('click', () => {
            this.refreshCache();
        });

        document.getElementById('geocodeBtn').addEventListener('click', () => {
            this.startGeocoding();
        });

        // Export dropdown
        document.getElementById('exportBtn').addEventListener('click', () => {
            this.toggleDropdown();
        });

        document.querySelectorAll('.dropdown-menu a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const format = e.target.dataset.format;
                this.exportData(format);
            });
        });

        // Search and filter
        document.getElementById('addressSearch').addEventListener('input', (e) => {
            this.filterMapMarkers(e.target.value);
        });

        document.getElementById('addressListSearch').addEventListener('input', (e) => {
            this.filterAddressList(e.target.value);
        });

        document.getElementById('cityFilter').addEventListener('change', (e) => {
            this.filterByCity(e.target.value);
        });

        document.getElementById('zipFilter').addEventListener('change', (e) => {
            this.filterByZip(e.target.value);
        });

        // Status panel
        document.getElementById('dismissStatus').addEventListener('click', () => {
            this.hideStatus();
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.dropdown')) {
                this.closeDropdown();
            }
        });
    }

    // Load initial data
    async loadInitialData() {
        this.showLoading();
        try {
            await this.loadStatistics();
            await this.loadAddresses();
            await this.loadGeocodedAddresses();
            this.populateFilters();
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showStatus('Error loading data', 'error');
        } finally {
            this.hideLoading();
        }
    }

    // API calls
    async loadStatistics() {
        try {
            const response = await fetch('/api/statistics');
            const data = await response.json();
            
            if (data.success) {
                this.updateStatistics(data);
            } else {
                console.error('Error loading statistics:', data.error);
            }
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }

    async loadAddresses() {
        try {
            const response = await fetch('/api/addresses');
            const data = await response.json();
            
            if (data.success) {
                this.currentAddresses = data.addresses;
                this.updateAddressList();
            } else {
                console.error('Error loading addresses:', data.error);
            }
        } catch (error) {
            console.error('Error loading addresses:', error);
        }
    }

    async loadGeocodedAddresses() {
        try {
            const response = await fetch('/api/geocoded-addresses');
            const data = await response.json();
            
            if (data.success) {
                this.currentGeocodedAddresses = data.addresses;
                this.updateMapMarkers();
            } else {
                console.error('Error loading geocoded addresses:', data.error);
            }
        } catch (error) {
            console.error('Error loading geocoded addresses:', error);
        }
    }

    async refreshCache() {
        try {
            this.showStatus('Refreshing address cache...', 'info');
            const response = await fetch('/api/refresh-cache', {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.success) {
                this.showStatus('Cache refresh started', 'success');
                this.startProgressTracking();
            } else {
                this.showStatus('Error starting cache refresh', 'error');
            }
        } catch (error) {
            console.error('Error refreshing cache:', error);
            this.showStatus('Error refreshing cache', 'error');
        }
    }

    async startGeocoding() {
        try {
            this.showStatus('Starting geocoding process...', 'info');
            const response = await fetch('/api/geocode', {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.success) {
                this.showStatus('Geocoding started', 'success');
                this.startProgressTracking();
            } else {
                this.showStatus('Error starting geocoding', 'error');
            }
        } catch (error) {
            console.error('Error starting geocoding:', error);
            this.showStatus('Error starting geocoding', 'error');
        }
    }

    async exportData(format) {
        try {
            this.showStatus(`Exporting data as ${format.toUpperCase()}...`, 'info');
            const response = await fetch(`/api/export/${format}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `ocean_addresses.${format}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                this.showStatus('Export completed', 'success');
            } else {
                this.showStatus('Export failed', 'error');
            }
        } catch (error) {
            console.error('Error exporting data:', error);
            this.showStatus('Export failed', 'error');
        }
        this.closeDropdown();
    }

    // Progress tracking
    startProgressTracking() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        this.progressInterval = setInterval(async () => {
            try {
                const response = await fetch('/api/progress');
                const data = await response.json();
                
                if (data.status === 'running') {
                    this.updateProgress(data);
                } else if (data.status === 'completed') {
                    this.showStatus(data.message, 'success');
                    this.hideProgress();
                    this.stopProgressTracking();
                    this.loadInitialData(); // Refresh data
                } else if (data.status === 'error') {
                    this.showStatus(data.message, 'error');
                    this.hideProgress();
                    this.stopProgressTracking();
                }
            } catch (error) {
                console.error('Error tracking progress:', error);
                this.stopProgressTracking();
            }
        }, 2000); // Check every 2 seconds
    }

    stopProgressTracking() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
    }

    // UI Updates
    updateStatistics(data) {
        const basicStats = data.basic_stats || {};
        const geocodedStats = data.geocoded_stats || {};
        
        document.getElementById('totalAddresses').textContent = 
            basicStats.total_addresses || 0;
        document.getElementById('geocodedAddresses').textContent = 
            geocodedStats.successful_geocoding || 0;
        document.getElementById('successRate').textContent = 
            `${Math.round(geocodedStats.success_rate || 0)}%`;
        document.getElementById('uniqueCities').textContent = 
            basicStats.unique_cities || 0;
    }

    updateMapMarkers() {
        // Clear existing markers
        this.markers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.markers = [];

        // Add new markers
        this.currentGeocodedAddresses.forEach(address => {
            if (address.latitude && address.longitude) {
                const marker = L.marker([address.latitude, address.longitude])
                    .addTo(this.map)
                    .bindPopup(`
                        <div class="popup-address">${address.full_address}</div>
                        <div class="popup-coords">
                            ${address.latitude.toFixed(6)}, ${address.longitude.toFixed(6)}
                        </div>
                    `);
                
                this.markers.push(marker);
            }
        });

        // Fit map to markers if we have any
        if (this.markers.length > 0) {
            const group = new L.featureGroup(this.markers);
            this.map.fitBounds(group.getBounds().pad(0.1));
        }
    }

    updateAddressList() {
        const listContainer = document.getElementById('addressList');
        listContainer.innerHTML = '';

        this.currentAddresses.forEach(address => {
            const addressItem = document.createElement('div');
            addressItem.className = 'address-item fade-in';
            
            const isGeocoded = address.latitude && address.longitude;
            const badge = isGeocoded ? 
                '<span class="geocoded-badge">Geocoded</span>' : 
                '<span class="failed-badge">Not Geocoded</span>';
            
            addressItem.innerHTML = `
                <h4>${address.full_address}</h4>
                <p>${address.city}, ${address.state} ${address.zip_code}</p>
                <div class="address-meta">
                    <span>Cached: ${this.formatDate(address.cached_date)}</span>
                    ${badge}
                </div>
            `;
            
            listContainer.appendChild(addressItem);
        });
    }

    populateFilters() {
        const cities = [...new Set(this.currentAddresses.map(addr => addr.city))].sort();
        const zipCodes = [...new Set(this.currentAddresses.map(addr => addr.zip_code))].sort();

        // Populate city filters
        [document.getElementById('cityFilter'), document.getElementById('listCityFilter')].forEach(select => {
            select.innerHTML = '<option value="">All Cities</option>';
            cities.forEach(city => {
                if (city) {
                    const option = document.createElement('option');
                    option.value = city;
                    option.textContent = city;
                    select.appendChild(option);
                }
            });
        });

        // Populate zip code filters
        [document.getElementById('zipFilter'), document.getElementById('listZipFilter')].forEach(select => {
            select.innerHTML = '<option value="">All Zip Codes</option>';
            zipCodes.forEach(zip => {
                if (zip) {
                    const option = document.createElement('option');
                    option.value = zip;
                    option.textContent = zip;
                    select.appendChild(option);
                }
            });
        });
    }

    // Filtering and search
    filterMapMarkers(searchTerm) {
        const term = searchTerm.toLowerCase();
        this.markers.forEach(marker => {
            const popup = marker.getPopup();
            if (popup) {
                const content = popup.getContent().toLowerCase();
                if (content.includes(term)) {
                    marker.addTo(this.map);
                } else {
                    this.map.removeLayer(marker);
                }
            }
        });
    }

    filterAddressList(searchTerm) {
        const term = searchTerm.toLowerCase();
        const addressItems = document.querySelectorAll('#addressList .address-item');
        
        addressItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(term)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    filterByCity(city) {
        // This would need to be implemented to filter both map and list
        console.log('Filter by city:', city);
    }

    filterByZip(zip) {
        // This would need to be implemented to filter both map and list
        console.log('Filter by zip:', zip);
    }

    // UI helpers
    switchTab(tabName) {
        // Remove active class from all tabs and content
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });

        // Add active class to clicked tab and corresponding content
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        document.getElementById(`${tabName}Tab`).classList.add('active');

        // Refresh map size if switching to map tab
        if (tabName === 'map') {
            setTimeout(() => {
                this.map.invalidateSize();
            }, 100);
        }
    }

    showStatus(message, type = 'info') {
        const statusPanel = document.getElementById('statusPanel');
        const statusIcon = statusPanel.querySelector('.status-icon i');
        const statusMessage = document.getElementById('statusMessage');
        
        statusPanel.className = `status-panel show ${type}`;
        statusMessage.textContent = message;
        
        // Update icon based on type
        statusIcon.className = type === 'error' ? 'fas fa-exclamation-triangle' :
                              type === 'success' ? 'fas fa-check-circle' :
                              'fas fa-info-circle';
    }

    hideStatus() {
        document.getElementById('statusPanel').classList.remove('show');
    }

    updateProgress(data) {
        const progressBar = document.getElementById('progressBar');
        const progressFill = document.getElementById('progressFill');
        const statusMessage = document.getElementById('statusMessage');
        
        progressBar.style.display = 'block';
        
        if (data.total > 0) {
            const percentage = (data.progress / data.total) * 100;
            progressFill.style.width = `${percentage}%`;
        }
        
        statusMessage.textContent = data.message;
    }

    hideProgress() {
        document.getElementById('progressBar').style.display = 'none';
    }

    showLoading() {
        document.getElementById('loadingOverlay').classList.add('show');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.remove('show');
    }

    toggleDropdown() {
        document.querySelector('.dropdown').classList.toggle('show');
    }

    closeDropdown() {
        document.querySelector('.dropdown').classList.remove('show');
    }

    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        return date.toLocaleDateString();
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new OceanTownshipApp();
});

// Handle window resize for map
window.addEventListener('resize', () => {
    if (window.app && window.app.map) {
        window.app.map.invalidateSize();
    }
});