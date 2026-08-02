-- ============================================================================
--  Mumbai Rent Radar — database schema
--  Two related tables, joined on locality_name (the fair-rent question lives
--  in how a flat's own features and its locality's attributes combine).
-- ============================================================================

DROP TABLE IF EXISTS listings;
CREATE TABLE listings (
    listing_id         TEXT PRIMARY KEY,
    city               TEXT,
    locality_name      TEXT,          -- join key -> locality_attributes.locality_name
    address            TEXT,
    bhk                INTEGER,
    rent               REAL,          -- monthly rent, rupees
    size               REAL,          -- carpet/super area, sq ft
    area_type          TEXT,
    floor_num          REAL,          -- 0 = ground, negative = basement
    total_floors       REAL,
    bathroom           REAL,
    furnishing_status  TEXT,
    tenant_preferred   TEXT,
    point_of_contact   TEXT
);

DROP TABLE IF EXISTS locality_attributes;
CREATE TABLE locality_attributes (
    locality_name         TEXT PRIMARY KEY,   -- join key
    address               TEXT,
    zone                  TEXT,
    metro_status          TEXT,
    nearest_metro_km      REAL,
    tech_park_proximity   TEXT,
    tech_park_km_approx   REAL,
    it_park_count_5km     INTEGER,
    school_count_2km      INTEGER,
    hospital_count_2km    INTEGER,
    retail_count_2km      INTEGER,
    distance_to_cbd_km    REAL,
    latitude              REAL,
    longitude             REAL
);

CREATE INDEX IF NOT EXISTS idx_listings_locality ON listings(locality_name);
CREATE INDEX IF NOT EXISTS idx_listings_bhk      ON listings(bhk);
