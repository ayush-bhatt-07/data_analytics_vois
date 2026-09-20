"""
Central settings: paths, constants and column groups.
Change things HERE once instead of editing every notebook.
"""
from pathlib import Path

# ---- Paths (relative to the project root, so it works on any computer) ----
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_CSV = PROJECT_ROOT / "data" / "raw" / "seasonal_agriculture_performance_dataset.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIG_DIR = OUTPUT_DIR / "figures"
TABLE_DIR = OUTPUT_DIR / "tables"
MODEL_DIR = OUTPUT_DIR / "models"
FINDINGS_MD = PROJECT_ROOT / "findings.md"

# ---- Reproducibility ----
RANDOM_STATE = 42

# ---- Expected dataset shape (from the project brief; verified in Phase 0) ----
EXPECTED_ROWS = 4000
EXPECTED_COLS = 28

# ---- Column groups, following the framework:
#      Season -> Environment -> Resources -> Production -> Economics -> Risk
# These groups are DESCRIPTIVE only (used for organising plots and tables).
# They are NOT a decision about which columns are allowed as ML predictors.
# That decision (leakage check) is made in Phase 7 after we test the formulas.
ID_COLS = ["Farm_ID"]
LOCATION_COLS = ["State", "District"]
CATEGORY_COLS = ["Crop", "Season", "Irrigation_Method"]
FARM_SIZE_COLS = ["Farm_Area_Hectares"]
ENVIRONMENT_COLS = [
    "Rainfall_mm", "Avg_Temperature_C", "Humidity_pct", "Sunlight_Hours_Day",
    "Soil_pH", "Soil_Moisture_pct", "Nitrogen_kg_ha", "Phosphorus_kg_ha", "Potassium_kg_ha",
]
RESOURCE_COLS = [
    "Fertilizer_kg_ha", "Pesticide_Litre_ha", "Seed_Quality_Score",
    "Water_Used_m3",
]
PRODUCTION_COLS = ["Yield_Tonnes_Ha", "Production_Tonnes", "Water_Efficiency_t_per_1000m3"]
ECONOMICS_COLS = ["Market_Price_INR_Tonne", "Total_Cost_INR", "Revenue_INR", "Profit_INR"]
RISK_COLS = ["Disease_Pest_Risk_pct"]

# Exact column order as given in the project spec (used only to verify the file).
ALL_EXPECTED_COLS = [
    "Farm_ID", "State", "District", "Crop", "Season", "Farm_Area_Hectares",
    "Rainfall_mm", "Avg_Temperature_C", "Humidity_pct", "Sunlight_Hours_Day",
    "Soil_pH", "Soil_Moisture_pct", "Nitrogen_kg_ha", "Phosphorus_kg_ha", "Potassium_kg_ha",
    "Irrigation_Method", "Fertilizer_kg_ha", "Pesticide_Litre_ha", "Seed_Quality_Score",
    "Yield_Tonnes_Ha", "Production_Tonnes", "Market_Price_INR_Tonne", "Total_Cost_INR",
    "Revenue_INR", "Profit_INR", "Water_Used_m3", "Water_Efficiency_t_per_1000m3",
    "Disease_Pest_Risk_pct",
]

# Primary ML target (Phase 7 will confirm this after the leakage check)
PRIMARY_TARGET = "Yield_Tonnes_Ha"
