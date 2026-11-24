#!/usr/bin/python3
import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster, StaticTransformBroadcaster, Buffer, TransformListener
from geometry_msgs.msg import TransformStamped, PoseStamped, Pose
from scipy.spatial.transform import Rotation as R
import numpy as np
from rclpy.qos import QoSReliabilityPolicy, QoSProfile

GREEN = "\033[92m"
RESET = "\033[0m"

class ViconTFBroadcaster(Node):
    """
    Run only once and set up the vicon->odom static transform. Robot should be
    stationary!
    """
    def __init__(self):
        super().__init__('vicon_tf_broadcaster')
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.static_br = StaticTransformBroadcaster(self)
        self.br = TransformBroadcaster(self)

        self.initial_vicon_transform = False

        # Subscribe to the Vicon position topic
        self.subscription = self.create_subscription(
            PoseStamped,                  # Custom message type
            '/vrpn_mocap/rb1/pose',               # Topic name
            self.vicon_callback,       # Callback function
            QoSProfile(reliability=QoSReliabilityPolicy.BEST_EFFORT, depth = 10)
        )

    def vicon_callback(self, msg: PoseStamped):
        quat = [msg.pose.orientation.x, msg.pose.orientation.y, msg.pose.orientation.z, msg.pose.orientation.w]
        # TODO Make this just check for norm=1 instead.
        if np.linalg.norm(quat) == 0:
            self.get_logger().error("Received zero norm quaternion, skipping this transform.")
            return

        # Set up our initial vicon->odom xform.
        if self.initial_vicon_transform is False:
            print("Running callback!")
            #self.initial_position = (x_trans, y_trans, z_trans)
            #self.initial_rotation = R.from_quat([msg.x_rot, msg.y_rot, msg.z_rot, msg.w])

            # Turn Pose message into a transform object.
            self.initial_vicon_transform = TransformStamped()
            self.initial_vicon_transform.header.stamp = self.get_clock().now().to_msg()
            self.initial_vicon_transform.header.frame_id = 'vicon'  
            self.initial_vicon_transform.child_frame_id = 'odom'  
            self.initial_vicon_transform.transform.translation.x = msg.pose.position.x
            self.initial_vicon_transform.transform.translation.y = msg.pose.position.y
            self.initial_vicon_transform.transform.translation.z = msg.pose.position.z
            self.initial_vicon_transform.transform.rotation.x = msg.pose.orientation.x
            self.initial_vicon_transform.transform.rotation.y =msg.pose.orientation.y
            self.initial_vicon_transform.transform.rotation.z =msg.pose.orientation.z
            self.initial_vicon_transform.transform.rotation.w = msg.pose.orientation.w

            # Send the xform as a static xform.
            self.static_br.sendTransform(self.initial_vicon_transform)
            self.initial_vicon_transform = True
            self.get_logger().info(f"{GREEN}Vicon to odom transform set! {self.initial_vicon_transform}{RESET}")


def main(args=None):
    rclpy.init(args=args)
    node = ViconTFBroadcaster()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
