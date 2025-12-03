---
title: Sea Level Rise — US Coastal Analysis
theme: light
toc: true
---

# US Coastal Sea Level Rise: Where, When, and How Fast?

<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 24px; border-radius: 12px; margin-bottom: 32px;">
  <h2 style="margin-top: 0; color: white;">US Sea Level Rise Through Two Lenses</h2>
  <p style="font-size: 16px; line-height: 1.6; margin-bottom: 16px;">
    This visualization explores IPCC AR6 sea level projections for <strong>141 US coastal cities</strong> (2020-2150) through complementary perspectives:
  </p>
  <div class="grid grid-cols-2" style="gap: 16px; margin-top: 16px;">
    <div style="background: rgba(255,255,255,0.15); padding: 16px; border-radius: 8px;">
      <strong style="font-size: 18px;">Spatial View (Map)</strong>
      <p style="margin-top: 8px; font-size: 14px;">WHERE is the risk? Which regions and cities are the most vulnerable?</p>
    </div>
    <div style="background: rgba(255,255,255,0.15); padding: 16px; border-radius: 8px;">
      <strong style="font-size: 18px;">Temporal View (Time Series)</strong>
      <p style="margin-top: 8px; font-size: 14px;">WHEN does risk accelerate? HOW FAST is sea level rising over time?</p>
    </div>
  </div>
  <p style="font-size: 14px; margin-top: 16px; margin-bottom: 0; opacity: 0.95;">
    <strong>Explore together:</strong> Click a city on the map to see its trajectory highlighted in the chart below. Adjust scenarios to compare different climate futures.
  </p>
</div>

## How to Use This Visualization

<div class="card" style="background: #f8fafc; border-left: 4px solid #3b82f6;">
  <ul style="margin: 0; padding-left: 20px;">
    <li><strong>Filters:</strong> Control both visualizations. Select an emission scenario and year.</li>
    <li><strong>Map exploration:</strong> Zoom (scroll) and pan (drag) to explore coastal regions in detail.</li>
    <li><strong>City selection:</strong> Click any city on the map to highlight its time series below.</li>
    <li><strong>Compare scenarios:</strong> Check "Compare all emission scenarios" to see how different climate futures diverge.</li>
    <li><strong>Uncertainty:</strong> Shaded bands and ranges show projection uncertainty (17th-83rd percentile, ~66% confidence).</li>
    <li><strong>Hover for details:</strong> Tooltips show exact values, uncertainty ranges, and comparisons.</li>
  </ul>
</div>

---

## Controls (Apply to Both Visualizations)

```js
import * as d3 from "npm:d3";
import * as topojson from "npm:topojson-client";

// Load all data
const cities = FileAttachment("../data/processed/us_coastal_cities.csv").csv({typed: true});
const projectionsData = FileAttachment("../data/processed/us_projections.json").json();
const usAvg = await FileAttachment("../data/processed/us_sea_level_average.csv").csv({ typed: true });
const us = FileAttachment("../data/processed/us-states-10m.json").json();

// Clean US average data (includes uncertainty bounds)
usAvg.forEach(d => {
  d.year = +d.year;
  d.ssp119_mm = +d.ssp119_mm;
  d.ssp119_lower = +d.ssp119_lower;
  d.ssp119_upper = +d.ssp119_upper;
  d.ssp245_mm = +d.ssp245_mm;
  d.ssp245_lower = +d.ssp245_lower;
  d.ssp245_upper = +d.ssp245_upper;
  d.ssp585_mm = +d.ssp585_mm;
  d.ssp585_lower = +d.ssp585_lower;
  d.ssp585_upper = +d.ssp585_upper;
});
```

```js
// Shared controls
const scenarioOptions = [
  {value: "ssp119", label: "Low Emissions (SSP1-1.9)"},
  {value: "ssp245", label: "Moderate Emissions (SSP2-4.5)"},
  {value: "ssp585", label: "High Emissions (SSP5-8.5)"}
];

const selectedScenario = view(Inputs.select(scenarioOptions, {
  label: "Emission Scenario",
  value: scenarioOptions[1],  // Default to moderate
  format: d => d.label
}));

const selectedYear = view(Inputs.range([2020, 2150], {
  label: "Year",
  step: 10,
  value: 2100
}));
```

```js
// Selected city using Inputs.bind for programmatic control
const urlParams = new URLSearchParams(window.location.search);
const urlCityId = urlParams.get('city');

const cityInput = Inputs.select(
  [null, ...cities.map(c => String(c.psmsl_id))],
  { value: urlCityId }
);

const selectedCityId = Generators.input(cityInput);
```

---

## WHERE Is The Risk? (Spatial Distribution)

**Explore which coastal cities and regions face the greatest sea level rise threat.** Cities are color-coded by risk level at the selected year and scenario. Zoom into dense coastal areas to see individual cities clearly.

```js
// Process cities with current scenario/year
const enrichedCities = cities.map(city => {
  const projData = projectionsData[city.psmsl_id];
  if (!projData || !projData.projections[selectedScenario.value]) {
    return null;
  }
  
  const yearStr = String(selectedYear);
  const projectionData = projData.projections[selectedScenario.value][yearStr];
  
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
function createUSMap(cities, topoData, scenario, year, currentSelectedCityId, onCityClick, cityInputElement) {
  const width = 975;
  const height = 610;

  const svg = d3.create("svg")
    .attr("viewBox", [0, 0, width, height])
    .style("width", "100%")
    .style("height", "auto");

  // Set up Albers USA projection
  const projection = d3.geoAlbersUsa()
    .scale(1300)
    .translate([width / 2, height / 2]);

  const path = d3.geoPath(projection);

  // Container for zoom/pan
  const g = svg.append("g");

  // Draw US states
  const states = topojson.feature(topoData, topoData.objects.states);
  g.append("g")
    .selectAll("path")
    .data(states.features)
    .join("path")
    .attr("fill", "#e5e7eb")
    .attr("stroke", "#fff")
    .attr("stroke-width", 1)
    .attr("d", path);

  // Color scale for risk levels
  const riskColors = {
    low: "#22c55e",
    moderate: "#f59e0b",
    high: "#ef4444",
    unknown: "#94a3b8"
  };

  const getRiskLevel = (proj_mm) => {
    if (proj_mm < 200) return "low";
    if (proj_mm < 400) return "moderate";
    return "high";
  };

  // Tooltip
  const tooltip = d3.select("body").append("div")
    .attr("class", "map-tooltip")
    .style("opacity", 0)
    .style("position", "absolute")
    .style("background", "white")
    .style("padding", "10px 12px")
    .style("border-radius", "6px")
    .style("box-shadow", "0 4px 12px rgba(0,0,0,0.15)")
    .style("pointer-events", "none")
    .style("font-size", "13px")
    .style("z-index", "1000");

  // Draw city points
  const cityPoints = g.append("g")
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
    .attr("r", d => String(d.psmsl_id) === currentSelectedCityId ? 7 : 4)
    .attr("fill", d => {
      const risk = getRiskLevel(d.projection_mm);
      return riskColors[risk];
    })
    .attr("fill-opacity", 0.8)
    .attr("stroke", d => String(d.psmsl_id) === currentSelectedCityId ? "#000" : "#fff")
    .attr("stroke-width", d => String(d.psmsl_id) === currentSelectedCityId ? 2.5 : 1)
    .style("cursor", "pointer")
    .on("mouseover", function(event, d) {
      const isSelected = String(d.psmsl_id) === currentSelectedCityId;
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
        <span style="color: #6b7280; font-size: 12px;">${isSelected ? '✓ Selected' : 'Click to select'}</span>
      `)
        .style("left", (event.pageX + 10) + "px")
        .style("top", (event.pageY - 28) + "px");
    })
    .on("mouseout", function(event, d) {
      const isSelected = String(d.psmsl_id) === currentSelectedCityId;
      d3.select(this)
        .attr("r", isSelected ? 7 : 4)
        .attr("stroke-width", isSelected ? 2.5 : 1);
      
      tooltip.transition()
        .duration(500)
        .style("opacity", 0);
    })
    .on("click", function(event, d) {
      event.stopPropagation();
      
      // Hide tooltip immediately on click
      tooltip.transition()
        .duration(200)
        .style("opacity", 0);
      
      // Update selected city via callback
      if (onCityClick) {
        onCityClick(String(d.psmsl_id));
      }
      
      // Scroll to line chart section
      setTimeout(() => {
        const lineChartSection = document.getElementById('line-chart-section');
        if (lineChartSection) {
          lineChartSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
    });

  // Zoom behavior
  const zoom = d3.zoom()
    .scaleExtent([1, 8])
    .on("zoom", (event) => {
      g.attr("transform", event.transform);
    });

  svg.call(zoom);

  // Reset zoom button
  const resetButton = svg.append("g")
    .attr("cursor", "pointer")
    .on("click", () => {
      svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
    });

  resetButton.append("rect")
    .attr("x", width - 120)
    .attr("y", 10)
    .attr("width", 110)
    .attr("height", 30)
    .attr("rx", 6)
    .attr("fill", "#3b82f6")
    .attr("fill-opacity", 0.9);

  resetButton.append("text")
    .attr("x", width - 65)
    .attr("y", 30)
    .attr("text-anchor", "middle")
    .attr("fill", "white")
    .attr("font-size", 13)
    .attr("font-weight", "600")
    .text("Reset Zoom");

  // Clear Selection button (only shows if a city is selected)
  if (currentSelectedCityId && cityInputElement) {
    const clearButton = svg.append("g")
      .attr("cursor", "pointer")
      .on("click", () => {
        cityInputElement.value = null;
        cityInputElement.dispatchEvent(new Event("input", { bubbles: true }));
      });

    clearButton.append("rect")
      .attr("x", width - 250)
      .attr("y", 10)
      .attr("width", 120)
      .attr("height", 30)
      .attr("rx", 6)
      .attr("fill", "#ef4444")
      .attr("fill-opacity", 0.9);

    clearButton.append("text")
      .attr("x", width - 190)
      .attr("y", 30)
      .attr("text-anchor", "middle")
      .attr("fill", "white")
      .attr("font-size", 13)
      .attr("font-weight", "600")
      .text("✕ Clear Selection");
  }

  return svg.node();
}
```

```js
// Map visualization
const currentSelectedCity = selectedCityId || null;
```

<div class="card">
  ${resize(width => {
    const mapSvg = createUSMap(
      enrichedCities, 
      us, 
      selectedScenario.value, 
      selectedYear,
      currentSelectedCity,
      // Callback to update city selection
      (cityId) => {
        cityInput.value = cityId;
        cityInput.dispatchEvent(new Event("input", {bubbles: true}));
      },
      cityInput
    );
    return mapSvg;
  })}
</div>

**Key Insights:**
- **Geographic patterns:** Gulf Coast and Mid-Atlantic cities typically face higher risk due to regional subsidence and ocean dynamics
- **Alaska difference:** Some Alaskan cities show lower projections due to glacial isostatic adjustment (land rising)
- **Zoom to explore:** Dense coastal regions (NYC, SF Bay, South Florida) require zooming to see individual cities

---

<div id="line-chart-section"></div>

## HOW FAST Is It Rising? (Temporal Acceleration)

**Explore when sea levels cross critical thresholds and how quickly they accelerate.** The chart shows US average projections with uncertainty bands. Click a city on the map above to overlay its trajectory (dashed lines) for comparison.

```js
// Get selected city data if available (depends on selectedCityId)
const selectedCityData = selectedCityId ? (() => {
  const currentCityId = selectedCityId;
  try {
    const cityInfo = cities.find(c => String(c.psmsl_id) === currentCityId);
    const projData = projectionsData[currentCityId];
    
    if (cityInfo && projData && projData.projections) {
      const cityTimeSeries = Object.keys(projData.projections.ssp119 || {}).map(year => {
        const ssp119 = projData.projections.ssp119[year];
        const ssp245 = projData.projections.ssp245[year];
        const ssp585 = projData.projections.ssp585[year];
        
        return {
          year: +year,
          ssp119_mm: ssp119?.median || ssp119,
          ssp119_lower: ssp119?.lower || ssp119?.median || ssp119,
          ssp119_upper: ssp119?.upper || ssp119?.median || ssp119,
          ssp245_mm: ssp245?.median || ssp245,
          ssp245_lower: ssp245?.lower || ssp245?.median || ssp245,
          ssp245_upper: ssp245?.upper || ssp245?.median || ssp245,
          ssp585_mm: ssp585?.median || ssp585,
          ssp585_lower: ssp585?.lower || ssp585?.median || ssp585,
          ssp585_upper: ssp585?.upper || ssp585?.median || ssp585
        };
      });
      
      return {
        id: currentCityId,
        name: projData.name.replace(/_/g, " "),
        timeSeries: cityTimeSeries
      };
    }
  } catch (e) {
    return null;
  }
  return null;
})() : null;

selectedCityData
```

```js
// Line chart specific: Toggle to show all scenarios (define early for Card 3 logic)
const showAllScenarios = view(Inputs.toggle({
  label: "Compare all emission scenarios", 
  value: false
}));
```

```js
// Statistics cards - calculate before rendering
const currentScenarioKey = selectedScenario.value + "_mm";
const currentYearData = usAvg.find(d => d.year === selectedYear);
const baselineData = usAvg.find(d => d.year === 2020);

const currentRise = currentYearData ? currentYearData[currentScenarioKey] : null;
const baselineRise = baselineData ? baselineData[currentScenarioKey] : null;
const riseFromBaseline = currentRise && baselineRise ? currentRise - baselineRise : null;

const yearsPassed = selectedYear - 2020;
const avgRate = riseFromBaseline && yearsPassed > 0 ? (riseFromBaseline / yearsPassed) : null;

// Calculate city-specific stats if city is selected
const cityCurrentData = selectedCityData?.timeSeries?.find(d => d.year === selectedYear);
const cityRise = cityCurrentData ? cityCurrentData[currentScenarioKey] : null;
const percentDiff = cityRise && currentRise ? ((cityRise - currentRise) / currentRise * 100) : null;

// If no city selected, find the most at-risk city for current scenario/year
const mostAtRiskCity = !selectedCityData ? (() => {
  const citiesWithProjection = enrichedCities
    .filter(c => c.projection_mm != null)
    .sort((a, b) => b.projection_mm - a.projection_mm);
  
  const topCity = citiesWithProjection[0];
  if (!topCity) return null;
  
  return {
    name: topCity.name.replace(/_/g, " "),
    rise_cm: topCity.projection_cm,
    rise_mm: topCity.projection_mm,
    percentAboveAvg: currentRise ? ((topCity.projection_mm - currentRise) / currentRise * 100) : null
  };
})() : null;

// When comparing all scenarios, calculate range across scenarios (for Card 3)
// Note: This is calculated before the toggle value is available, so we calculate it always
// The card will decide whether to show it based on showAllScenarios
const scenarioRange = currentYearData ? (() => {
  const lowRise = currentYearData.ssp119_mm / 10;
  const highRise = currentYearData.ssp585_mm / 10;
  const range = highRise - lowRise;
  return { lowRise, highRise, range };
})() : null;
```

<div class="grid grid-cols-3">
  <div class="card">
    <h2>Rise by ${selectedYear}</h2>
    <span class="big">${currentRise ? (currentRise / 10).toFixed(1) : '—'} cm</span>
    <span class="label">US average</span>
    ${currentYearData ? html`<p style="font-size: 12px; color: #64748b; margin-top: 4px;">Range: ${(currentYearData[selectedScenario.value + '_lower'] / 10).toFixed(1)}–${(currentYearData[selectedScenario.value + '_upper'] / 10).toFixed(1)} cm</p>` : ''}
  </div>
  <div class="card">
    <h2>Average Rate</h2>
    <span class="big">${avgRate ? (avgRate / 10).toFixed(1) : '—'} mm/yr</span>
    <span class="label">2020–${selectedYear}</span>
  </div>
  <div class="card">
    ${selectedCityData ? html`
      <h2>${selectedCityData.name}</h2>
      <span class="big">${(cityRise / 10).toFixed(1)} cm</span>
      <span class="label">
        ${percentDiff !== null ? html`
          <span style="color: ${percentDiff > 0 ? '#ef4444' : '#22c55e'}; font-weight: 600;">
            ${percentDiff > 0 ? '+' : ''}${percentDiff.toFixed(0)}%
          </span> vs US avg
          <br/>US avg: ${(currentRise / 10).toFixed(1)} cm
        ` : 'by ' + selectedYear}
      </span>
    ` : showAllScenarios && scenarioRange ? html`
      <h2>Scenario Range</h2>
      <span class="big">${scenarioRange.range.toFixed(1)} cm</span>
      <span class="label">
        Low: ${scenarioRange.lowRise.toFixed(1)} cm
        <br/>High: ${scenarioRange.highRise.toFixed(1)} cm
      </span>
    ` : mostAtRiskCity ? html`
      <h2>Highest Risk City</h2>
      <span class="big">${mostAtRiskCity.rise_cm} cm</span>
      <span class="label">
        ${mostAtRiskCity.name}
        ${mostAtRiskCity.percentAboveAvg ? html`
          <br/><span style="color: #ef4444; font-weight: 600;">
            +${mostAtRiskCity.percentAboveAvg.toFixed(0)}%
          </span> vs US avg
        ` : ''}
      </span>
    ` : html`<p class="label" style="margin: 0;">No data available</p>`}
  </div>
</div>

```js
// Event markers for historical context
const events = [
  { year: 2050, scenario: "ssp119_mm", label: "Paris Agreement 1.5°C target" },
  { year: 2100, scenario: "ssp245_mm", label: "End of century baseline" },
  { year: 2100, scenario: "ssp585_mm", label: "High emissions endpoint" }
];

function getYearPoint(data, year) {
  // Exact match if available
  let exact = data.find(d => d.year === year);
  if (exact) return exact;

  // Otherwise interpolate between nearest years
  const sorted = data.slice().sort((a, b) => a.year - b.year);
  const before = d3.max(sorted.filter(d => d.year < year), d => d.year);
  const after = d3.min(sorted.filter(d => d.year > year), d => d.year);
  if (before == null || after == null) return null;
  
  const d0 = sorted.find(d => d.year === before);
  const d1 = sorted.find(d => d.year === after);
  const t = (year - d0.year) / (d1.year - d0.year);
  
  // Interpolate all fields
  const interpolated = { year };
  
  // Interpolate each scenario's median and uncertainty bounds
  ['ssp119', 'ssp245', 'ssp585'].forEach(scenario => {
    const mmKey = `${scenario}_mm`;
    const lowerKey = `${scenario}_lower`;
    const upperKey = `${scenario}_upper`;
    
    if (d0[mmKey] != null && d1[mmKey] != null) {
      interpolated[mmKey] = d0[mmKey] + t * (d1[mmKey] - d0[mmKey]);
    }
    if (d0[lowerKey] != null && d1[lowerKey] != null) {
      interpolated[lowerKey] = d0[lowerKey] + t * (d1[lowerKey] - d0[lowerKey]);
    }
    if (d0[upperKey] != null && d1[upperKey] != null) {
      interpolated[upperKey] = d0[upperKey] + t * (d1[upperKey] - d0[upperKey]);
    }
  });
  
  return interpolated;
}
```

```js
function seaLevelLineChart(data, { width, cityData, selectedScenario, selectedYear, showAll } = {}) {
  const height = 500;
  const margin = { top: 40, right: 200, bottom: 50, left: 60 };

  const svg = d3.create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height])
    .style("max-width", "100%")
    .style("background", "white")
    .style("border-radius", "12px");

  const filteredData = data.filter(d => d.year <= selectedYear);
  const filteredCityData = cityData?.timeSeries?.filter(d => d.year <= selectedYear) || null;

  const years = filteredData.map(d => d.year);
  const minYear = d3.min(years);
  const maxYear = d3.max(years);

  const allData = filteredCityData ? [...filteredData, ...filteredCityData] : filteredData;
  const x = d3.scaleLinear()
    .domain([minYear, maxYear])
    .range([margin.left, width - margin.right]);

  const y = d3.scaleLinear()
    .domain([0, d3.max(allData, d => d.ssp585_upper || d.ssp585_mm)])
    .nice()
    .range([height - margin.bottom, margin.top]);

  // Projection background
  const projectionStart = 2020;
  svg.append("rect")
    .attr("x", x(projectionStart))
    .attr("y", margin.top)
    .attr("width", x(maxYear) - x(projectionStart))
    .attr("height", height - margin.top - margin.bottom)
    .attr("fill", "#eff6ff");

  svg.append("text")
    .attr("x", x(projectionStart) + 6)
    .attr("y", margin.top + 16)
    .attr("fill", "#1d4ed8")
    .attr("font-size", 12)
    .text("IPCC AR6 Projections (2020–2150)");

  // Axes
  const xAxis = d3.axisBottom(x).tickFormat(d3.format("d"));
  const yAxis = d3.axisLeft(y);

  svg.append("g")
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .call(xAxis);

  svg.append("g")
    .attr("transform", `translate(${margin.left},0)`)
    .call(yAxis);

  svg.append("text")
    .attr("x", width / 2)
    .attr("y", height - 10)
    .attr("text-anchor", "middle")
    .attr("font-size", 12)
    .text("Year");

  svg.append("text")
    .attr("transform", "rotate(-90)")
    .attr("x", -height / 2)
    .attr("y", 20)
    .attr("text-anchor", "middle")
    .attr("font-size", 12)
    .text("Sea Level Rise (mm)");

  // Scenario definitions
  const allScenarios = [
    { key: "ssp119_mm", lower: "ssp119_lower", upper: "ssp119_upper", label: "Low (SSP1-1.9)", color: "#22c55e" },
    { key: "ssp245_mm", lower: "ssp245_lower", upper: "ssp245_upper", label: "Moderate (SSP2-4.5)", color: "#fbbf24" },
    { key: "ssp585_mm", lower: "ssp585_lower", upper: "ssp585_upper", label: "High (SSP5-8.5)", color: "#ef4444" }
  ];

  // Filter scenarios based on toggle
  const scenarios = showAll ? allScenarios : allScenarios.filter(s => s.key === selectedScenario + "_mm");

  // Area and line generators
  const areaGen = (lowerKey, upperKey) =>
    d3.area()
      .x(d => x(d.year))
      .y0(d => y(d[lowerKey]))
      .y1(d => y(d[upperKey]));

  const lineGen = key =>
    d3.line()
      .x(d => x(d.year))
      .y(d => y(d[key]));

  const uncertaintyGroup = svg.append("g").attr("class", "uncertainty-bands");
  const linesGroup = svg.append("g").attr("class", "median-lines");

  // Draw uncertainty bands
  scenarios.forEach(s => {
    uncertaintyGroup.append("path")
      .datum(filteredData)
      .attr("fill", s.color)
      .attr("opacity", 0.15)
      .attr("d", areaGen(s.lower, s.upper))
      .append("title")
      .text(`${s.label} uncertainty range (17th-83rd percentile)`);
  });

  // Draw median lines
  scenarios.forEach(s => {
    const path = linesGroup.append("path")
      .datum(filteredData)
      .attr("fill", "none")
      .attr("stroke", s.color)
      .attr("stroke-width", 3)
      .attr("opacity", 1)
      .attr("d", lineGen(s.key));

    const totalLength = path.node().getTotalLength();
    path.attr("stroke-dasharray", `${totalLength} ${totalLength}`)
      .attr("stroke-dashoffset", totalLength)
      .transition()
      .duration(900)
      .ease(d3.easeCubicOut)
      .attr("stroke-dashoffset", 0);
  });

  // City overlay
  if (filteredCityData && filteredCityData.length > 0) {
    const cityUncertaintyGroup = svg.append("g").attr("class", "city-uncertainty-bands");
    const cityLinesGroup = svg.append("g").attr("class", "city-lines");
    
    scenarios.forEach(s => {
      cityUncertaintyGroup.append("path")
        .datum(filteredCityData)
        .attr("fill", s.color)
        .attr("opacity", 0.08)
        .attr("d", areaGen(s.lower, s.upper))
        .append("title")
        .text(`${cityData.name} ${s.label} uncertainty range`);
    });
    
    scenarios.forEach(s => {
      const cityPath = cityLinesGroup.append("path")
        .datum(filteredCityData)
        .attr("fill", "none")
        .attr("stroke", s.color)
        .attr("stroke-width", 3.5)
        .attr("opacity", 0.8)
        .attr("d", lineGen(s.key));

      const totalLength = cityPath.node().getTotalLength();
      cityPath.attr("stroke-dasharray", `8 4 ${totalLength}`)
        .attr("stroke-dashoffset", totalLength)
        .transition()
        .delay(400)
        .duration(1200)
        .ease(d3.easeCubicOut)
        .attr("stroke-dasharray", "8 4")
        .attr("stroke-dashoffset", 0);
    });
  }

  // Vertical time marker
  const marker = svg.append("line")
    .attr("stroke", "#2563eb")
    .attr("stroke-width", 2)
    .attr("stroke-dasharray", "4 2")
    .attr("y1", margin.top)
    .attr("y2", height - margin.bottom)
    .attr("x1", x(selectedYear))
    .attr("x2", x(selectedYear));

  // Tooltip
  let tooltip = d3.select("body").selectAll(".line-tooltip").data([null]);
  tooltip = tooltip.enter().append("div")
    .attr("class", "line-tooltip")
    .style("opacity", 0)
    .merge(tooltip);

  tooltip.style("position", "absolute")
    .style("background", "white")
    .style("padding", "10px 12px")
    .style("border-radius", "6px")
    .style("box-shadow", "0 4px 12px rgba(0,0,0,0.15)")
    .style("pointer-events", "none")
    .style("font-size", "13px")
    .style("z-index", "1000");

  function showTooltip(html, event) {
    tooltip.transition().duration(200).style("opacity", 0.95);
    tooltip.html(html)
      .style("left", (event.pageX + 10) + "px")
      .style("top", (event.pageY - 28) + "px");
  }

  function hideTooltip() {
    tooltip.transition().duration(500).style("opacity", 0);
  }

  // Interactive overlay
  if (filteredData.length > 0) {
    svg.append("rect")
      .attr("x", margin.left)
      .attr("y", margin.top)
      .attr("width", width - margin.left - margin.right)
      .attr("height", height - margin.top - margin.bottom)
      .attr("fill", "transparent")
      .on("mousemove", function(event) {
        const [mx] = d3.pointer(event);
        const hoveredYear = Math.round(x.invert(mx));
        const clamped = Math.max(minYear, Math.min(maxYear, hoveredYear));
        
        marker.attr("x1", x(clamped)).attr("x2", x(clamped));
        
        const pt = getYearPoint(filteredData, clamped);
        if (!pt) return;

        let tooltipHtml = `<strong style="font-size: 14px;">📍 Year ${clamped}</strong><br/>`;
        
        // When showing all scenarios, display all three
        if (showAll) {
          const scenarios = [
            { key: 'ssp119_mm', label: 'Low Emissions (SSP1-1.9)', color: '#22c55e' },
            { key: 'ssp245_mm', label: 'Moderate Emissions (SSP2-4.5)', color: '#3b82f6' },
            { key: 'ssp585_mm', label: 'High Emissions (SSP5-8.5)', color: '#ef4444' }
          ];
          
          scenarios.forEach((scenario, idx) => {
            const avgValueMm = pt[scenario.key];
            const avgValueCm = avgValueMm / 10;
            const lowerKey = scenario.key.replace('_mm', '_lower');
            const upperKey = scenario.key.replace('_mm', '_upper');
            const avgLowerCm = (pt[lowerKey] || avgValueMm) / 10;
            const avgUpperCm = (pt[upperKey] || avgValueMm) / 10;
            
            tooltipHtml += `
              <div style="margin-top: ${idx === 0 ? 8 : 6}px; padding-top: 6px; ${idx > 0 ? 'border-top: 1px solid #e5e7eb;' : ''}">
                <strong style="color: ${scenario.color};">${scenario.label}</strong><br/>
                <strong>US Avg:</strong> ${avgValueCm.toFixed(1)} cm
                <span style="font-size: 11px; color: #64748b;">(${avgLowerCm.toFixed(1)}–${avgUpperCm.toFixed(1)} cm)</span>
            `;
            
            if (filteredCityData && filteredCityData.length > 0) {
              const cityPt = getYearPoint(filteredCityData, clamped);
              if (cityPt) {
                const cityValueMm = cityPt[scenario.key];
                const cityValueCm = cityValueMm / 10;
                const diff = ((cityValueMm - avgValueMm) / avgValueMm * 100).toFixed(0);
                
                tooltipHtml += `<br/><strong>${cityData.name}:</strong> ${cityValueCm.toFixed(1)} cm 
                  <span style="color: ${diff > 0 ? '#ef4444' : '#22c55e'}; font-size: 12px;">
                    (${diff > 0 ? '+' : ''}${diff}%)
                  </span>`;
              }
            }
            
            tooltipHtml += `</div>`;
          });
        } else {
          // Single scenario mode - show detailed info
          const scenarioKey = selectedScenario + "_mm";
          const scenarioLabel = allScenarios.find(s => s.key === scenarioKey)?.label || "";
          const avgValueMm = pt[scenarioKey];
          const avgValueCm = avgValueMm / 10;

          const nextPt = getYearPoint(filteredData, clamped + 10) || pt;
          const slopeMmPerDecade = nextPt[scenarioKey] - pt[scenarioKey];

          const lowerKey = scenarioKey.replace('_mm', '_lower');
          const upperKey = scenarioKey.replace('_mm', '_upper');
          const avgLowerCm = (pt[lowerKey] || avgValueMm) / 10;
          const avgUpperCm = (pt[upperKey] || avgValueMm) / 10;

          tooltipHtml += `<br/><strong style="color: #3b82f6;">${scenarioLabel}</strong><br/>`;
          
          if (filteredCityData && filteredCityData.length > 0) {
            const cityPt = getYearPoint(filteredCityData, clamped);
            if (cityPt) {
              const cityValueMm = cityPt[scenarioKey];
              const cityValueCm = cityValueMm / 10;
              const cityLowerCm = (cityPt[lowerKey] || cityValueMm) / 10;
              const cityUpperCm = (cityPt[upperKey] || cityValueMm) / 10;
              const diff = ((cityValueMm - avgValueMm) / avgValueMm * 100).toFixed(0);
              
              tooltipHtml += `
                <div style="margin-top: 6px; padding-top: 6px; border-top: 1px solid #e5e7eb;">
                  <strong style="color: #1e293b;">${cityData.name}:</strong><br/>
                  Rise: <strong>${cityValueCm.toFixed(1)} cm</strong>
                  <span style="color: ${diff > 0 ? '#ef4444' : '#22c55e'}; font-size: 12px;">
                    (${diff > 0 ? '+' : ''}${diff}%)
                  </span><br/>
                  <span style="font-size: 11px; color: #64748b;">Range: ${cityLowerCm.toFixed(1)}–${cityUpperCm.toFixed(1)} cm</span>
                </div>
              `;
            }
          }
          
          tooltipHtml += `
            <div style="margin-top: 6px; padding-top: 6px; ${filteredCityData ? 'border-top: 1px solid #e5e7eb;' : ''}">
              <strong style="color: #1e293b;">US Average:</strong><br/>
              Rise: <strong>${avgValueCm.toFixed(1)} cm</strong><br/>
              <span style="font-size: 11px; color: #64748b;">Range: ${avgLowerCm.toFixed(1)}–${avgUpperCm.toFixed(1)} cm</span><br/>
              Rate: ${(slopeMmPerDecade / 10).toFixed(1)} mm/yr
            </div>
          `;
        }

        showTooltip(tooltipHtml, event);
      })
      .on("mouseleave", function() {
        hideTooltip();
        marker.attr("x1", x(selectedYear)).attr("x2", x(selectedYear));
      });
  }

  // Event markers
  const eventGroup = svg.append("g");
  const filteredEvents = events.filter(ev => {
    const matchesScenario = showAll || ev.scenario === (selectedScenario + "_mm");
    const inYearRange = ev.year <= selectedYear && ev.year >= minYear;
    return matchesScenario && inYearRange;
  });

  filteredEvents.forEach(ev => {
    const pt = getYearPoint(filteredData, ev.year);
    if (!pt) return;

    const yVal = pt[ev.scenario];
    if (yVal == null) return;

    const ex = x(ev.year);
    const ey = y(yVal);

    eventGroup.append("rect")
      .attr("x", ex - 5)
      .attr("y", ey - 5)
      .attr("width", 10)
      .attr("height", 10)
      .attr("transform", `rotate(45,${ex},${ey})`)
      .attr("fill", "#ea580c")
      .attr("stroke", "white")
      .attr("stroke-width", 1.2)
      .style("cursor", "pointer")
      .on("mouseover", function(event) {
        event.stopPropagation();
        showTooltip(`<strong>${ev.year}</strong><br/>Event: ${ev.label}`, event);
      })
      .on("mouseout", function(event) {
        event.stopPropagation();
        hideTooltip();
      })
      .on("click", function(event) {
        event.stopPropagation();
        showTooltip(`<strong>${ev.year}</strong><br/>${ev.label}<br/>Scenario: ${ev.scenario.toUpperCase().replace("_MM", "")}`, event);
      });
  });

  // Legend
  const legend = svg.append("g")
    .attr("transform", `translate(${width - margin.right + 20}, ${margin.top + 10})`);

  legend.append("text")
    .attr("x", 0)
    .attr("y", 0)
    .attr("font-size", 12)
    .attr("font-weight", "600")
    .attr("fill", "#374151")
    .text("Legend");

  let yOffset = 20;

  legend.append("text")
    .attr("x", 0)
    .attr("y", yOffset)
    .attr("font-size", 10)
    .attr("fill", "#6b7280")
    .text("US Average:");
  yOffset += 16;

  allScenarios.forEach(s => {
    if (!showAll && s.key !== selectedScenario + "_mm") return;
    
    const row = legend.append("g").attr("transform", `translate(0, ${yOffset})`);
    row.append("line")
      .attr("x1", 0).attr("x2", 24)
      .attr("y1", 0).attr("y2", 0)
      .attr("stroke", s.color)
      .attr("stroke-width", 2.5);
    row.append("text")
      .attr("x", 30).attr("y", 4)
      .attr("font-size", 10)
      .attr("fill", "#374151")
      .text(s.label);
    yOffset += 16;
  });

  if (filteredCityData && filteredCityData.length > 0) {
    yOffset += 8;
    legend.append("text")
      .attr("x", 0).attr("y", yOffset)
      .attr("font-size", 10)
      .attr("fill", "#6b7280")
      .text(`${cityData.name}:`);
    yOffset += 16;

    scenarios.forEach(s => {
      const row = legend.append("g").attr("transform", `translate(0, ${yOffset})`);
      row.append("line")
        .attr("x1", 0).attr("x2", 24)
        .attr("y1", 0).attr("y2", 0)
        .attr("stroke", s.color)
        .attr("stroke-width", 2.5)
        .attr("stroke-dasharray", "4 2");
      row.append("text")
        .attr("x", 30).attr("y", 4)
        .attr("font-size", 10)
        .attr("fill", "#374151")
        .text(s.label);
      yOffset += 16;
    });
  }

  yOffset += 12;
  legend.append("text")
    .attr("x", 0).attr("y", yOffset)
    .attr("font-size", 10)
    .attr("fill", "#6b7280")
    .text("Uncertainty:");
  yOffset += 16;

  scenarios.forEach(s => {
    const row = legend.append("g").attr("transform", `translate(0, ${yOffset})`);
    row.append("rect")
      .attr("x", 0).attr("y", -6)
      .attr("width", 24).attr("height", 8)
      .attr("fill", s.color)
      .attr("opacity", 0.15);
    row.append("text")
      .attr("x", 30).attr("y", 0)
      .attr("font-size", 9)
      .attr("fill", "#374151")
      .text(s.label);
    yOffset += 14;
  });

  legend.append("text")
    .attr("x", 0).attr("y", yOffset)
    .attr("font-size", 8)
    .attr("fill", "#9ca3af")
    .text("17th-83rd percentile");
  yOffset += 10;
  legend.append("text")
    .attr("x", 0).attr("y", yOffset)
    .attr("font-size", 8)
    .attr("fill", "#9ca3af")
    .text("(~66% confidence)");

  return svg.node();
}
```

<div class="card">
  ${resize(width => seaLevelLineChart(usAvg, {
    width,
    cityData: selectedCityData,
    selectedScenario: selectedScenario.value,
    selectedYear: selectedYear,
    showAll: showAllScenarios
  }))}
</div>

**Key Insights:**
- **Acceleration:** Sea level rise accelerates over time - notice how the slope steepens in later decades
- **Scenario divergence:** Different emission pathways look similar until ~2040, then diverge significantly
- **Uncertainty grows:** The shaded bands widen over time, reflecting increasing uncertainty in long-term projections
- **Non-linear:** Rise is not constant - expect faster increases in the late 21st and early 22nd centuries

---

## Understanding the Science

<div class="card" style="background: #f0fdf4; border-left: 4px solid #22c55e;">
  <h3 style="margin-top: 0; color: #166534;">What Do These Projections Mean?</h3>
  
  **Emission Scenarios (SSP Pathways):**
  - **SSP1-1.9 (Low):** Aggressive climate action, rapid renewable transition, peak warming <1.5°C
  - **SSP2-4.5 (Moderate):** Current policies trajectory, moderate warming (~2-3°C)
  - **SSP5-8.5 (High):** High emissions, fossil fuel intensive, warming >4°C
  
  **Uncertainty Ranges:**
  - Shaded bands show 17th-83rd percentile (~66% confidence interval)
  - Accounts for ice sheet dynamics, ocean circulation, regional variations
  - Uncertainty grows with time as complex processes compound
  
  **What Causes Regional Differences?**
  - **Subsidence:** Land sinking (Gulf Coast, Mid-Atlantic) amplifies relative sea level rise
  - **Ocean dynamics:** Gulf Stream changes affect East Coast differently than West Coast
  - **Gravitational effects:** Ice sheet melting affects sea level regionally, not uniformly
  - **Glacial rebound:** Some areas (Alaska) experience land uplift, reducing relative rise
</div>

---

## Data Sources & Methods

**Data:** IPCC AR6 Sea Level Projections (2021)  
**Cities:** 141 US coastal locations from PSMSL (Permanent Service for Mean Sea Level)  
**Scenarios:** SSP1-1.9, SSP2-4.5, SSP5-8.5 (medium confidence projections)  
**Time Range:** 2020-2150 (decadal intervals)  
**Uncertainty:** 17th-83rd percentile confidence intervals from ensemble projections

**Design Inspiration:** [NASA Sea Level Projection Tool](https://sealevel.nasa.gov/ipcc-ar6-sea-level-projection-tool)

**References:**
- Fox-Kemper, B., et al. (2021). Ocean, Cryosphere and Sea Level Change. In IPCC AR6 WG1.
- PSMSL Tide Gauge Database
- IPCC AR6 Regional Sea Level Projections Dataset

---

<div style="background: #fef3c7; padding: 20px; border-radius: 8px; border-left: 4px solid #f59e0b; margin-top: 32px;">
  <strong style="font-size: 16px;">Important Note</strong>
  <p style="margin: 8px 0 0 0;">These projections represent median (50th percentile) estimates with uncertainty ranges. Actual outcomes may differ. Low-probability, high-impact scenarios (e.g., rapid ice sheet collapse) are not fully captured in these ranges. Projections are for planning and adaptation purposes.</p>
</div>

---

<style>
  .map-tooltip, .line-tooltip {
    font-family: system-ui, -apple-system, sans-serif;
    line-height: 1.4;
  }
  
  .card h2 {
    font-size: 14px;
    color: #6b7280;
    margin: 0 0 8px 0;
  }
  
  .card .big {
    font-size: 32px;
    font-weight: 700;
    display: block;
    margin-bottom: 4px;
  }
  
  .card .label {
    font-size: 13px;
    color: #9ca3af;
    display: block;
  }
</style>

