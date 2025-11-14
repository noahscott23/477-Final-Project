#!/usr/bin/env python3
"""
Extract sea level projections for US coastal cities from IPCC AR6 NetCDF files.

This script reads NetCDF files containing sea level projections and extracts
data for US cities only, outputting a lightweight JSON file for visualization.
"""

import json
import csv
from pathlib import Path
from netCDF4 import Dataset
import numpy as np

# Configuration
DATA_DIR = Path(__file__).parent
NETCDF_BASE = DATA_DIR / "ar6-regional-confidence/regional/confidence_output_files/medium_confidence"
US_CITIES_FILE = DATA_DIR / "us_coastal_cities.csv"
OUTPUT_FILE = DATA_DIR / "us_projections.json"

# Scenarios to extract (focus on 3 key scenarios)
SCENARIOS = {
    "ssp119": "Low Emissions (SSP1-1.9)",
    "ssp245": "Moderate Emissions (SSP2-4.5)",
    "ssp585": "High Emissions (SSP5-8.5)"
}

# Years to extract (subset for visualization)
TARGET_YEARS = [2030, 2050, 2100, 2150]


def load_us_cities():
    """Load US coastal cities from CSV."""
    cities = {}
    with open(US_CITIES_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            psmsl_id = int(row['psmsl_id'])
            cities[psmsl_id] = {
                'name': row['location_name'],
                'lat': float(row['latitude']),
                'lon': float(row['longitude'])
            }
    print(f"Loaded {len(cities)} US coastal cities")
    return cities


def extract_projections_for_scenario(scenario, us_cities):
    """Extract sea level projections for all US cities for a given scenario."""
    
    # Open NetCDF file for this scenario
    nc_file = NETCDF_BASE / scenario / f"total_{scenario}_medium_confidence_values.nc"
    
    if not nc_file.exists():
        print(f"Warning: {nc_file} not found, skipping {scenario}")
        return {}
    
    print(f"\nProcessing {scenario}...")
    ds = Dataset(nc_file, 'r')
    
    # Get arrays
    locations = ds.variables['locations'][:]
    years = ds.variables['years'][:]
    quantiles = ds.variables['quantiles'][:]
    sea_level_change = ds.variables['sea_level_change'][:]  # (quantiles, years, locations)
    
    # Find median quantile index (50th percentile)
    median_idx = np.argmin(np.abs(quantiles - 0.5))
    print(f"  Using quantile: {quantiles[median_idx]:.2f} (index {median_idx})")
    
    # Build index lookup for PSMSL IDs
    location_index = {psmsl_id: idx for idx, psmsl_id in enumerate(locations)}
    
    # Extract data for each US city
    projections = {}
    found_count = 0
    
    for psmsl_id in us_cities.keys():
        if psmsl_id not in location_index:
            print(f"  Warning: PSMSL ID {psmsl_id} not found in NetCDF locations")
            continue
        
        loc_idx = location_index[psmsl_id]
        city_data = {}
        
        # Extract for target years
        for target_year in TARGET_YEARS:
            # Find closest year in dataset
            year_idx = np.argmin(np.abs(years - target_year))
            actual_year = int(years[year_idx])
            
            # Get sea level change (in mm)
            value = sea_level_change[median_idx, year_idx, loc_idx]
            
            # Handle masked values (missing data)
            if np.ma.is_masked(value):
                city_data[str(actual_year)] = None
            else:
                city_data[str(actual_year)] = int(value)
        
        projections[str(psmsl_id)] = city_data
        found_count += 1
    
    ds.close()
    print(f"  Extracted data for {found_count}/{len(us_cities)} cities")
    
    return projections


def calculate_risk_level(projections_2100):
    """Calculate risk level based on 2100 projection."""
    # Handle missing data
    if projections_2100 is None:
        return "unknown"
    
    # Thresholds in mm
    LOW_THRESHOLD = 200     # < 20 cm
    MODERATE_THRESHOLD = 400  # < 40 cm
    
    if projections_2100 < LOW_THRESHOLD:
        return "low"
    elif projections_2100 < MODERATE_THRESHOLD:
        return "moderate"
    else:
        return "high"


def main():
    """Main extraction pipeline."""
    print("=" * 60)
    print("IPCC AR6 Sea Level Projections - US Cities Extraction")
    print("=" * 60)
    
    # Load US cities
    us_cities = load_us_cities()
    
    # Extract projections for each scenario
    all_data = {}
    
    for scenario_id, scenario_name in SCENARIOS.items():
        scenario_projections = extract_projections_for_scenario(scenario_id, us_cities)
        
        # Add to combined dataset
        for psmsl_id, city_info in us_cities.items():
            psmsl_str = str(psmsl_id)
            
            # Initialize city entry if not exists
            if psmsl_str not in all_data:
                all_data[psmsl_str] = {
                    'name': city_info['name'],
                    'lat': city_info['lat'],
                    'lon': city_info['lon'],
                    'projections': {}
                }
            
            # Add scenario data if available
            if psmsl_str in scenario_projections:
                all_data[psmsl_str]['projections'][scenario_id] = scenario_projections[psmsl_str]
    
    # Calculate risk levels based on SSP2-4.5 2100 projections
    print("\nCalculating risk levels...")
    risk_counts = {'low': 0, 'moderate': 0, 'high': 0, 'unknown': 0}
    
    for psmsl_id, city_data in all_data.items():
        if 'ssp245' in city_data['projections'] and '2100' in city_data['projections']['ssp245']:
            projection_2100 = city_data['projections']['ssp245']['2100']
            risk = calculate_risk_level(projection_2100)
            city_data['risk_level'] = risk
            risk_counts[risk] += 1
        else:
            city_data['risk_level'] = 'unknown'
            risk_counts['unknown'] += 1
    
    print(f"  Low risk: {risk_counts['low']} cities")
    print(f"  Moderate risk: {risk_counts['moderate']} cities")
    print(f"  High risk: {risk_counts['high']} cities")
    if risk_counts['unknown'] > 0:
        print(f"  Unknown/Missing data: {risk_counts['unknown']} cities")
    
    # Write output JSON
    print(f"\nWriting output to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    # Calculate file size
    file_size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"  File size: {file_size_kb:.1f} KB")
    
    print("\n" + "=" * 60)
    print("Extraction complete!")
    print("=" * 60)
    
    # Print sample data for verification
    sample_cities = ['10', '12', '235']  # San Francisco, New York, Boston
    print("\nSample data (SSP2-4.5, Year 2100):")
    for psmsl_id in sample_cities:
        if psmsl_id in all_data:
            city = all_data[psmsl_id]
            if 'ssp245' in city['projections'] and '2100' in city['projections']['ssp245']:
                value_mm = city['projections']['ssp245']['2100']
                value_cm = value_mm / 10
                print(f"  {city['name']:20s}: {value_cm:5.1f} cm ({city['risk_level']})")


if __name__ == '__main__':
    main()

