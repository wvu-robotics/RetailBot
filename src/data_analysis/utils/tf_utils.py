import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, TwistStamped
from tf2_ros import TransformBroadcaster, StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped
import time


class TF2Publisher(Node):
    def __init__(self):
        super().__init__("tf2_publisher")
        self.tf_broadcaster = TransformBroadcaster(self)
        self.static_tf_broadcaster = StaticTransformBroadcaster(self)
        self.pose_pubber = self.create_publisher(PoseStamped, "test_pose",10)

    def send_tf(self, xform):
        """Just send the transform as is using the nodes broadcaster."""
        self.tf_broadcaster.sendTransform(xform)
        rclpy.spin_once(self, timeout_sec=0.2)

    def send_static_tf(self, xform):
        """Just send the transform as is using the nodes broadcaster."""
        self.static_tf_broadcaster.sendTransform(xform)
        rclpy.spin_once(self, timeout_sec=0.2)
        
    def send_pose_stamped(self, pose_stamped: PoseStamped):
        self.pose_pubber.publish(pose_stamped)


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


def publish_pose_stamped(poses:list[PoseStamped]):
    try_init()
    node = TF2Publisher()

    try:
        for pose_stamped in poses:
            node.send_pose_stamped(pose_stamped)
            time.sleep(0.1)  # Give time for Rviz to receive messages
    finally:
        node.destroy_node()
        rclpy.shutdown()


