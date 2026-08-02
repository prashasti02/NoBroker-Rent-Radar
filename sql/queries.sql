-- ============================================================================
--  Mumbai Rent Radar — analytical queries
--  Written to be read by the next analyst: every query answers one fair-rent
--  question, using joins, GROUP BY, window functions and CTEs — before any
--  Python touches the data.
--
--  Each query carries a machine-readable tag so the runner can execute and
--  label it automatically (see run_queries.py).
-- ============================================================================


-- @q1_locality_leaderboard | Which localities are most/least expensive, and where do they rank?
-- GROUP BY + window RANK() over the whole city.
WITH loc AS (
    SELECT locality_name,
           COUNT(*)               AS n_listings,
           ROUND(AVG(rent))       AS avg_rent
    FROM listings
    WHERE rent IS NOT NULL
    GROUP BY locality_name
    HAVING COUNT(*) >= 10
)
SELECT locality_name, n_listings, avg_rent,
       RANK() OVER (ORDER BY avg_rent DESC) AS rank_expensive
FROM loc
ORDER BY avg_rent DESC
LIMIT 12;


-- @q2_price_per_sqft | Best value: which localities give the most space per rupee?
-- Rent-per-sqft with PERCENT_RANK to place each locality on the affordability curve.
WITH per_sqft AS (
    SELECT locality_name,
           COUNT(*)                              AS n,
           ROUND(AVG(rent * 1.0 / size), 1)      AS rent_per_sqft
    FROM listings
    WHERE rent IS NOT NULL AND size IS NOT NULL AND size > 0
    GROUP BY locality_name
    HAVING COUNT(*) >= 10
)
SELECT locality_name, n, rent_per_sqft,
       ROUND(PERCENT_RANK() OVER (ORDER BY rent_per_sqft) * 100, 0) AS cheaper_than_pct
FROM per_sqft
ORDER BY rent_per_sqft ASC
LIMIT 12;


-- @q3_bhk_area_matrix | How does rent rise with BHK, and does area type matter?
SELECT bhk,
       area_type,
       COUNT(*)          AS n,
       ROUND(AVG(rent))  AS avg_rent
FROM listings
WHERE rent IS NOT NULL
GROUP BY bhk, area_type
HAVING COUNT(*) >= 15
ORDER BY bhk, avg_rent DESC;


-- @q4_rank_within_zone | Within each zone, which localities are the priciest? (window PARTITION BY)
WITH loc AS (
    SELECT l.locality_name, a.zone,
           ROUND(AVG(l.rent)) AS avg_rent, COUNT(*) AS n
    FROM listings l
    JOIN locality_attributes a ON lower(l.locality_name) = lower(a.locality_name)
    WHERE l.rent IS NOT NULL
    GROUP BY l.locality_name, a.zone
    HAVING COUNT(*) >= 8
)
SELECT * FROM (
    SELECT zone, locality_name, avg_rent,
           RANK() OVER (PARTITION BY zone ORDER BY avg_rent DESC) AS rank_in_zone
    FROM loc
)
WHERE rank_in_zone <= 3          -- top 3 priciest per zone
ORDER BY zone, rank_in_zone;


-- @q5_price_tiers | Split localities into 3 price tiers (budget / mid / premium) with NTILE, via a CTE.
WITH loc AS (
    SELECT locality_name, ROUND(AVG(rent)) AS avg_rent, COUNT(*) AS n
    FROM listings
    WHERE rent IS NOT NULL
    GROUP BY locality_name
    HAVING COUNT(*) >= 10
),
tiered AS (
    SELECT locality_name, avg_rent, n,
           NTILE(3) OVER (ORDER BY avg_rent) AS tier_id
    FROM loc
)
SELECT CASE tier_id WHEN 1 THEN '1 Budget' WHEN 2 THEN '2 Mid' ELSE '3 Premium' END AS price_tier,
       COUNT(*)                AS localities,
       ROUND(AVG(avg_rent))    AS tier_avg_rent,
       ROUND(MIN(avg_rent))    AS from_rent,
       ROUND(MAX(avg_rent))    AS to_rent
FROM tiered
GROUP BY tier_id
ORDER BY tier_id;


-- @q6_metro_effect | Do localities on an operational metro rent higher? (join + GROUP BY)
SELECT a.metro_status,
       COUNT(*)                          AS n_listings,
       ROUND(AVG(l.rent))                AS avg_rent,
       ROUND(AVG(l.rent * 1.0 / l.size), 1) AS avg_rent_per_sqft
FROM listings l
JOIN locality_attributes a ON lower(l.locality_name) = lower(a.locality_name)
WHERE l.rent IS NOT NULL AND l.size > 0 AND a.metro_status IS NOT NULL
GROUP BY a.metro_status
ORDER BY avg_rent DESC;


-- @q7_techpark_effect | Is being near a tech park worth more rent? (join + GROUP BY)
SELECT a.tech_park_proximity,
       COUNT(*)             AS n_listings,
       ROUND(AVG(l.rent))   AS avg_rent
FROM listings l
JOIN locality_attributes a ON lower(l.locality_name) = lower(a.locality_name)
WHERE l.rent IS NOT NULL AND a.tech_park_proximity IS NOT NULL
GROUP BY a.tech_park_proximity
ORDER BY avg_rent DESC;


-- @q8_over_under_priced | Which localities sit above/below their zone's average? (window AVG OVER PARTITION)
WITH loc AS (
    SELECT l.locality_name, a.zone, ROUND(AVG(l.rent)) AS avg_rent, COUNT(*) AS n
    FROM listings l
    JOIN locality_attributes a ON lower(l.locality_name) = lower(a.locality_name)
    WHERE l.rent IS NOT NULL
    GROUP BY l.locality_name, a.zone
    HAVING COUNT(*) >= 8
)
SELECT locality_name, zone, avg_rent,
       ROUND(AVG(avg_rent) OVER (PARTITION BY zone)) AS zone_avg,
       ROUND(avg_rent - AVG(avg_rent) OVER (PARTITION BY zone)) AS gap_vs_zone
FROM loc
ORDER BY gap_vs_zone DESC
LIMIT 12;
