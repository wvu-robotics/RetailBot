#!/bin/bash
# Make a dir for todays date
DIR="$(date +'%Y_%-m_%-d')_rosbags"
mkdir -p ${DIR}
echo "Saving to directory ${DIR}"

read -p "Enter a natural language description for the bag file: " USER_INPUT

# Replace spaces with '_'s
USER_INPUT=${USER_INPUT// /_}

NAME="$(TZ='America/New_York' date +'%Y_%-m_%-d__%H_%M_%S')${USER_INPUT}.bag"

TOPICS="-a"

# TOPICS="/joy \
# 	/robot_description \
# 	/tf /tf_static \
# 	/dynamic_joint_states \
# 	/joint_state_broadcaster/transition_event \
# 	/joint_states \
# 	/odom_in_vicon_frame \
# 	/parameter_events \
# 	/rb_slip_controller/cmd_vel \
# 	/rb_slip_controller/odom \
# 	/rb_slip_controller/transition_event \
# 	/rosout \
# 	/tf \
# 	/tf_static \
# 	/vrpn_mocap/rb1/accel \
# 	/vrpn_mocap/rb1/pose \
# 	/pico_imu \
# 	/vrpn_mocap/rb1/twist" 
	


ros2 bag record ${TOPICS} -o ${DIR}/${NAME}
