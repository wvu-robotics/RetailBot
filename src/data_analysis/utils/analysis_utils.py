from re import T
from typing import List

import numpy as np
import pandas as pd
import PyKDL
import rclpy
from geometry_msgs.msg import PoseStamped, TransformStamped, TwistStamped
from rclpy.time import Time
from scipy.signal import butter, filtfilt
from scipy.spatial.transform import Rotation
from scipy.spatial.transform import Rotation as R
from tf2_geometry_msgs import do_transform_pose
from tf2_kdl import transform_to_kdl

from utils.deriv_smoothing import quaternion_derivative_savgol, savgol_derivative, savgol_filter

# from tf_transformations import quaternion_matrix
from utils.ros_to_df import ros_message_to_df


# This is actually just broken in the tf2_kdl lib?
# http://docs.ros.org/en/diamondback/api/kdl/html/python/geometric_primitives.html?highlight=twist#PyKDL.Twist
# https://github.com/ros2/geometry2/tree/rolling/tf2_kdl
def do_transform_twist(twist, transform):
    """
    Apply a transform in the form of a geometry_msgs message to a PyKDL Twist.

    :param twist: The PyKDL twist to transform.
    :type twist: PyKDL.Twist
    :param transform: The transform to apply.
    :type transform: geometry_msgs.msg.TransformStamped
    :return: The transformed PyKDL twist.
    :rtype: PyKDL.Twist
    """
    # res: PyKDL.Frame = transform_to_kdl(transform) * twist
    # # res: PyKDL.Frame = twist * transform_to_kdl(transform)
    # # # res.header = transform.header
    # return res
    # Convert TransformStamped to PyKDL.Frame

    kdl_transform = transform_to_kdl(transform)

    # Extract rotation and translation
    kdl_rotation = kdl_transform.M
    kdl_translation = kdl_transform.p  # Position vector (translation)

    # Apply rotation to linear and angular velocity
    rotated_linear = kdl_rotation * twist.vel
    rotated_angular = kdl_rotation * twist.rot

    # Compute additional linear velocity due to rotation about translation
    additional_linear = rotated_angular * kdl_translation  # ω × r term

    # Final linear velocity = Rotated velocity + Translational component
    final_linear = rotated_linear + additional_linear

    # print(f"Before Transform - Linear: {twist.vel}, Angular: {twist.rot}")
    # print(f"Transform Rotation Matrix:\n{kdl_rotation}")
    # print(f"Transform Translation Vector: {kdl_translation}")
    # print(f"After Transform - Linear: {final_linear}, Angular: {rotated_angular}\n")

    return PyKDL.Twist(final_linear, rotated_angular)


def filter_twist_data(df, cutoff_freq, sampling_freq, order=4):
    """
    Applies a low-pass Butterworth filter to smooth the TwistStamped data.

    Args:
        df (pd.DataFrame): DataFrame containing TwistStamped data.
        cutoff_freq (float): Cutoff frequency for filtering (Hz).
        sampling_freq (float): Sampling frequency of the data (Hz).
        order (int, optional): Order of the Butterworth filter. Defaults to 4.

    Returns:
        pd.DataFrame: New DataFrame with filtered twist data.
    """

    def butter_lowpass_filter(data, cutoff, fs, order):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype="low", analog=False)
        return filtfilt(b, a, data, axis=0)

    # Ensure DataFrame has required columns
    twist_cols = [
        "twist.linear.x",
        "twist.linear.y",
        "twist.linear.z",
        "twist.angular.x",
        "twist.angular.y",
        "twist.angular.z",
    ]

    # Create a new DataFrame to store filtered data
    filtered_df = df.copy()

    # Apply filtering to each twist component
    for col in twist_cols:
        if col in df:
            filtered_df[col] = butter_lowpass_filter(
                df[col].values, cutoff_freq, sampling_freq, order
            )

    return filtered_df


def butter_lowpass_filter(data, cutoff, fs, order):
    """
    Applies a Butterworth low-pass filter to the given data.

    Args:
        data (array-like): The input signal.
        cutoff (float): Cutoff frequency of the filter.
        fs (float): Sampling frequency.
        order (int): Order of the filter.

    Returns:
        np.ndarray: Filtered signal.
    """
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype="low", analog=False)
    return filtfilt(b, a, data, axis=0)


def filter_dataframe(
    df: pd.DataFrame, columns_to_filter: list, cutoff: float, fs: float, order: int
) -> pd.DataFrame:
    """
    Applies a low-pass filter to specified columns in a DataFrame while keeping all other columns intact.

    Args:
        df (pd.DataFrame): The input DataFrame.
        columns_to_filter (list of str): List of column names to filter.
        cutoff (float): Cutoff frequency for the low-pass filter.
        fs (float): Sampling frequency.
        order (int): Order of the Butterworth filter.

    Returns:
        pd.DataFrame: DataFrame with specified columns filtered.
    """
    filtered_df = df.copy()
    for col in columns_to_filter:
        if col in filtered_df.columns:
            filtered_df[col] = butter_lowpass_filter(filtered_df[col].values, cutoff, fs, order)
    return filtered_df


def apply_filter(series: pd.Series) -> pd.Series:
    """
    Applies a filtering operation on a Pandas Series.

    Args:
        series (pd.Series): The column data to filter.

    Returns:
        pd.Series: Filtered column data.
    """
    return series.rolling(
        window=5, center=True, min_periods=1
    ).mean()  # Example: Moving average filter


def transform_twist_dataframe(df, transform):
    """Transforms a DataFrame of twists (linear xyz + angular rpy) into another frame using PyKDL.
    :param df: Pandas DataFrame with columns ['vx', 'vy', 'vz', 'wx', 'wy', 'wz'] representing a twist (linear and angular velocity).
    :param transform: Transform from the original frame to the target frame (geometry_msgs.msg.TransformStamped).
    :return: New DataFrame with transformed twists.
    """
    transformed_data = []

    # For each Twist msg, make a new KDL Twist version of it.
    for _, row in df.iterrows():
        # Create PyKDL Twist (linear velocity, angular velocity)
        twist_kdl = PyKDL.Twist(
            PyKDL.Vector(
                row["twist.linear.x"], row["twist.linear.y"], row["twist.linear.z"]
            ),  # Linear velocity
            PyKDL.Vector(
                row["twist.angular.x"], row["twist.angular.y"], row["twist.angular.z"]
            ),  # Angular velocity
        )

        transformed_twist = do_transform_twist(twist_kdl, transform)

        # Store transformed values
        transformed_data.append(
            {
                "twist.linear.x": transformed_twist.vel[0],
                "twist.linear.y": transformed_twist.vel[1],
                "twist.linear.z": transformed_twist.vel[2],
                "twist.angular.x": transformed_twist.rot[0],
                "twist.angular.y": transformed_twist.rot[1],
                "twist.angular.z": transformed_twist.rot[2],
            }
        )

    # Create a new DataFrame with the transformed data
    transformed_df = pd.DataFrame(transformed_data, index=df.index)

    return transformed_df


def transform_pose_dataframe(df: pd.DataFrame, transform: TransformStamped) -> pd.DataFrame:
    """
    Transforms a DataFrame of poses (position + orientation) into another frame using PyKDL.

    :param df: Pandas DataFrame with columns:
               ['pose.position.x', 'pose.position.y', 'pose.position.z',
                'pose.orientation.x', 'pose.orientation.y', 'pose.orientation.z', 'pose.orientation.w']
    :param transform: Transform from the original frame to the target frame (geometry_msgs.msg.TransformStamped).
    :return: New DataFrame with transformed poses.
    """

    transformed_data = []

    # Convert transform to KDL frame
    kdl_transform = transform_to_kdl(transform)

    for _, row in df.iterrows():
        # Convert pose to KDL frame
        pose_kdl = PyKDL.Frame(
            PyKDL.Rotation.Quaternion(
                row["pose.orientation.x"],
                row["pose.orientation.y"],
                row["pose.orientation.z"],
                row["pose.orientation.w"],
            ),
            PyKDL.Vector(row["pose.position.x"], row["pose.position.y"], row["pose.position.z"]),
        )

        # Apply transformation
        transformed_pose_kdl = kdl_transform * pose_kdl

        # Extract transformed position & orientation
        new_position = transformed_pose_kdl.p
        new_orientation = transformed_pose_kdl.M.GetQuaternion()

        transformed_data.append(
            {
                "pose.position.x": new_position[0],
                "pose.position.y": new_position[1],
                "pose.position.z": new_position[2],
                "pose.orientation.x": new_orientation[0],
                "pose.orientation.y": new_orientation[1],
                "pose.orientation.z": new_orientation[2],
                "pose.orientation.w": new_orientation[3],
            }
        )

    # Create a new DataFrame with transformed poses
    transformed_df = pd.DataFrame(transformed_data, index=df.index)

    return transformed_df


def pose_to_transform(pose_row) -> TransformStamped:
    """
    Convert a pose DataFrame row into a TransformStamped object.

    :param pose_row: A row from the pose DataFrame containing position & orientation.
    :return: TransformStamped object to transform from Vicon frame to base_link.
    """
    transform = TransformStamped()
    transform.header.stamp.sec = int(pose_row.name.timestamp())
    transform.header.stamp.nanosec = int((pose_row.name.timestamp() % 1) * 1e9)
    transform.child_frame_id = "base_link"
    transform.header.frame_id = "vicon"

    # Set translation
    transform.transform.translation.x = pose_row["pose.position.x"]
    transform.transform.translation.y = pose_row["pose.position.y"]
    transform.transform.translation.z = pose_row["pose.position.z"]

    # Set rotation (invert the quaternion for vicon -> base_link)
    q = R.from_quat(
        [
            pose_row["pose.orientation.x"],
            pose_row["pose.orientation.y"],
            pose_row["pose.orientation.z"],
            pose_row["pose.orientation.w"],
        ]
    ).inv()

    (
        transform.transform.rotation.x,
        transform.transform.rotation.y,
        transform.transform.rotation.z,
        transform.transform.rotation.w,
    ) = q.as_quat()

    return transform

    # def pose_df_to_transform(pose_stamped: pd.DataFrame, parent_frame: str, child_frame: str) -> TransformStamped:
    #     """
    #     Convert a PoseStamped message into a TransformStamped message.

    #     :param pose_stamped: The PoseStamped message to convert.
    #     :param parent_frame: The name of the parent frame.
    #     :param child_frame: The name of the child frame.
    #     :return: TransformStamped equivalent of the PoseStamped.
    #     """
    #     transform = TransformStamped()
    #     transform.header.stamp = pose_stamped.header.stamp
    #     transform.header.frame_id = parent_frame
    #     transform.child_frame_id = child_frame

    #     # Copy translation
    #     transform.transform.translation.x = pose_stamped.pose.position.x
    #     transform.transform.translation.y = pose_stamped.pose.position.y
    #     transform.transform.translation.z = pose_stamped.pose.position.z

    #     # Copy rotation (quaternion)
    #     transform.transform.rotation.x = pose_stamped.pose.orientation.x
    #     transform.transform.rotation.y = pose_stamped.pose.orientation.y
    #     transform.transform.rotation.z = pose_stamped.pose.orientation.z
    #     transform.transform.rotation.w = pose_stamped.pose.orientation.w

    #     return transform

    # def pose_df_to_transform_df(pose_df: pd.DataFrame, parent_frame: str, child_frame: str) -> pd.DataFrame:
    #     """
    #     Convert a PoseStamped DataFrame into a Transform DataFrame.

    #     Args:
    #         pose_df (pd.DataFrame): DataFrame containing pose data with timestamps.
    #         parent_frame (str): The parent frame name.
    #         child_frame (str): The child frame name.

    #     Returns:
    #         pd.DataFrame: A DataFrame containing the transformation data.
    #     """
    #     transform_df = pose_df.copy()

    #     # Rename columns to represent transformation
    #     transform_df = transform_df.rename(columns={
    #         "pose.position.x": "transform.translation.x",
    #         "pose.position.y": "transform.translation.y",
    #         "pose.position.z": "transform.translation.z",
    #         "pose.orientation.x": "transform.rotation.x",
    #         "pose.orientation.y": "transform.rotation.y",
    #         "pose.orientation.z": "transform.rotation.z",
    #         "pose.orientation.w": "transform.rotation.w"
    #     })

    #     # Add parent and child frame columns
    #     transform_df["parent_frame"] = parent_frame
    #     transform_df["child_frame"] = child_frame

    #     return transform_df


def pose_df_to_transforms(
    pose_df: pd.DataFrame, parent_frame: str, child_frame: str
) -> List[TransformStamped]:
    """
    Convert a DataFrame with the data equivalent to a PoseStamped message into a list of
    tf2_geometry_msgs.TransformStamped objects.

    Args:
        pose_df (pd.DataFrame): DataFrame containing pose data with timestamps.
        parent_frame (str): The parent frame name.
        child_frame (str): The child frame name.

    Returns:
        List[TransformStamped]: A list of TransformStamped objects.
    """
    transforms = []

    for index, row in pose_df.iterrows():
        transform = TransformStamped()

        # Set header
        # transform.header.stamp = Time(seconds=row["header.stamp.sec"], nanoseconds=row["header.stamp.nanosec"]).to_msg()
        sec = int(row["header.stamp.sec"])
        nanosec = int(row["header.stamp.nanosec"])  # Ensure integer conversion
        transform.header.stamp = Time(seconds=sec, nanoseconds=nanosec).to_msg()

        transform.header.frame_id = parent_frame
        transform.child_frame_id = child_frame

        # Set translation
        transform.transform.translation.x = row["pose.position.x"]
        transform.transform.translation.y = row["pose.position.y"]
        transform.transform.translation.z = row["pose.position.z"]

        # Set rotation (quaternion)
        transform.transform.rotation.x = row["pose.orientation.x"]
        transform.transform.rotation.y = row["pose.orientation.y"]
        transform.transform.rotation.z = row["pose.orientation.z"]
        transform.transform.rotation.w = row["pose.orientation.w"]

        transforms.append(transform)

    return transforms


def compute_twist_from_pose(
    vicon_poses: pd.DataFrame, window_size=21, poly_order=3
) -> pd.DataFrame:
    """
    Compute a TwistStamped-equivalent DataFrame from a PoseStamped DataFrame.

    :param vicon_poses: DataFrame containing ['pose.position.x', 'pose.position.y', 'pose.position.z',
                                              'pose.orientation.x', 'pose.orientation.y', 'pose.orientation.z', 'pose.orientation.w']
    :param window_size: Window size for Savitzky-Golay smoothing.
    :param poly_order: Polynomial order for Savitzky-Golay smoothing.
    :return: DataFrame with ['twist.linear.x', 'twist.linear.y', 'twist.linear.z',
                             'twist.angular.x', 'twist.angular.y', 'twist.angular.z']
    """
    # Ensure timestamps are numerical
    time = vicon_poses.index.view(np.int64) / 1e9  # Convert from nanoseconds to seconds

    # Extract linear position
    positions = vicon_poses[
        ["pose.position.x", "pose.position.y", "pose.position.z"]
    ].values.T  # (3, N)

    # Compute linear velocity
    linear_velocity = savgol_derivative(positions, time, window_size, poly_order)

    # Extract quaternion orientation
    quaternions = vicon_poses[
        [
            "pose.orientation.x",
            "pose.orientation.y",
            "pose.orientation.z",
            "pose.orientation.w",
        ]
    ].values.T  # (4, N)


# Convert quaternion to Euler angles (roll, pitch, yaw)
def quaternion_to_euler(x, y, z, w):
    """Convert a quaternion to roll, pitch, yaw (in radians)."""
    rot = Rotation.from_quat([x, y, z, w])
    return rot.as_euler("xyz", degrees=False)  # 'xyz' convention (roll, pitch, yaw)

    # Compute angular velocity
    angular_velocity = quaternion_derivative_savgol(quaternions, time, window_size, poly_order)[
        :3
    ]  # Take only (wx, wy, wz)

    # Create DataFrame for TwistStamped
    twist_df = pd.DataFrame(
        {
            "twist.linear.x": linear_velocity[0],
            "twist.linear.y": linear_velocity[1],
            "twist.linear.z": linear_velocity[2],
            "twist.angular.x": angular_velocity[0],
            "twist.angular.y": angular_velocity[1],
            "twist.angular.z": angular_velocity[2],
        },
        index=vicon_poses.index,
    )

    twist_df.index.name = "timestamp"

    return twist_df


# Convert DataFrame rows into PoseStamped messages
def df_to_pose_stamped(df, frame_id: str):
    poses = []
    for timestamp, row in df.iterrows():
        pose = PoseStamped()
        pose.header.stamp.sec = int(timestamp.timestamp())
        pose.header.stamp.nanosec = int((timestamp.timestamp() % 1) * 1e9)
        pose.header.frame_id = frame_id  # Transformed frame

        pose.pose.position.x = row["pose.position.x"]
        pose.pose.position.y = row["pose.position.y"]
        pose.pose.position.z = row["pose.position.z"]

        pose.pose.orientation.x = row["pose.orientation.x"]
        pose.pose.orientation.y = row["pose.orientation.y"]
        pose.pose.orientation.z = row["pose.orientation.z"]
        pose.pose.orientation.w = row["pose.orientation.w"]

        poses.append(pose)
    return poses


# Convert DataFrame rows into TwistStamped messages
def df_to_twist_stamped(df, frame_id: str):
    twists = []
    for timestamp, row in df.iterrows():
        twist = TwistStamped()
        twist.header.stamp.sec = int(timestamp.timestamp())
        twist.header.stamp.nanosec = int((timestamp.timestamp() % 1) * 1e9)
        twist.header.frame_id = frame_id

        twist.twist.linear.x = row["twist.linear.x"]
        twist.twist.linear.y = row["twist.linear.y"]
        twist.twist.linear.z = row["twist.linear.z"]

        twist.twist.angular.x = row["twist.angular.x"]
        twist.twist.angular.y = row["twist.angular.y"]
        twist.twist.angular.z = row["twist.angular.z"]

        twists.append(twist)
    return twists


def offset_pose_df(df: pd.DataFrame, transform: TransformStamped) -> pd.DataFrame:
    """
    Offsets a DataFrame of poses (position + orientation) by applying an affine transform
    in the local frame of each pose.

    :param df: DataFrame with columns:
               ['pose.position.x', 'pose.position.y', 'pose.position.z',
                'pose.orientation.x', 'pose.orientation.y', 'pose.orientation.z', 'pose.orientation.w']
    :param transform: Affine offset to apply in the local frame of each pose.
    :return: New DataFrame with offset poses.
    """

    transformed_data = []

    # Convert transform to KDL frame
    kdl_transform = transform_to_kdl(transform)

    for _, row in df.iterrows():
        pose_kdl = PyKDL.Frame(
            PyKDL.Rotation.Quaternion(
                row["pose.orientation.x"],
                row["pose.orientation.y"],
                row["pose.orientation.z"],
                row["pose.orientation.w"],
            ),
            PyKDL.Vector(row["pose.position.x"], row["pose.position.y"], row["pose.position.z"]),
        )

        # Apply transform in local frame of pose
        transformed_pose_kdl = pose_kdl * kdl_transform

        # Extract new pose
        new_position = transformed_pose_kdl.p
        new_orientation = transformed_pose_kdl.M.GetQuaternion()

        transformed_data.append(
            {
                "pose.position.x": new_position[0],
                "pose.position.y": new_position[1],
                "pose.position.z": new_position[2],
                "pose.orientation.x": new_orientation[0],
                "pose.orientation.y": new_orientation[1],
                "pose.orientation.z": new_orientation[2],
                "pose.orientation.w": new_orientation[3],
            }
        )

    transformed_df = pd.DataFrame(transformed_data, index=df.index)

    return transformed_df

    # def transform_to_kdl(transform: TransformStamped) -> PyKDL.Frame:
    #     """Convert a ROS2 TransformStamped into a PyKDL Frame."""
    #     # Convert Quaternion to Rotation Matrix
    #     q = transform.transform.rotation
    #     rot_matrix = quaternion_matrix([q.x, q.y, q.z, q.w])[:3, :3]  # Extract rotation part

    #     # Convert Translation
    #     trans = transform.transform.translation
    #     trans_vector = PyKDL.Vector(trans.x, trans.y, trans.z)

    #     # Create PyKDL Frame
    #     kdl_frame = PyKDL.Frame(PyKDL.Rotation(*rot_matrix.flatten()), trans_vector)
    # return kdl_frame


def offset_twist_df(df: pd.DataFrame, transform: TransformStamped) -> pd.DataFrame:
    """
    Offsets a DataFrame of twists (linear xyz + angular rpy) by applying an affine transform
    as a simple offset in the local frame (without complicated frame transformations).

    :param df: DataFrame with columns ['vx', 'vy', 'vz', 'wx', 'wy', 'wz']
    :param transform: Affine offset to apply, interpreted in local frame.
    :return: New DataFrame with offset twists.
    """

    # transformed_data = []
    # kdl_transform = transform_to_kdl(transform)

    # for _, row in df.iterrows():
    #     twist_kdl = PyKDL.Twist(
    #         PyKDL.Vector(row["twist.linear.x"], row["twist.linear.y"], row["twist.linear.z"]),
    #         PyKDL.Vector(row["twist.angular.x"], row["twist.angular.y"], row["twist.angular.z"])
    #     )

    #     # Rotate linear and angular velocities by the transform's rotation
    #     rotated_linear = kdl_transform.M * twist_kdl.vel
    #     rotated_angular = kdl_transform.M * twist_kdl.rot

    #     # No translation effect on angular velocity; linear velocity unaffected by positional offset directly
    #     transformed_data.append({
    #         'twist.linear.x': rotated_linear[0],
    #         'twist.linear.y': rotated_linear[1],
    #         'twist.linear.z': rotated_linear[2],
    #         'twist.angular.x': rotated_angular[0],
    #         'twist.angular.y': rotated_angular[1],
    #         'twist.angular.z': rotated_angular[2],
    #     })
    # return pd.DataFrame(transformed_data, index=df.index)

    transformed_data = []

    for _, row in df.iterrows():
        # Create PyKDL Twist (linear velocity, angular velocity)
        twist_kdl = PyKDL.Twist(
            PyKDL.Vector(
                row["twist.linear.x"], row["twist.linear.y"], row["twist.linear.z"]
            ),  # Linear velocity
            PyKDL.Vector(
                row["twist.angular.x"], row["twist.angular.y"], row["twist.angular.z"]
            ),  # Angular velocity
        )

        # Apply the transformation in the correct order
        transformed_twist = do_transform_twist(twist_kdl, transform)

        # transformed_twist = transform * twist_kdl
        # # Store transformed values
        transformed_data.append(
            {
                "twist.linear.x": transformed_twist.vel[0],
                "twist.linear.y": transformed_twist.vel[1],
                "twist.linear.z": transformed_twist.vel[2],
                "twist.angular.x": transformed_twist.rot[0],
                "twist.angular.y": transformed_twist.rot[1],
                "twist.angular.z": transformed_twist.rot[2],
            }
        )

    # Create a new DataFrame with the transformed data
    transformed_df = pd.DataFrame(transformed_data, index=df.index)

    return transformed_df


def normalize_quaternion(q):
    """Ensure quaternion is normalized and replace zero-norm quaternions with an identity quaternion."""
    norm = np.linalg.norm(q)
    if norm < 1e-6:  # Avoid division by zero
        return np.array([0, 0, 0, 1])  # Identity quaternion
    return q / norm


# def df_offset_twist_df(
#     twist_df: pd.DataFrame, transforms: List[TransformStamped]
# ) -> pd.DataFrame:
#     """
#     Given a DataFrame of TwistStamped data and a list of TransformStamped transform the TwistStamped data correctly
#     using the transform. Will return  DataFrame of the Pose data. Will create a tf buffer and load the transforms so
#     that tf2 will do quat interpolation for us.
#     """

#     return transformed_twist_df


def pose_offset(pose: PoseStamped, transform: TransformStamped) -> PoseStamped:
    """Apply transform directly and explicitly to pose position and orientation, ignoring pose orientation."""

    # Extract original pose position and orientation
    orig_pos = np.array([pose.pose.position.x, pose.pose.position.y, pose.pose.position.z])
    orig_rot = R.from_quat(
        [
            pose.pose.orientation.x,
            pose.pose.orientation.y,
            pose.pose.orientation.z,
            pose.pose.orientation.w,
        ]
    )

    # Extract transform translation and rotation
    trans_vec = np.array(
        [
            transform.transform.translation.x,
            transform.transform.translation.y,
            transform.transform.translation.z,
        ]
    )
    trans_rot = R.from_quat(
        [
            transform.transform.rotation.x,
            transform.transform.rotation.y,
            transform.transform.rotation.z,
            transform.transform.rotation.w,
        ]
    )

    # Explicitly apply transform's rotation to the position (ignoring pose rotation entirely!)
    new_pos = orig_pos + trans_vec
    new_rot = trans_rot * orig_rot

    # Construct explicitly new PoseStamped (same header)
    new_pose = PoseStamped()
    new_pose.header = pose.header
    new_pose.pose.position.x, new_pose.pose.position.y, new_pose.pose.position.z = new_pos
    new_q = new_rot.as_quat()
    new_pose.pose.orientation.x = new_q[0]
    new_pose.pose.orientation.y = new_q[1]
    new_pose.pose.orientation.z = new_q[2]
    new_pose.pose.orientation.w = new_q[3]

    return new_pose


def remove_outliers(data: pd.DataFrame, threshold=1000, hard_limit=0.5e6) -> pd.DataFrame:
    """
    Removes outliers from a numerical DataFrame based on sudden jumps in values.

    Parameters:
        data (pd.DataFrame): DataFrame containing time-series numerical data.
        threshold (float): Difference threshold for detecting outliers.

    Returns:
        pd.DataFrame: Filtered DataFrame with outliers removed.
    """
    # Select only numerical columns
    numeric_cols = data.select_dtypes(include=[np.number]).columns

    if numeric_cols.empty:
        raise ValueError("No numeric columns found in DataFrame.")

    # Compute absolute differences between consecutive values
    diffs = np.abs(data[numeric_cols].diff())

    # Compute forward and backward differences (to detect double-sided jumps)
    left_diffs = diffs.shift(-1)  # Forward shift (right-side differences)
    right_diffs = diffs.shift(1)  # Backward shift (left-side differences)

    # Identify outliers: sudden jumps exceeding the threshold
    outlier_mask = (diffs > threshold) | (left_diffs > threshold) | (right_diffs > threshold)

    # Remove absurd magnitude outliers.
    hard_outliers = data[numeric_cols].abs() > hard_limit

    final_outlier_mask = outlier_mask | hard_outliers

    # Keep the first and last row unchanged
    outlier_mask.iloc[0] = False
    outlier_mask.iloc[-1] = False

    # Create a mask for rows where any encoder column has an outlier.
    rows_to_remove = final_outlier_mask.any(axis=1)

    # Drop rows where any column has an outlier
    num_removed = rows_to_remove.sum()
    num_hard_outliers = hard_outliers.any(axis=1).sum()

    print(
        f"Removed {num_removed} outlier samples, including {num_hard_outliers} hard limit outliers."
    )
    return data[~rows_to_remove].copy()
