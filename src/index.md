# Climate Change + Projected Sea Level Rise

<div class="hero">
  <h1>Sea Level Rise & US Coastal Cities</h1>
  <h2>Visualizing the Future Impact of Climate Change</h2>
  <p class="subtitle">Explore how projected sea level rise will affect 141 US coastal cities under different greenhouse gas emission scenarios from 2020 - 2150.</p>
  <a href="/pages/sea-level-visualization" class="cta-button" style="color: white;"> US Coastal Sea Level Rise: Where, When, and How Fast? →</a>
  
  <div class="button-group" style="margin-top: 1rem;">
    <a href="/pages/sea-level-over-time" class="cta-button" style="color: white;">
      Line Graph: U.S. Sea Level Projections →
    </a>
  </div>

</div>

---

## Project Overview

Rising seas threaten over **600 million people** living in coastal zones worldwide, making this one of the most urgent environmental challenges of our time. This project visualizes both global trends and localized impacts of sea level rise based on authoritative climate projections from the IPCC Sixth Assessment Report.

<div class="grid grid-cols-3">
  <div class="card">
    <h3>US Focused</h3>
    <p>Explore 141 US coastal cities from all coasts—Atlantic, Pacific, Gulf, Alaska, and Hawaii.</p>
  </div>
  <div class="card">
    <h3>Data-Driven</h3>
    <p>Based on peer-reviewed IPCC AR6 projections maintained by NASA JPL, covering 2020-2150.</p>
  </div>
  <div class="card">
    <h3>Interactive</h3>
    <p>Compare emission scenarios, adjust timeframes, and see city-specific projections with tooltips.</p>
  </div>
</div>

---

## Key Questions

This visualization helps answer:

- **WHERE is the risk?** Which coastal cities and regions face the greatest sea level rise threat?
- **WHEN does risk accelerate?** How do different emission scenarios affect the timing of critical thresholds?
- **HOW FAST is it rising?** What are the rates of change over time and how do they vary by location?
- **What's the uncertainty?** How confident are we in these projections and how does uncertainty grow over time?

---

## Visualization Approach

Our interactive visualization tells a cohesive story through **two complementary perspectives**:

### Spatial View (Map)
**WHERE is the risk?** An interactive U.S. map showing projected sea level rise for 141 coastal cities, color-coded by risk level. Users can zoom into dense coastal regions, click cities to explore their individual trajectories, and compare scenarios at specific years.

### Temporal View (Time Series)
**WHEN and HOW FAST?** A line chart displaying U.S. average sea level rise from 2020-2150 under three emission scenarios (SSP1-1.9, SSP2-4.5, SSP5-8.5). When a city is selected on the map, its trajectory appears as dashed lines for direct comparison. Uncertainty bands (17th-83rd percentile) show projection confidence.

### Key Features
- **Synchronized controls:** Filters for emission scenario and year apply to both visualizations
- **Cross-chart linking:** Click any city on the map to see its time series and statistics
- **Uncertainty visualization:** Shaded bands and ranges show the 66% confidence interval
- **Interactive exploration:** Zoom/pan on the map, hover for detailed tooltips, compare all scenarios
- **Data transparency:** Clear documentation of sources, methods, and limitations


## About This Project

**Team:** Megan Fung, Noah Scott, Archie Phyo  
**Course:** CSC-477 Information Visualization  
**Institution:** California Polytechnic State University, San Luis Obispo

**Data Sources:**
- IPCC Sixth Assessment Report (AR6) Sea Level Projections
- NASA JPL Sea Level Projection Tool
- PSMSL (Permanent Service for Mean Sea Level) Tide Gauge Database

**Design Inspiration:** [NASA Sea Level Projection Tool](https://sealevel.nasa.gov/ipcc-ar6-sea-level-projection-tool)

---

<style>

.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: var(--sans-serif);
  margin: 4rem 0 6rem;
  text-wrap: balance;
  text-align: center;
}

.hero h1 {
  margin: 1rem 0 0.5rem;
  padding: 1rem 0;
  max-width: none;
  font-size: 14vw;
  font-weight: 900;
  line-height: 1.1;
  background: linear-gradient(135deg, #1e3a8a, #3b82f6, #06b6d4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero h2 {
  margin: 0 0 1rem;
  max-width: 34em;
  font-size: 24px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--theme-foreground);
}

.hero .subtitle {
  margin: 0 0 2rem;
  max-width: 42em;
  font-size: 18px;
  font-weight: 400;
  line-height: 1.6;
  color: var(--theme-foreground-muted);
}

.button-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.cta-button {
  display: inline-block;
  padding: 0.75rem 2rem;
  background: linear-gradient(135deg, #3b82f6, #06b6d4);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(59, 130, 246, 0.3);
}

.cta-section {
  text-align: center;
  margin: 4rem 0;
  padding: 3rem 2rem;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(6, 182, 212, 0.05));
  border-radius: 12px;
}

.cta-button-large {
  display: inline-block;
  padding: 1rem 3rem;
  background: linear-gradient(135deg, #3b82f6, #06b6d4);
  color: white;
  text-decoration: none;
  border-radius: 10px;
  font-weight: 700;
  font-size: 18px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.cta-button-large:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(59, 130, 246, 0.3);
}

.card h3 {
  margin-top: 0;
  font-size: 1.2rem;
  font-weight: 600;
}

@media (min-width: 640px) {
  .hero h1 {
    font-size: 72px;
  }
}

</style>
