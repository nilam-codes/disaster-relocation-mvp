import pandas as pd
import geopandas as gpd

CENSUS_FILE = "data/processed/final/uttarakhand_census_4districts.csv"
GIS_FILE = "data/processed/villages/villages_master.geojson"


def clean_code(series):
    return (
        series.astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
        .str.zfill(6)
    )


census = pd.read_csv(CENSUS_FILE)
gis = gpd.read_file(GIS_FILE)

# Fix district names from Census district codes
district_map = {
    "59": "Tehri Garhwal",
    "64": "Almora",
    "Garhwal": "Pauri Garhwal",
    "Dehradun": "Dehradun",
}

census["district"] = (
    census["district"]
    .astype(str)
    .str.strip()
    .replace(district_map)
)

# Clean village codes
census["village_code_clean"] = clean_code(census["village_code"])
gis["village_code_clean"] = clean_code(gis["vlcode"])

# Match by village code
matched = census.merge(
    gis[["village_code_clean", "village", "district"]],
    on="village_code_clean",
    how="inner",
    suffixes=("_census", "_gis")
)

print("\n" + "=" * 60)
print("CENSUS → GIS MATCH CHECK")
print("=" * 60)

print(f"Census villages:       {len(census):,}")
print(f"GIS villages:          {len(gis):,}")
print(f"Matched by village code: {len(matched):,}")

match_pct = len(matched) / len(census) * 100
state_pct = len(matched) / len(gis) * 100

print(f"\nCensus match rate:      {match_pct:.2f}%")
print(f"Uttarakhand GIS coverage: {state_pct:.2f}%")

print("\nMatched villages by district:")
print(
    matched["district_census"]
    .value_counts()
    .to_string()
)

print("\nCensus villages by district:")
print(
    census["district"]
    .value_counts()
    .to_string()
)

# Check unmatched records
unmatched = census[
    ~census["village_code_clean"].isin(
        matched["village_code_clean"]
    )
].copy()

print(f"\nUnmatched Census villages: {len(unmatched):,}")

print("\nSample unmatched villages:")
print(
    unmatched[
        ["district", "village", "village_code"]
    ].head(20).to_string(index=False)
)