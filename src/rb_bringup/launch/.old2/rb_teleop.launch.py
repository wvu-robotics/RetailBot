import os
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource

import launch
import launch_ros.actions


def generate_launch_description():
    joy_config = launch.substitutions.LaunchConfiguration('joy_config')
    joy_dev = launch.substitutions.LaunchConfiguration('joy_dev')
    config_filepath = launch.substitutions.LaunchConfiguration('config_filepath')
    rb_bringup_dir  = get_package_share_directory('rb_bringup')


    return launch.LaunchDescription([
        # launch.actions.DeclareLaunchArgument('joy_vel', default_value='/rb_base_controller/cmd_vel_unstamped'),
        launch.actions.DeclareLaunchArgument('joy_vel', default_value='/diff_drive_controller/cmd_vel'),
        launch.actions.DeclareLaunchArgument('joy_config', default_value='ps3'),
        launch.actions.DeclareLaunchArgument('joy_dev', default_value='/dev/input/js0'),
        launch.actions.DeclareLaunchArgument('config_filepath', default_value=[
            launch.substitutions.TextSubstitution(text=os.path.join(
                get_package_share_directory('rb_teleop'), 'config', '')),
            joy_config, launch.substitutions.TextSubstitution(text='.config.yaml')]),

        launch_ros.actions.Node(
            package='joy', executable='joy_node', name='joy_node',
            parameters=[{
                'dev': joy_dev,
                'deadzone': 0.3,
                'autorepeat_rate': 20.0,
            }]),
        launch_ros.actions.Node(
            package='teleop_twist_joy', executable='teleop_node',
            name='teleop_twist_joy_node', parameters=[config_filepath],
            remappings={('/cmd_vel', launch.substitutions.LaunchConfiguration('joy_vel'))},
            ),

        IncludeLaunchDescription(
            launch_description_source=PythonLaunchDescriptionSource(
                launch_file_path=os.path.join(rb_bringup_dir, 'launch', 'rb_diffdrive.launch.py')
            ),
            launch_arguments={
                "mode": "real",
                "use_sime_time": "false",
            }.items()
        )

    ])
