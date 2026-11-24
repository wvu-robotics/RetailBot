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
    robot_description_share = get_package_share_path("robot_description")
    urdf_path = os.path.join(robot_description_share, 'urdf/gz_robot_description.urdf')

    robot_description = ParameterValue(
            Command(["xacro ", urdf_path]), value_type=str
            )

    robot_controllers = PathJoinSubstitution(
            [
                FindPackageShare("rb_sim"),
                "config",
                "diff_drive_controller_velocity.yaml",
                ]
            )

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
    spawn_entity = launch_ros.actions.Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-entity', 'rb', '-topic', 'robot_description'],
            output='screen'
            )

    ros_gz_bridge_node = Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='ros_gz_bridge_parameter_bridge',
            #parameters=[{'config_file': config_file_path}],
            arguments=['--ros-args', '-p', f'config_file:={bridge_config}'],
            output='screen'
            )

    # Our ros2_control controllers.
    # I think this runs the ros2 control mangaing nodes via URDF parsing.
    joint_state_broadcaster_spawner = Node(
            package="controller_manager",
            executable="spawner",
            #arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
            arguments=["joint_state_broadcaster"],
            )

    robot_controller_spawner = Node(
            package="controller_manager",
            executable="spawner",
            #arguments=["diff_drive_base_controller", "--controller-manager", "/controller_manager"],
            arguments=["diff_drive_base_controller"],
            # Doesn't work...
            remappings=[
                ('/diff_drive_base_controller/cmd_vel_unstamped', '/cmd_vel')
                ]
            )

    # Give the joint_state controller a bit to run before we run DiffDrive.
    delay_robot_controller_spawner_after_joint_state_broadcaster_spawner = RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[robot_controller_spawner],
                )
            )

    # Needed to run things with sim time.
    bridge = Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=['/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock'],
            output='screen'
            )

    env_vars = SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH','/home/devuser/retail-bot/src')

    # For now put localization in here
#    robot_localization_node = launch_ros.actions.Node(
#            package='robot_localization',
#            executable='ekf_node',
#            name='ekf_filter_node',
#            output='screen',
            #parameters=[os.path.join(get_package_share_directory('rb_localization'), 'config', 'gz_ekf.yaml'), {'use_sim_time': LaunchConfiguration('use_sim_time')}]
            #parameters=[os.path.join(get_package_share_directory('rb_localization'), 'config', 'gz_ekf.yaml')]
#            )

    return LaunchDescription([
        env_vars,
        #SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH','/home/devuser/retail-bot/src'),
        launch.actions.ExecuteProcess(cmd=['ign','gazebo', 'empty.sdf', '-v 5'], output='screen'),
        spawn_entity,
        delay_robot_controller_spawner_after_joint_state_broadcaster_spawner,
        joint_state_broadcaster_spawner,
        bridge, # TODO roll this into the yaml config and delete this.
        ros_gz_bridge_node,
        ])
