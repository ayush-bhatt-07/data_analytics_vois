"""Small helpers to save figures and tables into /outputs (reused by every notebook)."""
from pathlib import Path
import matplotlib.pyplot as plt
from src.config import FIG_DIR, TABLE_DIR


def save_figure(fig, name, folder=FIG_DIR, overwrite=False):
    """Save a matplotlib figure as PNG. Refuses to overwrite unless overwrite=True."""
    path = Path(folder) / f"{name}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError(f"{path} already exists. Use overwrite=True if you really mean it.")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def save_table(df, name, folder=TABLE_DIR, overwrite=False, index=True):
    """Save a DataFrame as CSV. Refuses to overwrite unless overwrite=True."""
    path = Path(folder) / f"{name}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError(f"{path} already exists. Use overwrite=True if you really mean it.")
    df.to_csv(path, index=index)
    return path
