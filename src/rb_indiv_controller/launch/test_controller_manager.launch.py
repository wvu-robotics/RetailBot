import launch
import launch_ros
import os

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable, ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessStart
from launch.conditions import IfCondition

from launch_ros.substitutions import FindPackageShare 
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, Command, PythonExpression
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.parameter_descriptions import ParameterValue

from ament_index_python.packages import get_package_share_directory, get_package_share_path

def generate_launch_description():
    description_path = get_package_share_path('rb_description')
    urdf_path = description_path / "urdf/rb.urdf"
    rb_indiv_controller_path = get_package_share_path('rb_indiv_controller')

    urdf_contents = Command(['xacro ',str(urdf_path), ' mode:=', 'mock'])
    robot_state_publisher_node = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                'use_sim_time': False,
                'robot_description':ParameterValue(urdf_contents,value_type=str)
            }]
    )

    ros2_control_conf_path = rb_indiv_controller_path/"config/rb_indiv_controller.yaml"

    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[ros2_control_conf_path], # run hw_interface, register controllers.
        output="both",
        remappings=[
            ("~/robot_description", "/robot_description"),
        ],
    )
    return LaunchDescription(
        [
            ros2_control_node,
            robot_state_publisher_node
        ]
    )
