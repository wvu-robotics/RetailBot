from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, LaunchConfiguration
from ament_index_python.packages import get_package_share_directory, get_package_share_path
from ament_index_python.packages import get_package_share_directory

from launch_ros.parameter_descriptions import ParameterValue

import os
import xacro
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    declared_arguments = []
    declared_arguments.append(
            DeclareLaunchArgument(
                "gui",
                default_value="false",
                description="Start RViz2 automatically with this launch file.",
                )
            )

    #xacro_file_path = os.path.join(FindPackageShare('robot_description'), 'urdf', 'robot_description.urdf.xacro')
#    xacro_file_path = PathJoinSubstitution([
#        FindPackageShare('robot_description'),  # Finds the share directory of 'robot_description' package
#        'urdf', 
#        'robot_description.urdf.xacro'
#        ])

    #robot_description_content = xacro.process_file(xacro_file_path).toxml()



    description_path = get_package_share_path('rb_description')
    urdf_path = description_path / "urdf/rb.urdf"
    urdf_contents = Command(['xacro ',str(urdf_path), ' mode:=', 'mock' ])
    robot_state_pub_node = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                # 'use_sim_time': False,
                'robot_description':ParameterValue(urdf_contents,value_type=str)
                }]
            )


    # Use get_package_share_directory to get the path as a string
    # robot_description_package_path = get_package_share_directory('rb_description')
    # # Construct the file path using os.path.join
    # xacro_file_path = os.path.join(robot_description_package_path, 'urdf', 'rb.urdf')
    # # Now, xacro_file_path is a string that can be passed to xacro.process_file
    # robot_description_content = xacro.process_file(xacro_file_path).toxml()
    #
    # # Put in a dict with the name 'robot_description' as a key per convention.
    # robot_description = {"robot_description": robot_description_content}

    robot_controllers = PathJoinSubstitution(
            [
                FindPackageShare("rb_drivebase_interface"),
                "config",
                "rb_controllers.yaml",
                ]
            )
    control_node = Node(
            package="controller_manager",
            executable="ros2_control_node",
            parameters=[urdf_contents, robot_controllers],
            output="both",
            )

    # robot_state_pub_node = Node(
    #         package="robot_state_publisher",
    #         executable="robot_state_publisher",
    #         output="both",
    #         parameters=[robot_description],
    #         remappings=[
    #             ("/diff_drive_controller/cmd_vel_unstamped", "/cmd_vel"), #???
    #             ],
    #         )

    # This is a controller.
    joint_state_broadcaster_spawner = Node(
            package="controller_manager",
            executable="spawner",
            arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
            )

    robot_controller_spawner = Node(
            package="controller_manager",
            executable="spawner",
            arguments=["rb_base_controller", "--controller-manager", "/controller_manager"],
            # arguments=[, "--controller-manager", "/controller_manager"],
            )

    # Delay start of robot_controller after `joint_state_broadcaster`
    delay_robot_controller_spawner_after_joint_state_broadcaster_spawner = RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[robot_controller_spawner],
                )
            )

    nodes = [
            control_node,
            robot_state_pub_node,
            joint_state_broadcaster_spawner,
            delay_robot_controller_spawner_after_joint_state_broadcaster_spawner,
            ]

    return LaunchDescription(declared_arguments + nodes)
