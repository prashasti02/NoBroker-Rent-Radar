"""
Build the Rent Radar SQLite database from the processed tables.
Run from the sql/ folder:   python build_db.py
Creates rent.db with two related tables (listings, locality_attributes).
"""
import sqlite3
import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROC = HERE.parent / "data" / "processed"
DB = HERE / "rent.db"

listings = pd.read_csv(PROC / "listings_clean.csv")   # full cleaned set (pre-imputation is fine for SQL exploration)
attrs_raw = pd.read_csv(PROC / "locality_attributes.csv")

# keep only the columns the schema declares, in order
attr_cols = ["locality_name", "address", "zone", "metro_status", "nearest_metro_km",
             "tech_park_proximity", "tech_park_km_approx", "it_park_count_5km",
             "school_count_2km", "hospital_count_2km", "retail_count_2km",
             "distance_to_cbd_km", "latitude", "longitude"]
attrs = attrs_raw[[c for c in attr_cols if c in attrs_raw.columns]].copy()

con = sqlite3.connect(DB)
con.executescript((HERE / "schema.sql").read_text())
listings.to_sql("listings", con, if_exists="append", index=False)
attrs.to_sql("locality_attributes", con, if_exists="append", index=False)
con.commit()

n1 = con.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
n2 = con.execute("SELECT COUNT(*) FROM locality_attributes").fetchone()[0]
matched = con.execute("""
    SELECT COUNT(*) FROM listings l
    JOIN locality_attributes a ON lower(l.locality_name) = lower(a.locality_name)
""").fetchone()[0]
print(f"Built {DB.name}: {n1} listings, {n2} localities, {matched} listings join to a locality.")
con.close()
