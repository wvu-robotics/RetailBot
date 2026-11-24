import launch
import launch_ros
import os

from launch import LaunchDescription

from ament_index_python.packages import get_package_share_path

from launch import LaunchDescription 
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable, RegisterEventHandler, \
        ExecuteProcess, IncludeLaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration, FindExecutable, \
        PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.event_handlers import OnProcessExit
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
#    robot_description_share = get_package_share_path("robot_description")
#    urdf_path = os.path.join(robot_description_share, 'urdf/gz_robot_description.urdf')
#
#    robot_description = ParameterValue(
#            Command(["xacro ", urdf_path]), value_type=str
#            )
#
    # Config for the ros-gz bridge.
    bridge_config = os.path.join(
            get_package_share_directory('rb_sim'),
            'config',
            'bridge.yaml'
            )

    # Find the param bridge.
    ros_gz_bridge_launch_file = os.path.join(
            get_package_share_directory('ros_gz_bridge'),
            'launch',
            'parameter_bridge.launch.py'
            )

    rb_sim_share = get_package_share_directory('rb_sim')  
    bridge_config = os.path.join(rb_sim_share, 'config', 'bridge.yaml')

    # Run the gz-ros bridge with the config file.
    ros_gz_bridge = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([ros_gz_bridge_launch_file]),
            launch_arguments={'config_file': bridge_config}.items(),
            )

    # This will hang until /robot_description has something on it.
#    spawn_entity = launch_ros.actions.Node(
#            package='ros_gz_sim',
#            executable='create',
#            arguments=['-entity', 'rb', '-topic', 'robot_description'],
#            output='screen'
#            )

    ros_gz_bridge_node = Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='ros_gz_bridge_parameter_bridge',
            #parameters=[{'config_file': config_file_path}],
            arguments=['--ros-args', '-p', f'config_file:={bridge_config}'],
            output='screen'
            )

    # Needed to run things with sim time.

    env_vars = SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH','/home/devuser/retail-bot/src')

    initial_x = '1.0'
    initial_y = '4.0'
    initial_z = '3.0'
    initial_roll = '0.0'
    initial_pitch = '0.0'
    initial_yaw = '1.57'

    # Define the node to spawn the entity with hardcoded pose
    spawn_entity = launch_ros.actions.Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-entity', 'rb',
                '-topic', 'robot_description',
                '-x', initial_x,
                '-y', initial_y,
                '-z', initial_z,
                '-R', initial_roll,
                '-P', initial_pitch,
                '-Y', initial_yaw
                ],
            output='screen'
            )

    return LaunchDescription([
        env_vars,
        launch.actions.ExecuteProcess(cmd=['gz','sim', 'shapes.sdf', '-v 5'], output='screen'),
        spawn_entity,
        ros_gz_bridge_node,
        ])
