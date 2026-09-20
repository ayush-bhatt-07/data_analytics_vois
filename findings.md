# KrishiDrishti: Verified Findings Log

This file is updated after each phase. Only things that were actually computed from the data are recorded.

**Evidence labels** (every entry must carry one):
- `[OBSERVED]` a value read directly from the dataset
- `[DERIVED]` a metric we calculated from dataset columns
- `[MODEL]` a model prediction or model-based estimate (never causal)
- `[ASSUMPTION]` an external assumption, not in the dataset
- `[RECOMMENDATION]` a suggestion that follows from the evidence above

---

## Phase 0: Setup & environment

| # | Label | Finding | How verified |
|---|-------|---------|--------------|
| 0.1 | [OBSERVED] | Raw CSV has 4,000 rows x 28 columns | `pd.read_csv(...).shape` |
| 0.2 | [OBSERVED] | All 28 column names match the project spec, in the same order | `check_shape_and_columns()` in `src/data_loader.py` |
| 0.3 | [OBSERVED] | Raw file SHA-256: `fe17b9752e998a7463e5ac2e1e03f6d8c781be3541aaa3e422442ff1bb455c43` | `sha256sum`; saved in `data/raw/SHA256.txt` |

No data-quality, seasonal, or model findings exist yet.

## Phase 1: Data audit (read-only; nothing was cleaned or modified)

Raw file checksum re-verified after the audit (unchanged). Tables: `outputs/tables/p1_*.csv`. Figures: `outputs/figures/p1_*.png`. Code: `src/audit.py`.

### A. Structure and quality
| # | Label | Finding |
|---|-------|---------|
| 1.1 | [OBSERVED] | 17 float, 5 int and 6 text columns. No duplicate rows (full-row, Farm_ID, or ignoring Farm_ID). Farm_ID runs SF10001-SF14000 with no gaps. No stray spaces or case-variant labels in any text column. |
| 1.2 | [OBSERVED] | Only 3 columns have missing values: Rainfall_mm 48 (1.2%), Soil_Moisture_pct 40 (1.0%), Yield_Tonnes_Ha 32 (0.8%). Each affected row has exactly one missing cell: 120 rows (3.0%) in total. |
| 1.3 | [DERIVED] | Missingness looks close to random but this is not proven. 75 tests were run; 9 gave p<0.05 (about 3.8 expected by chance), 2 gave p<0.01, and none pass a Bonferroni threshold (smallest p = 0.0028 vs 0.00067). 5 of the 9 involve Yield-missing rows (only 32 rows, so low power). Evidence is weak either way. |
| 1.4 | [OBSERVED] | No negative values except Profit_INR (1,966 of 4,000 rows, 49.2%, are negative). No zeros anywhere. Humidity, Soil_Moisture and Disease_Pest_Risk are all within 0-100. |

### B. Formula checks (mathematical identities in the data)
| # | Label | Finding |
|---|-------|---------|
| 1.5 | [DERIVED] | **Production = Yield x Area** holds in 3,968 / 3,968 testable rows (100%), within the 0.005 rounding error of a 2-decimal Production column. (32 rows have no Yield, so cannot be tested.) |
| 1.6 | [DERIVED] | **Revenue = round(Production x Price)** holds exactly in 4,000 / 4,000 rows using the STORED (2-decimal) Production. Using un-rounded Yield x Area x Price instead, only 216 / 3,968 rows (5.4%) fall within 1 INR. So Revenue is built from the rounded Production column. |
| 1.7 | [DERIVED] | **Profit = Revenue - Total_Cost** holds exactly in 4,000 / 4,000 rows. |
| 1.8 | [DERIVED] | **Water_Efficiency = Production / Water_Used x 1000** holds within 0.0005 (3-decimal rounding) in 4,000 / 4,000 rows. |
| 1.9 | [DERIVED] | The 32 missing Yield values could be recovered as Production / Area: on rows where Yield is known, this recovery differs from the stored Yield by 0.0006 on average and 0.01 at most. **Not applied.** |

### C. Categories
| # | Label | Finding |
|---|-------|---------|
| 1.10 | [OBSERVED] | **All 10 districts appear under all 8 states** (every State x District cell has 34-71 farms; none are empty). For example, Rajkot appears under Punjab and Ludhiana under Tamil Nadu. |
| 1.10b | [ASSUMPTION] | External knowledge: in reality each district belongs to one state. So District is not a genuine sub-division of State in this file. |
| 1.11 | [OBSERVED] | Season counts: Kharif 1,779 (44.5%), Rabi 1,627 (40.7%), Zaid 594 (14.9%). Every crop appears in all 3 seasons. |
| 1.12 | [DERIVED] | Crop mix does not differ detectably across seasons: chi-square = 13.93, dof = 14, p = 0.455. E.g. Wheat is 47.6% Kharif, 38.6% Rabi, 13.8% Zaid. |
| 1.12b | [ASSUMPTION] | External knowledge: Wheat is normally a Rabi crop in India, so Kharif-heavy Wheat is agronomically unusual. |

### D. Ranges and outliers
| # | Label | Finding |
|---|-------|---------|
| 1.13 | [OBSERVED] | **Values pile up exactly at the minimum.** Rainfall_mm = 80.0 in 103 rows (2.6%): 0 Kharif, 38 Rabi, 65 Zaid. Yield = 0.3 in 220 of 3,968 rows (5.5%), spread across Kharif 93 / Rabi 77 / Zaid 50, and none are Sugarcane (its minimum is 1.39). Smaller pile-ups also at Soil_pH = 5.2 (44 rows), Seed_Quality = 0.65 (53) and = 1.0 (73), Pesticide = 0.5 (51), Fertilizer = 40 (33). |
| 1.13b | [DERIVED] | This pattern is consistent with values being clipped at a lower limit (the true value may be lower than the recorded one). This is an inference from the histograms, not confirmed by any documentation. |
| 1.14 | [DERIVED] | **Most "outliers" are crop scale, not errors.** Yield has 302 IQR outliers overall (7.55%) but only 1 within crop, because Sugarcane averages 46.9 t/ha (max 101.44) versus 0.9-2.7 t/ha for the other crops. Same effect for Water_Used (276 -> 5) and Production (333 -> 31). Profit stays high within crop (404 -> 201), i.e. it is genuinely skewed. |
| 1.15 | [OBSERVED] | Prices differ enormously by crop: mean about 3,490 INR/t for Sugarcane, 20,991 Maize, 22,023 Rice, 23,829 Wheat, 56,310 Groundnut, 67,921 Cotton, 71,432 Pulses, 103,373 Chilli. |
| 1.16 | [DERIVED] | **Cost per hectare is almost identical across crops** (mean 66,056-67,089 INR/ha for all 8 crops). Combined with 1.15, the share of farms with negative profit is: Wheat 74.1%, Rice 66.4%, Maize 63.7%, Pulses 49.2%, Groundnut 40.8%, Cotton 34.6%, Chilli 18.0%, Sugarcane 11.5%. |
| 1.17 | [OBSERVED] | Water_Used per hectare is not zero for Rainfed farms: mean 446 m3/ha (Drip 727, Sprinkler 795, Flood 1,029). |

### E. Implications for later phases (nothing applied yet)
| # | Label | Suggestion |
|---|-------|------------|
| 1.18 | [RECOMMENDATION] | **Leakage (decide in Phase 7):** with Yield as the target, Production, Revenue, Profit and Water_Efficiency are all exact functions of Yield (given Area, Price, Cost), so they should be excluded as predictors. Total_Cost is not an exact function of anything tested, but cost per hectare is nearly constant, so it should be examined before being used. |
| 1.19 | [RECOMMENDATION] | Missing values (Phase 2): decide between recovering Yield from Production / Area or dropping those 32 rows, and how to handle Rainfall / Soil_Moisture. Any imputation for ML should happen inside the cross-validation pipeline to avoid leakage. |
| 1.20 | [RECOMMENDATION] | Do not treat District as nested inside State until the data source is clarified (see 1.10). |
| 1.21 | [RECOMMENDATION] | Because of the yield floor (1.13), report the share of rows at 0.3 when presenting yield models, and be careful with conclusions about the lowest-yield farms. |

---

## Change log (overwrites / important revisions)

| Date | Phase | What changed | Why |
|------|-------|--------------|-----|
| 2026-09-20 | 0 | File created | Project setup |
| 2026-09-20 | 1 | Added `src/audit.py`, `src/audit_plots.py`, `scripts/run_phase1.py`; filled `notebooks/01_data_audit.ipynb`; created `outputs/tables/p1_*.csv` and `outputs/figures/p1_*.png`. Runner was executed twice; the second run regenerated the same Phase 1 outputs (overwrite=True) after extra tables were added. Values were identical. | Phase 1 audit |
