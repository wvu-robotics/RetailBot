import launch
import launch_ros
import os

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable, ExecuteProcess, RegisterEventHandler, ExecuteProcess
from launch.event_handlers import OnProcessStart

from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from ament_index_python.packages import get_package_share_directory, get_package_share_path

def generate_launch_description():
    # Get path to rb_bringup for our configs and other launch files.
    rb_bringup_dir  = get_package_share_directory('rb_bringup')
    rb_description_dir = get_package_share_directory('rb_description')
    conf_path = os.path.join(rb_bringup_dir, 'config', 'rb_diffdrive.yaml')

    controlled_driving_dir = get_package_share_directory('controlled_driving')

    max_vel_arg = DeclareLaunchArgument(
        'max_speed',
        default_value='0.3',
        description='Maximum velocity for the robot'
    )

    accel_arg = DeclareLaunchArgument(
        'accel',
        default_value='1.0',
        description='Acceleration for the robot'
    )

    duration_arg = DeclareLaunchArgument(
        'duration',
        default_value='5.0',
        description='Acceleration for the robot'
    )
    stop_duration_arg = DeclareLaunchArgument(
        'stop_duration',
        default_value='1.0',
        description='Acceleration for the robot'
    )

    slide_node = Node(
            package="controlled_driving",
            executable="slide_drive",
            output="screen",
            parameters=[{
                'max_speed':LaunchConfiguration('max_speed'),
                'accel': LaunchConfiguration('accel'),
                'duration': LaunchConfiguration('duration'),
                'stop_duration': LaunchConfiguration('stop_duration'),
                }]
            )


    return LaunchDescription([
        max_vel_arg,
        accel_arg,
        duration_arg,
        stop_duration_arg,
        slide_node
    ])

