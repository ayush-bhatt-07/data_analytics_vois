"""
Phase 1 audit functions.

RULE: every function here only READS the DataFrame and returns a new table.
Nothing is cleaned, filled, dropped or changed.
"""
import numpy as np
import pandas as pd
from scipy import stats

CATEGORICAL = ["State", "District", "Crop", "Season", "Irrigation_Method"]


# ---------------------------------------------------------------- basic checks
def dtype_summary(df):
    """Data type, non-null count and number of unique values per column."""
    return pd.DataFrame({
        "dtype": df.dtypes.astype(str),
        "non_null": df.notna().sum(),
        "n_unique": df.nunique(),
    })


def missing_summary(df):
    """Missing count and % per column (only columns that have any missing)."""
    out = pd.DataFrame({"missing": df.isna().sum(), "missing_pct": df.isna().mean() * 100})
    return out[out.missing > 0].sort_values("missing", ascending=False)


def duplicate_summary(df):
    """Different ways of looking for duplicate rows."""
    no_id = [c for c in df.columns if c != "Farm_ID"]
    return pd.Series({
        "fully duplicated rows": int(df.duplicated().sum()),
        "duplicated Farm_ID": int(df["Farm_ID"].duplicated().sum()),
        "duplicated rows ignoring Farm_ID": int(df.duplicated(subset=no_id).sum()),
    })


def category_hygiene(df, cols=CATEGORICAL + ["Farm_ID"]):
    """Check for stray spaces and upper/lower-case duplicates in text columns."""
    rows = []
    for c in cols:
        s = df[c]
        rows.append({
            "column": c,
            "n_unique": s.nunique(),
            "rows_with_extra_spaces": int((s != s.str.strip()).sum()),
            "case_variant_labels": s.nunique() - s.str.strip().str.lower().nunique(),
        })
    return pd.DataFrame(rows).set_index("column")


# ---------------------------------------------------------------- ranges
def numeric_range_summary(df):
    """min / percentiles / max plus how many rows sit EXACTLY on the min and max."""
    num = df.select_dtypes("number")
    out = num.describe(percentiles=[0.01, 0.5, 0.99]).T[["count", "mean", "std", "min", "1%", "50%", "99%", "max"]]
    out["n_at_min"] = [(num[c] == num[c].min()).sum() for c in num.columns]
    out["n_at_max"] = [(num[c] == num[c].max()).sum() for c in num.columns]
    out["n_zero"] = (num == 0).sum()
    out["n_negative"] = (num < 0).sum()
    return out


def _iqr_flag(s, k=1.5):
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    return (s < q1 - k * iqr) | (s > q3 + k * iqr)


def iqr_outlier_summary(df, group_col="Crop"):
    """
    Count IQR (1.5 x IQR rule) outliers for each numeric column:
      - overall
      - within each group (default: within each Crop)
    A big drop from 'overall' to 'within group' means the values are only
    'outliers' because groups have different scales (e.g. Sugarcane yield).
    """
    rows = []
    for c in df.select_dtypes("number").columns:
        overall = int(_iqr_flag(df[c].dropna()).sum())
        within = int(df.groupby(group_col)[c].transform(_iqr_flag).sum())
        rows.append({"column": c, "outliers_overall": overall,
                     "overall_pct": 100 * overall / len(df),
                     f"outliers_within_{group_col}": within})
    return pd.DataFrame(rows).set_index("column")


# ---------------------------------------------------------------- formula checks
def formula_checks(df):
    """
    Test whether some columns are exact mathematical functions of others.
    Tolerances come from the number of decimals stored in the file
    (Production is stored with 2 decimals, so the rounding error is at most 0.005).
    """
    rows = []

    def add(name, diff, tol, note=""):
        diff = diff.dropna()
        rows.append({
            "formula": name,
            "rows_tested": len(diff),
            "within_tolerance": int((diff.abs() <= tol + 1e-9).sum()),
            "tolerance": tol,
            "max_abs_diff": diff.abs().max(),
            "note": note,
        })

    # 1. Production = Yield x Area  (rounded to 2 decimals)
    calc = df.Yield_Tonnes_Ha * df.Farm_Area_Hectares
    add("Production = Yield x Area", df.Production_Tonnes - calc, 0.005,
        "Yield missing in 32 rows, so those rows cannot be tested")

    # 2a. Revenue = round(Production_column x Price)
    calc = (df.Production_Tonnes * df.Market_Price_INR_Tonne).round()
    add("Revenue = round(Production x Price)", df.Revenue_INR - calc, 0.0,
        "uses the stored (rounded) Production column")

    # 2b. Same test using the un-rounded Yield x Area  (to see which one Revenue follows)
    calc = df.Yield_Tonnes_Ha * df.Farm_Area_Hectares * df.Market_Price_INR_Tonne
    add("Revenue = (Yield x Area) x Price  [alt.]", df.Revenue_INR - calc, 1.0,
        "tolerance 1 INR; fails for most rows, so Revenue uses the ROUNDED Production")

    # 3. Profit = Revenue - Total_Cost
    add("Profit = Revenue - Total_Cost", df.Profit_INR - (df.Revenue_INR - df.Total_Cost_INR), 0.0)

    # 4. Water efficiency = Production / Water x 1000 (3 decimals)
    calc = df.Production_Tonnes / df.Water_Used_m3 * 1000
    add("Water_Eff = Production / Water_Used x 1000", df.Water_Efficiency_t_per_1000m3 - calc, 0.0005)

    out = pd.DataFrame(rows).set_index("formula")
    out["pct_within_tolerance"] = 100 * out.within_tolerance / out.rows_tested
    return out


def recoverable_yield_check(df):
    """
    For the rows where Yield is missing: could Production / Area recover it?
    Also reports how accurate that recovery is on rows where Yield is known.
    (Only a check. Nothing is filled in.)
    """
    known = df.dropna(subset=["Yield_Tonnes_Ha"])
    err = (known.Production_Tonnes / known.Farm_Area_Hectares - known.Yield_Tonnes_Ha).abs()
    miss = df[df.Yield_Tonnes_Ha.isna()]
    return pd.Series({
        "rows with Yield missing": len(miss),
        "...of which Production and Area are present": int(miss[["Production_Tonnes", "Farm_Area_Hectares"]].notna().all(axis=1).sum()),
        "recovery error on known rows: mean": err.mean(),
        "recovery error on known rows: max": err.max(),
    })


# ---------------------------------------------------------------- categories
def state_district_table(df):
    """Rows for every District x State combination."""
    return pd.crosstab(df.District, df.State)


def crop_season_tables(df):
    """Counts, row-% and a chi-square independence test for Crop x Season."""
    counts = pd.crosstab(df.Crop, df.Season)
    row_pct = pd.crosstab(df.Crop, df.Season, normalize="index") * 100
    chi2, p, dof, _ = stats.chi2_contingency(counts)
    return counts, row_pct, {"chi2": chi2, "p_value": p, "dof": dof}


# ---------------------------------------------------------------- missingness
def missingness_association(df, missing_cols=("Rainfall_mm", "Soil_Moisture_pct", "Yield_Tonnes_Ha")):
    """
    Does 'is missing' depend on anything else?
      - vs categorical columns: chi-square test
      - vs numeric columns: Mann-Whitney U test
    Many tests are run, so a few p < 0.05 are expected by chance alone.
    """
    rows = []
    for m in missing_cols:
        flag = df[m].isna()
        for c in ["Season", "Crop", "State", "Irrigation_Method"]:
            p = stats.chi2_contingency(pd.crosstab(df[c], flag))[1]
            rows.append({"missing_column": m, "compared_with": c, "test": "chi-square", "p_value": p})
        for c in df.select_dtypes("number").columns:
            if c == m:
                continue
            a, b = df.loc[flag, c].dropna(), df.loc[~flag, c].dropna()
            p = stats.mannwhitneyu(a, b)[1]
            rows.append({"missing_column": m, "compared_with": c, "test": "Mann-Whitney", "p_value": p})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- group profiles
def floor_pileups_by_season(df):
    """Rows sitting exactly on the minimum value of Rainfall (80) and Yield (0.3), split by Season."""
    rows = {}
    for col, floor in [("Rainfall_mm", 80), ("Yield_Tonnes_Ha", 0.3)]:
        at_floor = df[df[col] == floor]
        rows[f"{col} == {floor}"] = at_floor.Season.value_counts().reindex(["Kharif", "Rabi", "Zaid"]).fillna(0).astype(int)
    out = pd.DataFrame(rows).T
    out["total"] = out.sum(axis=1)
    return out


def group_profiles(df):
    """Plausibility tables: per-crop yield/price/cost-per-ha, water use per ha by irrigation, loss share."""
    d = df.assign(Cost_per_ha=df.Total_Cost_INR / df.Farm_Area_Hectares,
                  Water_per_ha=df.Water_Used_m3 / df.Farm_Area_Hectares,
                  Loss_making=(df.Profit_INR < 0) * 100)
    agg = ["count", "mean", "std", "min", "median", "max"]
    return {
        "yield_by_crop": d.groupby("Crop").Yield_Tonnes_Ha.agg(agg),
        "price_by_crop": d.groupby("Crop").Market_Price_INR_Tonne.agg(agg),
        "cost_per_ha_by_crop": d.groupby("Crop").Cost_per_ha.agg(agg),
        "water_per_ha_by_irrigation": d.groupby("Irrigation_Method").Water_per_ha.agg(agg),
        "loss_making_pct_by_crop": d.groupby("Crop").Loss_making.mean().to_frame("pct_farms_with_negative_profit"),
    }


# ---------------------------------------------------------------- run everything
def run_full_audit(df):
    """Run every check and return the tables in a dict (used by notebook 01 and the runner)."""
    counts, row_pct, chi = crop_season_tables(df)
    return {
        "dtype_summary": dtype_summary(df),
        "missing_summary": missing_summary(df),
        "duplicate_summary": duplicate_summary(df).to_frame("count"),
        "category_hygiene": category_hygiene(df),
        "numeric_range_summary": numeric_range_summary(df),
        "iqr_outlier_summary": iqr_outlier_summary(df),
        "formula_checks": formula_checks(df),
        "recoverable_yield_check": recoverable_yield_check(df).to_frame("value"),
        "state_district_counts": state_district_table(df),
        "crop_season_counts": counts,
        "crop_season_row_pct": row_pct,
        "crop_season_chi2": pd.Series(chi).to_frame("value"),
        "missingness_association": missingness_association(df),
        "floor_pileups_by_season": floor_pileups_by_season(df),
        **{f"profile_{k}": v for k, v in group_profiles(df).items()},
    }
