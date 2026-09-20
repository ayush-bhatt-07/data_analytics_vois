"""Run the Phase 1 audit and save tables/figures to /outputs. Read-only on the data."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib
matplotlib.use("Agg")
from src.data_loader import load_raw, check_shape_and_columns
from src.audit import run_full_audit
from src import audit_plots
from src.io_utils import save_table, save_figure

df = load_raw()
assert all(v in (True, [] ) for v in check_shape_and_columns(df).values())
results = run_full_audit(df)
for name, tbl in results.items():
    print("saved", save_table(tbl, f"p1_{name}", overwrite=True))
for name, fn in [("yield_by_crop", audit_plots.fig_yield_by_crop),
                 ("rainfall_yield_floor_pileups", audit_plots.fig_floor_pileups),
                 ("crop_season_mix_heatmap", audit_plots.fig_crop_season_heatmap)]:
    print("saved", save_figure(fn(df), f"p1_{name}", overwrite=True))
