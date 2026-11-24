#!/bin/bash
TOPICS="/joy \
	/pico_imu \
	/robot_description \
	/tf /tf_static \
	/odometry/filtered \
	/dynamic_joint_states \
	/diff_drive_base_controller/odom \
	/diff_drive_base_controller/cmd_vel_unstamped"
ros2 bag record ${TOPICS}
