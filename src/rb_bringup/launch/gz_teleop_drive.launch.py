from launch.launch_description import LaunchDescription

import os
from ament_index_python.packages import get_package_share_directory, get_package_share_path
from launch.actions import (
    GroupAction,
    IncludeLaunchDescription,
    ExecuteProcess,
    DeclareLaunchArgument,
    include_launch_description,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, TextSubstitution

import launch
from launch_ros.actions import Node, PushRosNamespace


def generate_launch_description() -> LaunchDescription:
    # -----------------------------------------------------------------------------
    # Paths
    # -----------------------------------------------------------------------------
    rb_bringup_pkg = get_package_share_path(package_name="rb_bringup")
    rb_description_pkg = get_package_share_path(package_name="rb_description")
    rb_sim_pkg = get_package_share_path(package_name="rb_sim")

    # -----------------------------------------------------------------------------
    # Launch Arguments
    # -----------------------------------------------------------------------------
    # Namespace for all nodes. Defaults to "/rb".
    declare_namespace = DeclareLaunchArgument(
        name="namespace",
        description="Namespace for all nodes",
        default_value="rb",
    )
    namespace = LaunchConfiguration(variable_name="namespace")

    # Top level config file for all nodes.
    declare_cfg_path = DeclareLaunchArgument(
        name="cfg_path",
        description="Config file to be used by all nodes",
        default_value=str(rb_bringup_pkg / "config" / "teleop_drive.yaml"),
    )
    cfg_path = LaunchConfiguration(variable_name="cfg_path")

    # -----------------------------------------------------------------------------
    # LaunchDescriptionEntities
    # -----------------------------------------------------------------------------
    # Get joystick input.
    joy_node = Node(
        package="joy",
        executable="joy_node",
        name="joy_node",
        parameters=[cfg_path],
    )

    # Turn joystick input into Twist/ messages.
    teleop_node = Node(
        package="teleop_twist_joy",
        executable="teleop_node",
        name="teleop_twist_joy_node",
        parameters=[cfg_path],
        # remappings={("/cmd_vel", "joy_vel")},
    )

    # Publish the xacro with simulation plugins and tags.
    rb_description_launch = IncludeLaunchDescription(
        launch_description_source=str(rb_description_pkg / "launch" / "rb_description.launch.py"),
        launch_arguments=[
            ("cfg_path", cfg_path),
            ("urdf_mode", "sim"),
            ("urdf", str(rb_description_pkg / "urdf" / "rb.urdf")),
        ],
    )

    # Spawn the ros2_control DiffDrive controller.
    diff_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_drive_slip_base_controller"],
    )

    # Spawn the ros2_control joint_state_broadcaster pseudo controller.
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    gz_sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(rb_sim_pkg / "launch" / "gz_sim.launch.py")),
        launch_arguments=[
            # ("bridge_config", "")
        ],
    )

    # -----------------------------------------------------------------------------
    # Push namespace and return final LaunchDescription.
    # -----------------------------------------------------------------------------
    # All the nodes and launches we want to run.
    actions = [
        joy_node,
        teleop_node,
        rb_description_launch,
        diff_drive_controller_spawner,
        joint_state_broadcaster_spawner,
        gz_sim_launch,
    ]

    # Make all nodes and launches be under same namespace.
    namespaced_actions = GroupAction(
        actions=[
            PushRosNamespace(namespace=namespace),
            *actions,
        ]
    )

    return launch.LaunchDescription(
        [
            declare_cfg_path,
            declare_namespace,
            namespaced_actions,
        ]
    )
