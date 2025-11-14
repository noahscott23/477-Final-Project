---
title: Data Documentation
toc: true
---

# Data Documentation

Technical overview of datasets, processing pipeline, and methodology.

---

## Datasets

### IPCC AR6 Sea Level Projections
**Source:** [Zenodo DOI: 10.5281/zenodo.5914709](https://doi.org/10.5281/zenodo.5914709)  
**Maintained by:** NASA Jet Propulsion Laboratory  
**Size:** 9.2 GB (NetCDF format)  
**Coverage:** 1,030 tide gauge stations + 65,160 grid points globally  
**Time span:** 2020-2150 (decadal intervals)  
**Scenarios:** 5 SSP pathways (SSP1-1.9, SSP1-2.6, SSP2-4.5, SSP3-7.0, SSP5-8.5)  
**Confidence levels:** Medium and low  
**Uncertainty:** 107 quantile distributions (5th-95th percentiles)

### PSMSL Tide Gauge Locations
**Source:** Permanent Service for Mean Sea Level via IPCC package  
**File:** `locations.lst`  
**Format:** Tab-separated values  
**Entries:** 66,190 total (1,030 tide gauges + 65,160 grid points)  
**Data:** Station names, PSMSL IDs, latitude, longitude

### US States Map
**Source:** [US Atlas TopoJSON](https://github.com/topojson/us-atlas)  
**File:** `us-states-10m.json`  
**Resolution:** 1:10,000,000  
**Features:** State boundaries, Albers USA projection with AK/HI positioning

---

## Data Pipeline

### Stage 1: Acquisition
- Downloaded IPCC AR6 NetCDF files (9.2 GB)
- Downloaded PSMSL location list (2.5 MB)
- Downloaded US states TopoJSON (112 KB)

### Stage 2: Filtering
- Extracted 153 US cities from 66,190 global locations
- Geographic bounds: mainland US (24-48.5°N, 67-125°W), Alaska (51-71°N, 130-172°W), Hawaii (18.5-22.5°N, 154-161°W)
- Excluded Canadian stations and grid points
- Output: `us_coastal_cities.csv` (4.5 KB)

### Stage 3: Extraction
**Script:** `src/scripts/extract_us_projections.py`  
**Process:**
1. Read NetCDF files for 3 scenarios (SSP1-1.9, SSP2-4.5, SSP5-8.5)
2. Extract median (50th percentile) projections
3. Select years: 2030, 2050, 2100, 2150
4. Match PSMSL IDs to US cities
5. Output: `us_projections.json` (70 KB)

**Runtime:** ~10-15 seconds  
**Compression:** 9.2 GB → 70 KB (99.999% reduction)

### Stage 4: Risk Classification
**Algorithm:**
```python
if sea_level_rise_2100 < 200mm:
    risk = "low"
elif sea_level_rise_2100 < 400mm:
    risk = "moderate"
else:
    risk = "high"
```

**Results (SSP2-4.5, Year 2100):**
- High risk: 13 cities (> 40cm)
- Moderate: 88 cities (20-40cm)
- Low: 38 cities (< 20cm)
- Unknown: 14 cities (missing data)

### Stage 5: Visualization
- D3.js + Observable Framework
- Albers USA projection (includes AK/HI insets)
- Interactive controls: scenario selector, year slider
- Color-coded risk levels: green (low), yellow (moderate), red (high)
- Hover tooltips with city-specific data

---

## File Organization

### Processed Data (`src/data/processed/`)
**Actively used in visualization:**
- `us_coastal_cities.csv` (4.5 KB) - 153 cities with coordinates
- `us_projections.json` (70 KB) - Sea level projections
- `us-states-10m.json` (112 KB) - US map

### Raw Data (`src/data/raw/`)
**Source material:**
- `locations.lst` (2.5 MB) - Complete PSMSL list
- `ar6-regional-confidence/` (9.2 GB) - NetCDF projection files

### Archived Data (`src/data/archived/`)
**Historical/unused:**
- `coastal_cities.csv` (28 KB) - Global dataset (1,030 cities)
- `countries-110m.json` (105 KB) - World map

---

## Data Quality

### Validation
- ✅ Coordinate ranges verified (lat: -90 to 90, lon: -180 to 180)
- ✅ PSMSL IDs unique and cross-referenced
- ✅ Projection values physically reasonable
- ✅ Risk classifications align with IPCC thresholds

### Limitations
- Decadal time steps only (no yearly data)
- Median projections (50th percentile) used; uncertainty ranges not visualized
- No population or economic impact data integrated
- Missing data for 14 cities (out of 153)

### Geographic Coverage
- **East Coast:** 62 cities - New York, Boston, Miami, Charleston
- **West Coast:** 48 cities - San Francisco, Los Angeles, Seattle, San Diego
- **Gulf Coast:** 21 cities - Galveston, Key West, Pensacola
- **Alaska:** 15 cities - Juneau, Sitka, Ketchikan
- **Hawaii:** 4 cities - Honolulu, Hilo
- **Puerto Rico:** 3 cities

---

## Technical Implementation

### Tools & Libraries
- **Data Processing:** Python 3, netCDF4, NumPy
- **Visualization:** D3.js v7, Observable Framework, TopoJSON
- **Map Projection:** D3 Albers USA

### Performance
- Total data load: ~190 KB (optimized for web)
- Map render time: < 100ms (153 cities)
- Interaction latency: < 10ms (slider/selector updates)

---

## Citations

**IPCC AR6 Data:**
Garner, G. G., et al., 2021. IPCC AR6 Sea Level Projections. Version 20210809. [doi:10.5281/zenodo.5914709](https://doi.org/10.5281/zenodo.5914709)

**IPCC Chapter:**
Fox-Kemper, B., et al., 2021. Ocean, Cryosphere and Sea Level Change. In *Climate Change 2021: The Physical Science Basis. IPCC AR6*. [doi:10.1017/9781009157896.011](https://doi.org/10.1017/9781009157896.011)

**FACTS Model:**
Kopp, R. E., et al., 2023. The Framework for Assessing Changes To Sea-Level (FACTS) v1.0. *Geoscientific Model Development*, 16, 7461–7489. [doi:10.5194/gmd-16-7461-2023](https://doi.org/10.5194/gmd-16-7461-2023)

**License:** Creative Commons Attribution 4.0 International (CC BY 4.0)

---

**Last Updated:** November 13, 2024  
**Team:** Megan Fung, Noah Scott, Archie Phyo
