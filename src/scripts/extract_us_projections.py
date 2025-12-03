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

# config
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
NETCDF_BASE = DATA_DIR / "raw/medium_confidence"
US_CITIES_FILE = DATA_DIR / "processed/us_coastal_cities.csv"
OUTPUT_FILE = DATA_DIR / "processed/us_projections.json"

# scenarios
SCENARIOS = {
    "ssp119": "Low Emissions (SSP1-1.9)",
    "ssp245": "Moderate Emissions (SSP2-4.5)",
    "ssp585": "High Emissions (SSP5-8.5)"
}

# years (separated by 10 years)
TARGET_YEARS = [2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100, 2110, 2120, 2130, 2140, 2150]


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
    """Extract sea level projections with uncertainty for all US cities for a given scenario."""
    
    nc_file = NETCDF_BASE / scenario / f"total_{scenario}_medium_confidence_values.nc"
    
    if not nc_file.exists():
        print(f"Warning: {nc_file} not found, skipping {scenario}")
        return {}
    
    print(f"\nProcessing {scenario}...")
    ds = Dataset(nc_file, 'r')
    
    locations = ds.variables['locations'][:]
    years = ds.variables['years'][:]
    quantiles = ds.variables['quantiles'][:]
    sea_level_change = ds.variables['sea_level_change'][:]  # (quantiles, years, locations)
    
    # Find indices for 17th, 50th (median), and 83rd percentiles
    p17_idx = np.argmin(np.abs(quantiles - 0.17))
    median_idx = np.argmin(np.abs(quantiles - 0.5))
    p83_idx = np.argmin(np.abs(quantiles - 0.83))
    
    print(f"  Using quantiles: 17th={quantiles[p17_idx]:.2f}, 50th={quantiles[median_idx]:.2f}, 83rd={quantiles[p83_idx]:.2f}")
    
    location_index = {psmsl_id: idx for idx, psmsl_id in enumerate(locations)}
    
    projections = {}
    found_count = 0
    
    for psmsl_id in us_cities.keys():
        if psmsl_id not in location_index:
            print(f"  Warning: PSMSL ID {psmsl_id} not found in NetCDF locations")
            continue
        
        loc_idx = location_index[psmsl_id]
        city_data = {}
        
        for target_year in TARGET_YEARS:
            year_idx = np.argmin(np.abs(years - target_year))
            actual_year = int(years[year_idx])
            
            # Extract median, lower, and upper bounds
            median_value = sea_level_change[median_idx, year_idx, loc_idx]
            lower_value = sea_level_change[p17_idx, year_idx, loc_idx]
            upper_value = sea_level_change[p83_idx, year_idx, loc_idx]
            
            # Handle masked values (missing data)
            if np.ma.is_masked(median_value):
                city_data[str(actual_year)] = None
            else:
                city_data[str(actual_year)] = {
                    "median": int(median_value),
                    "lower": int(lower_value) if not np.ma.is_masked(lower_value) else int(median_value),
                    "upper": int(upper_value) if not np.ma.is_masked(upper_value) else int(median_value)
                }
        
        projections[str(psmsl_id)] = city_data
        found_count += 1
    
    ds.close()
    print(f"  Extracted data for {found_count}/{len(us_cities)} cities with uncertainty bounds")
    
    return projections


def calculate_risk_level(projections_2100):
    """Calculate risk level based on 2100 median projection."""

    # missing data
    if projections_2100 is None:
        return "unknown"
    
    # Extract median value (now data is a dict with median/lower/upper)
    median_value = projections_2100.get("median") if isinstance(projections_2100, dict) else projections_2100
    
    if median_value is None:
        return "unknown"
    
    LOW_THRESHOLD = 200     # < 20 cm
    MODERATE_THRESHOLD = 400  # < 40 cm
    
    if median_value < LOW_THRESHOLD:
        return "low"
    elif median_value < MODERATE_THRESHOLD:
        return "moderate"
    else:
        return "high"


def main():
    """Main extraction pipeline."""
    print("=" * 60)
    print("IPCC AR6 Sea Level Projections - US Cities Extraction")
    print("=" * 60)
    
    # load cities
    us_cities = load_us_cities()
    
    # get projections for scenarios 
    all_data = {}
    
    for scenario_id, scenario_name in SCENARIOS.items():
        scenario_projections = extract_projections_for_scenario(scenario_id, us_cities)
        
        for psmsl_id, city_info in us_cities.items():
            psmsl_str = str(psmsl_id)
            
            if psmsl_str not in all_data:
                all_data[psmsl_str] = {
                    'name': city_info['name'],
                    'lat': city_info['lat'],
                    'lon': city_info['lon'],
                    'projections': {}
                }
            
            if psmsl_str in scenario_projections:
                all_data[psmsl_str]['projections'][scenario_id] = scenario_projections[psmsl_str]
    
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
    
    print(f"\nWriting output to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    file_size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"  File size: {file_size_kb:.1f} KB")
    
    print("\n" + "=" * 60)
    print("Extraction complete!")
    print("=" * 60)
    print(f"  {len(all_data)} cities × {len(SCENARIOS)} scenarios × {len(TARGET_YEARS)} years")
    print(f"  Each projection includes: median, lower (17th %), upper (83rd %)")
    
    sample_cities = ['10', '12', '235']  
    print("\nSample data (SSP2-4.5, Year 2100 with uncertainty):")
    for psmsl_id in sample_cities:
        if psmsl_id in all_data:
            city = all_data[psmsl_id]
            if 'ssp245' in city['projections'] and '2100' in city['projections']['ssp245']:
                proj = city['projections']['ssp245']['2100']
                if isinstance(proj, dict):
                    median_cm = proj['median'] / 10
                    lower_cm = proj['lower'] / 10
                    upper_cm = proj['upper'] / 10
                    print(f"  {city['name']:20s}: {median_cm:5.1f} cm ({lower_cm:5.1f}–{upper_cm:5.1f} cm) [{city['risk_level']}]")
                else:
                    # Fallback for old format
                    value_cm = proj / 10
                    print(f"  {city['name']:20s}: {value_cm:5.1f} cm ({city['risk_level']})")


if __name__ == '__main__':
    main()

