from launch.launch_description import LaunchDescription

import os
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription, ExecuteProcess, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, TextSubstitution

import launch
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    rb_bringup_share = get_package_share_directory("rb_bringup")

    joy_vel_arg = DeclareLaunchArgument(name="joy_vel", default_value="/rb/cmd_vel")
    joy_vel = LaunchConfiguration("joy_vel")

    joy_config_arg = DeclareLaunchArgument(name="joy_config", default_value="ps3")
    joy_config = LaunchConfiguration("joy_config")

    joy_dev_arg = DeclareLaunchArgument(name="joy_dev", default_value="/dev/input/js0")
    joy_dev = LaunchConfiguration("joy_dev")

    teleop_cfg_arg = DeclareLaunchArgument(
        name="teleop_config_file",
        default_value=PathJoinSubstitution(
            [rb_bringup_share, "config", "teleop_configs", "ps3.config.yaml"]
        ),
        description="Full path to teleop_twist_joy config file",
    )
    teleop_cfg = LaunchConfiguration("teleop_config_file")

    joy_node = Node(
        package="joy",
        executable="joy_node",
        name="joy_node",
        parameters=[
            {
                "dev": joy_dev,
                "deadzone": 0.1,
                "autorepeat_rate": 20.0,
            }
        ],
    )

    teleop_node = Node(
        package="teleop_twist_joy",
        executable="teleop_node",
        name="teleop_twist_joy_node",
        parameters=[teleop_cfg],
        remappings={("/cmd_vel", joy_vel)},
    )

    return launch.LaunchDescription(
        [
            joy_vel_arg,
            joy_config_arg,
            joy_dev_arg,
            teleop_cfg_arg,
            joy_node,
            teleop_node,
        ]
    )

    # return launch.LaunchDescription(
    # [
    # launch.actions.DeclareLaunchArgument('joy_vel', default_value='/rb_base_controller/cmd_vel_unstamped'),
    # launch.actions.DeclareLaunchArgument(name="joy_vel", default_value="/rb/cmd_vel"),
    # launch.actions.DeclareLaunchArgument(name="joy_config", default_value="ps3"),
    # launch.actions.DeclareLaunchArgument(name="joy_dev", default_value="/dev/input/js0"),
    # launch.actions.DeclareLaunchArgument(
    #     name="config_filepath",
    #     default_value=[
    #         launch.substitutions.TextSubstitution(
    #             text=os.path.join(
    #                 get_package_share_directory(package_name="rb_teleop"), "config", ""
    #             )
    #         ),
    #         joy_config,
    #         launch.substitutions.TextSubstitution(text=".config.yaml"),
    #     ],
    # ),
    # Node(
    #     package="joy",
    #     executable="joy_node",
    #     name="joy_node",
    #     parameters=[
    #         {
    #             "dev": joy_dev,
    #             "deadzone": 0.3,
    #             "autorepeat_rate": 20.0,
    #         }
    #     ],
    # ),
    # Node(
    #     package="teleop_twist_joy",
    #     executable="teleop_node",
    #     name="teleop_twist_joy_node",
    #     parameters=[config_filepath],
    #     remappings={("/cmd_vel", launch.substitutions.LaunchConfiguration("joy_vel"))},
    # ),
    # IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         os.path.join(rb_bringup_dir, 'launch', 'rb_diffdrive.launch.py')
    #     ),
    #     launch_arguments={
    #         "mode": "real",
    #         "use_sime_time": "false",
    #     }.items()
    # )
    # ]
    # )
