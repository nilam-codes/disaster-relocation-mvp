import pandas as pd
import os

CENSUS_DIR = "data/raw/census"
OUTPUT_FILE = "data/processed/final/uttarakhand_census_4districts.csv"

FILES = [
    "PCA_CDB_0505_F_Census.xls",              # Dehradun
    "PCA_CDB_0506_F_Census.xls",              # Garhwal / Pauri
    "DDW_PCA0509_2011_MDDS with UI.xlsx",     # Almora
    "DDW_PCA0504_2011_MDDS with UI.xlsx",     # Tehri Garhwal
]


def clean_columns(df):
    """Convert both Census column formats into one common format."""

    rename_map = {
        # Newer XLSX format
        "State": "state",
        "District": "district",
        "Subdistt": "subdistrict",
        "Town/Village": "village_code",
        "Ward": "ward",
        "EB": "eb",
        "Level": "level",
        "Name": "village",
        "TRU": "tru",
        "No_HH": "households",
        "TOT_P": "population",
        "TOT_M": "male_population",
        "TOT_F": "female_population",
        "P_06": "children_0_6",
        "M_06": "male_children_0_6",
        "F_06": "female_children_0_6",
        "P_SC": "sc_population",
        "M_SC": "male_sc_population",
        "F_SC": "female_sc_population",
        "P_ST": "st_population",
        "M_ST": "male_st_population",
        "F_ST": "female_st_population",
        "P_LIT": "literates",
        "M_LIT": "male_literates",
        "F_LIT": "female_literates",
        "P_ILL": "illiterates",
        "M_ILL": "male_illiterates",
        "F_ILL": "female_illiterates",
        "TOT_WORK_P": "total_workers",

        # Older XLS format
        "State/UTs_Code": "state_code",
        "District_Code": "district_code",
        "CD Block_Code": "subdistrict_code",
        "Town/Village_Code": "village_code",
        "Ward_Code": "ward",
        "EB_Code": "eb",
        "State/UTs_Name": "state",
        "District_Name": "district",
        "Total/Rural/Urban": "tru",
        "No of Households": "households",
        "Total Population Person": "population",
        "Total Population Male": "male_population",
        "Total Population Female": "female_population",
        "Population in the age group 0-6 Person": "children_0_6",
        "Population in the age group 0-6 Male": "male_children_0_6",
        "Population in the age group 0-6 Female": "female_children_0_6",
        "Scheduled Castes population Person": "sc_population",
        "Scheduled Castes population Male": "male_sc_population",
        "Scheduled Castes population Female": "female_sc_population",
        "Scheduled Tribes population Person": "st_population",
        "Scheduled Tribes population Male": "male_st_population",
        "Scheduled Tribes population Female": "female_st_population",
        "Literates Population Person": "literates",
        "Literates Population Male": "male_literates",
        "Literates Population Female": "female_literates",
        "Illiterate Persons": "illiterates",
        "Illiterate Male": "male_illiterates",
        "Illiterate Female": "female_illiterates",
        "Total Worker Population Person": "total_workers",
    }

    df = df.rename(columns=rename_map)

    # Keep only the fields needed for our risk calculation
    required = [
        "state",
        "district",
        "subdistrict",
        "village_code",
        "level",
        "village",
        "tru",
        "households",
        "population",
        "male_population",
        "female_population",
        "children_0_6",
        "sc_population",
        "st_population",
        "literates",
        "illiterates",
        "total_workers",
    ]

    # Add missing columns if a file doesn't contain one
    for col in required:
        if col not in df.columns:
            df[col] = None

    df = df[required].copy()

    # Clean text
    for col in ["state", "district", "subdistrict", "level", "village", "tru"]:
        df[col] = df[col].astype(str).str.strip()

    # Numeric fields
    numeric_cols = [
        "households",
        "population",
        "male_population",
        "female_population",
        "children_0_6",
        "sc_population",
        "st_population",
        "literates",
        "illiterates",
        "total_workers",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def read_census_file(filename):
    path = os.path.join(CENSUS_DIR, filename)

    print(f"\nReading: {filename}")

    df = pd.read_excel(path, sheet_name=0)

    print(f"  Raw rows: {len(df):,}")

    df = clean_columns(df)

    # Keep village-level records only.
    # Census files can contain district/block/town/ward summary rows.
    level_upper = df["level"].str.upper()

    village_mask = (
        level_upper.str.contains("VILLAGE", na=False)
        | level_upper.eq("VILL")
    )

    village_df = df[village_mask].copy()

    print(f"  Village rows: {len(village_df):,}")

    return village_df


def main():

    all_data = []

    for filename in FILES:
        df = read_census_file(filename)
        all_data.append(df)

    census = pd.concat(all_data, ignore_index=True)

    # Remove completely empty village names
    census = census[
        census["village"].notna()
        & (census["village"].astype(str).str.strip() != "")
        & (census["village"].astype(str).str.lower() != "nan")
    ].copy()

    # Remove duplicate village records using district + village code
    before = len(census)

    census = census.drop_duplicates(
        subset=["district", "village_code"],
        keep="first"
    )

    duplicates_removed = before - len(census)

    # Calculate useful vulnerability percentages
    pop = census["population"].replace(0, pd.NA)

    census["children_0_6_pct"] = (
        census["children_0_6"] / pop * 100
    )

    census["illiteracy_pct"] = (
        census["illiterates"] / pop * 100
    )

    census["sc_st_pct"] = (
        (census["sc_population"].fillna(0)
         + census["st_population"].fillna(0))
        / pop * 100
    )

    # Create output directory
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    census.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 60)
    print("CENSUS COMBINATION COMPLETE")
    print("=" * 60)

    print(f"Total village records: {len(census):,}")
    print(f"Duplicates removed:    {duplicates_removed:,}")
    print(f"Output: {OUTPUT_FILE}")

    print("\nDistrict distribution:")
    print(census["district"].value_counts().to_string())

    print("\nPopulation:")
    print(f"Total population: {census['population'].sum():,.0f}")

    print("\nMissing population:")
    print(
        census["population"].isna().sum()
    )


if __name__ == "__main__":
    main()