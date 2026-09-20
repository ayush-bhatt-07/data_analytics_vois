"""Load the raw data and check it matches what we expect."""
import pandas as pd
from src.config import RAW_CSV, EXPECTED_ROWS, EXPECTED_COLS, ALL_EXPECTED_COLS


def load_raw(path=RAW_CSV):
    """Read the raw CSV exactly as it is. No cleaning happens here."""
    return pd.read_csv(path)


def check_shape_and_columns(df):
    """
    Compare a DataFrame with the expected shape/column names.
    Returns a dict of results; it does not change the data.
    """
    return {
        "rows_ok": len(df) == EXPECTED_ROWS,
        "cols_ok": df.shape[1] == EXPECTED_COLS,
        "missing_columns": [c for c in ALL_EXPECTED_COLS if c not in df.columns],
        "unexpected_columns": [c for c in df.columns if c not in ALL_EXPECTED_COLS],
        "order_matches": list(df.columns) == ALL_EXPECTED_COLS,
    }
