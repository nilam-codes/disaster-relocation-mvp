import sqlite3

# Connect to SQLite database
connection = sqlite3.connect("database/disaster.db")

# Enable foreign key enforcement
connection.execute("PRAGMA foreign_keys = ON")

# Create a cursor
cursor = connection.cursor()

print("Database connected successfully!")

# --------------------------------------------------
# DROP OLD TABLES
# Child tables must be dropped before parent tables
# --------------------------------------------------

cursor.execute("DROP TABLE IF EXISTS relocation_assignments")
cursor.execute("DROP TABLE IF EXISTS risk_assessment")
cursor.execute("DROP TABLE IF EXISTS hazards")
cursor.execute("DROP TABLE IF EXISTS relocation_sites")
cursor.execute("DROP TABLE IF EXISTS villages")

# --------------------------------------------------
# CREATE VILLAGES TABLE
# --------------------------------------------------

cursor.execute("""
CREATE TABLE villages (
    village_id INTEGER PRIMARY KEY,
    village_name TEXT NOT NULL,
    district TEXT,
    block TEXT,
    subdistrict TEXT,
    latitude REAL,
    longitude REAL,
    population INTEGER CHECK (population >= 0),
    households INTEGER,
    children_0_6 INTEGER,
    male_population INTEGER,
    female_population INTEGER,
    illiterate_population INTEGER,
    sc_population INTEGER,
    st_population INTEGER
)
""")

print("Villages table created successfully!")

# --------------------------------------------------
# CREATE HAZARDS TABLE
# --------------------------------------------------

cursor.execute("""
CREATE TABLE hazards (
    hazard_id INTEGER PRIMARY KEY,
    village_id INTEGER NOT NULL,
    landslide_count INTEGER,
    rainfall_exposure REAL,
    river_flood_exposure REAL,
    slope REAL,
    hazard_score REAL,
    FOREIGN KEY (village_id) REFERENCES villages(village_id)
)
""")

print("Hazards table created successfully!")

# --------------------------------------------------
# CREATE RISK ASSESSMENT TABLE
# --------------------------------------------------

cursor.execute("""
CREATE TABLE risk_assessment (
    risk_id INTEGER PRIMARY KEY,
    village_id INTEGER NOT NULL,
    risk_score REAL NOT NULL,
    risk_level TEXT NOT NULL,
    relocation_priority TEXT,
    assessment_date TEXT,
    FOREIGN KEY (village_id) REFERENCES villages(village_id)
)
""")

print("Risk assessment table created successfully!")

# --------------------------------------------------
# CREATE RELOCATION SITES TABLE
# --------------------------------------------------

cursor.execute("""
CREATE TABLE relocation_sites (
    site_id INTEGER PRIMARY KEY,
    site_name TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    available_area REAL,
    capacity INTEGER,
    accessibility_score REAL,
    site_risk_score REAL,
    suitability_score REAL
)
""")

print("Relocation sites table created successfully!")

# --------------------------------------------------
# CREATE RELOCATION ASSIGNMENTS TABLE
# --------------------------------------------------

cursor.execute("""
CREATE TABLE relocation_assignments (
    assignment_id INTEGER PRIMARY KEY,
    village_id INTEGER NOT NULL,
    site_id INTEGER NOT NULL,
    people_to_relocate INTEGER NOT NULL,
    distance REAL,
    allocation_status TEXT NOT NULL,
    FOREIGN KEY (village_id) REFERENCES villages(village_id),
    FOREIGN KEY (site_id) REFERENCES relocation_sites(site_id)
)
""")

print("Relocation assignments table created successfully!")

# --------------------------------------------------
# SAVE CHANGES
# --------------------------------------------------

connection.commit()

print("All database tables created successfully!")

# --------------------------------------------------
# CLOSE DATABASE
# --------------------------------------------------

connection.close()

print("Database connection closed successfully!")