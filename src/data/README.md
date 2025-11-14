# Data Directory

This directory contains all datasets used in the Sea Level Rise visualization project.

## Directory Structure

```
data/
├── processed/      # Transformed/filtered datasets actively used in visualizations
├── raw/            # Original downloaded datasets (unmodified)
├── archived/       # Historical datasets no longer used in current visualization
└── README.md       # This file
```

## Data Organization

### processed/
Contains datasets that have been created through data cleaning, transformation, or filtering operations. These are the datasets actively loaded by the visualization.

**Files:**
- `us_coastal_cities.csv` - Filtered list of 153 US coastal cities
- `us_projections.json` - Sea level projections for US cities (3 scenarios × 4 years)
- `us-states-10m.json` - US states map TopoJSON for visualization

### raw/
Contains original, unmodified datasets downloaded from authoritative sources. These serve as the source material for processed datasets.

**Files:**
- `locations.lst` - Complete PSMSL tide gauge location list (66,190 entries)
- `ar6-regional-confidence/` - IPCC AR6 NetCDF files with sea level projections

### archived/
Contains datasets that were used during development but are no longer actively used in the current visualization (e.g., world map when we switched to US-only focus).

**Files:**
- `coastal_cities.csv` - Global dataset of 1,030 coastal cities
- `countries-110m.json` - World map TopoJSON
- `ipcc_ar6_sea_level_projection_psmsl_id_24.csv` - Single-location example

## Data Lineage

```
raw/locations.lst
    └─→ [filtered to US cities] 
        └─→ processed/us_coastal_cities.csv

raw/ar6-regional-confidence/*.nc
    └─→ [extracted via scripts/extract_us_projections.py]
        └─→ processed/us_projections.json
```

## Size Information

- **processed/**: ~70 KB (lightweight for web delivery)
- **raw/**: ~9.2 GB (large NetCDF files, used only for processing)
- **archived/**: ~300 KB (historical reference)

**Last Updated:** November 13, 2024

