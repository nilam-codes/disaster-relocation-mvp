import pandas as pd

input_file = "data/raw/rainfall/rainfall_tel_hr_uttarakhand_uk_2021_2025.csv"
output_file = "data/processed/rainfall/rainfall_processed.csv"

# Load rainfall data
df = pd.read_csv(input_file)

rainfall_col = "Telemetry Hourly Rainfall (mm)"
date_col = "Data Acquisition Time"

# Convert date column
df[date_col] = pd.to_datetime(df[date_col], dayfirst=True)

# Convert rainfall to numeric
df[rainfall_col] = pd.to_numeric(df[rainfall_col], errors="coerce")

# Remove invalid/negative rainfall values
df = df[df[rainfall_col] >= 0].copy()

# Save processed data
df.to_csv(output_file, index=False)

print("\n===== RAINFALL PROCESSING COMPLETE =====")
print("Processed rows:", len(df))
print("Rainfall minimum:", df[rainfall_col].min())
print("Rainfall maximum:", df[rainfall_col].max())
print("Stations:", df["Station"].nunique())
print("Output:", output_file)