#!/usr/bin/env python3

import os
import sys
import math
import subprocess
import traceback
import signal
import numpy as np
import threading
import queue
import time
from multiprocessing import Queue, Process
import matplotlib.pyplot as plt
from rclpy.executors import MultiThreadedExecutor

from geometry_msgs.msg import Twist, TwistStamped
from twist_slip_msg.msg import TwistSlipStamped

import rclpy
from rclpy.node import Node
from rclpy.time import Time
from std_msgs.msg import String, Float64MultiArray, Float32MultiArray
from builtin_interfaces.msg import Duration


class TwistToTwistSlipStamped(Node):
    def __init__(self,twist_topic, twist_slip_stamped_topic):
        super().__init__('twist_to_twist_slip_stamped')

        # Declare parameters to allow overrides via launch files
        self.declare_parameter('twist_topic', twist_topic)
        self.declare_parameter('twist_slip_stamped_topic', twist_slip_stamped_topic)
        self.twist_topic = self.get_parameter('twist_topic').get_parameter_value().string_value
        self.twist_slip_stamped_topic = self.get_parameter('twist_slip_stamped_topic').get_parameter_value().string_value


        # Subscribe to the normal cmd_vel topic.
        self.twist_subber = self.create_subscription(TwistStamped, twist_topic, 
                                 self.twist_callback,
                                 10)
        self.twist_slip_pubber = self.create_publisher(TwistSlipStamped,
                              twist_slip_stamped_topic,
                              10)


    def twist_callback(self, msg):
        slip_msg = TwistSlipStamped()
        slip_msg.header = msg.header
        slip_msg.twist = msg.twist
        self.twist_slip_pubber.publish(slip_msg)


def main(args=None):
    rclpy.init(args=args)

     # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Convert Twist to TwistSlipStamped")
    parser.add_argument("--twist_topic", type=str, default="/rb/cmd_vel", help="Input Twist topic")
    parser.add_argument("--twist_slip_stamped_topic", type=str, default="/rb_slip_controller/cmd_vel", help="Output TwistSlipStamped topic")
    parsed_args, _ = parser.parse_known_args()  # Ignore unrecognized ROS args

    executor = MultiThreadedExecutor()
    node = TwistToTwistSlipStamped(parsed_args.twist_topic, parsed_args.twist_slip_stamped_topic)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
