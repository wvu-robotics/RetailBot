"""Functions to plot specific data structures in the notebooks."""

from pandas import DataFrame
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
import pandas as pd

import pandas as pd
import matplotlib.pyplot as plt
from tf2_ros import TransformStamped
from geometry_msgs.msg import PoseStamped
from typing import Any, Dict, List, Optional

def plot_raw_data(raw_data: list[DataFrame]) -> None :
    """ Make a small subplots figure so we can peek at the raw data.

    The provided data will be all DataFrame objects with timestamp indexing.

    We can expect a dict of the following form:
        name=/tf_static                    type=DataFrame   Count=    7
        name=/tf                           type=DataFrame   Count= 3418
        name=/vrpn_mocap/rb1/twist         type=DataFrame   Count= 4122
        name=/dynamic_joint_states         type=DataFrame   Count= 1122
        name=/joint_states                 type=DataFrame   Count= 1122
        name=/joy                          type=DataFrame   Count=  596
        name=/rb_slip_controller/odom      type=DataFrame   Count= 1118
        name=/pico_imu                     type=DataFrame   Count= 5255
        name=/diagnostics                  type=DataFrame   Count=   42
        name=/rosout                       type=DataFrame   Count=   10
        name=/left_motor_currents          type=DataFrame   Count= 6698
        name=/right_motor_currents         type=DataFrame   Count= 6425
        name=/robot_description            type=DataFrame   Count=    1
        name=/rb_slip_controller/cmd_vel   type=DataFrame   Count= 4271
        name=/vrpn_mocap/rb1/accel         type=DataFrame   Count= 4117
        name=/vrpn_mocap/rb1/pose          type=DataFrame   Count= 4119

    """
    ...

def plot_tf_xy_scatter(raw_data: dict[str, pd.DataFrame]) -> None:
    """
    For '/tf_static' and '/tf', plot scatter of X vs time and Y vs time in one figure,
    annotating each point with its child_frame_id for clarity.
    """
    for topic in ("/tf_static", "/tf"):
        df = raw_data.get(topic)
        if df is None or df.empty:
            print(f"No data for {topic}")
            continue

        # time axis (seconds since start)
        t = df.index.to_numpy().astype(float)
        x = df["transform.translation.x"].to_numpy()
        y = df["transform.translation.y"].to_numpy()
        labels = df["_child_frame_id"].to_numpy()

        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 6))
        fig.suptitle(f"{topic} — X and Y over time (annotated)", fontsize=14)

        # X vs time
        ax1.scatter(t, x, s=20, c='C0')
        for ti, xi, lab in zip(t, x, labels):
            ax1.annotate(lab, (ti, xi),
                         textcoords="offset points", xytext=(2, 2),
                         fontsize=6)
        ax1.set_ylabel("X (m)")
        ax1.grid(True)

        # Y vs time
        ax2.scatter(t, y, s=20, c='C1')
        for ti, yi, lab in zip(t, y, labels):
            ax2.annotate(lab, (ti, yi),
                         textcoords="offset points", xytext=(2, 2),
                         fontsize=6)
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Y (m)")
        ax2.grid(True)

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()

# Usage:
# plot_tf_xy_over_time(raw_data)



def plot_static_and_pose_xy(
    df_static: pd.DataFrame,
    pose_dfs: Dict[str, pd.DataFrame]
) -> None:
    """
    - Scatter static frames (X vs Y) labeled by child_frame_id
    - For each PoseStamped topic, scatter X & Y vs time, labeled by topic
    """
    # Static scatter
    plt.figure(figsize=(6,6))
    x_s = df_static["transform.translation.x"]
    y_s = df_static["transform.translation.y"]
    for xi, yi, lab in zip(x_s, y_s, df_static["_child_frame_id"]):
        plt.scatter(xi, yi, s=30, c='C0')
        plt.text(xi, yi, lab, fontsize=8)
    plt.title("Static frames (X vs Y)")
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.gca().set_aspect('equal', 'box')
    plt.show()

    # Poses over time
    for topic, df in pose_dfs.items():
        t = df.index.to_numpy().astype(float)
        x = df["x"].to_numpy()
        y = df["y"].to_numpy()

        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8,5))
        fig.suptitle(f"{topic} – Pose X/Y vs time", fontsize=12)

        ax1.scatter(t, x, s=15)
        ax1.set_ylabel("X (m)")
        ax1.grid(True)

        ax2.scatter(t, y, s=15)
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Y (m)")
        ax2.grid(True)

        plt.tight_layout(rect=[0,0.03,1,0.95])
        plt.show()


import numpy as np
import plotly.graph_objects as go
from scipy.spatial.transform import Rotation

def plot_static_tf_frames_3d(
    df_static: pd.DataFrame,
    base_frame: str = "base_link",
    axis_len: float = 0.1
) -> None:
    """
    Plot all static TF frames in 3D relative to `base_frame`.
    Each frame’s origin is labelled, and its local x/y/z axes are drawn
    (x=red, y=green, z=blue).
    """
    # 1. Build parent→child map and local transforms
    parent = {}
    t_local = {}
    R_local = {}
    for p, c, tx, ty, tz, qx, qy, qz, qw in zip(
        df_static["header._frame_id"],
        df_static["_child_frame_id"],
        df_static["transform.translation.x"],
        df_static["transform.translation.y"],
        df_static["transform.translation.z"],
        df_static["transform.rotation.x"],
        df_static["transform.rotation.y"],
        df_static["transform.rotation.z"],
        df_static["transform.rotation.w"],
    ):
        parent[c] = p
        t_local[c] = np.array([tx, ty, tz])
        R_local[c] = Rotation.from_quat([qx, qy, qz, qw]).as_matrix()

    # 2. Recursively compute global poses
    t_global = {}
    R_global = {}

    def compute(frame):
        if frame in t_global:
            return
        if frame == base_frame:
            t_global[frame] = np.zeros(3)
            R_global[frame] = np.eye(3)
        else:
            p = parent.get(frame, base_frame)
            compute(p)
            t_global[frame] = t_global[p] + R_global[p] @ t_local[frame]
            R_global[frame] = R_global[p] @ R_local[frame]

    for f in set(parent) | {base_frame}:
        compute(f)

    # 3. Build Plotly figure
    fig = go.Figure()
    for f, T in t_global.items():
        R = R_global[f]
        # frame label
        fig.add_trace(go.Scatter3d(
            x=[T[0]], y=[T[1]], z=[T[2]],
            mode="text", text=[f], showlegend=False
        ))
        # axes
        for axis_vec, col in zip(np.eye(3), ("red", "green", "blue")):
            end = T + R @ (axis_vec * axis_len)
            fig.add_trace(go.Scatter3d(
                x=[T[0], end[0]],
                y=[T[1], end[1]],
                z=[T[2], end[2]],
                mode="lines",
                line=dict(color=col, width=4),
                showlegend=False
            ))

    fig.update_layout(
        title="Static TF Frames (3D) relative to “base_link”",
        scene=dict(
            xaxis_title="X (m)",
            yaxis_title="Y (m)",
            zaxis_title="Z (m)",
            aspectmode="data"
        )
    )
    fig.show()