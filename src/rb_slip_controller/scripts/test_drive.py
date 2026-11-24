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

import rclpy
from rclpy.node import Node
from rclpy.time import Time
from std_msgs.msg import String
from builtin_interfaces.msg import Duration
# from builtin_interfaces.msg import Time

from twist_slip_msg.msg import TwistSlipStamped
from geometry_msgs.msg import TwistStamped
# from sensor_msgs.msg import JointState
from control_msgs.msg import DynamicJointState

from plotting import plot_process
from utils import zero_twist


class DrivingNode(Node):
    def __init__(self, driver, queue):
        signal.signal(signal.SIGINT, self.handle_sigint) # Register the interrupt handler callback.
        super().__init__('driving_node')
        
        timer_period = 0.2  # seconds -> 100Hz.
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.publisher_ = self.create_publisher(TwistStamped, '/diff_drive_controller/cmd_vel', 10)
        self.joint_sub = self.create_subscription(
            DynamicJointState, '/dynamic_joint_states', self.sub_dynamic_joint_callback, 10)
        
        # This is the brain of our driving. We call its drive() method later.
        self.driver = driver(self.log, queue)
        
        # Keep copies of sensor data for controller.
        self.joint_state = None
        self.now = self.get_clock().now # Handy function handle to make later calls shorter.     
        self.reset_time()
     
    def handle_sigint(self,signal_num, frame):
        """
        This will catch when we interrupt the jupyter kernel. This is a weird case because it 
        doesn't actually send a normal interrupt? So we can't use a try except block. Don't need this
        for normal nodes, i.e not in jupyter.
        """
        print("Caught SIGINT. Cleaning up...")
        if rclpy.ok():
            rclpy.shutdown()
        self.destroy_node()
        sys.exit(0)
    
    def reset_time(self):
        self.start_time = self.now()
        
    def log(self, msg):
        self.get_logger().info(f'{msg}', throttle_duration_sec=1)
       
    def sub_dynamic_joint_callback(self, msg):
        self.joint_state = msg
        # Until first joint_state message is received reset time start time.
        if self.joint_state == None:
            self.reset_time()
#         print(self.joint_state)
            
    def timer_callback(self):
        if self.joint_state == None:
            self.log("Still waiting on joint data...")
            return
            
        current_time = self.get_clock().now()
        time_elapsed = (current_time - self.start_time)
        print(time_elapsed)
        # Drive the robot!
        # msg = self.driver.drive(self, time_elapsed, self.joint_state)
        print(self.get_clock().now().to_msg())
        msg = self.driver.drive(self.get_clock().now().to_msg(), time_elapsed, self.joint_state)
        self.publisher_.publish(msg)
        

def main(args=None):
    # Avoid variable not defined error in finally block.
    test_node = None

    queue = Queue()  # Create a multiprocessing queue
    # process = Process(target=plot_process, args=(queue,))
    # process.start()  # Start the plotting process

    try:
    # If ros2 context is not intialized do so now.
        if not rclpy.ok():
            rclpy.init(args=args)

        # Make our node.
        driving_node = DrivingNode(Driver, queue)
        rclpy.spin(driving_node)

    finally:
        # If code finishes before we interrupt then clean up ros2 context and our node object.
        if test_node:
            driving_node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    

class Driver:
    def __init__(self, log_func, queue):
        msg = TwistStamped()
        self.twist_slip_msg = zero_twist(msg)
        self.log = log_func # logging function of main node.
        self.stead_vel = 1 # m/s
        self.queue = queue
        
    # def unpack_dynamic_joint_state(self, msg):
    #     vels = [x.values[1] for x in msg.interface_values]
    #     return vels

        
    def drive(self, t, time_elapsed, joint_state: DynamicJointState):
        if joint_state == None:
            self.log("No joint data!")
            return self.twist_slip_msg # Zero out? Time out then zero out?
        
        # Get feedback.
        # self.log(f"velocities: {self.unpack_dynamic_joint_state(joint_state)}")
        
        # Send commands.
        # time = t.sec + t.nanosec /1e9
        # vel = np.sin(time)
        # self.queue.put((t.nanoseconds/1e9,vel))
        self.queue.put(joint_state)

        self.twist_slip_msg.header.stamp = t
        self.twist_slip_msg.header.frame_id = "base_link"

        rate = 5
        top_speed = 3
        vel = top_speed * (1 + math.tanh(rate * time_elapsed.nanoseconds/1e9))
        # print(f"vel type: {type(vel)}, value: {vel}")

        self.twist_slip_msg.twist.linear.x = -0.5

        # if time_elapsed.nanoseconds/1e9 > 10:
        #     self.twist_slip_msg.twist.linear.x = 0.0

        # self.twist_slip_msg.bl_wheel = -2.0
        # self.twist_slip_msg.br_wheel = -2.0
        # self.twist_slip_msg.fl_wheel = -2.0
        # self.twist_slip_msg.fr_wheel = -2.0

        
        # if time_elapsed.nanoseconds/1e9 > 5 and time_elapsed.nanoseconds/1e9 < 8:
        #     self.twist_slip_msg.bl_wheel = 0.0
        #     self.twist_slip_msg.br_wheel = 0.0
        #     self.twist_slip_msg.fl_wheel = 0.0
        #     self.twist_slip_msg.fr_wheel = 0.0

        # elif time_elapsed.nanoseconds/1e9 > 8:
        #     self.twist_slip_msg.bl_wheel = 0.0
        #     self.twist_slip_msg.br_wheel = 0.0
        #     self.twist_slip_msg.fl_wheel = 0.0
        #     self.twist_slip_msg.fr_wheel = 0.0


        # self.twist_slip_msg.bl_wheel = -5.0
        # self.twist_slip_msg.br_wheel = 5.0
        # self.twist_slip_msg.fl_wheel = -5.0
        # self.twist_slip_msg.fr_wheel = 5.0
        #
        #
        # if time_elapsed.nanoseconds/1e9 > 41:
        #     self.twist_slip_msg.bl_wheel = 0.0
        #     self.twist_slip_msg.br_wheel = 0.0
        #     self.twist_slip_msg.fl_wheel = 0.0
        #     self.twist_slip_msg.fr_wheel = 0.0

        # if(joint_state.header.stamp > 
        # if(time %2 < 0.5):
        # # if ((t.nanoseconds/1e9) % 2 < 0.5):
        #     self.twist_slip_msg.fr_wheel = 8.0
        #     self.twist_slip_msg.br_wheel = 8.0
        #
        # self.log(f"Time={time}, Vel={vel}!")
        return self.twist_slip_msg



main()

