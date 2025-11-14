import xarray as xr
import pandas as pd


# ------------------------------------------------------
# 1. Load U.S. location IDs from location_list.lst
# ------------------------------------------------------
us_locations = []
with open("location_list.lst") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 4:
            name, loc_id, lat, lon = parts
            lat = float(lat)
            lon = float(lon)
            loc_id = int(loc_id)

            # US bounding box
            if 24 <= lat <= 49 and -125 <= lon <= -66:
                us_locations.append(loc_id)

print("US location IDs:", us_locations)


# ------------------------------------------------------
# 2. Function to load and average across all US locations
# ------------------------------------------------------
def load_ssp(filename):
    print(f"\nLoading: {filename}")

    ds = xr.open_dataset(filename)

    # We ONLY want the main data variable
    da = ds["sea_level_change"]

    # Select only US locations
    sel = da.sel(locations=us_locations)

    # Average across all dims except years
    dims_to_avg = [d for d in sel.dims if d != "years"]

    averaged = sel.mean(dim=dims_to_avg)

    # Now averaged is 1D (years)
    years = averaged["years"].values
    values = averaged.values

    # Build pandas Series manually
    df = pd.Series(values, index=years)
    df.index = df.index.astype(int)

    return df


# ------------------------------------------------------
# 3. Load each SSP dataset
# ------------------------------------------------------
ssp119 = load_ssp("../data/raw/medium_confidence/ssp119/total_ssp119_medium_confidence_values.nc")
ssp245 = load_ssp("../data/raw/medium_confidence/ssp245/total_ssp245_medium_confidence_values.nc")
ssp585 = load_ssp("../data/raw/medium_confidence/ssp585/total_ssp585_medium_confidence_values.nc")


# ------------------------------------------------------
# 4. Merge results into a DataFrame
# ------------------------------------------------------
out = pd.DataFrame({
    "year": ssp119.index,
    "ssp119_mm": ssp119.values,
    "ssp245_mm": ssp245.values,
    "ssp585_mm": ssp585.values
})


# ------------------------------------------------------
# 5. Save output
# ------------------------------------------------------
out.to_csv("us_sea_level_average.csv", index=False)
print("\nSAVED: us_sea_level_average.csv")
