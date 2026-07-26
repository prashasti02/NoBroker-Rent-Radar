# `mumbai_attributes.csv` — locality attributes for Mumbai

**File:** `Attributes.csv` — 604 rows × 37 columns
**Grain:** one row per distinct `Area Locality` in Mumbai's house-rent listings
**Join key:** `locality_name` + `city`, matching the raw `Area Locality` string **verbatim** —
including its original spelling, casing and trailing road name, so the join needs no fuzzy matching
**Reference date:** 2022-04-13 (see *The 2022 framing* below)

604 Mumbai localities, spanning listings posted between **13 Apr 2022 and 9 Jul 2022**.

## Where it comes from

Everything positional was fetched from the web; nothing is typed in from memory.

| Source | What it supplied |
|---|---|
| [Photon](https://photon.komoot.io) (OSM geocoder) | a lat/lon for every raw locality string, bounded to Mumbai's box so a namesake elsewhere cannot win |
| [Overpass](https://overpass-api.de) (OSM query API) | metro stations + the route relations they belong to, suburban/mainline rail, airports, schools, hospitals, malls, IT-park features |
| Wikipedia, per metro line | the opening date of every line and section, read 2026-07-22 |

Two hand-authored inputs live in `src/city_reference.py` and are the only judgement calls in the
table: the list of employment hubs worth measuring distance to (14 curated Mumbai hubs — Bandra
Kurla Complex, Mindspace Malad, Lower Parel Business District, SEEPZ Andheri East, Nirlon Knowledge
Park, Hiranandani Business Park Powai, Godrej One Vikhroli, Wagle Estate Thane, MIDC Andheri East,
Nariman Point CBD, Belapur CBD, Mindspace Airoli, Vashi Business District, Millennium Business Park
Mahape), and the state of the metro network in 2022. Both are code, so both are reviewable in a diff.

Raw API responses are cached in `data/geo_cache/`. A rebuild needs no network.

## The 2022 framing — the point of this table

Every listing was posted between **13 Apr and 9 Jul 2022**, and Mumbai's metro network grew
substantially afterwards — Lines 2A and 7 reached Andheri in Jan 2023. Scoring a 2022 listing
against today's map credits those localities with access nobody had — a leak that flatters the
model and cannot be caught downstream.

So a station only counts as operational if it was open on **2022-04-13**, the first day of the
posting window, which makes one status column true for every row rather than just the late ones.
The table then carries both readings so the difference can be measured:

| Column | Reading |
|---|---|
| `metro_access_sample` | today's network — the naive answer, and the one a current map gives you |
| `metro_access_verified` | the network as it stood on 2022-04-13 |
| `metro_flag_agrees` | `False` wherever the two differ |

**Today's map would over-credit metro access for 215 of 604 localities.** 117 Residency, Chembur
East is a clean example: `metro_status` is `under_construction`, because its nearest station
(Shivaji Chowk) opened after the last listing in the file — the row's `nearest_metro_station`
(the 2022-operational one) is Ghatkopar L1, 5.74 km away.

## Columns

### The requested eight, in order

| Column | Type | Notes |
|---|---|---|
| `locality_name` | str | the raw `Area Locality` string, unmodified |
| `city` | str | `Mumbai` throughout |
| `zone` | str | `north` / `east` / `south` / `west` / `unknown` — see *Zone* below |
| `metro_status` | str | `operational` (a 2022 station within 2.5 km), `under_construction` (a station there today but not in 2022), `none`, `unknown` |
| `nearest_metro_station` | str | nearest station **that was running in 2022** |
| `tech_park_proximity` | str | `yes` if the nearest employment hub is ≤ 6 km |
| `nearest_tech_park` | str | nearest hub from the curated list above |
| `tech_park_km_approx` | float | straight-line km to it |

### Metro detail

| Column | Type | Notes |
|---|---|---|
| `nearest_metro_line` | str | colour/key of the line serving `nearest_metro_station` (`blue`, `red`, or `yellow` in this file) |
| `nearest_metro_km` | float | distance to the nearest 2022-operational station |
| `metro_access_sample` | str | `yes`/`no` — naive flag, today's network |
| `metro_access_verified` | str | `yes`/`no` — 2022 network |
| `metro_flag_agrees` | bool | `False` = the naive flag would have been wrong here |
| `nearest_metro_station_today` | str | nearest station on the current network |
| `nearest_metro_km_today` | float | and its distance |

### Employment and infrastructure

| Column | Type | Notes |
|---|---|---|
| `tech_park_band` | str | `0-3km` / `3-6km` / `6km+` |
| `it_park_count_5km` | Int | OSM features that look like IT parks within 5 km — **noisy, see caveats** |
| `nearest_rail_station` | str | suburban/mainline station — this is the one that matters in Mumbai |
| `rail_station_km` | float | |
| `airport_km` | float | to Mumbai's commercial airport, selected by IATA code |
| `school_count_2km` | Int | schools, colleges and universities |
| `hospital_count_2km` | Int | hospitals and clinics |
| `retail_count_2km` | Int | malls, supermarkets, department stores |

### Geography and listing metadata

| Column | Type | Notes |
|---|---|---|
| `latitude`, `longitude` | float | the geocoded point; null where the string never resolved |
| `distance_to_cbd_km` | float | to Mumbai's business district, not the zone origin |
| `geo_district`, `geo_state` | str | OSM's admin labels — sparse (3.3% / 2.8% null in this file) |
| `n_listings_2022` | int | listings in this locality |
| `first_posted_on`, `last_posted_on` | date | posting window for this locality |

**No rent, size or BHK statistics are included.** They would be target leakage in a rent model, and
they are derivable from the listings file anyway.

### Geocoding provenance

| Column | Type | Notes |
|---|---|---|
| `geocode_confidence` | str | `high` (landed on a `place/*` feature within 45 km of the CBD), `medium`, `low`, `none` |
| `geocode_match_name` | str | what the geocoder actually matched — compare it to `locality_name` to audit a row |
| `geocode_feature_type` | str | e.g. `place/suburb`, `highway/bus_stop` |
| `geocode_query` | str | which of the query variants produced the hit |
| `reference_year`, `metro_status_asof` | | `2022`, `2022-04-13` — constant, carried so a joined table stays self-describing |

## What to expect

| | |
|---|---|
| Geocode confidence | 386 high · 104 medium · 97 low · 17 none |
| Localities that never resolved | 17 (2.8%), affecting 27 listings (2.8%) |
| `metro_status` | 223 operational · 149 none · 215 under_construction · 17 unknown |
| `tech_park_proximity` | 531 yes · 56 no · 17 unknown |
| `zone` | 181 south · 169 east · 156 north · 81 west · 17 unknown |
| Median nearest metro | 3.70 km · median nearest hub 2.94 km · median rail station 1.11 km |

Every distance and count column is null for the 17 unresolved localities. Those rows carry
`unknown` in the categorical columns rather than a guessed value — the attributes are honestly
missing, not zero.

### Zone

`zone` is a quadrant measured from **the median of Mumbai's own localities**, with the lat/lon
offsets divided by the city's spread before the direction is read. Both corrections are needed: a
plain bearing off the CBD makes almost every Mumbai locality "north" (the city is linear and Fort is
at its foot). In this file that resolves to Andheri West as west, Chembur/Ghatkopar/Powai as east,
Kandivali East/Malad West as north, and Dadar West/Lower Parel/Worli as south — but it is a
heuristic, not an administrative boundary, and localities near a quadrant edge can land on either
side of it.

## What this dataset is lacking

1. **The geocode repair pass did not run for Mumbai.** Photon began refusing connections after
   roughly 10k requests, and Mumbai was one of the cities still waiting when that happened. The pass
   re-scores ambiguous matches on name similarity *and* distance from the parent locality — it is
   what would catch a compound locality string resolving to a same-named place elsewhere. This file
   keeps its first-pass geocodes: city-bounded and mostly right, but weaker on compound strings.
   **This is the single biggest quality gap**, and it is fixable with one command (below).

2. **Only the metro columns are time-corrected.** Schools, hospitals, retail, rail stations, IT-park
   features and the employment hubs all reflect **today's** OpenStreetMap, not 2022. For amenities
   this is mostly a mapping-coverage artefact rather than real change — OSM's India coverage grew a
   lot between 2022 and now — so treat those counts as *relative* density between localities, not
   absolute 2022 counts.

3. **`it_park_count_5km` is noisy.** It comes from matching OSM names against patterns like
   "Tech Park" / "Cyber City", which also matches flyovers, approach roads and car parks named after
   them. The obvious junk is filtered, but this column is a weak signal. `nearest_tech_park` and
   `tech_park_km_approx`, which use the curated hub list, are the reliable ones.

4. **The employment-hub list is curated, not exhaustive** (14 hubs). It covers the centres that
   actually move rents, but a small office park will never appear as somebody's nearest hub.

5. **Thresholds are baked into the categorical columns.** `metro_status` uses 2.5 km and
   `tech_park_proximity` uses 6 km. Both raw distances are in the table, so re-derive the flags at
   your own cut-off rather than accepting these. Friends Colony, for instance, reads `none` on a
   2.51 km nearest station — just over the line.

6. **Some locality strings are apartment names with no locality in them.** Nothing can geocode
   them; they stay `unknown` (17 rows here).

7. **Distances are straight-line, not travel time.** In Mumbai especially, 3 km across a creek is
   not 3 km.

8. **No pincode.** Photon returns postcodes too inconsistently for Indian localities to be worth a
   column; if you need one, it would have to come from a separate PIN-code dataset.

9. **The monorail is not counted as metro.** Mumbai's monorail is excluded by the city's default
   rule.

## Fixing the geocodes later

Photon rate-limits by IP and the block clears on its own — give it a few hours. Then, from the repo
root:

```bash
python src/fetch_locality_geodata.py --repair Mumbai
```

It resumes from `data/geo_cache/`, re-checks only the suspect entries, and overwrites a cached hit
**only** when a better-scoring candidate is found — so it cannot make the file worse, and it is safe
to interrupt and re-run.

Then fold the improved coordinates through into zones, distances and nearest-station columns:

```bash
python src/build_all_cities_attributes.py
```

If Photon is still refusing connections, raise `SLEEP_PHOTON` in `src/fetch_locality_geodata.py`
from `0.35` to about `1.0` — slower, but under the limit.

## Files

| File | Role |
|---|---|
| `src/fetch_locality_geodata.py` | fetches and caches Photon geocodes + Overpass layers; `--repair` re-scores ambiguous matches |
| `src/city_reference.py` | curated employment hubs, per-line 2022 metro rules, airport IATA code |
| `src/build_all_cities_attributes.py` | assembles the table |
| `data/geo_cache/` | raw API responses, so a rebuild needs no network |
