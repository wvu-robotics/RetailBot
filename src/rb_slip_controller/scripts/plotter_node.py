#!/bin/python3
import rclpy
from rclpy.node import Node
from rclpy.time import Time
from rclpy.executors import MultiThreadedExecutor
from std_msgs.msg import String
import numpy as np
import threading
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from multiprocessing import Process, Queue

from matplotlib.axes import Axes

from twist_slip_msg.msg import TwistSlipStamped
# from sensor_msgs.msg import JointState
from control_msgs.msg import DynamicJointState

from plot_objects import TwistSlipStampedBuffer

import random
import time

class PlotterNode(Node):
    def __init__(self, window_size = 100):
        super().__init__("plotter_node")
        # self.joint_subber = self.create_subscription(
        #     DynamicJointState, '/dynamic_joint_states', self.sub_dynamic_joint_callback, 10)
        self.twist_slip_subber = self.create_subscription(
            TwistSlipStamped, '/rb_slip_controller/cmd_vel', self.twist_slip_callback, 10)
        self.data_lock = threading.Lock()

        self.window_size = window_size # How much data to plot.

        # Create our data structures to hold the message data received so far.
        self.buffers = {}
        self.twist_slip_buff = TwistSlipStampedBuffer(self.window_size)
        self.buffers['twist_slip_buff'] =  self.twist_slip_buff

        self.plot_thread = threading.Thread(target=self.plot)
        self.plot_thread.daemon = True
        self.plot_thread.start()

    # Call this in a thread
    def plot(self):
        fig, ax = plt.subplots()
        ax.margins(x=0.1, y=0.1)
        for buffer in self.buffers:
            self.buffers[buffer].create_lines(ax)

        def update(frame): # Redraw our plot lines.
            lines = None
            with self.data_lock:
                for buffer in self.buffers:
                    lines = self.buffers[buffer].update_lines()

                    time_lim, data_lim = self.buffers[buffer].get_ax_lims()
                    ax.set_xlim(time_lim)
                    ax.set_ylim(data_lim)
            # plt.pause(0.05)
            return lines

        ani = FuncAnimation(fig, update, interval=100)  # 10 Hz update
        plt.show()

    def twist_slip_callback(self, msg):
        self.buffers['twist_slip_buff'].update_data(msg)

    def sub_dynamic_joint_callback(self, msg):
        # Append to end of data arrays in self.dat
        # self.dat.dynamic_joint_states.time[0] = msg.header.stamp.sec
        # self.dat.dynamic_joint_states.br_wheel[0] = msg.interface_values[0].values[0]
        ...


def main(args=None):
    rclpy.init(args=args)
    executor = MultiThreadedExecutor()
    node = PlotterNode()
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
