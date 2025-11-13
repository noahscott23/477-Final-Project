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

