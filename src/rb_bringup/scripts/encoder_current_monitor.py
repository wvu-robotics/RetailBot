import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
import numpy as np
from collections import deque
from control_msgs.msg import DynamicJointState
from geometry_msgs.msg import PoseStamped, AccelStamped  # Import AccelStamped
from rclpy.time import Time


class EncoderCurrentMonitor(Node):
    def __init__(self):
        super().__init__('encoder_current_monitor')

        # Subscribe to Dynamic Joint States
        self.subscription_dynamic_joint = self.create_subscription(
            DynamicJointState,
            '/dynamic_joint_states',
            self.callback_dynamic_joint,
            QoSProfile(depth=10, reliability=QoSReliabilityPolicy.BEST_EFFORT)
        )
        self.get_logger().info("Subscribed to /dynamic_joint_states")

        # Subscribe to Pose Data
        self.subscription_pose = self.create_subscription(
            PoseStamped,
            '/vrpn_mocap/rb1/pose',
            self.callback_pose,
            QoSProfile(depth=10, reliability=QoSReliabilityPolicy.BEST_EFFORT)
        )
        self.get_logger().info("Subscribed to /vrpn_mocap/rb1/pose")

        # Subscribe to Acceleration Data
        self.subscription_accel = self.create_subscription(
            AccelStamped,
            '/vrpn_mocap/rb1/accel',
            self.callback_accel,
            QoSProfile(depth=10, reliability=QoSReliabilityPolicy.BEST_EFFORT)
        )
        self.get_logger().info("Subscribed to /vrpn_mocap/rb1/accel")

        # Data storage buffers (for last 1000 values)
        self.encoder_counts = {joint: deque(maxlen=1000) for joint in ["fr_wheel_joint", "br_wheel_joint", "fl_wheel_joint", "bl_wheel_joint"]}
        self.currents = {joint: deque(maxlen=1000) for joint in ["fr_wheel_joint", "br_wheel_joint", "fl_wheel_joint", "bl_wheel_joint"]}
        self.pose_data = deque(maxlen=1000)
        self.accel_data = {axis: deque(maxlen=1000) for axis in ["x", "y", "z"]}  # Stores acceleration values

        self.timer = self.create_timer(1.0, self.compute_statistics)

    def callback_dynamic_joint(self, msg):
        """ Parse encoder_count and current values and store them in buffers """
        for i, joint_name in enumerate(msg.joint_names):
            if i >= len(msg.interface_values):
                continue

            joint = msg.interface_values[i]
            if "encoder_count" in joint.interface_names and "current" in joint.interface_names:
                encoder_idx = joint.interface_names.index("encoder_count")
                current_idx = joint.interface_names.index("current")

                encoder_value = joint.values[encoder_idx]
                current_value = joint.values[current_idx]

                self.encoder_counts[joint_name].append(encoder_value)
                self.currents[joint_name].append(current_value)

    def callback_pose(self, msg):
        """ Store x-position from PoseStamped messages """
        position_x = msg.pose.position.x
        self.pose_data.append(position_x)

    def callback_accel(self, msg):
        """ Store acceleration values (linear x, y, z) from AccelStamped messages """
        self.accel_data["x"].append(msg.accel.linear.x)
        self.accel_data["y"].append(msg.accel.linear.y)
        self.accel_data["z"].append(msg.accel.linear.z)

    def compute_statistics(self):
        output = "\n==== Encoder Count & Current Statistics ====\n"
        for joint_name in self.encoder_counts.keys():
            if len(self.encoder_counts[joint_name]) > 1:
                enc_vals = np.array(self.encoder_counts[joint_name])
                cur_vals = np.array(self.currents[joint_name])

                enc_mean = np.mean(enc_vals)
                enc_var = np.var(enc_vals)
                cur_mean = np.mean(cur_vals)
                cur_var = np.var(cur_vals)

                output += (
                    f"Joint: {joint_name}\n"
                    f"  Encoder Count - Mean: {enc_mean:.3f}, Variance: {enc_var:.3f}\n"
                    f"  Current - Mean: {cur_mean:.3f}, Variance: {cur_var:.3f}\n"
                )

        # Pose data statistics
        if len(self.pose_data) > 1:
            pose_vals = np.array(self.pose_data)
            pose_mean = np.mean(pose_vals)
            pose_var = np.var(pose_vals)

            output += (
                f"\n==== Pose Data (X Position) Statistics ====\n"
                f"  X Position - Mean: {pose_mean:.3f}, Variance: {pose_var:.3f}\n"
            )

        # Acceleration statistics
        if len(self.accel_data["x"]) > 1:
            accel_x_vals = np.array(self.accel_data["x"])
            accel_y_vals = np.array(self.accel_data["y"])
            accel_z_vals = np.array(self.accel_data["z"])

            accel_x_mean = np.mean(accel_x_vals)
            accel_x_var = np.var(accel_x_vals)
            accel_y_mean = np.mean(accel_y_vals)
            accel_y_var = np.var(accel_y_vals)
            accel_z_mean = np.mean(accel_z_vals)
            accel_z_var = np.var(accel_z_vals)

            output += (
                f"\n==== Acceleration Data Statistics ====\n"
                f"  Linear X - Mean: {accel_x_mean:.3f}, Variance: {accel_x_var:.3f}\n"
                f"  Linear Y - Mean: {accel_y_mean:.3f}, Variance: {accel_y_var:.3f}\n"
                f"  Linear Z - Mean: {accel_z_mean:.3f}, Variance: {accel_z_var:.3f}\n"
            )

        # Log output
        self.get_logger().info(output)


def main(args=None):
    rclpy.init(args=args)
    node = EncoderCurrentMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()