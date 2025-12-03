import xarray as xr
import pandas as pd
import csv
from pathlib import Path


# Load U.S. coastal cities 
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
US_CITIES_FILE = DATA_DIR / "processed/us_coastal_cities.csv"

us_locations = []
with open(US_CITIES_FILE, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        us_locations.append(int(row['psmsl_id']))

print(f"Loaded {len(us_locations)} US coastal cities (same as map visualization)")
print(f"Sample IDs: {sorted(us_locations)[:10]}")


# Function to load and average across all US locations
# Returns median, 17th percentile (lower bound), and 83rd percentile (upper bound)
def load_ssp(filename):
    print(f"\nLoading: {filename}")

    ds = xr.open_dataset(filename)

    # We ONLY want the main data variable
    da = ds["sea_level_change"]

    # Select only US locations (same 141 cities as the map)
    sel = da.sel(locations=us_locations)

    # Get the quantiles dimension to extract specific percentiles
    quantiles = ds["quantiles"].values
    
    # Find indices for 17th, 50th (median), and 83rd percentiles
    p17_idx = (quantiles >= 0.17).argmax()
    p50_idx = (quantiles >= 0.50).argmax()
    p83_idx = (quantiles >= 0.83).argmax()
    
    print(f"  Using quantiles: 17th={quantiles[p17_idx]:.2f}, 50th={quantiles[p50_idx]:.2f}, 83rd={quantiles[p83_idx]:.2f}")

    # Extract each percentile and average across locations
    results = {}
    for name, idx in [("median", p50_idx), ("lower", p17_idx), ("upper", p83_idx)]:
        # Select this quantile
        quantile_data = sel.isel(quantiles=idx)
        # Average across locations
        averaged = quantile_data.mean(dim="locations")
        results[name] = averaged

    # Build DataFrame with all three bounds
    years = results["median"]["years"].values
    df = pd.DataFrame({
        'year': years.astype(int),
        'median': results["median"].values,
        'lower': results["lower"].values,
        'upper': results["upper"].values
    })

    return df


# Load each SSP dataset (now returns DataFrames with median, lower, upper)
ssp119_df = load_ssp(DATA_DIR / "raw/medium_confidence/ssp119/total_ssp119_medium_confidence_values.nc")
ssp245_df = load_ssp(DATA_DIR / "raw/medium_confidence/ssp245/total_ssp245_medium_confidence_values.nc")
ssp585_df = load_ssp(DATA_DIR / "raw/medium_confidence/ssp585/total_ssp585_medium_confidence_values.nc")


# Merge results into a single DataFrame with all scenarios and uncertainty bounds
out = pd.DataFrame({
    "year": ssp119_df["year"],
    # SSP1-1.9 (Low Emissions)
    "ssp119_mm": ssp119_df["median"],
    "ssp119_lower": ssp119_df["lower"],
    "ssp119_upper": ssp119_df["upper"],
    # SSP2-4.5 (Moderate Emissions)
    "ssp245_mm": ssp245_df["median"],
    "ssp245_lower": ssp245_df["lower"],
    "ssp245_upper": ssp245_df["upper"],
    # SSP5-8.5 (High Emissions)
    "ssp585_mm": ssp585_df["median"],
    "ssp585_lower": ssp585_df["lower"],
    "ssp585_upper": ssp585_df["upper"]
})


# Save output
OUTPUT_FILE = DATA_DIR / "processed/us_sea_level_average.csv"
out.to_csv(OUTPUT_FILE, index=False)
print(f"\nSAVED: {OUTPUT_FILE}")
print(f"  {len(out)} years × 3 scenarios × 3 bounds (median, lower, upper)")
print(f"  Averaged across {len(us_locations)} US coastal cities")
print(f"  (Including Alaska, Hawaii, Puerto Rico - same as map visualization)")
print(f"  Uncertainty bounds: 17th-83rd percentile (~66% confidence interval)")
