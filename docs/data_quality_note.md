# Data Quality Note — Mumbai Rent Radar
**The Outliers** · Akshara · Prashasthi · Sudarshan

This note records **what was wrong with the raw data, what we did about it, and what
stays imperfect.** Honesty about limits is part of the deliverable.

---

## The raw material
- **Rental listings:** 5,100 rows × 12 columns — one crawl of Mumbai rental adverts.
- **Locality attributes:** a companion table describing each locality (zone, metro access,
  tech-park distance, schools/hospitals/retail nearby, coordinates, distance to the city centre).
- The two are joined on the **locality**, which had to be extracted before anything else worked.

---

## What was wrong, and what we did

| # | Problem in the raw data | Fix applied | Why |
|---|---|---|---|
| 1 | **City** spelled 6 ways (`Bombay`, `mumbai`, `MUMBAI`, stray spaces) | collapsed to a single value `Mumbai` | one city only — this was pure noise |
| 2 | **Rent** stored as text in 4 formats: `₹1,47,500`, `40,000`, `50k`, `102500/-` | stripped symbols; expanded the `k` shorthand (×1000); parsed to a number | a price must be numeric to analyse or model |
| 3 | **Area Type** with casing/spacing variants (`Super  Area`, `super area`) | trimmed + Title-Cased into 3 clean types | same category, split by formatting |
| 4 | **Furnishing** variants and a typo (`Semi Furnished`, `Unfurnishd`) | mapped to 3 canonical labels | typos were splitting real groups |
| 5 | **Tenant** and **Contact** with slashes/spacing (`Bachelors / Family`, `Contact  Agent`) | canonicalised | same issue |
| 6 | **Floor** as free text: `7 out of 9`, `Ground`, `Upper Basement out of 8`, `Unknown` | split into **floor number** (basement −ve, ground 0) and **building height**; unparseable → missing | two useful numbers were hidden in one string |
| 7 | **Bathroom = 0** | set to missing | a flat cannot have zero bathrooms — impossible value |
| 8 | **Size < 100 sq ft** | set to missing | too small to be a whole home — a typo, not a studio |
| 9 | **Locality** mixed building + area (`Green Gate Apartment, Pali Hill`) | split into **address** (full) and **locality_name** (the area, city token removed) | the locality is both the join key and a price driver |
| 10 | **Duplicates** — 27 exact repeats + 23 repeated listing IDs | dropped, keeping the first | double-counting biases every statistic |

**Result of cleaning:** 5,100 → **5,050** rows; six text fields reduced to their true
categories; ~1,350 prices recovered from text (including ~475 hidden behind the `k` shorthand).

---

## Missing values — resolved honestly
10.8% of rows had at least one gap. We imputed **inputs**, never the **target**.

| Field | Missing | Method | Reasoning |
|---|---|---|---|
| `size` | 241 | median **by BHK** | size scales with BHK; chosen over global median (which spikes the distribution) and KNN (harder to explain), after testing all three |
| `bathroom` | 88 | median **by BHK** | bathrooms track BHK almost exactly |
| `floor_num`, `total_floors` | 29 / 50 | median | small, structural gaps |
| `furnishing_status` | 53 | mode (`Semi-Furnished`) | too few rows to shift the category mix |
| `locality_name` | 84 | tagged **Unknown** | an identity cannot be averaged; these fall back to a city-level estimate |
| `rent` (target) | 50 | **set aside** | a listing with no price cannot train a price model — imputing it would be inventing the answer |

---

## The locality join
After extracting `locality_name`, **98.3%** of listings matched a locality in the attributes
table (the only misses are the 84 rows with no locality at all). The two datasets share the
same 267 locality vocabulary — the join is clean and near-complete.

---

## What remains imperfect (carried forward, stated plainly)
1. **One snapshot in time.** A single crawl — no seasonality, no trend. Refresh before pricing.
2. **Listing noise is real.** Identical flats are advertised at different prices; this sets a
   hard ceiling on how well *any* model can do (~R² 0.7), independent of technique.
3. **The luxury tail is thin and wild.** A few extreme rents (e.g. a ₹65 lakh entry that is
   almost certainly a typo) were winsorised for modelling, not deleted — we keep the row's other
   honest data.
4. **Amenity columns add little.** Metro/school/hospital counts barely correlate with rent
   (see the diagnostic notebook); richer inputs would be needed to improve accuracy.
5. **84 "Unknown" localities** are priced less precisely, on city-level information only.

*Anything that looked too clean, we double-checked. The results here are believable, not perfect.*
