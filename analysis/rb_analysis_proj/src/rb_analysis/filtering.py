"""
Functions to remove noise from signals stored in dataframes.
"""

import numpy as np
import pandas as pd
from pandas import DataFrame
from scipy.interpolate import interp1d
from scipy.linalg import logm
from scipy.signal import savgol_filter
from scipy.spatial.transform import Rotation, Slerp

# import scipy.spatial.transform.Rotation as R
from scipy.spatial.transform import Rotation as R


def low_pass_filter(df: pd.DataFrame, window_size=5, poly_order=3) -> pd.DataFrame:
    if window_size % 2 == 0:
        window_size += 1
    window_size = max(window_size, poly_order + 2)

    print(f"=== Filtering with window={window_size}, poly_order={poly_order} ===")

    out = pd.DataFrame(index=df.index)

    for col in df.columns:
        y = df[col]
        print(f"\n--- Column: {col} ---")
        print(f"Input dtype: {y.dtype}, NaNs: {y.isna().sum()}, Total: {len(y)}")

        if y.isna().all():
            print("→ All values are NaN. Skipping.")
            out[col] = y
            continue

        valid_mask = y.notna()
        y_valid = y[valid_mask]

        if len(y_valid) < window_size:
            print(f"→ Not enough valid points ({len(y_valid)}) for filtering. Skipping.")
            out[col] = y
            continue

        # Apply filter to the valid portion
        try:
            y_filt = savgol_filter(
                y_valid, window_length=window_size, polyorder=poly_order, mode="interp"
            )
            print("→ Successfully applied Savitzky-Golay filter.")
        except Exception as e:
            print(f"→ ERROR applying filter: {e}")
            out[col] = y
            continue

        # Rebuild with original index
        y_filt_series = pd.Series(y_filt, index=y_valid.index)
        result_series = pd.Series(index=df.index, dtype=np.float64)
        result_series[y_valid.index] = y_filt_series
        out[col] = result_series

        # Compare to scipy result directly
        if col == "vx":
            vx_direct = savgol_filter(
                y_valid, window_length=window_size, polyorder=poly_order, mode="interp"
            )
            diff = np.abs(vx_direct - y_filt)
            print(f"vx filter diff (max): {np.max(diff):.3e}, mean: {np.mean(diff):.3e}")

    return out


def diff_pose(pose_df: pd.DataFrame) -> pd.DataFrame:
    """
    Numerically differentiate a Pose/Transform DataFrame <x,y,z,qx,qy,qz,qw>
    and return a twist DataFrame <vx,vy,vz,roll_rate,pitch_rate,yaw_rate>
    without any smoothing.
    """
    # Time array and intervals
    t = pose_df.index.to_numpy()
    dt = np.diff(t)  # shape (N-1,)

    # Linear velocity by finite difference
    pos = pose_df[["x", "y", "z"]].to_numpy()  # shape (N,3)
    vel = np.diff(pos, axis=0) / dt[:, None]  # shape (N-1,3)
    vel_full = np.vstack([[np.nan, np.nan, np.nan], vel])  # pad to (N,3)

    # Euler-angle rates by finite difference on euler angles
    quats = pose_df[["qx", "qy", "qz", "qw"]].to_numpy()
    eulers = R.from_quat(quats).as_euler("xyz", degrees=False)  # shape (N,3)
    ang_rates = np.diff(eulers, axis=0) / dt[:, None]  # shape (N-1,3)
    ang_full = np.vstack([[np.nan, np.nan, np.nan], ang_rates])  # pad to (N,3)

    # Combine into twist DataFrame
    twist = pd.DataFrame(
        np.hstack([vel_full, ang_full]),
        index=pose_df.index,
        columns=["vx", "vy", "vz", "wx", "wy", "wz"],
    )
    return twist


import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline
from scipy.linalg import expm, logm
from scipy.signal import savgol_filter
from scipy.spatial.transform import Rotation as R


def smooth_pose_spline(
    pose_df: pd.DataFrame,
    *,
    spline_s: float = 0.01,
    correct_quat_sign: bool = True,
) -> pd.DataFrame:
    """
    Smooth pose (position + quaternion) using spline interpolation.
    Quaternion smoothing done via rotation matrix logarithmic interpolation (logm/expm).
    """
    t = pose_df.index.to_numpy()
    smoothed = {}

    # ---- Smooth linear position ----
    for dim in ["x", "y", "z"]:
        y = pose_df[dim].to_numpy()
        spline = UnivariateSpline(t, y, s=spline_s)
        smoothed[dim] = spline(t)

    # ---- Smooth rotation using logm / expm ----
    q_arr = pose_df[["qx", "qy", "qz", "qw"]].to_numpy()
    if correct_quat_sign:
        dots = np.sum(q_arr[1:] * q_arr[:-1], axis=1)
        flips = np.where(dots < 0)[0] + 1
        q_arr[flips] *= -1

    # Convert to rotation matrices
    R_list = R.from_quat(q_arr).as_matrix()

    # Log map to get angular velocity-like quantities
    logm_flat = np.stack([logm(Ri).flatten() for Ri in R_list])
    logm_smooth = np.empty_like(logm_flat)

    # Smooth each matrix component in log-space
    for i in range(logm_flat.shape[1]):
        spline = UnivariateSpline(t, logm_flat[:, i], s=spline_s)
        logm_smooth[:, i] = spline(t)

    # Exponentiate back to rotation matrices
    R_smooth = [expm(logm_smooth[i].reshape(3, 3)) for i in range(len(t))]
    q_smooth = R.from_matrix(R_smooth).as_quat()
    q_smooth /= np.linalg.norm(q_smooth, axis=1, keepdims=True)

    for i, name in enumerate(["qx", "qy", "qz", "qw"]):
        smoothed[name] = q_smooth[:, i]

    return pd.DataFrame(smoothed, index=pose_df.index)


def diff_pose_savgol(
    pose_df: pd.DataFrame,
    *,
    sg_window: int = 33,
    sg_order: int = 3,
    use_sg_deriv: bool | str = True,  # now accepts "spline"
    correct_quat_sign: bool = True,
    spline_s: float = 0.01,
) -> pd.DataFrame:
    """
    Return body-frame twist <vx, vy, vz, wx, wy, wz> from a pose DataFrame
    <x,y,z,qx,qy,qz,qw> that is indexed by time (seconds).
    """
    import numpy as np
    import pandas as pd
    from scipy.interpolate import UnivariateSpline
    from scipy.spatial.transform import Rotation as R

    # ---- timing --------------------------------------------------------
    t = pose_df.index.to_numpy()
    dt = np.median(np.diff(t))
    if sg_window and sg_window % 2 == 0:
        sg_window += 1

    # ---- position → linear velocity ------------------------------------
    pos = pose_df[["x", "y", "z"]].to_numpy()
    if use_sg_deriv == "spline":
        vel = np.empty_like(pos)
        for i in range(3):
            spline = UnivariateSpline(t, pos[:, i], s=spline_s)
            vel[:, i] = spline.derivative()(t)
    elif sg_window:
        if use_sg_deriv:
            vel = savgol_filter(pos, sg_window, sg_order, deriv=1, delta=dt, axis=0, mode="interp")
        else:
            pos = savgol_filter(pos, sg_window, sg_order, axis=0, mode="interp")
            vel = np.diff(pos, axis=0) / np.diff(t)[:, None]
            vel = np.vstack([np.nan * np.ones(3), vel])
    else:
        vel = np.diff(pos, axis=0) / np.diff(t)[:, None]
        vel = np.vstack([np.nan * np.ones(3), vel])

    # ---- quaternion → angular velocity using dR Rᵀ ---------------------
    q_arr = pose_df[["qx", "qy", "qz", "qw"]].to_numpy()

    if correct_quat_sign:
        flips = np.sum(q_arr[1:] * q_arr[:-1], axis=1) < 0
        mask = flips.nonzero()[0] + 1
        q_arr[mask, :] *= -1

    # Normalize if filtered
    if sg_window:
        q_arr = savgol_filter(q_arr, sg_window, sg_order, axis=0, mode="interp")
        q_arr /= np.linalg.norm(q_arr, axis=1, keepdims=True)

    Rs = R.from_quat(q_arr).as_matrix()  # shape (N,3,3)

    dRdt = np.empty_like(Rs)
    for i in range(3):
        for j in range(3):
            spline = UnivariateSpline(t, Rs[:, i, j], s=spline_s)
            dRdt[:, i, j] = spline.derivative()(t)

    omega = np.empty((len(t), 3))
    for k in range(len(t)):
        Rt = Rs[k]
        dRt = dRdt[k]
        skew = dRt @ Rt.T
        omega[k] = [
            0.5 * (skew[2, 1] - skew[1, 2]),
            0.5 * (skew[0, 2] - skew[2, 0]),
            0.5 * (skew[1, 0] - skew[0, 1]),
        ]

    # ---- assemble ------------------------------------------------------
    twist = pd.DataFrame(
        np.hstack([vel, omega]),
        index=pose_df.index,
        columns=["vx", "vy", "vz", "wx", "wy", "wz"],
    )
    return twist


def print_timestamp_jitter(df_or_index):
    """
    Compute and print statistics on timestamp jitter and sample rate.

    Parameters:
    -----------
    df_or_index : pd.DataFrame or pd.Index
        If a DataFrame is passed, its index will be used.
        If an Index is passed, it must be numeric (seconds) or datetime64.
    """
    # Extract index
    idx = df_or_index.index if isinstance(df_or_index, pd.DataFrame) else df_or_index

    # Convert index to seconds since start
    if np.issubdtype(idx.dtype, np.datetime64):
        t = idx.astype("int64") / 1e9
    elif np.issubdtype(idx.dtype, np.floating) or np.issubdtype(idx.dtype, np.integer):
        t = idx.to_numpy().astype(float)
    else:
        raise ValueError("Index must be numeric (seconds) or datetime64")

    # Compute deltas and jitter
    dt = np.diff(t)
    mean_dt = dt.mean()
    median_dt = np.median(dt)
    jitter = dt - mean_dt

    # Compute sample rates
    rate = 1.0 / dt
    mean_rate = rate.mean()
    std_rate = rate.std()
    max_rate = rate.max()
    min_rate = rate.min()
    pct5_rate = np.percentile(rate, 5)
    pct95_rate = np.percentile(rate, 95)

    # Compute effective and median rates
    duration = t[-1] - t[0]
    n_intervals = len(dt)
    effective_rate = n_intervals / duration
    median_rate = 1.0 / median_dt

    # Summary statistics
    print(f"Samples: {n_intervals}")
    print(f"Total duration: {duration:.2f} s")
    print(
        f"Effective Rate: {effective_rate:.2f} Hz  ({n_intervals} samples over {duration:.2f} s)"
    )
    print(
        f"Mean Δt: {mean_dt:.6f} s  (Median Δt: {median_dt:.6f} s, Std jitter: {jitter.std():.6f} s)"
    )
    print(
        f"Mean Rate: {mean_rate:.2f} Hz  (Median Rate: {median_rate:.2f} Hz, Std: {std_rate:.2f} Hz)"
    )
    print(f"Rate range: {min_rate:.2f} to {max_rate:.2f} Hz")
    print(f"5th pct Rate: {pct5_rate:.2f} Hz, 95th pct Rate: {pct95_rate:.2f} Hz")


def interpolate_pose_uniform(
    pose_df: pd.DataFrame, dt: float = None, kind: str = "linear"
) -> pd.DataFrame:
    """
    Resample a pose DataFrame to a uniform time grid.

    Parameters:
    -----------
    pose_df : pd.DataFrame
        Index must be a Float64Index of timestamps in seconds.
        Columns: ['x','y','z','qx','qy','qz','qw'].
    dt : float, optional
        Desired time step in seconds. If None, uses median Δt of the original data.
    kind : {'linear', 'cubic', ...}, optional
        Interpolation method for position. Passed to scipy.interpolate.interp1d.

    Returns:
    --------
    pd.DataFrame
        New DataFrame indexed by uniform timestamps, with same columns.
    """
    # Extract times and positions/quaternions
    t = pose_df.index.to_numpy().astype(float)
    pos = pose_df[["x", "y", "z"]].to_numpy()
    quats = pose_df[["qx", "qy", "qz", "qw"]].to_numpy()

    # Determine dt
    dt_orig = np.diff(t)
    if dt is None:
        dt = np.median(dt_orig)

    # Create uniform time grid
    t0, t_max = t[0], t[-1]
    new_t = np.arange(t0, t_max, dt)
    if new_t[-1] < t_max:
        new_t = np.append(new_t, t_max)

    # Interpolate positions
    pos_interp = interp1d(t, pos, kind=kind, axis=0, fill_value="extrapolate")
    new_pos = pos_interp(new_t)

    # Slerp for quaternions
    rots = Rotation.from_quat(quats)
    slerp = Slerp(t, rots)
    new_rots = slerp(new_t)
    new_quats = new_rots.as_quat()

    # Assemble DataFrame
    new_df = pd.DataFrame(
        np.hstack([new_pos, new_quats]),
        index=new_t,
        columns=["x", "y", "z", "qx", "qy", "qz", "qw"],
    )
    return new_df


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import welch


def plot_psd(
    df: pd.DataFrame,
    cols: list[str] | None = None,
    fs: float = 100.0,  # sample rate [Hz]
    nperseg: int = 4096,
    detrend: str = "constant",
    logscale: bool = True,
    db: bool = True,
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
) -> None:
    """
    Welch PSD for each selected column.

    Parameters
    ----------
    df        : DataFrame indexed by time (seconds).
    cols      : list of column names to analyse; default = all numeric.
    fs        : sampling frequency in Hz.
    nperseg   : Welch segment length (power-of-2 recommended).
    detrend   : detrend mode passed to scipy.signal.welch.
    logscale  : x-axis log10 if True.
    db        : y-axis in dB/Hz if True, else linear power.
    xlim,ylim : axis limits if wanted.
    """
    if cols is None:
        cols = df.select_dtypes(include=["number"]).columns

    plt.figure(figsize=(8, 4))
    for c in cols:
        f, Pxx = welch(
            df[c].to_numpy(),
            fs=fs,
            nperseg=nperseg,
            detrend=detrend,
            axis=0,
        )
        if db:
            Pxx = 10 * np.log10(Pxx + np.finfo(float).eps)
            label = f"{c}  [dB/Hz]"
        else:
            label = f"{c}"

        plt.plot(f, Pxx, label=label)

    if logscale:
        plt.xscale("log")
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("PSD" + (" [dB/Hz]" if db else ""))
    if xlim:
        plt.xlim(*xlim)
    if ylim:
        plt.ylim(*ylim)
    plt.grid(True, which="both", ls=":")
    plt.legend()
    plt.tight_layout()
    plt.show()


def low_pass_regular(df: pd.DataFrame, cutoff: float, order: int = 4) -> pd.DataFrame:
    # get sampling rate
    t = df.index.to_numpy(dtype=float)
    dt = np.median(np.diff(t))
    fs = 1.0 / dt
    print(f"{fs=}")
    nyq = fs / 2.0
    # design Butterworth
    b, a = butter(order, cutoff / nyq, btype="low")
    # apply zero-phase filter
    filtered = filtfilt(b, a, df.to_numpy(), axis=0)
    return pd.DataFrame(filtered, index=df.index, columns=df.columns)


from scipy.interpolate import UnivariateSpline
from scipy.signal import butter, filtfilt
from scipy.spatial.transform import Rotation as R


def spline_smooth(df: pd.DataFrame, s: float = 1.0) -> pd.DataFrame:
    """
    Smooth each column of the DataFrame using UnivariateSpline.
    `s` is the smoothing factor; larger means more smoothing.
    """
    t = df.index.to_numpy()
    out = pd.DataFrame(index=df.index, columns=df.columns)

    for col in df.columns:
        y = df[col].to_numpy()
        if np.isnan(y).all():
            continue
        mask = ~np.isnan(y)
        spline = UnivariateSpline(t[mask], y[mask], s=s)
        out[col] = spline(t)

    return out


def lowpass_pose(
    pose_df: pd.DataFrame,
    fs: float = 100.0,  # sample rate  [Hz]
    fc: float = 10.0,  # cut-off      [Hz]  ( < 0.5 fs )
    order: int = 4,  # Butterworth order
) -> pd.DataFrame:
    """
    Zero-phase Butterworth low-pass on a Pose DataFrame
    (x,y,z,qx,qy,qz,qw).  Quaternion columns are handled by
    converting to rotation-vector form, filtering each component,
    then mapping back to unit quaternions.

    Returns a pose DataFrame with the same index and column order.
    """
    if fc >= 0.5 * fs:
        raise ValueError("cut-off must be < Nyquist")

    # ── design filter ────────────────────────────────────────────────
    b, a = butter(order, fc / (0.5 * fs), btype="low")

    # ── linear part ─────────────────────────────────────────────────
    lin_cols = ["x", "y", "z"]
    lin = pose_df[lin_cols].to_numpy()
    lin_lp = filtfilt(b, a, lin, axis=0)

    # ── quaternion part ─────────────────────────────────────────────
    q_cols = ["qx", "qy", "qz", "qw"]
    q_arr = pose_df[q_cols].to_numpy()

    # keep sign continuity to avoid π flips
    dots = np.sum(q_arr[1:] * q_arr[:-1], axis=1)
    flips = dots < 0
    q_arr[1:][flips] *= -1

    rot_vec = R.from_quat(q_arr).as_rotvec()  # (N,3)
    rot_lp = filtfilt(b, a, rot_vec, axis=0)
    q_lp = R.from_rotvec(rot_lp).as_quat()

    # ── assemble ────────────────────────────────────────────────────
    out = pd.DataFrame(
        np.hstack([lin_lp, q_lp]),
        index=pose_df.index,
        columns=lin_cols + q_cols,
    )
    return out


import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


def diff_df_savgol(
    df: pd.DataFrame,
    *,
    sg_window: int = 33,
    sg_order: int = 3,
    use_sg_deriv: bool = True,
    suffix: str = "_dot",
) -> pd.DataFrame:
    """
    Generic Savitzky–Golay derivative for any time-indexed DataFrame
    that contains only *scalar* numeric columns (angles, encoder counts,
    positions, currents, …).  Quaternion handling is *not* included.

    Parameters
    ----------
    df            : DataFrame whose index is strictly monotonic in (float)
                    seconds or a DatetimeIndex.  Non-numeric columns are ignored.
    sg_window     : SG window length (odd).  0 → no filtering.
    sg_order      : SG polynomial order (< sg_window).
    use_sg_deriv  : True  → SG analytic derivative  (quiet, no extra lag)
                    False → SG smooth then central finite difference.
    suffix        : String appended to original column names in the output.

    Returns
    -------
    pd.DataFrame  (same index, numeric columns suffixed with *suffix*)
    """
    # ------------------------------------------------------------------ timing
    t_idx = df.index
    if isinstance(t_idx, pd.DatetimeIndex):
        t = t_idx.view("int64") * 1e-9  # ns → s
    else:
        t = t_idx.to_numpy(dtype=float)
    if not np.all(np.diff(t) > 0):
        raise ValueError("Index must be strictly increasing")

    dt_const = np.median(np.diff(t))  # step for SG deriv
    if sg_window and sg_window % 2 == 0:
        sg_window += 1

    # ------------------------------------------------------------------ data
    num_cols = df.select_dtypes(include="number").columns
    x = df[num_cols].to_numpy(float)

    # ------------------------------------------------------------------ SG smooth / deriv
    if sg_window:
        if use_sg_deriv:
            dx = savgol_filter(
                x, sg_window, sg_order, deriv=1, delta=dt_const, axis=0, mode="interp"
            )
        else:
            x_sg = savgol_filter(x, sg_window, sg_order, axis=0, mode="interp")
            # central diff for interior, forward/backward for edges
            dt = np.diff(t)
            dx_mid = (x_sg[2:] - x_sg[:-2]) / (t[2:] - t[:-2])[:, None]
            dx = np.vstack(
                [
                    (x_sg[1] - x_sg[0]) / dt[0],  # forward
                    dx_mid,
                    (x_sg[-1] - x_sg[-2]) / dt[-1],  # backward
                ]
            )
    else:  # no SG window
        dt = np.diff(t)
        dx_mid = (x[2:] - x[:-2]) / (t[2:] - t[:-2])[:, None]
        dx = np.vstack(
            [
                (x[1] - x[0]) / dt[0],
                dx_mid,
                (x[-1] - x[-2]) / dt[-1],
            ]
        )

    # ------------------------------------------------------------------ assemble
    out_cols = [f"{c}{suffix}" for c in num_cols]
    return pd.DataFrame(dx, index=df.index, columns=out_cols)
