import pandas as pd

input_file = "data/raw/river/river_discharge_tele_hr_cwc_uk_1970_2025.csv"
output_file = "data/processed/river/river_processed.csv"

df = pd.read_csv(input_file)

discharge_col = "Telemetry Hourly River Water Discharge (m3/sec)"

# Convert discharge to numeric
df[discharge_col] = pd.to_numeric(
    df[discharge_col],
    errors="coerce"
)

# Convert date/time
df["Data Acquisition Time"] = pd.to_datetime(
    df["Data Acquisition Time"],
    errors="coerce",
    dayfirst=True
)

# Remove invalid discharge values
valid = (
    df[discharge_col].notna()
    & (df[discharge_col] > 0)
    & (df[discharge_col] < 99999)
)

df_clean = df[valid].copy()

# Create output directory
import os
os.makedirs("data/processed/river", exist_ok=True)

# Save processed data
df_clean.to_csv(output_file, index=False)

print("\n===== RIVER PROCESSING COMPLETE =====")
print("Original rows:", len(df))
print("Processed rows:", len(df_clean))
print("Removed rows:", len(df) - len(df_clean))
print("Stations:", df_clean["Station"].nunique())
print("Discharge minimum:", df_clean[discharge_col].min())
print("Discharge maximum:", df_clean[discharge_col].max())
print("Output:", output_file)