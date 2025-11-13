---
title: Sea Level Rise Projections
theme: light
toc: true
---

# Sea Level Rise: US Coastal Cities

Interactive visualization of projected sea level rise for 153 US coastal cities (2030-2150) based on IPCC AR6 climate models.

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
// Scenario selector
const scenarioOptions = [
  {value: "ssp119", label: "Low Emissions (SSP1-1.9)"},
  {value: "ssp245", label: "Moderate Emissions (SSP2-4.5)"},
  {value: "ssp585", label: "High Emissions (SSP5-8.5)"}
];
const selectedScenario = view(Inputs.select(scenarioOptions, {
  label: "Emission Scenario",
  value: "ssp245",
  format: d => d.label
}));
```

```js
// Year slider
const selectedYear = view(Inputs.range([2030, 2150], {
  label: "Year",
  step: 20,
  value: 2100
}));
```

```js
// Process cities with projections
const enrichedCities = cities.map(city => {
  const projData = projectionsData[city.psmsl_id];
  if (!projData || !projData.projections[selectedScenario.value]) {
    return null;
  }
  
  const yearStr = String(selectedYear);
  const projection = projData.projections[selectedScenario.value][yearStr];
  
  return {
    ...city,
    name: projData.name,
    projection_mm: projection,
    projection_cm: projection ? (projection / 10).toFixed(1) : null,
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
// Map visualization function
function createUSMap(cities, {width} = {}) {
  const height = width * 0.6;
  
  // Create Albers USA projection (includes AK/HI insets)
  const projection = d3.geoAlbersUsa()
    .scale(width * 1.3)
    .translate([width / 2, height / 2]);
  
  const path = d3.geoPath(projection);
  
  // Create SVG
  const svg = d3.create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height])
    .attr("style", "max-width: 100%; height: auto;");
  
  // Draw states
  const states = topojson.feature(us, us.objects.states);
  svg.append("g")
    .selectAll("path")
    .data(states.features)
    .join("path")
    .attr("fill", "#f9fafb")
    .attr("stroke", "#d1d5db")
    .attr("stroke-width", 0.5)
    .attr("d", path);
  
  // Create tooltip div
  const tooltip = d3.select("body")
    .append("div")
    .attr("class", "map-tooltip")
    .style("opacity", 0);
  
  // Plot cities as points
  const cityPoints = svg.append("g")
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
    .attr("r", 4)
    .attr("fill", d => getRiskColor(d.projection_mm))
    .attr("fill-opacity", 0.8)
    .attr("stroke", "#fff")
    .attr("stroke-width", 1)
    .style("cursor", "pointer")
    .on("mouseover", function(event, d) {
      d3.select(this)
        .attr("r", 6)
        .attr("stroke-width", 2);
      
      tooltip.transition()
        .duration(200)
        .style("opacity", 0.95);
      
      const riskLabel = d.projection_mm < 200 ? "Low" : 
                        d.projection_mm < 400 ? "Moderate" : "High";
      
      tooltip.html(`
        <strong>${d.name.replace(/_/g, " ")}</strong><br/>
        Sea Level Rise: <strong>${d.projection_cm} cm</strong><br/>
        Risk Level: <strong>${riskLabel}</strong>
      `)
        .style("left", (event.pageX + 10) + "px")
        .style("top", (event.pageY - 28) + "px");
    })
    .on("mouseout", function() {
      d3.select(this)
        .attr("r", 4)
        .attr("stroke-width", 1);
      
      tooltip.transition()
        .duration(500)
        .style("opacity", 0);
    });
  
  // Filter out cities that couldn't be projected (outside map bounds)
  svg.selectAll("circle")
    .filter(d => {
      const coords = projection([d.longitude, d.latitude]);
      return !coords;
    })
    .remove();
  
  return svg.node();
}
```

<div class="card">
  ${resize((width) => createUSMap(enrichedCities, {width}))}
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
- Extracted 153 US coastal cities from 66,190 global locations
- Filtered geographic bounds: mainland US, Alaska, Hawaii, Puerto Rico
- Converted formats from tab-separated to CSV for web compatibility

### Stage 3: Projection Data Extraction
- Processed NetCDF files using Python script
- Extracted median projections for 3 scenarios (SSP1-1.9, SSP2-4.5, SSP5-8.5)
- Selected key years: 2030, 2050, 2100, 2150
- Generated compact JSON (70 KB) from large binary files (9.2 GB)

### Stage 4: Risk Classification
- Calculated risk levels based on 2100 projections under SSP2-4.5
- **Thresholds:** Low (< 20cm), Moderate (20-40cm), High (> 40cm)
- Result: 13 high risk, 88 moderate, 38 low risk cities

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



**Primary Data:** [IPCC AR6 Sea Level Projections](https://doi.org/10.5281/zenodo.5914709) via NASA/JPL  
**Location Data:** Permanent Service for Mean Sea Level (PSMSL) tide gauge network  
**Cartography:** US Atlas TopoJSON from Observable

---


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
</style>

