---
title: Global Sea Level Rise — IPCC AR6 Projections
---

# Global Sea Level Rise — IPCC AR6 Projections


```js
const data = await FileAttachment("./data/ipcc_sea_level_total.csv").csv({typed: true});

console.log("Rows loaded:", data.length);
console.log("Sample:", data.slice(0, 5));

display(Inputs.table(data.slice(0, 20)));

// loading data from csv

import * as Plot from "npm:@observablehq/plot";

// Convert to numeric
data.forEach(d => {
  d.Year = +d.Year;
  d.Sea_Level_cm = +d.Sea_Level_cm;
});

// Aggregate average per year
const avgByYear = Array.from(
  d3.rollup(
    data,
    v => d3.mean(v, d => d.Sea_Level_cm),
    d => d.Year
  ),
  ([Year, Sea_Level_cm]) => ({Year, Sea_Level_cm})
);

// Simple line chart
Plot.plot({
  width: 800,
  height: 400,
  marginLeft: 60,
  x: {label: "Year"},
  y: {label: "Sea Level Rise (cm)"},
  marks: [
    Plot.line(avgByYear, {x: "Year", y: "Sea_Level_cm", stroke: "#0077b6", strokeWidth: 2}),
    Plot.dot(avgByYear, {x: "Year", y: "Sea_Level_cm", r: 3, fill: "#0077b6"})
  ]
});


