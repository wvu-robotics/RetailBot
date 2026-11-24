"""
Utilities to work with encoder data.
"""

import numpy as np
import pandas as pd


def angle_from_encoder_count(
    encoder_counts: pd.DataFrame, output_col_names: list[str] | None = None, ppr=1539
) -> pd.DataFrame:
    """Given a DataFrame of TimeStamped encoder counts will return the timestamped angular positions in radians.

    Will take the first count as the zero count and start from there.

    :param encoder_counts: DataFrame with time-indexed encoder columns.
    :param ppr: Pulses per revolution (default: 1539)
    :return: DataFrame with index as timestamps and angular positions in radians.
    """
    if output_col_names is None:
        output_col_names = [
            "fl_ang_pos",
            "bl_ang_pos",
            "fr_ang_pos",
            "br_ang_pos",
        ]

    # Counts per rev = Pulse per rev * 4.
    cpr = ppr * 4

    # Find the starting counts for all four encoders.
    start_counts = encoder_counts.iloc[0, :]

    # Offset encoder count by the starting count and calc angle from that.
    angle_rads = ((encoder_counts - start_counts) / cpr) * (2 * np.pi)
    angle_rads.columns = output_col_names
    angle_rads.index = encoder_counts.index

    # ---- 2π-unwrap each wheel independently
    angle_rads[:] = np.unwrap(angle_rads.to_numpy(), axis=0)
    return angle_rads

    # 1. look for count jumps
    dc = encoder_counts.diff().abs()

    # jumps larger than 1/2 revolution in one sample
    thresh = (ppr * 4) // 2
    suspect = dc.gt(thresh)
    print("suspect rows:", suspect.any(axis=1).sum())

    # 2. look for rollover ( > 0.9 × 2**32 change )
    rollover = dc.gt(0.9 * 2**32)
    print("rollover rows:", rollover.any(axis=1).sum())

    # 3. plot the offending intervals
    idx = suspect.any(axis=1) | rollover.any(axis=1)
    encoder_counts[idx.to_numpy()].plot(style=".")

    return angle_rads


def angvel_from_angle(
    angles: pd.DataFrame, output_col_names: list[str] | None = None
) -> pd.DataFrame:
    """
    Given a DataFrame of time‐indexed angles (radians), compute the angular velocity (rad/s).

    :param angles: DataFrame with timestamps as index and angle columns.
    :param output_col_names: Optional list of names for the output angular‐velocity columns.
                             Defaults to ['fl_ang_vel','bl_ang_vel','fr_ang_vel','br_ang_vel'].
    :return: DataFrame of the same shape with angular velocities in rad/s.
    """
    if output_col_names is None:
        output_col_names = ["fl_ang_vel", "bl_ang_vel", "fr_ang_vel", "br_ang_vel"]

    # Validate names match number of columns
    n_cols = angles.shape[1]
    if len(output_col_names) != n_cols:
        raise ValueError(f"Expected {n_cols} output names, got {len(output_col_names)}")

    # Compute time differences in seconds
    if isinstance(angles.index, pd.DatetimeIndex):
        dt = angles.index.to_series().diff().dt.total_seconds()
    else:
        dt = pd.Series(angles.index.to_series().diff(), index=angles.index).astype(float)

    # Compute angular velocity via forward difference; first row becomes NaN
    dtheta = angles.diff()
    angvel = dtheta.div(dt, axis=0)

    # Rename columns, preserve index
    angvel.columns = output_col_names
    angvel.index = angles.index

    return angvel
