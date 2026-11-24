from numpy.typing import NDArray
from scipy.signal import savgol_filter
import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation as R

from scipy.signal import savgol_filter


def savgol_derivative(
    df: pd.DataFrame, window_size=21, poly_order=3, derivative_col_names=None
) -> pd.DataFrame:
    """
    Compute the numerical derivative using Savitzky-Golay filtering on a DataFrame.

    Parameters:
        df (pd.DataFrame): DataFrame with timestamps as the index and data columns.
        window_size (int): Filter window size (must be odd).
        poly_order (int): Polynomial order (should be < window_size).
        derivative_col_names (list, optional): List of column names for the derivative DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing the computed derivatives with the specified column names.
    """

    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError(
            "DataFrame index must be a DatetimeIndex for time-based differentiation."
        )

    # Extract time in seconds from the index
    time = df.index.astype(np.int64) / 1e9  # Convert nanoseconds to seconds
    dt = np.mean(np.diff(time))  # Use average timestep to reduce noise

    # Compute derivatives using Savitzky-Golay filter
    derivatives = savgol_filter(
        df.values,
        window_length=window_size,
        polyorder=poly_order,
        deriv=1,
        delta=dt,
        axis=0,
    )

    # Create new DataFrame with derivatives
    derivative_df = pd.DataFrame(derivatives, index=df.index)

    # Assign column names if provided
    if derivative_col_names:
        if len(derivative_col_names) != df.shape[1]:
            raise ValueError(
                "Number of derivative column names must match number of data columns."
            )
        derivative_df.columns = derivative_col_names
    else:
        derivative_df.columns = [
            f"{col}_derivative" for col in df.columns
        ]  # Default naming

    return derivative_df

    # def quaternion_derivative_savgol(
    #     quats: NDArray, time: NDArray, window_size=21, poly_order=3
    # ) -> NDArray:
    #     """
    #     Compute the angular velocity from a sequence of quaternions using Savitzky-Golay filtering.

    #     Parameters:
    #         quats (NDArray): (4, N) array of quaternions (qx, qy, qz, qw) at each time step.
    #         time (NDArray): (N,) array of time values corresponding to each quaternion.
    #         window_size (int): The window length for Savitzky-Golay filtering (must be odd).
    #         poly_order (int): Polynomial order for Savitzky-Golay filtering.

    #     Returns:
    #         NDArray: (3, N) array of angular velocities (wx, wy, wz) in rad/s.
    #         NDArray: (7, N) array of angular velocities (qx,qy,qz,qw, wx, wy, wz) in rad/s.
    #     """
    #     quats = quats.T  # Convert from (4, N) to (N, 4) for scipy.
    #     print(quats.shape)
    #     rotations = R.from_quat(quats)

    #     # Convert quaternion differences to rotation vectors
    #     rotvecs = np.zeros((len(time), 3))  # (N, 3)
    #     rotvecs[1:] = (rotations[:-1].inv() * rotations[1:]).as_rotvec()

    #     # TODO make this not a single scalar constant?
    #     dt = np.mean(np.diff(time), axis=0)

    #     # TODO Find optimal way to tune polyorder and window size params to avoid over smoothing/fitting.
    #     ang_vels = savgol_filter(
    #         rotvecs.T,
    #         window_length=window_size,
    #         polyorder=poly_order,
    #         deriv=1,
    #         delta=dt,
    #         axis=1,
    #     )

    #     # Turn euler back to quat?
    #     quat_vels = R.from_euler("xyz", ang_vels.T).as_quat()
    #     print("Qual vels", quat_vels.shape)

    #     ang_vels = np.vstack([ang_vels, quat_vels.T])
    #     print("Final angles shape", ang_vels.shape)

    #     return ang_vels  # (7, N)













# def savgol_derivative(data: NDArray, time: NDArray, window_size=21, poly_order=3):
#     """
#     Compute the numerical derivative using Savitzky-Golay filtering.

#     Parameters:
#         data (NDArray): (D, N) position or quaternion data.
#         time (NDArray): (N,) time vector.
#         window_size (int): Filter window size (must be odd).
#         poly_order (int): Polynomial order (should be < window_size).

#     Returns:
#         NDArray: (D, N) filtered derivative (velocity or angular velocity).
#     """
#     # TODO See how much using a single mean dt value affects accuracy.
#     # TODO Would it be better to interp to an evenly spaced dt grid?
#     dt = np.mean(
#         np.diff(time), axis=0
#     )  # Average timestep to avoid noise from small dt variations

#     return savgol_filter(
#         data, window_length=window_size, polyorder=poly_order, deriv=1, delta=dt, axis=1
#     )


def quaternion_derivative_savgol(
    quats: NDArray, time: NDArray, window_size=21, poly_order=3
) -> NDArray:
    """
    Compute the angular velocity from a sequence of quaternions using Savitzky-Golay filtering.

    Parameters:
        quats (NDArray): (4, N) array of quaternions (qx, qy, qz, qw) at each time step.
        time (NDArray): (N,) array of time values corresponding to each quaternion.
        window_size (int): The window length for Savitzky-Golay filtering (must be odd).
        poly_order (int): Polynomial order for Savitzky-Golay filtering.

    Returns:
        NDArray: (3, N) array of angular velocities (wx, wy, wz) in rad/s.
        NDArray: (7, N) array of angular velocities (qx,qy,qz,qw, wx, wy, wz) in rad/s.
    """
    quats = quats.T  # Convert from (4, N) to (N, 4) for scipy.
    print(quats.shape)
    rotations = R.from_quat(quats)

    # Convert quaternion differences to rotation vectors
    rotvecs = np.zeros((len(time), 3))  # (N, 3)
    rotvecs[1:] = (rotations[:-1].inv() * rotations[1:]).as_rotvec()

    # TODO make this not a single scalar constant?
    dt = np.mean(np.diff(time), axis=0)

    # TODO Find optimal way to tune polyorder and window size params to avoid over smoothing/fitting.
    ang_vels = savgol_filter(
        rotvecs.T,
        window_length=window_size,
        polyorder=poly_order,
        deriv=1,
        delta=dt,
        axis=1,
    )

    # Turn euler back to quat?
    quat_vels = R.from_euler("xyz", ang_vels.T).as_quat()
    print("Qual vels", quat_vels.shape)

    ang_vels = np.vstack([ang_vels, quat_vels.T])
    print("Final angles shape", ang_vels.shape)

    return ang_vels  # (7, N)
