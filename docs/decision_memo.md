# Decision Memo — What should a Mumbai flat cost?
**To:** NoBroker Pricing Team **From:** The Outliers (Akshara · Prashasthi · Sudarshan)
**Re:** A fair-rent model for Mumbai, and what to do with it — *one page*

---

### The question
The same 2BHK is listed at wildly different prices across Mumbai. We built a **fair-rent
model** that estimates what a flat *should* cost from its features, and flags listings that
look mispriced.

### What the data shows
- **Size and bedrooms set the rent.** A flat's square footage is by far the strongest driver,
  bedrooms second. Adding ~250 sq ft is worth more than an extra bedroom, an extra bathroom,
  or moving to a top-decile locality.
- **Location barely moves the needle — the surprise.** In a city obsessed with location,
  neither amenity counts (metro, schools, hospitals ≈ 0 correlation) nor even the locality's
  own price level add much once size is known. Turning location into a number beats raw
  amenities, but still trails the physical features.
- **An operational metro is *not* a premium.** Localities with a running metro rent slightly
  *lower* per sq ft — Mumbai's metro serves mid-income suburbs, while the priciest addresses
  grew rich without one. Verified, not a glitch.
- **Bigger flats cost *more* per sq ft,** the opposite of a bulk discount — luxury clusters in
  premium pockets.

### The model
A tuned **Random Forest** on `log(rent)`, chosen after benchmarking 7 models on an honest
train/test split. On unseen flats: **R² ≈ 0.70**, typical error **~27%** (average miss ≈ ₹31k).
It is dependable below ~₹1L and looser for the thin luxury tail. We deliberately kept it
*believable* — an early pipeline scored R² > 0.9, which we traced to a data leak and removed.

### Recommendation — do this, in order
1. **Ship the fair-rent estimate for the mass market (< ₹1L).** That's where it's reliable and
   where most renters are. Route luxury flats (> ₹2L) to a human.
2. **Launch the mispriced-listing detector.** On the test set it flagged **221 listings as
   over-priced** and **117 as under-priced (bargains)** — the fastest win for renters.
3. **Price by size first, location second.** Lead pricing rules with square footage and
   bedrooms; do **not** pay up for metro/amenity flags — the data says renters don't.
4. **Refresh the data before trusting the number.** It is a single snapshot; schedule a
   recurring crawl and watch for drift.
5. **Invest in better features, not more rows.** The learning curve is flat — the next accuracy
   gain comes from richer inputs (verified area, photos, exact address), not a bigger sample.

### Trade-offs & limits (stated up front)
The ~0.70 ceiling is **genuine listing noise** — identical flats are advertised at different
prices; no model beats that here. The luxury tail is under-predicted (a known, safe bias).
84 listings with an unknown locality are priced on city-level information only.

> **Bottom line:** Mumbai rent is set by *how big* a flat is far more than *where* it is. Ship
> the estimate for ordinary flats, flag the mispriced ones, and price by size — with eyes open
> about the luxury tail we can't yet pin down.
