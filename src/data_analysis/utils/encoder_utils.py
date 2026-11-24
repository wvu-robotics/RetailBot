import pandas as pd
import numpy as np

# Calculate wheel angles from encoder counts.
# def encoder_to_rad(encoder_data: pd.DataFrame, ppr=1539) -> pd.DataFrame:
#     """ Given a DataFrame of encoder values, return the angular positions in radians.
    
#     :param encoder_data: DataFrame with time-indexed encoder columns **joint.{fr,br,fl,bl}_wheel_joint.encoder_count**
#     :param ppr: Pulses per revolution (default: 1539)
#     :return: DataFrame with index as timestamps and angular positions in radians.
#     """

#     # Counts per rev = Pulse per rev * 4.
#     cpr = ppr * 4 
#     # Extract encoder count columns.
#     wheel_columns = [col for col in encoder_data.columns if "wheel_joint.encoder_count" in col]

#     # Compute wheel angles in radians.
#     angle_rads = (encoder_data[wheel_columns] / cpr) * (2 * np.pi)

#     # Ensure the output keeps the original timestamp index
#     angle_rads.index = encoder_data.index

#     return angle_rads




def encoder_to_rad(encoder_data: pd.DataFrame, ppr=1539) -> pd.DataFrame:
    """Given a DataFrame of encoder values, return the angular positions in radians.

    :param encoder_data: DataFrame with time-indexed encoder columns **joint.{fr,br,fl,bl}_wheel_joint.encoder_count**
    :param ppr: Pulses per revolution (default: 1539)
    :return: DataFrame with index as timestamps and angular positions in radians.
    """

    # Counts per rev = Pulse per rev * 4.
    cpr = ppr * 4
    # Extract encoder count columns.
    wheel_columns = [
        col for col in encoder_data.columns if "wheel_joint.encoder_count" in col
    ]

    # Compute wheel angles in radians.
    angle_rads = (encoder_data[wheel_columns] / cpr) * (2 * np.pi)

    new_column_names = {
        col: col.replace("encoder_count", "angle") for col in wheel_columns
    }
    angle_rads.rename(columns=new_column_names, inplace=True)

    # Ensure the output keeps the original timestamp index
    angle_rads.index = encoder_data.index

    return angle_rads

# TODO Hard limit is hacky and requires checking for every new dataset.
def remove_encoder_outliers(
    encoder_data: pd.DataFrame, threshold=1000, hard_limit=0.5e9
) -> pd.DataFrame:
    """
    Removes outliers from encoder data based on sudden jumps in encoder counts.

    Parameters:
        encoder_data (pd.DataFrame): A DataFrame containing encoder count columns.
        threshold (int): Difference threshold for detecting outliers.

    Returns:
        pd.DataFrame: Filtered DataFrame with outliers removed.
    """

    # Extract encoder count columns.
    wheel_columns = [
        col for col in encoder_data.columns if "wheel_joint.encoder_count" in col
    ]

    if not wheel_columns:
        raise ValueError("No encoder count columns found in DataFrame.")

    # Compute absolute differences between consecutive values.
    diffs = np.abs(encoder_data[wheel_columns].diff())

    # Compute left and right differences (n-1 shape).
    left_diffs = diffs.shift(-1)  # Forward shift (right-side differences)
    right_diffs = diffs.shift(1)  # Backward shift (left-side differences)

    # Identify outliers (jumps exceeding the threshold).
    outlier_mask = (
        (diffs > threshold) | (left_diffs > threshold) | (right_diffs > threshold)
    )

    # Ensure the first and last row remain unchanged.
    outlier_mask.iloc[0] = False
    outlier_mask.iloc[-1] = False

    # Remove absurd magnitude outliers.
    hard_outliers = encoder_data[wheel_columns].abs() > hard_limit
    final_outlier_mask = outlier_mask | hard_outliers

    # Create a mask for rows where any encoder column has an outlier.
    rows_to_remove = final_outlier_mask.any(axis=1)

    num_removed = len(rows_to_remove)
    print(f"# removed encoder samples: {num_removed}")

    # Drop the outlier rows.
    filtered_data = encoder_data[~rows_to_remove].copy()
    # filtered_data = encoder_data[~final_outlier_mask.any(axis=1)].copy()

    return filtered_data