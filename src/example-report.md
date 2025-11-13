---
title: Global Sea Level Rise — IPCC AR6 Projections
---

# 🌊 Global Sea Level Rise — IPCC AR6 Projections

This page loads the cleaned IPCC sea-level projection data from NASA and shows the first few rows.

```js
// Load CSV
const data = await FileAttachment("data/ipcc_sea_level_total.csv").csv({typed: true});

// Debug: confirm in console
console.log("✅ Rows loaded:", data.length);
console.log("✅ Sample:", data.slice(0, 5));

// Create a visible preformatted block
const pre = document.createElement("pre");
pre.textContent = `Loaded ${data.length} rows:\n\n` + JSON.stringify(data.slice(0, 10), null, 2);
pre.style.background = "#f4f4f4";
pre.style.padding = "10px";
pre.style.borderRadius = "6px";
pre.style.overflow = "auto";
pre.style.height = "300px";
pre.style.color = "#111";

// Return for display
pre;
