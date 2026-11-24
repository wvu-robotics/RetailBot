#!/bin/bash

# Make a dir for todays date
DIR="$(date +'%Y_%-m_%-d')_rosbags"
mkdir -p ${DIR}

NAME="bag_$(date +'%Y_%-m_%-d')"

TOPICS="/joy \
	/pico_imu \
	/robot_description \
	/tf /tf_static \
	/odometry/filtered \
	/dynamic_joint_states \
	/diff_drive_base_controller/odom \
	/diff_drive_base_controller/cmd_vel_unstamped \
	/zed/zed_node/pose \
	/zed/zed_node/pose/status \
	/zed/zed_node/pose_with_covariance \
	/zed/zed_node/odom \
	/zed/zed_node/path_odom \
	/zed/zed_node/imu/data \
	/zed/zed_node/imu/data_raw"
ros2 bag record ${TOPICS} -o ${DIR}/${NAME}
