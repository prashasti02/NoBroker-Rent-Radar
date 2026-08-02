# 🏙️ Mumbai Rent Radar — a fair-rent model for a noisy market
**Team The Outliers** · Akshra · Prashasthi · Sudarshan
*IIT Mandi — AI-Powered Coding & Analytics Programme*

---

## The question (business first)
Every tenant in Mumbai asks the same thing: **what should this flat actually cost?** The same
2BHK is advertised at wildly different prices across localities, floors and furnishing levels.
This project builds a **fair-rent model** from real listings, and turns it into a tool that
**flags over- and under-priced flats.**

## The answer, in one line
> **Mumbai rent is set by how *big* a flat is far more than *where* it is.** Our model predicts
> a fair rent within a typical ~27% for ordinary flats, flags mispriced listings, and is honest
> about the luxury tail it can't pin down.

## What we found
| Finding | So what |
|---|---|
| **Size & bedrooms drive rent**; location barely does | Price by square footage first, not by address |
| **Amenities (metro, schools) ≈ 0 correlation** with rent | Don't pay up for amenity flags — renters don't |
| **An operational metro is *not* a premium** (slightly cheaper) | A verified, counter-intuitive fact |
| **Bigger flats cost *more* per sq ft** | Luxury clusters in premium pockets |
| **~R² 0.70 ceiling = genuine listing noise** | Identical flats are priced differently; that's the real limit |

## The model
A **tuned Random Forest** on `log(rent)`, picked after benchmarking 7 models on an honest
train/test split. **R² ≈ 0.70**, typical error **~27%** (avg miss ≈ ₹31k). Reliable under ₹1L;
looser for luxury. We kept it *believable* — and caught a data leak that had faked R² > 0.9.

## How the work is laid out
```
notebooks/   01 cleaning → 02 imputation → 03 descriptive EDA → 04 diagnostic EDA →
             05 feature engineering → 06 modelling → 07 tuning → 08 predictive EDA →
             09 interpretation → 10 AI-failures & recommendations
sql/         SQLite database (build_db.py), analytical queries (queries.sql), results
data/raw/    the original files      data/processed/  cleaned & modelling tables
figures/     every chart, exported   assets/          IIT Mandi logo + hero images
presentation/  full deck + lite deck  docs/  data-quality note · decision memo
```
Each notebook flows into the next (each saves what the next loads). Every chart carries its
own **insight** and, where a choice was made, the **decision** it drove.

## Run it yourself
```bash
pip install -r requirements.txt
python -m ipykernel install --user --name outliers-rent --display-name "Rent Radar"
python sql/build_db.py && python sql/run_queries.py     # build DB + run SQL
# then run the notebooks in order (01 → 10)
```

## Read these first
- **`docs/decision_memo.md`** — the one-page recommendation for a decision owner.
- **`docs/data_quality_note.md`** — what was wrong, what we did, what stays imperfect.
- **`notebooks/10_ai_failures.ipynb`** — how we used AI, the confidently-wrong moment we caught,
  and the honest limitations.

## Honest limitations
One snapshot in time · listing noise caps accuracy at ~0.70 · luxury tail under-predicted ·
amenity data adds little · 84 unknown-locality listings priced on city-level info.

## The AI appendix (short version)
We used AI as a **fast drafting partner** — messy-string parsers, chart scaffolding, refactors —
but **not as a certifier**. When an early model reported R² > 0.9, that was the tell: we hunted
down the leakage (locality encoded on all data + a rent-derived feature) and fixed it. 

