"""Phase 1 diagnostic figures. Each function returns a matplotlib figure (does not save)."""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def fig_yield_by_crop(df):
    """Yield by crop (log scale) - shows why 'overall' Yield outliers are just Sugarcane."""
    order = df.groupby("Crop").Yield_Tonnes_Ha.median().sort_values().index
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.boxplot(data=df, x="Crop", y="Yield_Tonnes_Ha", order=order, ax=ax)
    ax.set_yscale("log")
    ax.set_ylabel("Yield (tonnes/ha, log scale)")
    ax.set_title("Yield by crop: crops differ hugely in scale")
    return fig


def fig_floor_pileups(df):
    """Histograms of Rainfall and Yield: spikes at the minimum value."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    axes[0].hist(df.Rainfall_mm.dropna(), bins=50)
    axes[0].set_title(f"Rainfall_mm  ({(df.Rainfall_mm == 80).sum()} rows exactly 80)")
    axes[0].set_xlabel("mm")
    y = df.loc[df.Crop != "Sugarcane", "Yield_Tonnes_Ha"].dropna()
    axes[1].hist(y, bins=50)
    axes[1].set_title(f"Yield, non-Sugarcane  ({(y == 0.3).sum()} rows exactly 0.3)")
    axes[1].set_xlabel("tonnes/ha")
    fig.tight_layout()
    return fig


def fig_crop_season_heatmap(df):
    """Row-% of each crop falling in each season (rows sum to 100)."""
    import pandas as pd
    pct = pd.crosstab(df.Crop, df.Season, normalize="index") * 100
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    sns.heatmap(pct, annot=True, fmt=".1f", cmap="Blues", vmin=0, vmax=60, ax=ax, cbar_kws={"label": "% of crop's farms"})
    ax.set_title("Season mix within each crop (%)")
    return fig
