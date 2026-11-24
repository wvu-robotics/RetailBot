import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, TwistStamped
from tf2_ros import TransformBroadcaster, StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped
import time


# class TF2Publisher(Node):
#     def __init__(self):
#         super().__init__("tf2_publisher")
#         self.tf_broadcaster = TransformBroadcaster(self)
#         self.static_tf_broadcaster = StaticTransformBroadcaster(self)
#         self.pose_pubber = self.create_publisher(PoseStamped, "test_pose",10)

#     def send_tf(self, xform):
#         """Just send the transform as is using the nodes broadcaster."""
#         self.tf_broadcaster.sendTransform(xform)
#         rclpy.spin_once(self, timeout_sec=0.2)

#     def send_static_tf(self, xform):
#         """Just send the transform as is using the nodes broadcaster."""
#         self.static_tf_broadcaster.sendTransform(xform)
#         rclpy.spin_once(self, timeout_sec=0.2)
        
#     def send_pose_stamped(self, pose_stamped: PoseStamped):
#         self.pose_pubber.publish(pose_stamped)


class TF2Publisher(Node):
    def __init__(self, rate_hz=100.0):
        super().__init__("tf2_publisher")
        self.pose_publishers = {}
        self.twist_publishers = {}
        self.pose_queues = {}
        self.twist_queues = {}
        self.pose_timers = {}
        self.twist_timers = {}
        self.rate_hz = rate_hz

        self.tf_broadcaster = TransformBroadcaster(self)
        self.static_tf_broadcaster = StaticTransformBroadcaster(self)

    def send_tf(self, xform):
        self.tf_broadcaster.sendTransform(xform)
        rclpy.spin_once(self, timeout_sec=0.2)

    def send_static_tf(self, xform):
        self.static_tf_broadcaster.sendTransform(xform)
        rclpy.spin_once(self, timeout_sec=0.2)

    def register_pose_publisher(self, topic_name):
        if topic_name not in self.pose_publishers:
            self.pose_publishers[topic_name] = self.create_publisher(PoseStamped, topic_name, 10)

    def register_twist_publisher(self, topic_name):
        if topic_name not in self.twist_publishers:
            self.twist_publishers[topic_name] = self.create_publisher(TwistStamped, topic_name, 10)

    def send_pose_stamped(self, topic_name, poses):
        self.register_pose_publisher(topic_name)
        self.pose_queues[topic_name] = poses
        if topic_name in self.pose_timers:
            self.pose_timers[topic_name].cancel()
        self.pose_timers[topic_name] = self.create_timer(
            1.0 / self.rate_hz, lambda: self.pose_timer_callback(topic_name)
        )

    def send_twist_stamped(self, topic_name, twists):
        self.register_twist_publisher(topic_name)
        self.twist_queues[topic_name] = twists
        if topic_name in self.twist_timers:
            self.twist_timers[topic_name].cancel()
        self.twist_timers[topic_name] = self.create_timer(
            1.0 / self.rate_hz, lambda: self.twist_timer_callback(topic_name)
        )

    def pose_timer_callback(self, topic_name):
        if self.pose_queues[topic_name]:
            pose = self.pose_queues[topic_name].pop(0)
            self.pose_publishers[topic_name].publish(pose)
        if not self.pose_queues[topic_name]:
            self.pose_timers[topic_name].cancel()

    def twist_timer_callback(self, topic_name):
        if self.twist_queues[topic_name]:
            twist = self.twist_queues[topic_name].pop(0)
            self.twist_publishers[topic_name].publish(twist)
        if not self.twist_queues[topic_name]:
            self.twist_timers[topic_name].cancel()




def try_init():
    if rclpy.ok():
        return rclpy.get_global_executor()
    else:
        rclpy.init()

def send_transform(transforms:list[TransformStamped]):
    try_init()
    node = TF2Publisher()

    try:
        for tf in transforms:
            node.send_tf(tf)
            time.sleep(0.1)  # Give time for Rviz to receive messages
    finally:
        node.destroy_node()
        rclpy.shutdown()

def send_static_transform(transforms:list[TransformStamped]):
    try_init()
    node = TF2Publisher()

    try:
        for tf in transforms:
            node.send_static_tf(tf)
            time.sleep(0.1)  # Give time for Rviz to receive messages
    finally:
        node.destroy_node()
        rclpy.shutdown()


def publish_pose_stamped(poses: list[PoseStamped], rate_hz=100.0):
    try_init()
    node = TF2Publisher(rate_hz)

    try:
        node.send_pose_stamped(poses)
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


def publish_pose_stamped_list(poses_dict: dict[str, list[PoseStamped]], rate_hz=100.0):
    """ Publish multiple lists of PoseStamped messages on separate topics. """
    try_init()
    node = TF2Publisher(rate_hz)

    try:
        for topic_name, poses in poses_dict.items():
            node.send_pose_stamped(topic_name, poses)

        rclpy.spin(node)

    finally:
        node.destroy_node()
        rclpy.shutdown()

def publish_twist_stamped_list(poses_dict: dict[str, list[TwistStamped]], rate_hz=100.0):
    """ Publish multiple lists of TwistStamped messages on separate topics. """
    try_init()
    node = TF2Publisher(rate_hz)

    try:
        for topic_name, twists in poses_dict.items():
            node.send_twist_stamped(topic_name, twists)

        rclpy.spin(node)

    finally:
        node.destroy_node()
        rclpy.shutdown()




def publish_df_pose_stamped(df, frame_id:str, rate_hz=100.0,):
    """ Convert a DataFrame into PoseStamped messages and publish """
    try_init()
    node = TF2Publisher(rate_hz)

    try:
        # Convert DataFrame to PoseStamped messages
        poses = []
        for timestamp, row in df.iterrows():
            pose = PoseStamped()
            pose.header.stamp.sec = int(timestamp.timestamp())
            pose.header.stamp.nanosec = int((timestamp.timestamp() % 1) * 1e9)
            pose.header.frame_id = frame_id

            pose.pose.position.x = row["pose.position.x"]
            pose.pose.position.y = row["pose.position.y"]
            pose.pose.position.z = row["pose.position.z"]

            pose.pose.orientation.x = row["pose.orientation.x"]
            pose.pose.orientation.y = row["pose.orientation.y"]
            pose.pose.orientation.z = row["pose.orientation.z"]
            pose.pose.orientation.w = row["pose.orientation.w"]

            poses.append(pose)

        # Publish the converted poses
        node.send_pose_stamped(poses)
        rclpy.spin(node)  # Keep node running until all messages are sent

    finally:
        node.destroy_node()
        rclpy.shutdown()


import rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage
from geometry_msgs.msg import TransformStamped

class TFStaticCapture(Node):
    def __init__(self):
        super().__init__('tf_static_capture')
        self.subscription = self.create_subscription(
            TFMessage, "/tf_static", self.callback, 10)
        self.static_transforms = []
        self.received = False

    def callback(self, msg):
        """ Callback for receiving /tf_static messages. """
        if not self.received:
            self.get_logger().info(f"Received /tf_static with {len(msg.transforms)} transforms.")
            self.static_transforms = msg.transforms
            self.received = True
            self.destroy_subscription(self.subscription)

# def capture_tf_static(timeout=5.0):
#     """
#     Captures /tf_static and prints it as Python code.

#     :param timeout: Time in seconds to wait for the message.
#     """
#     rclpy.init()
#     node = TFStaticCapture()

#     try:
#         start_time = node.get_clock().now().to_msg().sec
#         while rclpy.ok() and not node.received:
#             rclpy.spin_once(node, timeout_sec=0.1)
#             elapsed = node.get_clock().now().to_msg().sec - start_time
#             if elapsed > timeout:
#                 node.get_logger().warn("Timeout: No /tf_static received.")
#                 break

#         if node.received:
#             print("\n# Copy-paste this into a Jupyter cell to recreate static transforms\n")
#             transform_list = []

#             for tf in node.static_transforms:
#                 var_name = tf.child_frame_id.replace("-", "_") + "_tf"
#                 transform_list.append(var_name)

#                 print(f"""
# {var_name} = TransformStamped()
# {var_name}.header.frame_id = "{tf.header.frame_id}"
# {var_name}.child_frame_id = "{tf.child_frame_id}"
# {var_name}.transform.translation.x = {tf.transform.translation.x}
# {var_name}.transform.translation.y = {tf.transform.translation.y}
# {var_name}.transform.translation.z = {tf.transform.translation.z}
# {var_name}.transform.rotation.x = {tf.transform.rotation.x}
# {var_name}.transform.rotation.y = {tf.transform.rotation.y}
# {var_name}.transform.rotation.z = {tf.transform.rotation.z}
# {var_name}.transform.rotation.w = {tf.transform.rotation.w}
# """)

#             # Generate the list of transforms
#             print("\n# Store all transforms in a list\n")
#             print("static_transforms = [")
#             for var in transform_list:
#                 print(f"    {var},")
#             print("]\n")

#             # Code to add them to tf_buffer
#             # print("# Add all transforms to the tf_buffer\n")
#             # print("tf_buffer = tf2_ros.Buffer()\n")
#             # print("for tf in static_transforms:")
#             # print("    tf_buffer.set_transform(tf, 'default_authority')\n")

#     finally:
#         node.destroy_node()
#         rclpy.shutdown()



import rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage
from geometry_msgs.msg import TransformStamped
import time

class TFStaticCapture(Node):
    def __init__(self):
        super().__init__("tf_static_capture")
        self.static_transforms = []
        self.dynamic_transforms = []
        self.received_static = False
        self.received_dynamic = False

        # Subscribe to both /tf_static and /tf
        self.static_sub = self.create_subscription(TFMessage, "/tf_static", self.static_callback, 10)
        self.dynamic_sub = self.create_subscription(TFMessage, "/tf", self.dynamic_callback, 10)

    def static_callback(self, msg):
        self.static_transforms.extend(msg.transforms)
        self.received_static = True

    def dynamic_callback(self, msg):
        if not self.received_dynamic:  # Only capture first TF messages (zeroed transforms)
            self.dynamic_transforms.extend(msg.transforms)
            self.received_dynamic = True

def capture_tf_static(timeout=5.0):
    """
    Captures /tf_static and the first /tf messages and prints them as Python code.

    :param timeout: Time in seconds to wait for messages.
    """
    rclpy.init()
    node = TFStaticCapture()

    try:
        start_time = node.get_clock().now().to_msg().sec
        while rclpy.ok() and (not node.received_static or not node.received_dynamic):
            rclpy.spin_once(node, timeout_sec=0.1)
            elapsed = node.get_clock().now().to_msg().sec - start_time
            if elapsed > timeout:
                node.get_logger().warn("Timeout: No /tf_static or /tf received.")
                break

        # Combine static and first-received dynamic transforms
        all_transforms = node.static_transforms + node.dynamic_transforms

        if all_transforms:
            print("\n# Copy-paste this into a Jupyter cell to recreate static transforms\n")
            transform_list = []

            for tf in all_transforms:
                var_name = tf.child_frame_id.replace("-", "_") + "_tf"
                transform_list.append(var_name)

                print(f"""
{var_name} = TransformStamped()
{var_name}.header.frame_id = "{tf.header.frame_id}"
{var_name}.child_frame_id = "{tf.child_frame_id}"
{var_name}.transform.translation.x = {tf.transform.translation.x}
{var_name}.transform.translation.y = {tf.transform.translation.y}
{var_name}.transform.translation.z = {tf.transform.translation.z}
{var_name}.transform.rotation.x = {tf.transform.rotation.x}
{var_name}.transform.rotation.y = {tf.transform.rotation.y}
{var_name}.transform.rotation.z = {tf.transform.rotation.z}
{var_name}.transform.rotation.w = {tf.transform.rotation.w}
""")

            # Generate the list of transforms
            print("\n# Store all transforms in a list\n")
            print("static_transforms = [")
            for var in transform_list:
                print(f"    {var},")
            print("]\n")

    finally:
        node.destroy_node()
        rclpy.shutdown()





import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
from std_msgs.msg import ColorRGBA

class TransformVisualizer(Node):
    def __init__(self):
        super().__init__("transform_visualizer")
        self.marker_publisher = self.create_publisher(Marker, "transform_markers", 10)

    def publish_transform_markers(self, transforms):
        """Publishes transform markers in RViz."""
        for i, transform in enumerate(transforms):
            marker = Marker()
            marker.header.frame_id = transform.header.frame_id
            marker.header.stamp = transform.header.stamp
            marker.ns = "transform_arrows"
            marker.id = i
            marker.type = Marker.ARROW
            marker.action = Marker.ADD

            # Arrow color and scale
            marker.scale.x = 0.1  # Shaft diameter
            marker.scale.y = 0.2  # Head diameter
            marker.scale.z = 0.2  # Head length
            # marker.color = ColorRGBA(1.0, 0.0, 0.0, 1.0)  # Red color, full opacity


            # Arrow start and end points
            marker.points.append(Point(
                x=transform.transform.translation.x,
                y=transform.transform.translation.y,
                z=transform.transform.translation.z
            ))
            marker.points.append(Point(
                x=transform.transform.translation.x + 0.2,  # Slightly offset
                y=transform.transform.translation.y,
                z=transform.transform.translation.z
            ))

            self.marker_publisher.publish(marker)

def visualize_transforms(transforms):
    """Start a ROS node to publish transform markers."""
    rclpy.init()
    node = TransformVisualizer()
    
    try:
        node.publish_transform_markers(transforms)
        rclpy.spin_once(node, timeout_sec=0.2)
    finally:
        node.destroy_node()
        rclpy.shutdown()




import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from queue import Queue
from IPython.display import HTML
from matplotlib import rc

# Enable HTML5 animation
rc("animation", html="html5")

class ViconPoseAnimator:
    def __init__(self, df, max_size_mb=3, figsize=(8, 8), dpi=100, elev=20, azim=30, interval=20):
        """
        Initializes the VICON Pose Animator.
        
        Args:
            df (pd.DataFrame): DataFrame containing VICON pose data.
            max_size_mb (int, optional): Maximum allowed memory size for animation. Defaults to 3MB.
            figsize (tuple, optional): Size of the figure in inches. Defaults to (8,8).
            dpi (int, optional): Dots per inch for rendering. Defaults to 100.
            elev (int, optional): Elevation angle for 3D view. Defaults to 20.
            azim (int, optional): Azimuth angle for 3D view. Defaults to 30.
            interval (int, optional): Interval between frames in milliseconds. Defaults to 20ms.
        """
        self.df = df
        self.max_size_mb = max_size_mb
        self.figsize = figsize
        self.dpi = dpi
        self.elev = elev
        self.azim = azim
        self.interval = interval

        # Compute frame skipping factor
        self.frame_skip = self._compute_frame_skip()
        self.df = self.df.iloc[::self.frame_skip]
        self.total_timesteps = len(self.df)

        # Compute axis limits for equal scaling
        self._compute_axis_limits()

        # Setup Matplotlib figure and axis
        self._setup_plot()

        # Initialize data queue
        self.data_queue = Queue()
        for _, row in self.df.iterrows():
            self.data_queue.put(row)

    def _compute_frame_skip(self):
        """Calculates the number of frames to skip to fit within the memory limit."""
        total_timesteps = len(self.df)

        # Estimate per-frame memory usage
        byte_per_frame = (self.dpi * (self.figsize[0] * self.figsize[1])) * 4  # 4 bytes per pixel (RGBA)
        max_frames = int((self.max_size_mb * 1024**2) / byte_per_frame)

        frame_skip = max(1, total_timesteps // max_frames)
        print(f"Max frames allowed: {max_frames}, Frame skipping factor: {frame_skip}")
        return frame_skip

    def _compute_axis_limits(self):
        """Computes equal axis limits to maintain aspect ratio."""
        x_min, x_max = self.df["pose.position.x"].min(), self.df["pose.position.x"].max()
        y_min, y_max = self.df["pose.position.y"].min(), self.df["pose.position.y"].max()
        z_min, z_max = self.df["pose.position.z"].min(), self.df["pose.position.z"].max()

        x_mid, y_mid, z_mid = (x_max + x_min) / 2, (y_max + y_min) / 2, (z_max + z_min) / 2
        max_range = max(x_max - x_min, y_max - y_min, z_max - z_min) / 2

        self.axis_limits = {
            "x": (x_mid - max_range, x_mid + max_range),
            "y": (y_mid - max_range, y_mid + max_range),
            "z": (z_mid - max_range, z_mid + max_range),
        }

    def _setup_plot(self):
        """Sets up the 3D Matplotlib figure and axis."""
        self.fig = plt.figure(figsize=self.figsize)
        self.ax = self.fig.add_subplot(111, projection="3d")

        # Apply equal axis limits
        self.ax.set_xlim(self.axis_limits["x"])
        self.ax.set_ylim(self.axis_limits["y"])
        self.ax.set_zlim(self.axis_limits["z"])

        # Set camera perspective
        self.ax.view_init(elev=self.elev, azim=self.azim)

        # Format labels & ticks
        self.ax.set_xlabel("X", labelpad=15)
        self.ax.set_ylabel("Y", labelpad=15)
        self.ax.set_zlabel("Z", labelpad=15)
        self.ax.tick_params(labelsize=8)
        self.ax.set_title("VICON Pose Animation", fontsize=12)

        # Initialize the plot objects (Keep them persistent)
        self.trajectory_x, self.trajectory_y, self.trajectory_z = [], [], []
        self.trajectory_line, = self.ax.plot([], [], [], color="b", label="Trajectory")
        self.current_point = self.ax.scatter([], [], [], color="r", s=50, label="Current Position")
        self.ax.legend(fontsize=10)

    def _update(self, frame):
        """Animation update function."""
        if not self.data_queue.empty():
            row = self.data_queue.get()
            x, y, z = row["pose.position.x"], row["pose.position.y"], row["pose.position.z"]

            # Append to trajectory
            self.trajectory_x.append(x)
            self.trajectory_y.append(y)
            self.trajectory_z.append(z)

            # Update trajectory line
            self.trajectory_line.set_data(self.trajectory_x, self.trajectory_y)
            self.trajectory_line.set_3d_properties(self.trajectory_z)

            # Update current position marker
            self.current_point._offsets3d = (np.array([x]), np.array([y]), np.array([z]))

            self.ax.set_title(f"VICON Pose Animation - Frame {frame}")

        return self.trajectory_line, self.current_point

    def run(self):
        """Runs the animation and displays it in the Jupyter Notebook."""
        ani = FuncAnimation(self.fig, self._update, frames=self.total_timesteps, interval=self.interval, blit=True)
        return HTML(ani.to_html5_video())



from queue import Queue
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML
from matplotlib import rc

# Enable HTML5 animation
rc("animation", html="html5")

class MultiViconPoseAnimator:
    def __init__(self, dfs, labels=None, max_size_mb=3, figsize=(8, 8), dpi=100, elev=20, azim=30, interval=20):
        """
        Initializes the multi-dataset VICON Pose Animator.

        Args:
            dfs (list of pd.DataFrame): List of dataframes containing VICON pose data.
            labels (list of str, optional): Labels for each trajectory. Defaults to None.
            max_size_mb (int, optional): Max memory size for animation. Defaults to 3MB.
            figsize (tuple, optional): Size of the figure in inches. Defaults to (8,8).
            dpi (int, optional): Dots per inch for rendering. Defaults to 100.
            elev (int, optional): Elevation angle for 3D view. Defaults to 20.
            azim (int, optional): Azimuth angle for 3D view. Defaults to 30.
            interval (int, optional): Interval between frames in milliseconds. Defaults to 20ms.
        """
        self.dfs = dfs
        self.labels = labels if labels else [f"Trajectory {i}" for i in range(len(dfs))]
        self.max_size_mb = max_size_mb
        self.figsize = figsize
        self.dpi = dpi
        self.elev = elev
        self.azim = azim
        self.anim = None
        self.interval = interval

        # Compute frame skipping factor per dataframe
        self.frame_skips = [self._compute_frame_skip(df) for df in dfs]
        self.dfs = [df.iloc[::skip] for df, skip in zip(dfs, self.frame_skips)]
        self.total_timesteps = max(len(df) for df in self.dfs)

        # Compute axis limits
        self._compute_axis_limits()

        # Setup Matplotlib figure and axis
        self._setup_plot()

        # Initialize queues and plotting elements
        self.data_queues = [Queue() for _ in self.dfs]
        for i, df in enumerate(self.dfs):
            for _, row in df.iterrows():
                self.data_queues[i].put(row)

    def _compute_frame_skip(self, df):
        """Calculates the number of frames to skip to fit within memory limit."""
        total_timesteps = len(df)

        # Estimate per-frame memory usage
        byte_per_frame = (self.dpi * (self.figsize[0] * self.figsize[1])) * 4  # 4 bytes per pixel (RGBA)
        max_frames = int((self.max_size_mb * 1024**2) / byte_per_frame)

        frame_skip = max(1, total_timesteps // max_frames)
        print(f"Max frames allowed: {max_frames}, Frame skipping factor: {frame_skip}")
        return frame_skip

    def _compute_axis_limits(self):
        """Computes equal axis limits for consistent visualization across datasets."""
        x_min = min(df["pose.position.x"].min() for df in self.dfs)
        x_max = max(df["pose.position.x"].max() for df in self.dfs)
        y_min = min(df["pose.position.y"].min() for df in self.dfs)
        y_max = max(df["pose.position.y"].max() for df in self.dfs)
        z_min = min(df["pose.position.z"].min() for df in self.dfs)
        z_max = max(df["pose.position.z"].max() for df in self.dfs)

        x_mid, y_mid, z_mid = (x_max + x_min) / 2, (y_max + y_min) / 2, (z_max + z_min) / 2
        max_range = max(x_max - x_min, y_max - y_min, z_max - z_min) / 2

        self.axis_limits = {
            "x": (x_mid - max_range, x_mid + max_range),
            "y": (y_mid - max_range, y_mid + max_range),
            "z": (z_mid - max_range, z_mid + max_range),
        }

    def _setup_plot(self):
        """Sets up the 3D Matplotlib figure and axis."""
        self.fig = plt.figure(figsize=self.figsize)
        self.ax = self.fig.add_subplot(111, projection="3d")

        # Apply equal axis limits
        self.ax.set_xlim(self.axis_limits["x"])
        self.ax.set_ylim(self.axis_limits["y"])
        self.ax.set_zlim(self.axis_limits["z"])

        # Set camera perspective
        self.ax.view_init(elev=self.elev, azim=self.azim)

        # Format labels & ticks
        self.ax.set_xlabel("X", labelpad=15)
        self.ax.set_ylabel("Y", labelpad=15)
        self.ax.set_zlabel("Z", labelpad=15)
        self.ax.tick_params(labelsize=8)
        self.ax.set_title("VICON Pose Animation", fontsize=12)

        # Initialize the plot objects for multiple datasets
        colors = ["b", "g", "r", "c", "m", "y"]  # Cycle colors
        self.trajectories = []
        self.points = []
        self.trajectory_data = [[] for _ in self.dfs]

        for i in range(len(self.dfs)):
            color = colors[i % len(colors)]
            trajectory_line, = self.ax.plot([], [], [], color=color, label=self.labels[i])
            current_point = self.ax.scatter([], [], [], color=color, s=50)
            self.trajectories.append(trajectory_line)
            self.points.append(current_point)

        self.ax.legend(fontsize=10)

    def _update(self, frame):
        """Animation update function for multiple datasets."""
        for i, queue in enumerate(self.data_queues):
            if not queue.empty():
                row = queue.get()
                x, y, z = row["pose.position.x"], row["pose.position.y"], row["pose.position.z"]

                # Append to trajectory data
                self.trajectory_data[i].append((x, y, z))

                # Convert trajectory data to arrays
                xs, ys, zs = zip(*self.trajectory_data[i])

                # Update trajectory line
                self.trajectories[i].set_data(xs, ys)
                self.trajectories[i].set_3d_properties(zs)

                # Update current position marker
                self.points[i]._offsets3d = (np.array([x]), np.array([y]), np.array([z]))

        self.ax.set_title(f"VICON Pose Animation - Frame {frame}")
        return self.trajectories + self.points

    def run(self):
        """Runs the animation and displays it in the Jupyter Notebook."""
        ani = FuncAnimation(self.fig, self._update, frames=self.total_timesteps, interval=self.interval, blit=True)
        self.anim = ani
        return HTML(ani.to_html5_video())



from queue import Queue
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML
from matplotlib import rc

# Enable HTML5 animation
rc("animation", html="html5")

    # class MultiViconPoseTwistAnimator:
    #     def __init__(self, pose_dfs, twist_dfs=None, labels=None, max_size_mb=3, figsize=(8, 8), dpi=100, elev=20, azim=30, interval=20):
    #         """
    #         Initializes the multi-dataset VICON Pose & Twist Animator.

    #         Args:
    #             pose_dfs (list of pd.DataFrame): List of dataframes containing VICON pose data.
    #             twist_dfs (list of pd.DataFrame, optional): List of dataframes containing TwistStamped data.
    #             labels (list of str, optional): Labels for each trajectory. Defaults to None.
    #             max_size_mb (int, optional): Max memory size for animation. Defaults to 3MB.
    #             figsize (tuple, optional): Size of the figure in inches. Defaults to (8,8).
    #             dpi (int, optional): Dots per inch for rendering. Defaults to 100.
    #             elev (int, optional): Elevation angle for 3D view. Defaults to 20.
    #             azim (int, optional): Azimuth angle for 3D view. Defaults to 30.
    #             interval (int, optional): Interval between frames in milliseconds. Defaults to 20ms.
    #         """
    #         self.pose_dfs = pose_dfs
    #         self.twist_dfs = twist_dfs if twist_dfs else [None] * len(pose_dfs)
    #         self.labels = labels if labels else [f"Trajectory {i}" for i in range(len(pose_dfs))]
    #         self.max_size_mb = max_size_mb
    #         self.figsize = figsize
    #         self.dpi = dpi
    #         self.elev = elev
    #         self.azim = azim
    #         self.interval = interval

    #         # Compute frame skipping factor per dataframe
    #         self.frame_skips = [self._compute_frame_skip(df) for df in pose_dfs]
    #         self.pose_dfs = [df.iloc[::skip] for df, skip in zip(pose_dfs, self.frame_skips)]
    #         self.total_timesteps = max(len(df) for df in self.pose_dfs)

    #         # Compute axis limits
    #         self._compute_axis_limits()

    #         # Setup Matplotlib figure and axis
    #         self._setup_plot()

    #         # Initialize queues and plotting elements
    #         self.pose_queues = [Queue() for _ in self.pose_dfs]
    #         self.twist_queues = [Queue() for _ in self.pose_dfs]

    #         for i, df in enumerate(self.pose_dfs):
    #             for _, row in df.iterrows():
    #                 self.pose_queues[i].put(row)

    #         for i, df in enumerate(self.twist_dfs):
    #             if df is not None:
    #                 for _, row in df.iterrows():
    #                     self.twist_queues[i].put(row)

    #     def _compute_frame_skip(self, df):
    #         """Calculates the number of frames to skip to fit within memory limit."""
    #         total_timesteps = len(df)

    #         # Estimate per-frame memory usage
    #         byte_per_frame = (self.dpi * (self.figsize[0] * self.figsize[1])) * 4  # 4 bytes per pixel (RGBA)
    #         max_frames = int((self.max_size_mb * 1024**2) / byte_per_frame)

    #         frame_skip = max(1, total_timesteps // max_frames)
    #         print(f"Max frames allowed: {max_frames}, Frame skipping factor: {frame_skip}")
    #         return frame_skip

    #     def _compute_axis_limits(self):
    #         """Computes equal axis limits for consistent visualization across datasets."""
    #         x_min = min(df["pose.position.x"].min() for df in self.pose_dfs)
    #         x_max = max(df["pose.position.x"].max() for df in self.pose_dfs)
    #         y_min = min(df["pose.position.y"].min() for df in self.pose_dfs)
    #         y_max = max(df["pose.position.y"].max() for df in self.pose_dfs)
    #         z_min = min(df["pose.position.z"].min() for df in self.pose_dfs)
    #         z_max = max(df["pose.position.z"].max() for df in self.pose_dfs)

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
    #         self.ax.set_title("VICON Pose & Twist Animation", fontsize=12)

    #         # Initialize the plot objects for multiple datasets
    #         colors = ["b", "g", "r", "c", "m", "y"]  # Cycle colors
    #         self.trajectories = []
    #         self.points = []
    #         self.vectors = []
    #         self.trajectory_data = [[] for _ in self.pose_dfs]

    #         for i in range(len(self.pose_dfs)):
    #             color = colors[i % len(colors)]
    #             trajectory_line, = self.ax.plot([], [], [], color=color, label=self.labels[i])
    #             current_point = self.ax.scatter([], [], [], color=color, s=50)
    #             velocity_vector = self.ax.quiver([], [], [], [], [], [], color=color, length=5)

    #             self.trajectories.append(trajectory_line)
    #             self.points.append(current_point)
    #             self.vectors.append(velocity_vector)

    #         self.ax.legend(fontsize=10)

    #     def _update(self, frame):
    #         """Animation update function for multiple datasets."""
    #         for i, pose_queue in enumerate(self.pose_queues):
    #             if not pose_queue.empty():
    #                 row = pose_queue.get()
    #                 x, y, z = row["pose.position.x"], row["pose.position.y"], row["pose.position.z"]

    #                 # Append to trajectory data
    #                 self.trajectory_data[i].append((x, y, z))

    #                 # Convert trajectory data to arrays
    #                 xs, ys, zs = zip(*self.trajectory_data[i])

    #                 # Update trajectory line
    #                 self.trajectories[i].set_data(xs, ys)
    #                 self.trajectories[i].set_3d_properties(zs)

    #                 # Update current position marker
    #                 self.points[i]._offsets3d = (np.array([x]), np.array([y]), np.array([z]))

    #                 # Update velocity vector (if twist data is available)
    #                 if not self.twist_queues[i].empty():
    #                     twist_row = self.twist_queues[i].get()
    #                     vx, vy, vz = twist_row["twist.linear.x"], twist_row["twist.linear.y"], twist_row["twist.linear.z"]
    #                     self.vectors[i].remove()
    #                     self.vectors[i] = self.ax.quiver(x, y, z, vx, vy, vz, color=self.points[i].get_facecolors()[0], length=0.5)

    #         self.ax.set_title(f"VICON Pose & Twist Animation - Frame {frame}")
    #         return self.trajectories + self.points + self.vectors

    #     def run(self):
    #         """Runs the animation and displays it in the Jupyter Notebook."""
    #         ani = FuncAnimation(self.fig, self._update, frames=self.total_timesteps, interval=self.interval, blit=False)
    #         return HTML(ani.to_html5_video())




import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from queue import Queue
from IPython.display import HTML
from matplotlib import rc

# Enable HTML5 animation
rc("animation", html="html5")

class MultiViconPoseTwistAnimator:
    def __init__(self, pose_dfs, twist_dfs=None, labels=None, max_size_mb=3, figsize=(8, 8), dpi=100, elev=20, azim=30, interval=20):
        self.pose_dfs = pose_dfs
        self.twist_dfs = twist_dfs if twist_dfs else [None] * len(pose_dfs)
        self.labels = labels if labels else [f"Trajectory {i}" for i in range(len(pose_dfs))]
        self.max_size_mb = max_size_mb
        self.figsize = figsize
        self.dpi = dpi
        self.elev = elev
        self.azim = azim
        self.anim = None
        self.interval = interval

        self.frame_skips = [self._compute_frame_skip(df) for df in pose_dfs]
        self.pose_dfs = [df.iloc[::skip] for df, skip in zip(pose_dfs, self.frame_skips)]
        self.total_timesteps = max(len(df) for df in self.pose_dfs)

        self._compute_axis_limits()
        self._setup_plot()

        self.pose_queues = [Queue() for _ in self.pose_dfs]
        self.twist_queues = [Queue() for _ in self.pose_dfs]

        for i, df in enumerate(self.pose_dfs):
            for _, row in df.iterrows():
                self.pose_queues[i].put(row)

        for i, df in enumerate(self.twist_dfs):
            if df is not None:
                for _, row in df.iterrows():
                    self.twist_queues[i].put(row)

    def _compute_frame_skip(self, df):
        total_timesteps = len(df)
        byte_per_frame = (self.dpi * (self.figsize[0] * self.figsize[1])) * 4  
        max_frames = int((self.max_size_mb * 1024**2) / byte_per_frame)

        return max(1, total_timesteps // max_frames)

    def _compute_axis_limits(self):
        x_min = min(df["pose.position.x"].min() for df in self.pose_dfs)
        x_max = max(df["pose.position.x"].max() for df in self.pose_dfs)
        y_min = min(df["pose.position.y"].min() for df in self.pose_dfs)
        y_max = max(df["pose.position.y"].max() for df in self.pose_dfs)
        z_min = min(df["pose.position.z"].min() for df in self.pose_dfs)
        z_max = max(df["pose.position.z"].max() for df in self.pose_dfs)

        x_mid, y_mid, z_mid = (x_max + x_min) / 2, (y_max + y_min) / 2, (z_max + z_min) / 2
        max_range = max(x_max - x_min, y_max - y_min, z_max - z_min) / 2

        self.axis_limits = {
            "x": (x_mid - max_range, x_mid + max_range),
            "y": (y_mid - max_range, y_mid + max_range),
            "z": (z_mid - max_range, z_mid + max_range),
        }

    def _setup_plot(self):
        self.fig = plt.figure(figsize=self.figsize)
        self.ax = self.fig.add_subplot(111, projection="3d")

        self.ax.set_xlim(self.axis_limits["x"])
        self.ax.set_ylim(self.axis_limits["y"])
        self.ax.set_zlim(self.axis_limits["z"])
        self.ax.view_init(elev=self.elev, azim=self.azim)

        self.ax.set_xlabel("X", labelpad=15)
        self.ax.set_ylabel("Y", labelpad=15)
        self.ax.set_zlabel("Z", labelpad=15)
        self.ax.set_title("VICON Pose & Twist Animation", fontsize=12)

        colors = ["b", "g", "r", "c", "m", "y"]  
        self.trajectories = []
        self.points = []
        self.vectors = []
        self.trajectory_data = [[] for _ in self.pose_dfs]

        for i in range(len(self.pose_dfs)):
            color = colors[i % len(colors)]
            trajectory_line, = self.ax.plot([], [], [], color=color, label=self.labels[i])
            current_point = self.ax.scatter([], [], [], color=color, s=50)
            velocity_vector = self.ax.quiver([], [], [], [], [], [], color=color, length=1.0)

            self.trajectories.append(trajectory_line)
            self.points.append(current_point)
            self.vectors.append(velocity_vector)

        self.ax.legend(fontsize=10)

    def _update(self, frame):
        """Animation update function."""
        for i, pose_queue in enumerate(self.pose_queues):
            if not pose_queue.empty():
                row = pose_queue.get()
                x, y, z = row["pose.position.x"], row["pose.position.y"], row["pose.position.z"]
                pose_time = row.name  # Timestamp index

                self.trajectory_data[i].append((x, y, z))
                xs, ys, zs = zip(*self.trajectory_data[i])

                self.trajectories[i].set_data(xs, ys)
                self.trajectories[i].set_3d_properties(zs)
                self.points[i]._offsets3d = (np.array([x]), np.array([y]), np.array([z]))

                if not self.twist_queues[i].empty():
                    twist_df = self.twist_dfs[i]
                    
                    # Find the closest twist timestamp
                    closest_idx = twist_df.index.get_indexer([pose_time], method="nearest")[0]
                    twist_row = twist_df.iloc[closest_idx]

                    vx, vy, vz = twist_row["twist.linear.x"], twist_row["twist.linear.y"], twist_row["twist.linear.z"]

                    # Normalize and scale twist vectors for visibility
                    scale_factor = 2.0  # Adjust for larger arrows
                    magnitude = np.linalg.norm([vx, vy, vz])
                    if magnitude > 0:
                        vx, vy, vz = [scale_factor * v / magnitude for v in [vx, vy, vz]]

                    self.vectors[i].remove()
                    self.vectors[i] = self.ax.quiver(
                        x, y, z, vx, vy, vz, color=self.points[i].get_facecolors()[0], length=magnitude, arrow_length_ratio=0.3
                    )

        self.ax.set_title(f"VICON Pose & Twist Animation - Frame {frame}")
        return self.trajectories + self.points + self.vectors

    def run(self):
        """Runs the animation and displays it in the Jupyter Notebook."""
        ani = FuncAnimation(self.fig, self._update, frames=self.total_timesteps, interval=self.interval, blit=False)
        self.anim = ani
        return HTML(ani.to_html5_video())
