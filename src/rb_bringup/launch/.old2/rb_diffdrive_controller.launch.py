import launch
import launch_ros
import os

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import (
    DeclareLaunchArgument,
    SetEnvironmentVariable,
    ExecuteProcess,
    RegisterEventHandler,
)
from launch.event_handlers import OnProcessStart

from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from ament_index_python.packages import get_package_share_directory, get_package_share_path


def generate_launch_description():
    # Get path to rb_bringup for our configs and other launch files.
    rb_bringup_dir = get_package_share_directory("rb_bringup")
    rb_description_dir = get_package_share_directory("rb_description")
    ros2_control_conf_path = os.path.join(rb_bringup_dir, "config", "rb_ros2_control.yaml")

    # Start publishing the /robot_description topic.
    rb_description_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(rb_bringup_dir, "launch", "description.launch.py")
        ),
        launch_arguments={"mode": "real"}.items(),
    )

    # Spawn the ros2_control DiffDrive controller.
    diff_drive_controller_spawner = Node(
        package="controller_manager", executable="spawner", arguments=["diff_drive_controller"]
    )

    # Start publishing on /dynamic_joint_states.
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    # TODO Include this launch in the teleop file.
    # Include the teleop joy launch file.
    # rb_teleop_joy_launch = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         os.path.join(rb_bringup_dir, 'launch', 'rb_teleop.launch.py')
    #     ),
    #     launch_arguments ={
    #         'joy_vel': '/diff_drive_controller/cmd_vel',
    #         'joy_config' : 'ps3',
    #         'config_filepath' : os.path.join(rb_bringup_dir, 'config', 'ps3.config.yaml')
    #     }.items()
    # )

    # Optional visualization.
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        arguments=["-d", os.path.join(rb_bringup_dir, "config", "tele1.rviz")],
    )

    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[ros2_control_conf_path],  # run hw_interface, register controllers.
        output="both",
        remappings=[
            ("~/robot_description", "/robot_description"),
        ],
    )

    return LaunchDescription(
        [
            rb_description_launch,
            ros2_control_node,
            joint_state_broadcaster_spawner,
            diff_drive_controller_spawner,
            # rviz_node,
        ]
    )
