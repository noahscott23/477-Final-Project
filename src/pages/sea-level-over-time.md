---
title: U.S. Sea Level Rise — SSP Projections (2020–2150)
theme: light
toc: true
---

# Sea Level Rise Projections — U.S. Average (2020–2150)

Interactive visualization of **average U.S. sea-level rise** across 141 coastal cities, extracted from IPCC AR6 projections.  
Averaged across the same cities shown in the map visualization (including Alaska, Hawaii, and Puerto Rico). **Shaded bands** show uncertainty ranges (17th-83rd percentile, ~66% confidence interval).

**How to use:**
- **Emission Scenario** selector filters which scenario lines to display (or "All Scenarios" to compare)
- **Year slider** controls the time range displayed (shows data from 2020 up to selected year)
- **Click a city on the map** to see its individual trajectory overlaid as dashed lines
- **Hover over chart** to see exact values and uncertainty ranges at any point in time
- Settings sync when navigating from the map page

---


```js
// load averaged U.S. projection dataset (now includes uncertainty bounds)
const usAvg = await FileAttachment("../data/processed/us_sea_level_average.csv").csv({ typed: true });

// clean numeric values (now includes lower and upper bounds)
usAvg.forEach(d => {
  d.year = +d.year;
  // SSP1-1.9 (Low Emissions)
  d.ssp119_mm = +d.ssp119_mm;
  d.ssp119_lower = +d.ssp119_lower;
  d.ssp119_upper = +d.ssp119_upper;
  // SSP2-4.5 (Moderate Emissions)
  d.ssp245_mm = +d.ssp245_mm;
  d.ssp245_lower = +d.ssp245_lower;
  d.ssp245_upper = +d.ssp245_upper;
  // SSP5-8.5 (High Emissions)
  d.ssp585_mm = +d.ssp585_mm;
  d.ssp585_lower = +d.ssp585_lower;
  d.ssp585_upper = +d.ssp585_upper;
});

// (sanity check - showing first row with uncertainty bounds)
usAvg.slice(0, 5)
```

```js
// Load individual city projections for comparison
const citiesData = FileAttachment("../data/processed/us_coastal_cities.csv").csv({typed: true});
const projectionsData = FileAttachment("../data/processed/us_projections.json").json();
```

```js
// Check if a city is selected from the URL (read earlier with other URL params)
const selectedCityId = urlParams.get('city');

// Get selected city data if available (only if city ID exists)
let selectedCity = null;
if (selectedCityId) {
  try {
    const cityInfo = citiesData.find(c => String(c.psmsl_id) === selectedCityId);
    const projData = projectionsData[selectedCityId];
    
    if (cityInfo && projData && projData.projections) {
      // Convert projection data to time series format (matching usAvg structure)
      // Now each year has {median, lower, upper} structure
      const cityTimeSeries = Object.keys(projData.projections.ssp119 || {}).map(year => {
        const ssp119 = projData.projections.ssp119[year];
        const ssp245 = projData.projections.ssp245[year];
        const ssp585 = projData.projections.ssp585[year];
        
        return {
          year: +year,
          ssp119_mm: ssp119?.median || ssp119,  // Handle both old and new format
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
      
      selectedCity = {
        id: selectedCityId,
        name: projData.name.replace(/_/g, " "),
        timeSeries: cityTimeSeries
      };
    }
  } catch (e) {
    // If anything goes wrong, just show US average
    selectedCity = null;
  }
}

selectedCity
```

```js
// Read URL parameters for syncing with map page
const urlParams = new URLSearchParams(window.location.search);
const urlScenario = urlParams.get('scenario');
const urlYear = urlParams.get('year');

// Emission scenario options - with "All Scenarios" option
const scenarioOptions = [
  {value: "all", label: "All Scenarios", color: "#6b7280"},
  {value: "ssp119_mm", label: "Low Emissions (SSP1-1.9)", color: "#22c55e"},
  {value: "ssp245_mm", label: "Moderate Emissions (SSP2-4.5)", color: "#fbbf24"},
  {value: "ssp585_mm", label: "High Emissions (SSP5-8.5)", color: "#ef4444"}
];

// If coming from map, use that specific scenario; otherwise default to "all"
const defaultScenario = urlScenario 
  ? scenarioOptions.find(s => s.value === urlScenario) || scenarioOptions[0]
  : scenarioOptions[0];

const selectedScenario = view(
  Inputs.select(scenarioOptions, {
    label: "Emission Scenario",
    value: defaultScenario,
    format: d => d.label
  })
);
```

```js
// Year slider - controls the END of the time range displayed
// If coming from map, use that year; otherwise show full range (2150)
const defaultYear = urlYear ? parseInt(urlYear) : 2150;

// projection horizon: controls how far solid lines extend
const selectedYear = view(
  Inputs.range([2020, 2150], {
    label: "Projection horizon (year revealed)",
    step: 10,
    value: defaultYear
  })
);
```

```js
// helper: get the data row closest to the current year
function getYearPoint(data, year) {
  // Exact match if available
  let exact = data.find(d => d.year === year);
  if (exact) return exact;

  // otherwise interpolate between nearest years
  const sorted = data.slice().sort((a, b) => a.year - b.year);
  const before = d3.max(sorted.filter(d => d.year < year), d => d.year);
  const after = d3.min(sorted.filter(d => d.year > year), d => d.year);
  if (before == null || after == null) return null;
  const d0 = sorted.find(d => d.year === before);
  const d1 = sorted.find(d => d.year === after);
  const t = (year - d0.year) / (d1.year - d0.year);
  return {
    year,
    ssp119_mm: d0.ssp119_mm + t * (d1.ssp119_mm - d0.ssp119_mm),
    ssp245_mm: d0.ssp245_mm + t * (d1.ssp245_mm - d0.ssp245_mm),
    ssp585_mm: d0.ssp585_mm + t * (d1.ssp585_mm - d0.ssp585_mm)
  };
}
```

<div>${selectedCity ? html`
<div class="city-selection-banner">
  <div style="display: flex; justify-content: space-between; align-items: center;">
    <div>
      <strong>🏙️ Viewing: ${selectedCity.name}</strong>
      <p style="margin: 4px 0 0 0; color: #6b7280; font-size: 14px;">
        Dashed lines show individual city trajectory overlaid on solid US average lines
      </p>
    </div>
    <a href="${(() => {
      // Build URL with city, scenario (without _mm suffix), and year
      const scenario = selectedScenario.value === "all" ? "ssp245" : selectedScenario.value.replace("_mm", "");
      return `/pages/sea-level-rise?city=${selectedCity.id}&scenario=${scenario}&year=${selectedYear}`;
    })()}" style="padding: 6px 12px; background: #3b82f6; color: white; text-decoration: none; border-radius: 6px; font-size: 14px;">
      ← Back to Map
    </a>
  </div>
</div>` : ''}</div>

<div class="grid grid-cols-3">
  <div class="card">
    <h2>📈 Scenario Filter</h2>
    <span class="big" style="color:${selectedScenario.color};">${selectedScenario.label}</span>
    <p class="label">${selectedScenario.value === "all" ? "showing all scenarios" : "isolated view"}</p>
  </div>
  <div class="card">
    <h2>📅 Year Range</h2>
    <span class="big">${selectedYear}</span>
    <p class="label">projection horizon (solid line)</p>
  </div>
  <div class="card">
    <h2>🌊 ${selectedCity ? selectedCity.name : 'US Average'}</h2>
    ${(() => {
      const scenarioKey = selectedScenario.value === "all" ? "ssp245_mm" : selectedScenario.value;
      if (selectedCity) {
        const cityPoint = selectedCity.timeSeries.find(d => d.year === selectedYear);
        const value = cityPoint ? (cityPoint[scenarioKey] / 10).toFixed(1) : "N/A";
        return html`<span class="big" style="color:#0ea5e9;">${value} cm</span>`;
      } else {
        const avgPoint = usAvg.find(d => d.year === selectedYear);
        const value = avgPoint ? (avgPoint[scenarioKey] / 10).toFixed(1) : "N/A";
        return html`<span class="big" style="color:#0ea5e9;">${value} cm</span>`;
      }
    })()}
    ${selectedCity 
      ? (() => {
          const scenarioKey = selectedScenario.value === "all" ? "ssp245_mm" : selectedScenario.value;
          const cityPoint = selectedCity.timeSeries.find(d => d.year === selectedYear);
          const avgPoint = usAvg.find(d => d.year === selectedYear);
          if (cityPoint && avgPoint) {
            const cityValue = cityPoint[scenarioKey];
            const avgValue = avgPoint[scenarioKey];
            const diff = ((cityValue - avgValue) / avgValue * 100).toFixed(0);
            const avgCm = (avgValue / 10).toFixed(1);
            if (diff > 0) {
              return html`<p class="label" style="color: #ef4444;"><strong>+${diff}%</strong> vs US avg (${avgCm} cm)</p>`;
            } else {
              return html`<p class="label" style="color: #22c55e;"><strong>${diff}%</strong> vs US avg (${avgCm} cm)</p>`;
            }
          }
          return html`<p class="label">at year ${selectedYear}</p>`;
        })()
      : html`<p class="label">US avg (141 cities) at ${selectedYear}</p>`
    }
  </div>
</div>

```js
// D3 import
import * as d3 from "npm:d3";
```

```js
// Notional "event" markers on the future curve
// can tweak years / labels later
const projectionEvents = [
  {
    year: 2035,
    scenario: "ssp585_mm",
    label: "Large coastal flooding becomes frequent"
  },
  {
    year: 2050,
    scenario: "ssp245_mm",
    label: "Major adaptation thresholds for U.S. coasts"
  },
  {
    year: 2080,
    scenario: "ssp585_mm",
    label: "High-tide flooding in many cities every year"
  },
  {
    year: 2100,
    scenario: "ssp585_mm",
    label: "Severe chronic inundation for low-lying areas"
  }
];
```



```js
function seaLevelLineChart(
  data,
  {
    width,
    selectedScenario,
    selectedYear,
    events,
    cityData = null // optional: selected city data to overlay
  } = {}
) {
  const height = 460;
  const margin = { top: 40, right: 180, bottom: 50, left: 70 }; // More right margin for legend

  const svg = d3
    .create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height])
    .style("max-width", "100%")
    .style("background", "white")
    .style("border-radius", "12px");

  // Filter data by selected year (show only up to selected year)
  const filteredData = data.filter(d => d.year <= selectedYear);
  const filteredCityData = cityData 
    ? cityData.timeSeries.filter(d => d.year <= selectedYear)
    : null;

  const years = filteredData.map(d => d.year);
  const minYear = d3.min(years);
  const maxYear = d3.max(years);

  // --- SCALES ---
  const x = d3
    .scaleLinear()
    .domain([minYear, maxYear])
    .range([margin.left, width - margin.right]);

  // Adjust y-scale to include city data AND uncertainty bounds if present
  const allData = filteredCityData 
    ? [...filteredData, ...filteredCityData] 
    : filteredData;
  const y = d3
    .scaleLinear()
    .domain([0, d3.max(allData, d => d.ssp585_upper || d.ssp585_mm)])  // Include upper bound
    .nice()
    .range([height - margin.bottom, margin.top]);

  // --- PROJECTION REGION (2020–2150) - Blue background ---
  const projectionStart = 2020;
  svg
    .append("rect")
    .attr("x", x(projectionStart))
    .attr("y", margin.top)
    .attr("width", x(maxYear) - x(projectionStart))
    .attr("height", height - margin.top - margin.bottom)
    .attr("fill", "#eff6ff");

  svg
    .append("text")
    .attr("x", x(projectionStart) + 6)
    .attr("y", margin.top + 16)
    .attr("fill", "#1d4ed8")
    .attr("font-size", 12)
    .text("IPCC AR6 Projections (2020–2150)");

  // --- AXES ---
  const xAxis = d3.axisBottom(x).tickFormat(d3.format("d"));
  const yAxis = d3.axisLeft(y);

  svg
    .append("g")
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .call(xAxis);

  svg
    .append("g")
    .attr("transform", `translate(${margin.left},0)`)
    .call(yAxis);

  // axis labels
  svg
    .append("text")
    .attr("x", width / 2)
    .attr("y", height - 10)
    .attr("text-anchor", "middle")
    .attr("font-size", 12)
    .text("Year");

  svg
    .append("text")
    .attr("transform", "rotate(-90)")
    .attr("x", -height / 2)
    .attr("y", 20)
    .attr("text-anchor", "middle")
    .attr("font-size", 12)
    .text("Sea Level Rise (mm)");

  // --- LINES FOR EACH SCENARIO (solid up to horizon, dashed beyond) ---
  const scenarios = [
    { key: "ssp119_mm", color: "#22c55e" },
    { key: "ssp245_mm", color: "#fbbf24" },
    { key: "ssp585_mm", color: "#ef4444" }
  ];

  // Filter scenarios based on selection
  const scenarios = selectedScenario.value === "all" 
    ? allScenarios 
    : allScenarios.filter(s => s.key === selectedScenario.value);

  // Area generator for uncertainty bands
  const areaGen = (lowerKey, upperKey) =>
    d3
      .area()
      .x(d => x(d.year))
      .y0(d => y(d[lowerKey]))
      .y1(d => y(d[upperKey]));

  // Line generator for median values
  const lineGen = key =>
    d3
      .line()
      .x(d => x(d.year))
      .y(d => y(d[key]));

  const uncertaintyGroup = svg.append("g").attr("class", "uncertainty-bands");
  const linesGroup = svg.append("g").attr("class", "median-lines");

  // Draw uncertainty bands first (behind the lines)
  scenarios.forEach(s => {
    uncertaintyGroup
      .append("path")
      .datum(filteredData)
      .attr("fill", s.color)
      .attr("opacity", 0.15)
      .attr("d", areaGen(s.lower, s.upper))
      .append("title")
      .text(`${s.label} uncertainty range (17th-83rd percentile)`);
  });

  scenarios.forEach(s => {
    const dataPast = data.filter(d => d.year <= selectedYear);
    const dataFuture = data.filter(d => d.year >= selectedYear);

    // solid segment up to projection horizon
    if (dataPast.length >= 2) {
      const pathPast = linesGroup
        .append("path")
        .datum(dataPast)
        .attr("fill", "none")
        .attr("stroke", s.color)
        .attr("stroke-width", s.key === selectedScenario.value ? 3.5 : 2.5)
        .attr("opacity", s.key === selectedScenario.value ? 1 : 0.7)
        .attr("d", lineGen(s.key));

      // draw animation for solid part
      const totalLengthPast = pathPast.node().getTotalLength();
      pathPast
        .attr("stroke-dasharray", `${totalLengthPast} ${totalLengthPast}`)
        .attr("stroke-dashoffset", totalLengthPast)
        .transition()
        .duration(900)
        .ease(d3.easeCubicOut)
        .attr("stroke-dashoffset", 0);
    }

    // dashed segment beyond projection horizon
    if (dataFuture.length >= 2) {
      const pathFuture = linesGroup
        .append("path")
        .datum(dataFuture)
        .attr("fill", "none")
        .attr("stroke", s.color)
        .attr("stroke-width", s.key === selectedScenario.value ? 3 : 2)
        .attr("opacity", s.key === selectedScenario.value ? 0.7 : 0.4)
        .attr("stroke-dasharray", "5 5")
        .attr("d", lineGen(s.key));
    }
  });

  // --- VERTICAL TIME MARKER (follows hover, resets to horizon on mouseleave) ---
  const marker = svg
    .append("line")
    .attr("stroke", "#2563eb")
    .attr("stroke-width", 2)
    .attr("stroke-dasharray", "4 2")
    .attr("y1", margin.top)
    .attr("y2", height - margin.bottom)
    .attr("x1", x(selectedYear))
    .attr("x2", x(selectedYear));

  // --- TOOLTIP DIV (singleton) ---
  let tooltip = d3.select("body").selectAll(".line-tooltip").data([null]);
  tooltip = tooltip.enter()
    .append("div")
    .attr("class", "line-tooltip")
    .style("opacity", 0)
    .merge(tooltip);

  function showTooltip(html, event) {
    tooltip
      .html(html)
      .style("opacity", 0.97)
      // clientX / clientY work with position: fixed and scrolling
      .style("left", (event.clientX + 12) + "px")
      .style("top", (event.clientY - 28) + "px");
  }

  function hideTooltip() {
    tooltip.style("opacity", 0);
  }

  // --- INTERACTION OVERLAY (hover along curve) ---
  svg
    .append("rect")
    .attr("x", margin.left)
    .attr("y", margin.top)
    .attr("width", width - margin.left - margin.right)
    .attr("height", height - margin.top - margin.bottom)
    .attr("fill", "transparent")
    .on("mousemove", function(event) {
      const [mx] = d3.pointer(event, this);
      const year = Math.round(x.invert(mx));
      const clamped = Math.max(minYear, Math.min(maxYear, year));
      const pt = getYearPoint(data, clamped);
      if (!pt) return;

      // marker follows mouse (acts like a draggable time marker)
      marker.attr("x1", x(clamped)).attr("x2", x(clamped));

      const scenarioLabel = selectedScenario.label;
      const valueMm = pt[selectedScenario.value];
      const valueCm = valueMm / 10;

      // approximate rate of change (forward difference)
      const nextPt = getYearPoint(data, clamped + 10) || pt;
      const slopeMmPerDecade = nextPt[selectedScenario.value] - pt[selectedScenario.value];

      showTooltip(
        `
        <strong>${clamped}</strong><br/>
        ${scenarioLabel}<br/>
        Rise: <strong>${valueCm.toFixed(1)} cm</strong><br/>
        Rate: ${(slopeMmPerDecade / 10).toFixed(1)} mm/yr
      `,
        event
      );
    })
    .on("mouseleave", function() {
      hideTooltip();
      // reset marker to the slider-selected horizon
      marker.attr("x1", x(selectedYear)).attr("x2", x(selectedYear));
    });

  // --- EVENT THRESHOLDS (horizontal lines + marker) ---
  const eventGroup = svg.append("g");

  const filteredEvents = events.filter(ev => {
    // Only show events that match the selected scenario (or all)
    const matchesScenario = selectedScenario.value === "all" || ev.scenario === selectedScenario.value;
    // Only show events within the displayed year range
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

    // horizontal threshold line across the chart
    eventGroup
      .append("line")
      .attr("x1", margin.left)
      .attr("x2", width - margin.right)
      .attr("y1", ey)
      .attr("y2", ey)
      .attr("stroke", "#ea580c")
      .attr("stroke-width", 1.5)
      .attr("stroke-dasharray", "4 4")
      .attr("opacity", 0.75);

    // small circle at the scenario intersection
    const markerCircle = eventGroup
      .append("circle")
      .attr("cx", ex)
      .attr("cy", ey)
      .attr("r", 4)
      .attr("fill", "#ea580c")
      .attr("stroke", "white")
      .attr("stroke-width", 1.2)
      .style("cursor", "pointer");

    // interaction on the circle (line is just visual)
    markerCircle
      .on("mouseover", function(event) {
        event.stopPropagation();
        showTooltip(
          `
          <strong>${ev.year}</strong><br/>
          Event: ${ev.label}
        `,
          event
        );
      })
      .on("mouseout", function(event) {
        event.stopPropagation();
        hideTooltip();
      })
      .on("click", function(event) {
        event.stopPropagation();
        showTooltip(
          `
          <strong>${ev.year}</strong><br/>
          ${ev.label}<br/>
          Scenario: ${ev.scenario.toUpperCase().replace("_MM", "")}
        `,
          event
        );
      });
  });

  // --- LEGEND (next to chart) ---
  const legend = svg
    .append("g")
    .attr("transform", `translate(${width - margin.right - 160}, ${margin.top})`);

  // Legend title
  legend.append("text")
    .attr("x", 0)
    .attr("y", 0)
    .attr("font-size", 12)
    .attr("font-weight", "600")
    .attr("fill", "#374151")
    .text("Legend");

  let yOffset = 20;

  // US Average scenarios
  legend.append("text")
    .attr("x", 0)
    .attr("y", yOffset)
    .attr("font-size", 10)
    .attr("fill", "#6b7280")
    .text("US Average:");
  yOffset += 16;

  allScenarios.forEach(s => {
    // Only show in legend if it's displayed
    if (selectedScenario.value !== "all" && s.key !== selectedScenario.value) return;
    
    const row = legend.append("g").attr("transform", `translate(0, ${yOffset})`);

    row
      .append("line")
      .attr("x1", 0)
      .attr("x2", 24)
      .attr("y1", 0)
      .attr("y2", 0)
      .attr("stroke", s.color)
      .attr("stroke-width", 2.5);

    row
      .append("text")
      .attr("x", 30)
      .attr("y", 4)
      .attr("font-size", 10)
      .attr("fill", "#374151")
      .text(s.label);

    yOffset += 16;
  });

  // City overlay legend (if applicable)
  if (filteredCityData && filteredCityData.length > 0) {
    yOffset += 8;
    legend.append("text")
      .attr("x", 0)
      .attr("y", yOffset)
      .attr("font-size", 10)
      .attr("fill", "#6b7280")
      .text(`${cityData.name}:`);
    yOffset += 16;

    scenarios.forEach(s => {
      const row = legend.append("g").attr("transform", `translate(0, ${yOffset})`);

      row
        .append("line")
        .attr("x1", 0)
        .attr("x2", 24)
        .attr("y1", 0)
        .attr("y2", 0)
        .attr("stroke", s.color)
        .attr("stroke-width", 2.5)
        .attr("stroke-dasharray", "4 2");

      row
        .append("text")
        .attr("x", 30)
        .attr("y", 4)
        .attr("font-size", 10)
        .attr("fill", "#374151")
        .text(s.label);

      yOffset += 16;
    });
  }

  // Uncertainty explanation
  yOffset += 12;
  legend.append("text")
    .attr("x", 0)
    .attr("y", yOffset)
    .attr("font-size", 10)
    .attr("fill", "#6b7280")
    .text("Uncertainty:");
  yOffset += 16;

  // Show shaded area samples for ALL visible scenarios
  scenarios.forEach(s => {
    const row = legend.append("g").attr("transform", `translate(0, ${yOffset})`);
    
    row.append("rect")
      .attr("x", 0)
      .attr("y", -6)
      .attr("width", 24)
      .attr("height", 8)
      .attr("fill", s.color)
      .attr("opacity", 0.15);
    
    row.append("text")
      .attr("x", 30)
      .attr("y", 0)
      .attr("font-size", 9)
      .attr("fill", "#374151")
      .text(s.label);
    
    yOffset += 14;
  });

  // Explanation text
  legend.append("text")
    .attr("x", 0)
    .attr("y", yOffset)
    .attr("font-size", 8)
    .attr("fill", "#9ca3af")
    .text("17th-83rd percentile");
  yOffset += 10;
  legend.append("text")
    .attr("x", 0)
    .attr("y", yOffset)
    .attr("font-size", 8)
    .attr("fill", "#9ca3af")
    .text("(~66% confidence)");

  return svg.node();
}

```

<div class="card">
  ${resize(width => seaLevelLineChart(usAvg, {
    width,
    selectedScenario: {
      value: selectedScenario.value,
      label: selectedScenario.label,
      color: selectedScenario.color
    },
    selectedYear,
    events: projectionEvents,
    cityData: selectedCity
  }))}
</div>

<style>
  .big {
    font-size: 2.25rem;
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

  .line-tooltip {
    position: fixed;
    pointer-events: none;
    padding: 10px 12px;
    font-size: 13px;
    background: rgba(255, 255, 255, 0.97);
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(15, 23, 42, 0.15);
    color: #111;
    z-index: 99999;
    line-height: 1.4;
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
