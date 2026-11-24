#!/usr/bin/env python3

import math

import rclpy
from geometry_msgs.msg import (
    Point,
    PoseStamped,  # Assuming VRPN publishes PoseStamped messages
    Twist,
)
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy

from twist_slip_msg.msg import TwistSlipStamped


class WaypointFollower(Node):
    def __init__(self):
        # Initialize the ROS 2 node
        super().__init__("waypoint_follower")

        # Publisher to send velocity commands to the robot
        self.cmd_vel_pub = self.create_publisher(
            TwistSlipStamped, "rb_slip_controller/cmd_vel", 10
        )
        # 'diff_drive_controller/cmd_vel', 10)

        # Subscriber to the VRPN topic for robot position
        self.vrpn_sub = self.create_subscription(
            PoseStamped,
            "/vrpn_mocap/rb1/pose",
            self.vrpn_callback,
            QoSProfile(reliability=QoSReliabilityPolicy.BEST_EFFORT, depth=10),
        )

        # List of waypoints (x, y) in order
        self.waypoints = [(0.5, 0.5), (0.5, -0.5), (-0.5, -0.5), (-0.5, 0.5), (0.0, 0.0)]
        self.current_waypoint_index = 0

        # Proportional gain for the controller
        self.kp = 0.1

        # Threshold distance to consider a waypoint reached
        self.distance_threshold = 0.2

        # Initialize the Twist message
        self.twist_msg = TwistSlipStamped()

        # Current robot position
        self.current_position = Point()

    def vrpn_callback(self, msg):
        # Update the current robot position from VRPN data
        self.current_position = msg.pose.position

        # Check if the robot has reached the current waypoint
        if self.reached_waypoint():
            self.get_logger().info(
                f"Reached waypoint: {self.waypoints[self.current_waypoint_index]}"
            )
            self.current_waypoint_index += 1

            # Stop the robot if all waypoints are reached
            if self.current_waypoint_index >= len(self.waypoints):
                self.get_logger().info("All waypoints reached. Stopping the robot.")
                self.twist_msg.twist.linear.x = 0.0
                self.twist_msg.twist.angular.z = 0.0
                self.cmd_vel_pub.publish(self.twist_msg)
                return

        # Move the robot toward the current waypoint
        self.move_to_waypoint()

    def reached_waypoint(self):
        # Calculate the distance to the current waypoint
        target_x, target_y = self.waypoints[self.current_waypoint_index]
        distance = math.sqrt(
            (target_x - self.current_position.x) ** 2 + (target_y - self.current_position.y) ** 2
        )

        # Check if the distance is below the threshold
        return distance < self.distance_threshold

    def move_to_waypoint(self):
        # Get the current waypoint
        target_x, target_y = self.waypoints[self.current_waypoint_index]

        # Calculate the error in x and y
        error_x = target_x - self.current_position.x
        error_y = target_y - self.current_position.y

        # Calculate the angle to the waypoint
        angle_to_waypoint = math.atan2(error_y, error_x)

        self.get_logger().info(f"{angle_to_waypoint=}")

        # Calculate the distance to the waypoint
        distance_to_waypoint = math.sqrt(error_x**2 + error_y**2)

        # Proportional control for linear and angular velocity
        self.twist_msg.twist.linear.x = self.kp * distance_to_waypoint * 0
        self.twist_msg.twist.angular.z = self.kp * 100 * angle_to_waypoint

        # Publish the Twist message
        self.cmd_vel_pub.publish(self.twist_msg)
        self.get_logger().info(
            f"Moving to waypoint: {self.waypoints[self.current_waypoint_index]}"
        )


def main(args=None):
    # Initialize the ROS 2 Python client library
    rclpy.init(args=args)

    # Create an instance of the WaypointFollower node
    waypoint_follower = WaypointFollower()

    # Keep the node running
    rclpy.spin(waypoint_follower)

    # Destroy the node explicitly when done
    waypoint_follower.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
