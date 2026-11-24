import numpy as np
import pandas as pd


def remove_outlier_and_interp(df: pd.DataFrame, window, z_thresh) -> pd.DataFrame:
    outlier_removed, stats = remove_outliers(df=df, window=window, z_thresh=z_thresh)

    interpolated = interpolate_data(df=outlier_removed)
    print(stats)

    return interpolated


def remove_spike_diff(df, max_dx_dt):
    # remove spikes based on derivative
    dt = df.index.to_numpy()
    diffs = df.diff().divide(np.diff(dt, prepend=dt[0])[:, None])
    mask = diffs.abs() > max_dx_dt
    df2 = df.mask(mask.any(axis=1))
    return interpolate_data(df2)


# TODO Fix. AI generated slop.
def remove_outliers(
    df: pd.DataFrame,
    window: int = 5,
    z_thresh: float = 3.0,
    output_col_names: list[str] | None = None,
) -> tuple[pd.DataFrame, dict[str, pd.Series]]:
    """
    Remove point outliers from each column of a timestamped DataFrame by
    masking values whose rolling-window deviation from the local median
    exceeds z_thresh × MAD.

    :param df: DataFrame of signals (e.g. counts, angles, velocities).
               Must be time–indexed or uniformly sampled.
    :param window: size of the moving window (odd integer ≥ 3).
    :param z_thresh: threshold on (|x−median|/MAD) beyond which values are set to NaN.
    :param output_col_names: if provided, renames the columns of the returned DataFrame.
    :return: DataFrame of same shape where outliers are replaced by NaN.
    """
    # How many NaNs before starting?
    orig_nans = df.isna().sum()

    if window < 3 or window % 2 == 0:
        raise ValueError("window must be an odd integer ≥ 3")

    # rolling median
    local_med = df.rolling(window=window, center=True, min_periods=1).median()

    # rolling MAD: median of absolute deviations from the local median
    def mad(arr: np.ndarray) -> float:
        return float(np.median(np.abs(arr - np.median(arr))))

    local_mad = df.rolling(window=window, center=True, min_periods=1).apply(mad, raw=True)

    # signed deviation from median
    dev = (df - local_med).abs()

    # scaled deviation
    scaled = dev.div(local_mad.replace(0, np.nan))

    # 4) mask logic that preserves flat regions
    mask = ((local_mad == 0) & (dev == 0)) | (dev <= z_thresh * local_mad)

    # 5) apply mask
    clean = df.where(mask)

    # keep only those within threshold
    # clean = df.where(scaled <= z_thresh)

    new_nans = clean.isna().sum()
    removed = new_nans - orig_nans

    # optionally rename
    if output_col_names is not None:
        if len(output_col_names) != clean.shape[1]:
            raise ValueError(f"Expected {clean.shape[1]} names, got {len(output_col_names)}")
        clean = clean.copy()
        clean.columns = output_col_names

    stats = {"orig_nans": orig_nans, "new_nans": new_nans, "removed": removed}

    return clean, stats


def interpolate_data(
    df: pd.DataFrame,
    method: str = "linear",
    limit: int = 5,
    time_index: bool = False,
) -> pd.DataFrame:
    """
    Fill NaNs in each column of a timestamped DataFrame by interpolation,
    but only up to `limit` consecutive points.

    :param df: DataFrame with time index (can be DatetimeIndex or numeric).
    :param method: 'linear' (default) or 'time' if using a DatetimeIndex.
    :param limit: maximum number of consecutive NaNs to fill.
    :param time_index: if True, use method='time' (requires DatetimeIndex).
    :return: new DataFrame with NaNs replaced where valid.
    """
    # copy so we don’t mutate the original
    out = df.copy()
    interp_method = "time" if time_index else method

    filled = out.interpolate(
        method=interp_method,
        # limit=limit,
        limit_direction="both",
        # limit_area="inside",  TODO just drop them.
    )
    return filled
