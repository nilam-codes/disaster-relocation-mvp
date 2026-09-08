import pandas as pd

input_file = "data/raw/rainfall/rainfall_tel_hr_uttarakhand_uk_2021_2025.csv"

df = pd.read_csv(input_file)

print("\n===== RAINFALL DATA INSPECTION =====")

print("Total rows:", len(df))
print("Total columns:", len(df.columns))

print("\nColumns:")
print(list(df.columns))

print("\nMissing values:")
print(df.isna().sum())

print("\nCoordinate range:")
print("Latitude:", df["Latitude"].min(), "to", df["Latitude"].max())
print("Longitude:", df["Longitude"].min(), "to", df["Longitude"].max())

print("\nUnique stations:", df["Station"].nunique())

print("\nDate range:")
print("Start:", df["Data Acquisition Time"].min())
print("End:", df["Data Acquisition Time"].max())

print("\nRainfall statistics:")
print(df["Telemetry Hourly Rainfall (mm)"].describe())

print("\n===== INSPECTION COMPLETE =====")