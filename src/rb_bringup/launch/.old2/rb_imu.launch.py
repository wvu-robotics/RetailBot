import launch
import launch_ros
import os

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable, ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessStart

from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from ament_index_python.packages import get_package_share_directory, get_package_share_path

def generate_launch_description():
    """ Run the ADIS16485 IMU node.
    """
    rb_bringup_dir  = get_package_share_directory('rb_bringup')
    # rb_description_dir = get_package_share_directory('rb_description')
    # ros2_control_conf_path = os.path.join(rb_bringup_dir, 'config', 'test_ros2_control.yaml')

    # Optional visualization.
    rviz_node = Node(
        package = 'rviz2',
        executable = 'rviz2',
        output='screen',
        arguments=['-d', os.path.join(rb_bringup_dir, 'config', 'imu.rviz')]
    )

    # Connect to the microROS agent on the pico. Requires udev rules to be setup.
    # If using a container then /dev must be mounted.
    imu_node = Node(
            package = 'micro_ros_agent',
            executable = 'micro_ros_agent',
            output='screen',
            arguments=['serial', '--dev', '/dev/pico_imu', '-b', '115200']
            )


    return LaunchDescription([
        imu_node
        #rviz_node,
    ])

