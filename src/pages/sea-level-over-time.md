---
title: U.S. Sea Level Rise — SSP Projections (2020–2150)
theme: light
toc: true
---

# Sea Level Rise Projections — U.S. Average (2020–2150)

Interactive visualization of **average U.S. sea-level rise**, extracted from IPCC AR6 projections.  
Use the controls to compare emission scenarios, drag the year marker, and explore future “what if” events.
---


```js
// load averaged U.S. projection dataset
const usAvg = await FileAttachment("../data/processed/us_sea_level_average.csv").csv({ typed: true });

// clean numeric values
usAvg.forEach(d => {
  d.year = +d.year;
  d.ssp119_mm = +d.ssp119_mm;
  d.ssp245_mm = +d.ssp245_mm;
  d.ssp585_mm = +d.ssp585_mm;
});

// (sanity check)
usAvg.slice(0, 5)
```

```js
// emission scenario options (all 3 lines are always visible)
const scenarioOptions = [
  {value: "ssp119_mm", label: "Low Emissions (SSP1-1.9)", color: "#22c55e"},
  {value: "ssp245_mm", label: "Moderate Emissions (SSP2-4.5)", color: "#fbbf24"},
  {value: "ssp585_mm", label: "High Emissions (SSP5-8.5)", color: "#ef4444"}
];

const selectedScenario = view(
  Inputs.select(scenarioOptions, {
    label: "Emission Scenario",
    value: scenarioOptions[1],
    format: d => d.label
  })
);
```

```js

// year slider (controls the vertical marker + summary cards)
const selectedYear = view(
  Inputs.range([2020, 2150], {
    label: "Year",
    step: 10,
    value: 2100
  })
);
```

```js

// optional button to retrigger drawing animation
const drawLinesTrigger = view(Inputs.button("Draw line animation"));
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

// current point used in cards
const currentPoint = getYearPoint(usAvg, selectedYear);

```

<div class="grid grid-cols-3">
  <div class="card">
    <h2>📈 Selected Scenario</h2>
    <span class="big" style="color:${selectedScenario.color};">${selectedScenario.label}</span>
    <p class="label">highlighted in the chart</p>
  </div>
  <div class="card">
    <h2>📅 Selected Year</h2>
    <span class="big">${selectedYear}</span>
    <p class="label">time marker on the curve</p>
  </div>
  <div class="card">
    <h2>🌊 Sea Level Rise</h2>
    <span class="big" style="color:#0ea5e9;">${currentPoint ? (currentPoint[selectedScenario.value] / 10).toFixed(1) : "N/A"} cm</span>
    <p class="label">relative to year 2020</p>
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
    drawLinesTrigger // just here so the button re-runs the chart
  } = {}
) {
  const height = 460;
  const margin = { top: 40, right: 40, bottom: 50, left: 70 };

  const svg = d3
    .create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height])
    .style("max-width", "100%")
    .style("background", "white")
    .style("border-radius", "12px");

  const years = data.map(d => d.year);
  const minYear = d3.min(years);
  const maxYear = d3.max(years);

  // --- SCALES ---
  const x = d3
    .scaleLinear()
    .domain([minYear, maxYear])
    .range([margin.left, width - margin.right]);

  const y = d3
    .scaleLinear()
    .domain([0, d3.max(data, d => d.ssp585_mm)])
    .nice()
    .range([height - margin.bottom, margin.top]);

  // --- PROJECTION REGION (2030–2150) ---
  const projectionStart = 2030;
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
    .text("Projections (2030–2150)");

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

  // Axis labels
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

  // --- LINES FOR EACH SCENARIO ---
  const scenarios = [
    { key: "ssp119_mm", color: "#22c55e" },
    { key: "ssp245_mm", color: "#fbbf24" },
    { key: "ssp585_mm", color: "#ef4444" }
  ];

  const lineGen = key =>
    d3
      .line()
      .x(d => x(d.year))
      .y(d => y(d[key]));

  const linesGroup = svg.append("g");

  scenarios.forEach(s => {
    const path = linesGroup
      .append("path")
      .datum(data)
      .attr("fill", "none")
      .attr("stroke", s.color)
      .attr("stroke-width", s.key === selectedScenario.value ? 3.5 : 2)
      .attr("opacity", s.key === selectedScenario.value ? 1 : 0.45)
      .attr("d", lineGen(s.key));

    // Simple draw animation when button is clicked
    const totalLength = path.node().getTotalLength();
    path
      .attr("stroke-dasharray", `${totalLength} ${totalLength}`)
      .attr("stroke-dashoffset", totalLength)
      .transition()
      .duration(900)
      .ease(d3.easeCubicOut)
      .attr("stroke-dashoffset", 0);
  });

  // --- VERTICAL TIME MARKER (driven by slider year) ---
  const marker = svg
    .append("line")
    .attr("stroke", "#2563eb")
    .attr("stroke-width", 2)
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

      // Marker follows mouse (acts like a draggable time marker)
      marker.attr("x1", x(clamped)).attr("x2", x(clamped));

      const scenarioLabel = selectedScenario.label;
      const valueMm = pt[selectedScenario.value];
      const valueCm = valueMm / 10;

      // Approximate rate of change (forward difference)
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
      // Reset marker to the slider-selected year
      marker.attr("x1", x(selectedYear)).attr("x2", x(selectedYear));
    });

  // --- EVENT MARKERS (only on their specified scenario line) ---
  const eventGroup = svg.append("g");

  events.forEach(ev => {
    const pt = getYearPoint(data, ev.year);
    if (!pt) return;

    const yVal = pt[ev.scenario];
    if (yVal == null) return;

    const ex = x(ev.year);
    const ey = y(yVal);

    // Little diamond marker
    eventGroup
      .append("rect")
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
        // prevent the overlay's mousemove from immediately overwriting text
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

  // --- SIMPLE LEGEND ---
  const legend = svg
    .append("g")
    .attr("transform", `translate(${width - margin.right - 140}, ${margin.top})`);

  scenarios.forEach((s, i) => {
    const row = legend.append("g").attr("transform", `translate(0, ${i * 18})`);

    row
      .append("line")
      .attr("x1", 0)
      .attr("x2", 22)
      .attr("y1", 6)
      .attr("y2", 6)
      .attr("stroke", s.color)
      .attr("stroke-width", s.key === selectedScenario.value ? 3 : 2)
      .attr("opacity", s.key === selectedScenario.value ? 1 : 0.5);

    row
      .append("text")
      .attr("x", 28)
      .attr("y", 9)
      .attr("font-size", 11)
      .text(
        s.key === "ssp119_mm"
          ? "Low (SSP1-1.9)"
          : s.key === "ssp245_mm"
          ? "Moderate (SSP2-4.5)"
          : "High (SSP5-8.5)"
      );
  });

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
    drawLinesTrigger
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
</style>
