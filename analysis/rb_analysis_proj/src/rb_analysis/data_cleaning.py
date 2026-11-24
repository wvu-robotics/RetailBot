from ast import Tuple

import numpy as np
import pandas as pd
from pandas import DataFrame, DatetimeIndex, Timestamp


def get_trial_epoch(dfs: dict[str, DataFrame]) -> tuple[str, Timestamp]:
    """
    Return the topic name and earliest timestamp among all DataFrames
    with a DatetimeIndex, skipping the '/tf_static' topic.
    """
    min_key: str | None = None
    min_ts: Timestamp | None = None

    for key, df in dfs.items():
        # Always skip tf_static
        if key == "/tf_static":
            continue
        # Only consider datetime indices
        if not isinstance(df.index, DatetimeIndex):
            continue
        # Get the earliest timestamp in this DataFrame
        ts = df.index.min()
        # Update global minimum
        if min_ts is None or ts < min_ts:
            min_ts = ts
            min_key = key

    if min_key is None or min_ts is None:
        raise ValueError(
            "No valid datetime indices found in provided DataFrames (excluding /tf_static)"
        )
    return min_key, min_ts


def reset_trial_epoch(dfs: list[pd.DataFrame], start: pd.Timestamp) -> None:
    """Shift each DataFrame’s index to seconds since `start`."""
    for df in dfs:
        if not isinstance(df.index, pd.DatetimeIndex):
            continue

        secs = (df.index - start).total_seconds()

        # one-liner that works on every pandas version
        df.index = pd.Index(secs, dtype="float64", name="seconds_since_start")

        # housekeeping ------------------------------------------------------
        if not df.index.is_monotonic_increasing:
            df.sort_index(inplace=True)
        df.drop_duplicates(inplace=True)
