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

    # Create launch arg objects.
    use_sim_time = DeclareLaunchArgument(name='use_sim_time',
                                         default_value='False',
                                         description='Flag to enable use_sim_time')

    # Get path to rb_bringup for our configs and other launch files.
    rb_bringup_dir  = get_package_share_directory('rb_bringup')
    rb_description_dir = get_package_share_directory('rb_description')

    conf_path = os.path.join(rb_bringup_dir, 'config', 'rb_diffdrive.yaml')
    ros2_control_conf_path = os.path.join(rb_bringup_dir, 'config',
    'ros2_control_conf.yaml')

    # Include the rb_description launch file. 
    rb_description_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(rb_description_dir, 'launch', 'rb_sim_urdf.launch.py')
        ),
            launch_arguments={"sim": "false"}.items()
    )

    # Spawn the ros2_control DiffDrive controller.
    diff_drive_slip_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        #arguments=["rb_base_controller", "--controller-manager", "/controller_manager"],
        arguments=["diff_drive_slip_base_controller"],
    )

    # Spawn the ros2_control joint_state_broadcaster pseudo controller.
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    # Include the teleop joy launch file.
    rb_teleop_joy_launch = IncludeLaunchDescription( 
        # Include teleop launch and pass on args
        #joy_config_arg = launch.substitutions.LaunchConfiguration('joy_config')
        #joy_dev_arg = launch.substitutions.LaunchConfiguration('joy_dev')
        PythonLaunchDescriptionSource(
            os.path.join(rb_bringup_dir, 'launch', 'rb_teleop.launch.py')
        ),
        launch_arguments ={
            'joy_vel' : '/diff_drive_base_controller/cmd_vel_unstamped',
            'joy_config' : 'ps3',
            'config_filepath' : os.path.join(rb_bringup_dir, 'config', 'ps3.config.yaml')
        }.items()
    )

    ekf_config_path = os.path.join(rb_bringup_dir, "config", "gz_ekf.yaml")
    # Launch the EKF node.
    robot_localization_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_node',
        output='screen',
        arguments=['--ros-args', '--log-level', 'INFO'],
        parameters=[ekf_config_path, conf_path] # Can I do this?
    )

    # Optional visualization.
    rviz_node = Node(
        package = 'rviz2',
        executable = 'rviz2',
        output='screen',
        arguments=['-d', os.path.join(rb_bringup_dir, 'config', 'tele1.rviz')]
    )

    env_vars = SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH','/home/devuser/retail-bot/src')

    slam_toolbox_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(rb_bringup_dir, 'launch', 'localization_launch.launch.py')
        )
    )

    ros2_control_node = Node(
            package="controller_manager",
            executable="ros2_control_node",
            parameters=[ros2_control_conf_path], # run hw_interface, register controllers.
            output="both",
            remappings=[
            ("~/robot_description", "/robot_description"),
        ],
            )

    return LaunchDescription([
        #rviz_node,
        env_vars,
        rb_description_launch,
        ros2_control_node,
        joint_state_broadcaster_spawner,
        diff_drive_slip_controller_spawner   ,
        rb_teleop_joy_launch,
        #robot_localization_node,
        #slam_toolbox_launch,
    ])

