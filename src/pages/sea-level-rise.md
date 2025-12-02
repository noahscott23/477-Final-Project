---
title: Sea Level Rise Projections
theme: light
toc: true
---

# Sea Level Rise: US Coastal Cities

Interactive visualization of projected sea level rise for 141 US coastal cities (2020-2150) based on IPCC AR6 climate models. Projections include uncertainty ranges (17th-83rd percentile, ~66% confidence interval).

**Interactive Features:**
- 🔍 **Zoom & Pan:** Scroll to zoom, drag to pan across the map
- 🎯 **City Selection:** Click any city to select it and see detailed time series
- 🔗 **Cross-Chart Linking:** Selected cities link to the time series chart
- 📊 **Uncertainty:** Hover to see projection ranges reflecting scientific uncertainty

```js
// Load US coastal cities and projections
const cities = FileAttachment("../data/processed/us_coastal_cities.csv").csv({typed: true});
const projectionsData = FileAttachment("../data/processed/us_projections.json").json();
```

```js
// Create a world map visualization with D3
import * as d3 from "npm:d3";
import * as topojson from "npm:topojson-client";

// Load US states map data
const us = FileAttachment("../data/processed/us-states-10m.json").json();
```

```js
// Read URL parameters to restore filters when navigating back
const urlParams = new URLSearchParams(window.location.search);
const urlScenario = urlParams.get('scenario');
const urlYear = urlParams.get('year');

// Scenario selector
const scenarioOptions = [
  {value: "ssp119", label: "Low Emissions (SSP1-1.9)"},
  {value: "ssp245", label: "Moderate Emissions (SSP2-4.5)"},
  {value: "ssp585", label: "High Emissions (SSP5-8.5)"}
];

// Restore scenario from URL if present
const defaultScenario = urlScenario 
  ? scenarioOptions.find(s => s.value === urlScenario || s.value + "_mm" === urlScenario) || scenarioOptions[1]
  : scenarioOptions[1];

const selectedScenario = view(Inputs.select(scenarioOptions, {
  label: "Emission Scenario",
  value: defaultScenario,
  format: d => d.label
}));
```

```js
// Year slider (aligned with line chart - every 10 years)
// Restore year from URL if present
const defaultYear = urlYear ? parseInt(urlYear) : 2100;

const selectedYear = view(Inputs.range([2020, 2150], {
  label: "Year",
  step: 10,
  value: defaultYear
}));
```


```js
// Process cities with projections (now includes uncertainty bounds)
const enrichedCities = cities.map(city => {
  const projData = projectionsData[city.psmsl_id];
  if (!projData || !projData.projections[selectedScenario.value]) {
    return null;
  }
  
  const yearStr = String(selectedYear);
  const projectionData = projData.projections[selectedScenario.value][yearStr];
  
  // Handle both old format (number) and new format ({median, lower, upper})
  const median = projectionData?.median !== undefined ? projectionData.median : projectionData;
  const lower = projectionData?.lower !== undefined ? projectionData.lower : median;
  const upper = projectionData?.upper !== undefined ? projectionData.upper : median;
  
  return {
    ...city,
    name: projData.name,
    projection_mm: median,
    projection_cm: median ? (median / 10).toFixed(1) : null,
    lower_mm: lower,
    upper_mm: upper,
    lower_cm: lower ? (lower / 10).toFixed(1) : null,
    upper_cm: upper ? (upper / 10).toFixed(1) : null,
    uncertainty_range: upper && lower ? ((upper - lower) / 10).toFixed(1) : null,
    risk_level: projData.risk_level
  };
}).filter(d => d !== null && d.projection_mm !== null);
```

```js
// Count cities by risk level for selected scenario/year
const riskCounts = enrichedCities.reduce((acc, city) => {
  // Calculate risk for current year
  const proj = city.projection_mm;
  let risk;
  if (proj < 200) risk = 'low';
  else if (proj < 400) risk = 'moderate';
  else risk = 'high';
  
  acc[risk] = (acc[risk] || 0) + 1;
  return acc;
}, {low: 0, moderate: 0, high: 0});
```

<div class="grid grid-cols-3">
  <div class="card">
    <h2>🔴 High Risk</h2>
    <span class="big" style="color: #ef4444;">${riskCounts.high}</span>
    <p class="label">cities (> 40cm rise)</p>
  </div>
  <div class="card">
    <h2>🟡 Moderate Risk</h2>
    <span class="big" style="color: #f59e0b;">${riskCounts.moderate}</span>
    <p class="label">cities (20-40cm rise)</p>
  </div>
  <div class="card">
    <h2>🟢 Low Risk</h2>
    <span class="big" style="color: #22c55e;">${riskCounts.low}</span>
    <p class="label">cities (< 20cm rise)</p>
  </div>
</div>

```js
// Color scale for risk levels
function getRiskColor(projection_mm) {
  if (projection_mm < 200) return "#22c55e"; // green - low
  if (projection_mm < 400) return "#f59e0b"; // amber - moderate
  return "#ef4444"; // red - high
}
```

```js
// URL state management for selected city
const urlParams = new URLSearchParams(window.location.search);
const selectedCityId = urlParams.get('city');

function selectCity(psmslId) {
  const url = new URL(window.location);
  if (psmslId) {
    url.searchParams.set('city', psmslId);
  } else {
    url.searchParams.delete('city');
  }
  window.history.pushState({}, '', url);
  
  // Trigger a re-render by dispatching an event
  window.dispatchEvent(new Event('cityselected'));
}
```

```js
// Map visualization function with zoom/pan and city selection
function createUSMap(cities, {width, scenario, year} = {}) {
  const height = width * 0.6;
  
  // Create Albers USA projection (includes AK/HI insets)
  const projection = d3.geoAlbersUsa()
    .scale(width * 1.3)
    .translate([width / 2, height / 2]);
  
  const path = d3.geoPath(projection);
  
  // Create container div for SVG and controls
  const container = d3.create("div")
    .style("position", "relative");
  
  // Create SVG
  const svg = container.append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height])
    .attr("style", "max-width: 100%; height: auto; background: #f0f4f8; border-radius: 8px;");
  
  // Create zoom-able group
  const g = svg.append("g");
  
  // Draw states
  const states = topojson.feature(us, us.objects.states);
  g.append("g")
    .attr("class", "states")
    .selectAll("path")
    .data(states.features)
    .join("path")
    .attr("fill", "#f9fafb")
    .attr("stroke", "#d1d5db")
    .attr("stroke-width", 0.5)
    .attr("d", path);
  
  // Create tooltip div
  let tooltip = d3.select("body").selectAll(".map-tooltip").data([null]);
  tooltip = tooltip.enter()
    .append("div")
    .attr("class", "map-tooltip")
    .style("opacity", 0)
    .merge(tooltip);
  
  // Plot cities as points
  const citiesGroup = g.append("g").attr("class", "cities");
  
  const cityPoints = citiesGroup
    .selectAll("circle")
    .data(cities)
    .join("circle")
    .attr("cx", d => {
      const coords = projection([d.longitude, d.latitude]);
      return coords ? coords[0] : null;
    })
    .attr("cy", d => {
      const coords = projection([d.longitude, d.latitude]);
      return coords ? coords[1] : null;
    })
    .attr("r", d => String(d.psmsl_id) === selectedCityId ? 7 : 4)
    .attr("fill", d => getRiskColor(d.projection_mm))
    .attr("fill-opacity", d => String(d.psmsl_id) === selectedCityId ? 1 : 0.8)
    .attr("stroke", d => String(d.psmsl_id) === selectedCityId ? "#000" : "#fff")
    .attr("stroke-width", d => String(d.psmsl_id) === selectedCityId ? 2.5 : 1)
    .style("cursor", "pointer")
    .on("mouseover", function(event, d) {
      const isSelected = String(d.psmsl_id) === selectedCityId;
      d3.select(this)
        .attr("r", isSelected ? 8 : 6)
        .attr("stroke-width", isSelected ? 3 : 2);
      
      tooltip.transition()
        .duration(200)
        .style("opacity", 0.95);
      
      const riskLabel = d.projection_mm < 200 ? "Low" : 
                        d.projection_mm < 400 ? "Moderate" : "High";
      
      tooltip.html(`
        <strong>${d.name.replace(/_/g, " ")}</strong><br/>
        Sea Level Rise: <strong>${d.projection_cm} cm</strong><br/>
        <span style="font-size: 11px; color: #64748b;">Uncertainty: ${d.lower_cm}–${d.upper_cm} cm</span><br/>
        Risk Level: <strong>${riskLabel}</strong><br/>
        <span style="color: #6b7280; font-size: 12px;">${isSelected ? '✓ Selected - Click for details' : 'Click to view time series'}</span>
      `)
        .style("left", (event.pageX + 10) + "px")
        .style("top", (event.pageY - 28) + "px");
    })
    .on("mouseout", function(event, d) {
      const isSelected = String(d.psmsl_id) === selectedCityId;
      d3.select(this)
        .attr("r", isSelected ? 7 : 4)
        .attr("stroke-width", isSelected ? 2.5 : 1);
      
      tooltip.transition()
        .duration(500)
        .style("opacity", 0);
    })
    .on("click", function(event, d) {
      event.stopPropagation();
      
      // Navigate to time series chart with city, scenario, and year synced
      // Add "_mm" suffix to scenario for line chart format
      const url = `/pages/sea-level-over-time?city=${d.psmsl_id}&scenario=${scenario}_mm&year=${year}`;
      window.location.href = url;
    });
  
  // Filter out cities that couldn't be projected (outside map bounds)
  cityPoints
    .filter(d => {
      const coords = projection([d.longitude, d.latitude]);
      return !coords;
    })
    .remove();
  
  // Add zoom behavior
  const zoom = d3.zoom()
    .scaleExtent([1, 8])
    .on("zoom", (event) => {
      g.attr("transform", event.transform);
    });
  
  svg.call(zoom);
  
  // Reset zoom button
  const resetButton = container.append("button")
    .attr("class", "zoom-reset-btn")
    .style("position", "absolute")
    .style("top", "10px")
    .style("right", "10px")
    .style("padding", "8px 12px")
    .style("background", "white")
    .style("border", "1px solid #d1d5db")
    .style("border-radius", "6px")
    .style("cursor", "pointer")
    .style("font-size", "13px")
    .style("box-shadow", "0 2px 4px rgba(0,0,0,0.1)")
    .text("Reset Zoom")
    .on("click", () => {
      svg.transition()
        .duration(750)
        .call(zoom.transform, d3.zoomIdentity);
    });
  
  // Clear selection button (only show if city is selected)
  if (selectedCityId) {
    const clearButton = container.append("button")
      .attr("class", "clear-selection-btn")
      .style("position", "absolute")
      .style("top", "10px")
      .style("right", "110px")
      .style("padding", "8px 12px")
      .style("background", "#fef3c7")
      .style("border", "1px solid #fbbf24")
      .style("border-radius", "6px")
      .style("cursor", "pointer")
      .style("font-size", "13px")
      .style("box-shadow", "0 2px 4px rgba(0,0,0,0.1)")
      .text("Clear Selection")
      .on("click", () => {
        selectCity(null);
        window.location.reload();
      });
  }
  
  // Click on background to deselect
  svg.on("click", function(event) {
    if (event.target === this) {
      selectCity(null);
      cityPoints
        .attr("r", 4)
        .attr("fill-opacity", 0.8)
        .attr("stroke", "#fff")
        .attr("stroke-width", 1);
    }
  });
  
  return container.node();
}
```

<div class="card">
  ${resize((width) => createUSMap(enrichedCities, {
    width, 
    scenario: selectedScenario.value,
    year: selectedYear
  }))}
</div>

<div class="legend-container">
  <div class="legend-item">
    <span class="legend-dot" style="background: #22c55e;"></span>
    <span>Low Risk (< 20cm)</span>
  </div>
  <div class="legend-item">
    <span class="legend-dot" style="background: #f59e0b;"></span>
    <span>Moderate Risk (20-40cm)</span>
  </div>
  <div class="legend-item">
    <span class="legend-dot" style="background: #ef4444;"></span>
    <span>High Risk (> 40cm)</span>
  </div>
</div>

---

## Data Pipeline

### Stage 1: Data Acquisition
- Downloaded IPCC AR6 sea level projections from [Zenodo](https://doi.org/10.5281/zenodo.5914709) (9.2 GB)
- Obtained PSMSL tide gauge locations with coordinates
- Downloaded US states map TopoJSON for visualization

### Stage 2: Data Filtering & Transformation
- Extracted 141 US coastal cities from 66,190 global locations
- Filtered geographic bounds: mainland US, Alaska, Hawaii, Puerto Rico (excluded Canadian cities)
- Converted formats from tab-separated to CSV for web compatibility

### Stage 3: Projection Data Extraction
- Processed NetCDF files using Python script
- Extracted median projections for 3 scenarios (SSP1-1.9, SSP2-4.5, SSP5-8.5)
- Selected years: 2020-2150 in 10-year increments (aligned with line chart visualization)
- Generated compact JSON (152 KB) from large binary files (9.2 GB)

### Stage 4: Risk Classification
- Calculated risk levels based on 2100 projections under SSP2-4.5
- **Thresholds:** Low (< 20cm), Moderate (20-40cm), High (> 40cm)
- Result: 119 high risk, 6 moderate, 12 low risk cities

### Stage 5: Visualization
- Built interactive D3.js map with Albers USA projection
- Implemented reactive controls (scenario selector, year slider)
- Added hover tooltips and dynamic statistics
- Color-coded cities by projected risk level

---

## Emission Scenarios

- **SSP1-1.9** (Low): Strong mitigation, limits warming to 1.5°C
- **SSP2-4.5** (Moderate): Middle-of-the-road, current policies trajectory
- **SSP5-8.5** (High): High emissions, fossil fuel-intensive development

---

## Implemented Features ✅

- ✅ **Interactive Zoom & Pan:** Users can zoom (scroll) and pan (drag) to explore specific coastal regions
- ✅ **City Selection:** Click any city to select it and view its detailed projection trajectory
- ✅ **Cross-Chart Linking:** Selected cities automatically link to the time series chart for detailed temporal analysis
- ✅ **URL State Management:** Selected cities persist in the URL for sharing specific views

## Future Enhancements

- **Multi-Scenario Comparison:** Side-by-side map views to compare different emission scenarios simultaneously
- **City Search & Filtering:** Add search functionality and filters by state, risk level, or population size
- **Historical Data Integration:** Overlay actual historical sea level measurements from tide gauges (1900-2023)
- **Uncertainty Visualization:** Display confidence intervals alongside median projections
- **Export & Share:** Enable users to download maps as images

---

## Citations/ References 

**Primary Data:** [IPCC AR6 Sea Level Projections](https://doi.org/10.5281/zenodo.5914709) via NASA/JPL  
**Location Data:** Permanent Service for Mean Sea Level (PSMSL) tide gauge network  
**Cartography:** US Atlas TopoJSON from Observable

**IPCC Chapter:**
Fox-Kemper, B., H.T. Hewitt, C. Xiao, G. Aðalgeirsdóttir, S.S. Drijfhout, T.L. Edwards, N.R. Golledge, M. Hemer, R.E. Kopp, G. Krinner, A. Mix, D. Notz, S. Nowicki, I.S. Nurhati, L. Ruiz, J.-B. Sallée, A.B.A. Slangen, and Y. Yu, 2021: Ocean, Cryosphere and Sea Level Change. In *Climate Change 2021: The Physical Science Basis. Contribution of Working Group I to the Sixth Assessment Report of the Intergovernmental Panel on Climate Change* [Masson-Delmotte, V., P. Zhai, A. Pirani, et al. (eds.)]. Cambridge University Press, pp. 1211–1362, [doi:10.1017/9781009157896.011](https://doi.org/10.1017/9781009157896.011)

**FACTS Model:**
Kopp, R. E., Garner, G. G., Hermans, T. H. J., Jha, S., Kumar, P., Reedy, A., Slangen, A. B. A., Turilli, M., Edwards, T. L., Gregory, J. M., Koubbe, G., Levermann, A., Merzky, A., Nowicki, S., Palmer, M. D., & Smith, C. (2023). The Framework for Assessing Changes To Sea-Level (FACTS) v1.0: A platform for characterizing parametric and structural uncertainty in future global, relative, and extreme sea-level change. *Geoscientific Model Development*, 16, 7461–7489. [doi:10.5194/gmd-16-7461-2023](https://doi.org/10.5194/gmd-16-7461-2023)

**Dataset:**
Garner, G. G., T. Hermans, R. E. Kopp, A. B. A. Slangen, T. L. Edwards, A. Levermann, S. Nowikci, M. D. Palmer, C. Smith, B. Fox-Kemper, H. T. Hewitt, C. Xiao, et al., 2021. IPCC AR6 Sea Level Projections. Version 20210809. Dataset accessed 2024-11-13 at [doi:10.5281/zenodo.5914709](https://doi.org/10.5281/zenodo.5914709)

**Acknowledgement:**
We thank the projection authors for developing and making the sea-level rise projections available, multiple funding agencies for supporting the development of the projections, and the NASA Sea Level Change Team for developing and hosting the IPCC AR6 Sea Level Projection Tool.

<style>
.big {
  font-size: 3rem;
  font-weight: 700;
  color: var(--theme-foreground-focus);
}

.card h2 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--theme-foreground-muted);
  margin-bottom: 0.5rem;
}

.card .label {
  font-size: 0.875rem;
  color: var(--theme-foreground-muted);
  margin-top: 0.25rem;
}

.map-tooltip {
  position: absolute;
  text-align: left;
  padding: 12px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid #ccc;
  border-radius: 8px;
  pointer-events: none;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  font-family: var(--sans-serif);
  line-height: 1.5;
  z-index: 1000;
}

.legend-container {
  display: flex;
  gap: 2rem;
  justify-content: center;
  margin-top: 1rem;
  padding: 1rem;
  background: var(--theme-background-alt);
  border-radius: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 14px;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid #fff;
}

.city-selection-banner {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border: 2px solid #fbbf24;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(251, 191, 36, 0.15);
}

.city-selection-banner strong {
  font-size: 16px;
  color: #92400e;
}
</style>

