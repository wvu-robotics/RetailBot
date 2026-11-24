#!/bin/python3

import rclpy
import time
from rclpy.node import Node
from tf2_ros import TransformBroadcaster, StaticTransformBroadcaster, Buffer, TransformListener
import tf2_geometry_msgs
from tf2_geometry_msgs import do_transform_pose
from geometry_msgs.msg import TransformStamped, PoseStamped, Pose
from tf_transformations import quaternion_from_euler
from rclpy.qos import QoSReliabilityPolicy, QoSProfile
from nav_msgs.msg import Odometry
from scipy.spatial.transform import Rotation as R
# import numpy as np

class ViconOdomPubber(Node):
    """
    Uses the vicon-odom static xform to publish the odom message in the
    vicon frame.
    """
    def __init__(self):
        super().__init__('vicon_odom_pubber')
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.static_br = StaticTransformBroadcaster(self)
        self.br = TransformBroadcaster(self)

        self.odom_in_vicon_pubber = self.create_publisher(PoseStamped, "/odom_in_vicon_frame",
                                                   QoSProfile(reliability=QoSReliabilityPolicy.BEST_EFFORT, depth = 10)
                                                   )

        # Subscribe to the Vicon Pose topic.
        self.vicon_subber = self.create_subscription(
            Odometry,
            '/rb_slip_controller/odom',
            self.odom_callback,
            QoSProfile(reliability=QoSReliabilityPolicy.BEST_EFFORT, depth = 10)
        )

    def odom_callback(self, msg: Odometry):
        # Republish odometry message in vicon frame.
        # pose = msg.pose
        try:
            odom_to_vicon = self.tf_buffer.lookup_transform('vicon', 'odom', rclpy.time.Time())
        except Exception as e:
            self.get_logger().error(f"Waiting for transform: {e}")
            return

        odom_in_vicon = tf2_geometry_msgs.do_transform_pose_stamped(msg.pose, odom_to_vicon)
        self.odom_in_vicon_pubber.publish(odom_in_vicon)





def main(args=None):
    rclpy.init(args=args)
    node = ViconOdomPubber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
