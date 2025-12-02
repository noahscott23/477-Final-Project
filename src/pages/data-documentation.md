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
**Used in this project:** 3 scenarios (SSP1-1.9, SSP2-4.5, SSP5-8.5), medium confidence, 17th/50th/83rd percentiles

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
- Extracted 141 US cities from 66,190 global locations
- Geographic bounds: mainland US (24-48.5°N, 67-125°W), Alaska (51-71°N, 130-172°W), Hawaii (18.5-22.5°N, 154-161°W)
- Excluded Canadian stations (12 removed) and grid points
- Output: `us_coastal_cities.csv` (4.2 KB)

### Stage 3: Extraction
**Script:** `src/scripts/extract_us_projections.py`  
**Process:**
1. Read NetCDF files for 3 scenarios (SSP1-1.9, SSP2-4.5, SSP5-8.5)
2. Extract projections at three percentiles:
   - 50th percentile (median)
   - 17th percentile (lower bound)
   - 83rd percentile (upper bound)
3. Select years: 2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100, 2110, 2120, 2130, 2140, 2150 (14 years)
4. Match PSMSL IDs to US cities
5. Calculate risk levels based on median projections
6. Output: `us_projections.json` (~95 KB)

**Runtime:** ~15-20 seconds  
**Compression:** 9.2 GB → 95 KB (99.999% reduction)

### Stage 4: Risk Classification
**Algorithm:**
```python
if median_sea_level_rise_2100 < 200mm:
    risk = "low"
elif median_sea_level_rise_2100 < 400mm:
    risk = "moderate"
else:
    risk = "high"
```

**Results (SSP2-4.5, Year 2100):**
- High risk: ~15-20 cities (> 40cm)
- Moderate: ~80-90 cities (20-40cm)
- Low: ~30-40 cities (< 20cm)
- Total: 141 US coastal cities

### Stage 5: US Average Calculation
**Script:** `src/scripts/sea_level_us_average.py`  
**Process:**
1. Load same 141 US coastal cities from `us_coastal_cities.csv`
2. Extract projections for all 3 scenarios (SSP1-1.9, SSP2-4.5, SSP5-8.5)
3. Calculate average across cities for each year/scenario
4. Extract 17th, 50th (median), and 83rd percentiles
5. Output: `us_sea_level_average.csv` (~3 KB)

**Purpose:** Provides national average baseline for city-specific comparisons

### Stage 6: Visualization
**Framework:** D3.js v7 + Observable Framework  
**Two complementary views:**
1. **Spatial (Map):**
   - Albers USA projection (includes AK/HI insets)
   - Color-coded risk levels: green (low), orange (moderate), red (high)
   - Zoom/pan for detailed exploration
   - Click to select city
2. **Temporal (Line Chart):**
   - US average projections (2020-2150)
   - Uncertainty bands (17th-83rd percentile, ~66% confidence)
   - City overlay (dashed lines) when selected
   - Scenario comparison toggle

**Interactive features:**
- Synchronized controls (scenario selector, year slider)
- Cross-chart linking (map click → line chart update)
- Hover tooltips with city-specific data
- Clear selection button

---

## File Organization

### Processed Data (`src/data/processed/`)
**Actively used in visualization:**
- `us_coastal_cities.csv` (4.2 KB) - 141 US cities with coordinates
- `us_projections.json` (95 KB) - City-specific projections (14 years, 3 scenarios, median + uncertainty)
- `us_sea_level_average.csv` (3 KB) - National average projections
- `us-states-10m.json` (112 KB) - US states TopoJSON

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
- Coordinate ranges verified (lat: -90 to 90, lon: -180 to 180)
- PSMSL IDs unique and cross-referenced
- Projection values physically reasonable
- Risk classifications align with IPCC thresholds

### Limitations
- Decadal time steps only (no yearly data available in source)
- Uncertainty ranges show 17th-83rd percentile (~66% confidence); extreme tail risks not fully captured
- No population or economic impact data integrated
- Projections represent relative sea level rise (includes regional subsidence/uplift)
- Low-probability, high-impact scenarios (e.g., rapid ice sheet collapse) not included in confidence bands

### Geographic Coverage
**Total: 141 US coastal cities**
- **East Coast:** ~58 cities - New York, Boston, Miami, Charleston
- **West Coast:** ~45 cities - San Francisco, Los Angeles, Seattle, San Diego
- **Gulf Coast:** ~20 cities - Galveston, Key West, Pensacola
- **Alaska:** ~13 cities - Juneau, Sitka, Ketchikan
- **Hawaii:** ~3 cities - Honolulu, Hilo
- **Puerto Rico:** ~2 cities

*Note: 12 Canadian cities were removed from the original dataset to focus on US-only projections*

---

## Technical Implementation

### Tools & Libraries
- **Data Processing:** Python 3, netCDF4, NumPy
- **Visualization:** D3.js v7, Observable Framework, TopoJSON
- **Map Projection:** D3 Albers USA

### Performance
- Total data load: ~215 KB (optimized for web)
- Map render time: < 100ms (141 cities)
- Line chart render time: < 150ms (with uncertainty bands)
- Interaction latency: < 10ms (slider/selector updates)
- Cross-chart update: < 50ms (city selection)

---

## Citations

**IPCC AR6 Data:**
Garner, G. G., et al., 2021. IPCC AR6 Sea Level Projections. Version 20210809. [doi:10.5281/zenodo.5914709](https://doi.org/10.5281/zenodo.5914709)

**IPCC Chapter:**
Fox-Kemper, B., et al., 2021. Ocean, Cryosphere and Sea Level Change. In *Climate Change 2021: The Physical Science Basis. IPCC AR6*. [doi:10.1017/9781009157896.011](https://doi.org/10.1017/9781009157896.011)

**FACTS Model:**
Kopp, R. E., et al., 2023. The Framework for Assessing Changes To Sea-Level (FACTS) v1.0. *Geoscientific Model Development*, 16, 7461–7489. [doi:10.5194/gmd-16-7461-2023](https://doi.org/10.5194/gmd-16-7461-2023)

**Design Inspiration:**
NASA Sea Level Projection Tool. [sealevel.nasa.gov/ipcc-ar6-sea-level-projection-tool](https://sealevel.nasa.gov/ipcc-ar6-sea-level-projection-tool)

**License:** Creative Commons Attribution 4.0 International (CC BY 4.0)

---

**Team:** Megan Fung, Noah Scott, Archie Phyo
