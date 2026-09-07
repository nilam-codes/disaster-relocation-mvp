import pandas as pd

# Path to the raw landslide dataset
file_path = "data/raw/landslides/uttarakhand_landslides.csv"

# Load CSV
df = pd.read_csv(file_path)

print("\n===== LANDSLIDE DATASET INSPECTION =====")

# Number of rows and columns
print("\nShape:")
print(df.shape)

# Column names
print("\nColumns:")
print(df.columns.tolist())

# First 5 rows
print("\nFirst 5 rows:")
print(df.head())

# Data types
print("\nData types:")
print(df.dtypes)

# Missing values
print("\nMissing values:")
print(df.isnull().sum())

print("\n===== INSPECTION COMPLETE =====")

print("\nLatitude range:")
print(df["Latitude"].min(), "to", df["Latitude"].max())

print("\nLongitude range:")
print(df["Longitude"].min(), "to", df["Longitude"].max())