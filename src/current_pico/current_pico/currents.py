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

import rclpy
from rclpy.node import Node
from rclpy.time import Time
from std_msgs.msg import String, Float64MultiArray, Float32MultiArray
from builtin_interfaces.msg import Duration

from current_pico.read_adcs import start_capture
# from current_pico.msg import MotorCurrents
from motor_msgs.msg import MotorCurrents

# ADC_channel_names = {0:"GPIO 26", 1:"GPIO 27", 2:"GPIO 28", 3:"ref V", 4:"builtin thermo"}

def calc_amps(val):
    print(f"{val=}")
    volts =  val / (4096.0 / 3.2) 
    amps = (volts - 1.48) / 0.528
    return amps



class CurrentsNode(Node):
    def __init__(self, ksps_total= 72, channels=[1,2], num_samples=200):
        super().__init__("currents_node")

        # Flip these?
        left_id = 'E6612483CB58C423'
        right_id = 'E6613852837D762D'

        self.left_data_queue = Queue(maxsize=1)
        self.right_data_queue = Queue(maxsize=1)

        # Left ADC.
        self.left_adc_proc = Process(target=start_capture, 
                                     args=((
                                     self.left_data_queue,
                                     ksps_total,
                                     channels,
                                     num_samples,
                                     left_id
                                     ))
                                     )

        self.right_adc_proc = Process(target=start_capture, 
                                      args=((
                                      self.right_data_queue,
                                      ksps_total,
                                      channels,
                                      num_samples,
                                      right_id
                                      ))
                                      )

        # Make publisher for 200Hz that pops off queue.
        self.left_adc_pubber = self.create_publisher(MotorCurrents, 'left_motor_currents',
                                           10)
        self.right_adc_pubber = self.create_publisher(MotorCurrents, 'right_motor_currents',
                                           10)
        period = 1/200.0
        self.left_adc_timer = self.create_timer(period, self.left_timer_callback)
        self.right_adc_timer = self.create_timer(period, self.right_timer_callback)

        print("Starting adc callbacks!")
        self.left_adc_proc.start()
        self.right_adc_proc.start()


    def left_timer_callback(self):
        if self.left_data_queue.empty():
            return
        # Remove all but newest.
        try:
            while not self.left_data_queue.empty():
                data = self.left_data_queue.get_nowait()
            amps = calc_amps(data)
        except Exception as e:
            print(e)
            return

        msg = MotorCurrents()
        # Front, back.
        msg.data = [amps[0],amps[1]]
        msg.header.stamp = self.get_clock().now().to_msg()

        self.left_adc_pubber.publish(msg)


    def right_timer_callback(self):
        if self.right_data_queue.empty():
            return
        # Remove all but newest.
        try:
            while not self.right_data_queue.empty():
                data = self.right_data_queue.get_nowait()
            amps = calc_amps(data)
        except Exception as e:
            print(e)
            return

        msg = MotorCurrents()
        # Front, back.
        msg.data = [amps[0],amps[1]]
        msg.header.stamp = self.get_clock().now().to_msg()

        self.right_adc_pubber.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    executor = MultiThreadedExecutor()
    node = CurrentsNode()
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
