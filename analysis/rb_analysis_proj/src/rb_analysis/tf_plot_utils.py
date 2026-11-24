import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from queue import Queue
from IPython.display import HTML
from matplotlib import rc
import pandas as pd

# Enable HTML5 animation
rc("animation", html="html5")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML
from queue import Queue


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML
from queue import Queue


# class ViconPoseAnimator:
#     def __init__(
#         self,
#         df,
#         max_size_mb=3,
#         figsize=(8, 8),
#         dpi=100,
#         elev=20,
#         azim=30,
#         interval=20,
#         pose_cols=None,  # list: [x, y, z, qx, qy, qz, qw]
#     ):
#         """
#         Initializes the VICON Pose Animator.

#         Args:
#             df (pd.DataFrame): DataFrame containing VICON pose data.
#             max_size_mb (int, optional): Max memory for animation in MB.
#             figsize (tuple, optional): Figure size.
#             dpi (int, optional): Dots per inch.
#             elev (int, optional): Elevation angle for 3D view.
#             azim (int, optional): Azimuth angle for 3D view.
#             interval (int, optional): Frame interval in ms.
#             pose_cols (list, optional): List of 7 column names [x, y, z, qx, qy, qz, qw].
#                 Defaults to ['pose.position.x','pose.position.y','pose.position.z',
#                              'pose.orientation.x','pose.orientation.y','pose.orientation.z','pose.orientation.w'].
#         """
#         self.df = df.copy()
#         self.max_size_mb = max_size_mb
#         self.figsize = figsize
#         self.dpi = dpi
#         self.elev = elev
#         self.azim = azim
#         self.interval = interval

#         # Column names
#         if pose_cols is None:
#             self.pose_cols = [
#                 "pose.position.x",
#                 "pose.position.y",
#                 "pose.position.z",
#                 "pose.orientation.x",
#                 "pose.orientation.y",
#                 "pose.orientation.z",
#                 "pose.orientation.w",
#             ]
#         else:
#             if len(pose_cols) != 7:
#                 raise ValueError("pose_cols must be list of 7 column names [x,y,z,qx,qy,qz,qw]")
#             self.pose_cols = pose_cols

#         (
#             self.x_col,
#             self.y_col,
#             self.z_col,
#             self.qx_col,
#             self.qy_col,
#             self.qz_col,
#             self.qw_col,
#         ) = self.pose_cols

#         # compute skip
#         self.frame_skip = self._compute_frame_skip()
#         self.df = self.df.iloc[:: self.frame_skip]
#         self.total_timesteps = len(self.df)

#         # compute axis limits and axis length
#         self._compute_axis_limits()

#         # setup plot and initialize frame axes
#         self._setup_plot()

#         # build queue
#         self.data_queue = Queue()
#         for _, row in self.df.iterrows():
#             self.data_queue.put(row)

#     def _compute_frame_skip(self):
#         frames = len(self.df)
#         byte_per_frame = (self.dpi * (self.figsize[0] * self.figsize[1])) * 4
#         max_frames = int((self.max_size_mb * 1024**2) / byte_per_frame)
#         skip = max(1, frames // max_frames)
#         print(f"Max frames allowed: {max_frames}, skipping every {skip} frames")
#         return skip

#     def _compute_axis_limits(self):
#         xmin, xmax = self.df[self.x_col].min(), self.df[self.x_col].max()
#         ymin, ymax = self.df[self.y_col].min(), self.df[self.y_col].max()
#         zmin, zmax = self.df[self.z_col].min(), self.df[self.z_col].max()
#         xmid, ymid, zmid = (xmax + xmin) / 2, (ymax + ymin) / 2, (zmax + zmin) / 2
#         max_range = max(xmax - xmin, ymax - ymin, zmax - zmin) / 2
#         self.axis_limits = {
#             "x": (xmid - max_range, xmid + max_range),
#             "y": (ymid - max_range, ymid + max_range),
#             "z": (zmid - max_range, zmid + max_range),
#         }
#         # length of orientation axes
#         self.axis_length = max_range * 0.25

#     def _setup_plot(self):
#         self.fig = plt.figure(figsize=self.figsize)
#         self.ax = self.fig.add_subplot(111, projection="3d")
#         self.ax.set_xlim(*self.axis_limits["x"])
#         self.ax.set_ylim(*self.axis_limits["y"])
#         self.ax.set_zlim(*self.axis_limits["z"])
#         self.ax.view_init(elev=self.elev, azim=self.azim)
#         self.ax.set_xlabel("X", labelpad=15)
#         self.ax.set_ylabel("Y", labelpad=15)
#         self.ax.set_zlabel("Z", labelpad=15)
#         self.ax.tick_params(labelsize=8)
#         self.ax.set_title("VICON Pose Animation", fontsize=12)

#         # trajectory
#         self.traj_x, self.traj_y, self.traj_z = [], [], []
#         (self.traj_line,) = self.ax.plot([], [], [], label="Trajectory")
#         self.curr_pt = self.ax.scatter([], [], [], s=50, label="Current Position")

#         # orientation axes placeholders
#         self.quiver_x = None
#         self.quiver_y = None
#         self.quiver_z = None
#         self.ax.legend()

#     def _quat_to_rot(self, qx, qy, qz, qw):
#         # convert quaternion to rotation matrix
#         return np.array(
#             [
#                 [1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw), 2 * (qx * qz + qy * qw)],
#                 [2 * (qx * qy + qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw)],
#                 [2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw), 1 - 2 * (qx * qx + qy * qy)],
#             ]
#         )

#     def _update(self, frame):
#         if self.data_queue.empty():
#             return []
#         row = self.data_queue.get()
#         x, y, z = row[self.x_col], row[self.y_col], row[self.z_col]
#         self.traj_x.append(x)
#         self.traj_y.append(y)
#         self.traj_z.append(z)
#         self.traj_line.set_data(self.traj_x, self.traj_y)
#         self.traj_line.set_3d_properties(self.traj_z)
#         self.curr_pt._offsets3d = (np.array([x]), np.array([y]), np.array([z]))

#         # orientation axes
#         R = self._quat_to_rot(
#             row[self.qx_col], row[self.qy_col], row[self.qz_col], row[self.qw_col]
#         )
#         ux, uy, uz = R[:, 0] * self.axis_length
#         vx, vy, vz = R[:, 1] * self.axis_length
#         wx, wy, wz = R[:, 2] * self.axis_length
#         # remove old quivers
#         for q in (self.quiver_x, self.quiver_y, self.quiver_z):
#             if q:
#                 q.remove()
#         # draw new
#         self.quiver_x = self.ax.quiver(x, y, z, ux, uy, uz)
#         self.quiver_y = self.ax.quiver(x, y, z, vx, vy, vz)
#         self.quiver_z = self.ax.quiver(x, y, z, wx, wy, wz)

#         self.ax.set_title(f"VICON Pose Animation - Frame {frame}")
#         return (self.traj_line, self.curr_pt, self.quiver_x, self.quiver_y, self.quiver_z)

#     def run(self):
#         ani = FuncAnimation(
#             self.fig, self._update, frames=self.total_timesteps, interval=self.interval, blit=True
#         )
#         return HTML(ani.to_html5_video())

# Plot all
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML
from queue import Queue


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML
from queue import Queue


class ViconPoseAnimator:
    def __init__(
        self,
        dfs,
        max_size_mb=3,
        figsize=(8, 8),
        dpi=100,
        elev=20,
        azim=30,
        interval=20,
        pose_cols=None,  # list: [x, y, z, qx, qy, qz, qw]
    ):
        """
        Args:
            dfs (dict of pd.DataFrame): VICON pose data series.
            max_size_mb (int): Max memory for animation in MB.
            figsize (tuple): Figure size.
            dpi (int): Dots per inch.
            elev (int): Elevation angle.
            azim (int): Azimuth angle.
            interval (int): Frame interval ms.
            pose_cols (list): 7 column names [x,y,z,qx,qy,qz,qw].
        """
        if not isinstance(dfs, dict):
            raise ValueError("dfs must be a dict of DataFrames with series keys for legend")
        # preserve labels and data
        self.labels = list(dfs.keys())
        self.dfs = [dfs[key].copy() for key in self.labels]
        self.n_series = len(self.dfs)

        self.max_size_mb = max_size_mb
        self.figsize = figsize
        self.dpi = dpi
        self.elev = elev
        self.azim = azim
        self.interval = interval

        # column names
        if pose_cols is None:
            self.pose_cols = [
                "pose.position.x",
                "pose.position.y",
                "pose.position.z",
                "pose.orientation.x",
                "pose.orientation.y",
                "pose.orientation.z",
                "pose.orientation.w",
            ]
        else:
            if len(pose_cols) != 7:
                raise ValueError("pose_cols must be list of 7 column names [x,y,z,qx,qy,qz,qw]")
            self.pose_cols = pose_cols
        (
            self.x_col,
            self.y_col,
            self.z_col,
            self.qx_col,
            self.qy_col,
            self.qz_col,
            self.qw_col,
        ) = self.pose_cols

        # compute frame skip based on shortest series length
        lengths = [len(df) for df in self.dfs]
        min_len = min(lengths)
        self.frame_skip = self._compute_frame_skip(min_len)
        # apply skip and reset index
        self.dfs = [df.iloc[:: self.frame_skip].reset_index(drop=True) for df in self.dfs]
        self.total_timesteps = min(len(df) for df in self.dfs)

        self._compute_axis_limits()
        self._setup_plot()

        # build queue of row tuples
        self.data_queue = Queue()
        for i in range(self.total_timesteps):
            rows = [df.iloc[i] for df in self.dfs]
            self.data_queue.put(rows)

    def _compute_frame_skip(self, frames):
        byte_per_frame = (self.dpi * (self.figsize[0] * self.figsize[1])) * 4
        max_frames = int((self.max_size_mb * 1024**2) / byte_per_frame)
        skip = max(1, frames // max_frames)
        print(f"Max frames allowed: {max_frames}, skipping every {skip} frames")
        return skip

    def _compute_axis_limits(self):
        all_x = np.concatenate([df[self.x_col].to_numpy() for df in self.dfs])
        all_y = np.concatenate([df[self.y_col].to_numpy() for df in self.dfs])
        all_z = np.concatenate([df[self.z_col].to_numpy() for df in self.dfs])
        xmin, xmax = all_x.min(), all_x.max()
        ymin, ymax = all_y.min(), all_y.max()
        zmin, zmax = all_z.min(), all_z.max()
        xmid, ymid, zmid = (xmax + xmin) / 2, (ymax + ymin) / 2, (zmax + zmin) / 2
        max_range = max(xmax - xmin, ymax - ymin, zmax - zmin) / 2
        self.axis_limits = {
            "x": (xmid - max_range, xmid + max_range),
            "y": (ymid - max_range, ymid + max_range),
            "z": (zmid - max_range, zmid + max_range),
        }
        self.axis_length = max_range * 0.25

    def _setup_plot(self):
        self.fig = plt.figure(figsize=self.figsize)
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.ax.set_xlim(*self.axis_limits["x"])
        self.ax.set_ylim(*self.axis_limits["y"])
        self.ax.set_zlim(*self.axis_limits["z"])
        self.ax.view_init(elev=self.elev, azim=self.azim)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        self.ax.set_title("VICON Pose Animation")

        self.traj_lines = []
        self.curr_pts = []
        self.quiver_xs = []
        self.quiver_ys = []
        self.quiver_zs = []
        cmap = plt.get_cmap("tab10")
        for i, label in enumerate(self.labels):
            color = cmap(i % 10)
            (line,) = self.ax.plot([], [], [], color=color, label=label)
            pt = self.ax.scatter([], [], [], color=color, s=50)
            self.traj_lines.append(line)
            self.curr_pts.append(pt)
            self.quiver_xs.append(None)
            self.quiver_ys.append(None)
            self.quiver_zs.append(None)
        self.ax.legend()

    def _quat_to_rot(self, qx, qy, qz, qw):
        return np.array(
            [
                [1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw), 2 * (qx * qz + qy * qw)],
                [2 * (qx * qy + qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw)],
                [2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw), 1 - 2 * (qx * qx + qy * qy)],
            ]
        )

    def _update(self, frame):
        if self.data_queue.empty():
            return []
        rows = self.data_queue.get()
        artists = []
        for i, row in enumerate(rows):
            x, y, z = row[self.x_col], row[self.y_col], row[self.z_col]
            xl, yl, zl = self.traj_lines[i].get_data_3d()
            xl = np.append(xl, x)
            yl = np.append(yl, y)
            zl = np.append(zl, z)
            self.traj_lines[i].set_data(xl, yl)
            self.traj_lines[i].set_3d_properties(zl)
            self.curr_pts[i]._offsets3d = ([x], [y], [z])
            R = self._quat_to_rot(
                row[self.qx_col], row[self.qy_col], row[self.qz_col], row[self.qw_col]
            )
            ux, uy, uz = R[:, 0] * self.axis_length
            vx, vy, vz = R[:, 1] * self.axis_length
            wx, wy, wz = R[:, 2] * self.axis_length
            for q in (self.quiver_xs[i], self.quiver_ys[i], self.quiver_zs[i]):
                if q:
                    q.remove()
            self.quiver_xs[i] = self.ax.quiver(x, y, z, ux, uy, uz)
            self.quiver_ys[i] = self.ax.quiver(x, y, z, vx, vy, vz)
            self.quiver_zs[i] = self.ax.quiver(x, y, z, wx, wy, wz)
            artists += [
                self.traj_lines[i],
                self.curr_pts[i],
                self.quiver_xs[i],
                self.quiver_ys[i],
                self.quiver_zs[i],
            ]
        return artists

    def run(self):
        ani = FuncAnimation(
            self.fig, self._update, frames=self.total_timesteps, interval=self.interval, blit=True
        )
        return HTML(ani.to_html5_video())


# class ViconPoseAnimator:
#     def __init__(self, df, max_size_mb=3, figsize=(8, 8), dpi=100, elev=20, azim=30, interval=20):
#         """
#         Initializes the VICON Pose Animator.

#         Args:
#             df (pd.DataFrame): DataFrame containing VICON pose data.
#             max_size_mb (int, optional): Maximum allowed memory size for animation. Defaults to 3MB.
#             figsize (tuple, optional): Size of the figure in inches. Defaults to (8,8).
#             dpi (int, optional): Dots per inch for rendering. Defaults to 100.
#             elev (int, optional): Elevation angle for 3D view. Defaults to 20.
#             azim (int, optional): Azimuth angle for 3D view. Defaults to 30.
#             interval (int, optional): Interval between frames in milliseconds. Defaults to 20ms.
#         """
#         self.df = df
#         self.max_size_mb = max_size_mb
#         self.figsize = figsize
#         self.dpi = dpi
#         self.elev = elev
#         self.azim = azim
#         self.interval = interval

#         # Compute frame skipping factor
#         self.frame_skip = self._compute_frame_skip()
#         self.df = self.df.iloc[:: self.frame_skip]
#         self.total_timesteps = len(self.df)

#         # Compute axis limits for equal scaling
#         self._compute_axis_limits()

#         # Setup Matplotlib figure and axis
#         self._setup_plot()

#         # Initialize data queue
#         self.data_queue = Queue()
#         for _, row in self.df.iterrows():
#             self.data_queue.put(row)

#     def _compute_frame_skip(self):
#         """Calculates the number of frames to skip to fit within the memory limit."""
#         total_timesteps = len(self.df)

#         # Estimate per-frame memory usage
#         byte_per_frame = (
#             self.dpi * (self.figsize[0] * self.figsize[1])
#         ) * 4  # 4 bytes per pixel (RGBA)
#         max_frames = int((self.max_size_mb * 1024**2) / byte_per_frame)

#         frame_skip = max(1, total_timesteps // max_frames)
#         print(f"Max frames allowed: {max_frames}, Frame skipping factor: {frame_skip}")
#         return frame_skip

#     def _compute_axis_limits(self):
#         """Computes equal axis limits to maintain aspect ratio."""
#         x_min, x_max = self.df["pose.position.x"].min(), self.df["pose.position.x"].max()
#         y_min, y_max = self.df["pose.position.y"].min(), self.df["pose.position.y"].max()
#         z_min, z_max = self.df["pose.position.z"].min(), self.df["pose.position.z"].max()

#         x_mid, y_mid, z_mid = (x_max + x_min) / 2, (y_max + y_min) / 2, (z_max + z_min) / 2
#         max_range = max(x_max - x_min, y_max - y_min, z_max - z_min) / 2

#         self.axis_limits = {
#             "x": (x_mid - max_range, x_mid + max_range),
#             "y": (y_mid - max_range, y_mid + max_range),
#             "z": (z_mid - max_range, z_mid + max_range),
#         }

#     def _setup_plot(self):
#         """Sets up the 3D Matplotlib figure and axis."""
#         self.fig = plt.figure(figsize=self.figsize)
#         self.ax = self.fig.add_subplot(111, projection="3d")

#         # Apply equal axis limits
#         self.ax.set_xlim(self.axis_limits["x"])
#         self.ax.set_ylim(self.axis_limits["y"])
#         self.ax.set_zlim(self.axis_limits["z"])

#         # Set camera perspective
#         self.ax.view_init(elev=self.elev, azim=self.azim)

#         # Format labels & ticks
#         self.ax.set_xlabel("X", labelpad=15)
#         self.ax.set_ylabel("Y", labelpad=15)
#         self.ax.set_zlabel("Z", labelpad=15)
#         self.ax.tick_params(labelsize=8)
#         self.ax.set_title("VICON Pose Animation", fontsize=12)

#         # Initialize the plot objects (Keep them persistent)
#         self.trajectory_x, self.trajectory_y, self.trajectory_z = [], [], []
#         (self.trajectory_line,) = self.ax.plot([], [], [], color="b", label="Trajectory")
#         self.current_point = self.ax.scatter([], [], [], color="r", s=50, label="Current Position")
#         self.ax.legend(fontsize=10)

#     def _update(self, frame):
#         """Animation update function."""
#         if not self.data_queue.empty():
#             row = self.data_queue.get()
#             x, y, z = row["pose.position.x"], row["pose.position.y"], row["pose.position.z"]

#             # Append to trajectory
#             self.trajectory_x.append(x)
#             self.trajectory_y.append(y)
#             self.trajectory_z.append(z)

#             # Update trajectory line
#             self.trajectory_line.set_data(self.trajectory_x, self.trajectory_y)
#             self.trajectory_line.set_3d_properties(self.trajectory_z)

#             # Update current position marker
#             self.current_point._offsets3d = (np.array([x]), np.array([y]), np.array([z]))

#             self.ax.set_title(f"VICON Pose Animation - Frame {frame}")

#         return self.trajectory_line, self.current_point

#     def run(self):
#         """Runs the animation and displays it in the Jupyter Notebook."""
#         ani = FuncAnimation(
#             self.fig, self._update, frames=self.total_timesteps, interval=self.interval, blit=True
#         )
#         return HTML(ani.to_html5_video())


import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from queue import Queue
from IPython.display import HTML
from matplotlib import rc
from scipy.spatial.transform import Rotation

rc("animation", html="html5")


# class ViconTwistAnimator:
#     def __init__(
#         self,
#         df_pose: pd.DataFrame,
#         df_vicon_twist: pd.DataFrame,
#         df_body_twist: pd.DataFrame,
#         plot_step: int = 500,
#         max_size_mb: int = 3,
#         figsize: tuple = (8, 8),
#         dpi: int = 100,
#         elev: float = 20,
#         azim: float = 30,
#         interval: int = 20,
#         axis_len: float = 0.1,
#         twist_scale: float = 0.1,
#     ):
#         """
#         Animate Vicon marker pose + twists.

#         df_pose:           pose DataFrame (must have .index of timestamps)
#         df_vicon_twist:    vicon-frame twist (indexed same as df_pose)
#         df_body_twist:     body-frame twist (indexed same as df_pose)
#         axis_len:          length of frame axes
#         twist_scale:       scale factor for twist arrows
#         """
#         self.axis_len = axis_len
#         self.twist_scale = twist_scale

#         # frame skipping
#         self.df_pose = df_pose
#         self.max_size_mb = max_size_mb
#         self.dpi = dpi
#         self.figsize = figsize
#         self.frame_skip = self._compute_frame_skip()

#         self.elev = elev
#         self.azim = azim
#         self.interval = interval
#         self.axis_len = axis_len
#         self.twist_scale = twist_scale
#         self.plot_step = plot_step

#         mask = self.df_pose.index.isin(df_vicon_twist.index)
#         self.df_pose = self.df_pose.loc[mask]

#         # 2) now slice every plot_step frames on the already-filtered df_pose
#         self.df_pose = self.df_pose.iloc[::plot_step]

#         # 3) safe to align twists by index
#         self.df_vicon_twist = df_vicon_twist.loc[self.df_pose.index]
#         self.df_body_twist = df_body_twist.loc[self.df_pose.index]

#         self.total_timesteps = len(self.df_pose)

#         # axis limits
#         self._compute_axis_limits()

#         # setup plot
#         self._setup_plot()

#         # prepare dynamic queue
#         self.data_queue = Queue()
#         for idx, row in self.df_pose.iterrows():
#             self.data_queue.put(idx)

#     def _compute_frame_skip(self):
#         total = len(self.df_pose)
#         bytes_per_frame = self.dpi * (self.figsize[0] * self.figsize[1]) * 4
#         max_frames = int((self.max_size_mb * 1024**2) / bytes_per_frame)
#         return max(1, total // max_frames)

#     def _compute_axis_limits(self):
#         x = self.df_pose["x"]
#         y = self.df_pose["y"]
#         z = self.df_pose["z"]
#         x_mid = (x.min() + x.max()) / 2
#         y_mid = (y.min() + y.max()) / 2
#         z_mid = (z.min() + z.max()) / 2
#         r = max(x.max() - x.min(), y.max() - y.min(), z.max() - z.min()) / 2
#         self.axis_limits = {
#             "x": (x_mid - r, x_mid + r),
#             "y": (y_mid - r, y_mid + r),
#             "z": (z_mid - r, z_mid + r),
#         }

#     def _setup_plot(self):
#         self.fig = plt.figure(figsize=self.figsize, dpi=self.dpi)
#         self.ax = self.fig.add_subplot(111, projection="3d")
#         self.ax.set_xlim(*self.axis_limits["x"])
#         self.ax.set_ylim(*self.axis_limits["y"])
#         self.ax.set_zlim(*self.axis_limits["z"])
#         self.ax.view_init(elev=self.elev, azim=self.azim)
#         self.ax.set_xlabel("X")
#         self.ax.set_ylabel("Y")
#         self.ax.set_zlabel("Z")
#         self.ax.set_title("VICON Pose + Twists", fontsize=12)

#         # static vicon-frame axes at origin
#         for vec, col in zip(np.eye(3), ("r", "g", "b")):
#             self.ax.quiver(
#                 0,
#                 0,
#                 0,
#                 vec[0] * self.axis_len,
#                 vec[1] * self.axis_len,
#                 vec[2] * self.axis_len,
#                 color=col,
#                 linewidth=2,
#                 arrow_length_ratio=0.1,
#             )

#         # trajectory and current-point
#         self.traj_x, self.traj_y, self.traj_z = [], [], []
#         (self.traj_line,) = self.ax.plot([], [], [], color="k", lw=1)
#         self.curr_point = self.ax.scatter([], [], [], color="m", s=50)

#         # holders for dynamic artists (axes & arrows)
#         self.dynamic_artists = []

#     def _update(self, _frame):
#         # clear previous dynamic artists
#         for art in self.dynamic_artists:
#             art.remove()
#         self.dynamic_artists.clear()

#         idx = self.data_queue.get()
#         row = self.df_pose.loc[idx]
#         x, y, z = row["x"], row["y"], row["z"]

#         # update trajectory
#         self.traj_x.append(x)
#         self.traj_y.append(y)
#         self.traj_z.append(z)
#         self.traj_line.set_data(self.traj_x, self.traj_y)
#         self.traj_line.set_3d_properties(self.traj_z)
#         self.curr_point._offsets3d = (np.array([x]), np.array([y]), np.array([z]))

#         # draw marker-frame axes at current pose
#         quat = row[["qx", "qy", "qz", "qw"]].to_numpy()
#         R = Rotation.from_quat(quat).as_matrix()
#         for vec, col in zip(np.eye(3), ("r", "g", "b")):
#             end = np.array([x, y, z]) + R.dot(vec * self.axis_len)
#             art = self.ax.plot([x, end[0]], [y, end[1]], [z, end[2]], color=col, lw=2)[0]
#             self.dynamic_artists.append(art)

#         # draw vicon-frame twist arrow
#         vt = self.df_vicon_twist.loc[idx]
#         art_v = self.ax.quiver(
#             x,
#             y,
#             z,
#             vt["vx"],
#             vt["vy"],
#             vt["vz"],
#             length=self.twist_scale,
#             normalize=False,
#             color="cyan",
#             arrow_length_ratio=0.2,
#         )
#         self.dynamic_artists.append(art_v)

#         # draw body-frame twist arrow
#         bt = self.df_body_twist.loc[idx]
#         art_b = self.ax.quiver(
#             x,
#             y,
#             z,
#             bt["vx_b"],
#             bt["vy_b"],
#             bt["vz_b"],
#             length=self.twist_scale,
#             normalize=False,
#             color="magenta",
#             arrow_length_ratio=0.2,
#         )
#         self.dynamic_artists.append(art_b)

#         return [self.traj_line, self.curr_point] + self.dynamic_artists

#     def run(self):
#         ani = FuncAnimation(
#             self.fig, self._update, frames=self.total_timesteps, interval=self.interval, blit=True
#         )
#         return HTML(ani.to_html5_video())


class ViconTwistAnimator:
    def __init__(
        self,
        df_pose: pd.DataFrame,
        df_vicon_twist: pd.DataFrame,
        df_body_twist: pd.DataFrame,
        plot_step: int = 500,
        elev: float = 20,
        azim: float = 30,
        interval: int = 20,
        axis_len: float = 0.1,
        twist_scale: float = 0.1,
    ):
        # 1) align poses→twist, then subsample every plot_step
        mask = df_pose.index.isin(df_vicon_twist.index)
        self.df_pose = df_pose.loc[mask].iloc[::plot_step]
        self.df_vicon_twist = df_vicon_twist.loc[self.df_pose.index]
        self.df_body_twist = df_body_twist.loc[self.df_pose.index]

        self.frames = list(self.df_pose.index)
        self.interval = interval
        self.axis_len = axis_len
        self.twist_scale = twist_scale
        self.elev = elev
        self.azim = azim

        self._compute_axis_limits()
        self._setup_plot()

        self.dynamic_artists = []

        self.traj_x, self.traj_y, self.traj_z = [], [], []

        # build subsampled frames list
        mask = df_pose.index.isin(df_vicon_twist.index)

        self.frames = list(self.df_pose.index)

    def _compute_axis_limits(self):
        x = self.df_pose["x"]
        y = self.df_pose["y"]
        z = self.df_pose["z"]
        xm, xM = x.min(), x.max()
        ym, yM = y.min(), y.max()
        zm, zM = z.min(), z.max()
        cx, cy, cz = (xM + xm) / 2, (yM + ym) / 2, (zM + zm) / 2
        r = max(xM - xm, yM - ym, zM - zm) / 2
        self.axis_limits = {"x": (cx - r, cx + r), "y": (cy - r, cy + r), "z": (cz - r, cz + r)}

    def _setup_plot(self):
        self.fig = plt.figure(figsize=(8, 8))
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.ax.set_xlim(*self.axis_limits["x"])
        self.ax.set_ylim(*self.axis_limits["y"])
        self.ax.set_zlim(*self.axis_limits["z"])
        self.ax.view_init(elev=self.elev, azim=self.azim)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")

        (self.traj_line,) = self.ax.plot([], [], [], color="k", lw=1)

        # draw static world axes
        for v, c in zip(np.eye(3), ("r", "g", "b")):
            self.ax.quiver(
                0, 0, 0, *v * self.axis_len, color=c, linewidth=2, arrow_length_ratio=0.1
            )

        # trajectory & point
        (self.traj,) = self.ax.plot([], [], [], color="k", lw=1)
        self.point = self.ax.scatter([], [], [], color="m", s=50)

    def _update(self, timestamp):
        # clear previous dynamic artists
        for art in self.dynamic_artists:
            art.remove()
        self.dynamic_artists.clear()

        # grab pose & twists at this time
        row = self.df_pose.loc[timestamp]
        x, y, z = row["x"], row["y"], row["z"]

        # update trajectory
        self.traj_x.append(x)
        self.traj_y.append(y)
        self.traj_z.append(z)
        self.traj_line.set_data(self.traj_x, self.traj_y)
        self.traj_line.set_3d_properties(self.traj_z)
        self.point._offsets3d = ([x], [y], [z])

        # --- draw body‐frame axes at the marker pose ---
        quat = row[["qx", "qy", "qz", "qw"]].to_numpy()
        R = Rotation.from_quat(quat).as_matrix()
        for vec, col in zip(np.eye(3), ("r", "g", "b")):
            u, v, w = (R @ vec) * self.axis_len
            art = self.ax.quiver(x, y, z, u, v, w, color=col, linewidth=2, arrow_length_ratio=.3)
            self.dynamic_artists.append(art)

        # --- draw vicon‐frame twist arrow ---
        vt = self.df_vicon_twist.loc[timestamp]
        art_v = self.ax.quiver(
            x,
            y,
            z,
            vt["vx"],
            vt["vy"],
            vt["vz"],
            length=self.twist_scale,
            normalize=False,
            color="cyan",
            arrow_length_ratio=0.2,
        )
        self.dynamic_artists.append(art_v)

        # --- draw body‐frame twist arrow ---
        bt = self.df_body_twist.loc[timestamp]
        art_b = self.ax.quiver(
            x,
            y,
            z,
            bt["vx"],
            bt["vy"],
            bt["vz"],
            length=self.twist_scale,
            normalize=False,
            color="magenta",
            arrow_length_ratio=0.2,
        )
        self.dynamic_artists.append(art_b)

        return [self.traj_line, self.point] + self.dynamic_artists

    def run(self):
        ani = FuncAnimation(
            self.fig,
            self._update,
            frames=self.frames,  # only subsampled timestamps
            interval=self.interval,
            blit=True,
        )
        return HTML(ani.to_html5_video())
