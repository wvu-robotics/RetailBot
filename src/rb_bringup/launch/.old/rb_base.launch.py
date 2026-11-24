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

#from ros_gz_bridge.actions import RosGzBridge

def generate_launch_description():
    #### File scope Arguments and LaunchConfigurations
    ##################################################
    #use_sim_time = LaunchConfiguration('use_sim_time')
    #use_sim_time_arg = DeclareLaunchArgument(
    #        name='use_sim_time',
    #        default_value='True', description="Use /clock or not for time.")
    mode_arg = DeclareLaunchArgument(
            name="mode",
            default_value="gz",
            choices=['gz','realhw','isaac'],
            description="Mode to launch in. E.g. gz,realhw,isaac"
            )
    mode = LaunchConfiguration("mode")
    use_sim_time = PythonExpression(["'True' if '", mode, "' == 'gz' else 'False'"])

    #### Package Paths
    ##################################################
    description_path = get_package_share_path('rb_description')
    bub_bringup_path = get_package_share_path('rb_bringup')


    #### Nodes, Launch Files
    ##################################################
    urdf_path = description_path / "urdf/rb.urdf"
    #xacro_sim_bool = PythonExpression(["'True' if '", mode, "' == 'gz' else 'False'"])
    urdf_contents = Command(['xacro ',str(urdf_path), ' sim:=', use_sim_time])
    robot_state_publisher_node = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                'use_sim_time': use_sim_time,
                'robot_description':ParameterValue(urdf_contents,value_type=str)
                }]
            )

    # Rviz Node
    default_rviz_config = description_path/"rviz/urdf.rviz"
    rviz_config_arg = DeclareLaunchArgument(
            name='rviz_config',
            default_value=str(default_rviz_config),
            description="rviz config file")
    rviz_config = LaunchConfiguration('rviz_config')
    use_rviz_arg = DeclareLaunchArgument(
            name='use_rviz',
            default_value="False",
            description="Launch Rviz"
            )
    use_rviz = LaunchConfiguration('use_rviz')
    rviz_node = Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=["-d", rviz_config],
            condition=IfCondition(use_rviz),
            )

    initial_x = '1.0'
    initial_y = '4.0'
    initial_z = '7.0'
    initial_roll = '0.0'
    initial_pitch = '0.0'
    initial_yaw = '1.57'

    # Spawn robot in gz
    spawn_entity = Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-entity', 'rb',
                '-topic', 'robot_description',
                '-x', initial_x,
                '-y', initial_y,
                '-z', initial_z,
                '-R', initial_roll,
                '-P', initial_pitch,
                '-Y', initial_yaw
                ],
            output='screen'
            )

    joint_state_publisher_gui_node = Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            parameters=[{'use_sim_time' : use_sim_time}],
            )

    # Get ros2_control.yaml
    # Spawn controller_manager node (only for real hw)
    # Spawn diffdrive controller
    # Spawn joint_state_broadcaster controller
    #ros2_conf = bub_bringup_path/"config/ros2_control.yaml"

    diff_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        #arguments=["rb_base_controller", "--controller-manager", "/controller_manager"],
        arguments=["diff_drive_base_controller"],
    )
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )
    # Get nav2 config yaml
    # Nav 2 launch include

    # Get localization config yaml
    # run robot_localization


    # Get gz-bridge config yaml
    # Run gz-bridge node
    set_env_vars = SetEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            '${GZ_SIM_RESOURCE_PATH}'
            ':/home/devuser/retail-bot/src/non_ros_pkgs/gazebo_models'\
            ':/home/devuser/retail-bot/src'
            ':/opt/ros/jazzy/lib/')

    set_env_vars1 = SetEnvironmentVariable(
            'GZ_SIM_SYSTEM_PLUGIN_PATH',
            '/opt/ros/jazzy/lib/'
            )
    gz_bridge_config = bub_bringup_path / "config/gz_bridge.yaml"
    ros_gz_bridge = Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            name="ros_gz_parameter_bridge",
            arguments=['--ros-args', '-p', 
                       f'config_file:={gz_bridge_config}']
            )

    print_env = ExecuteProcess(
            cmd=['env'],  # Command to list environment variables
            output='screen',  # Output the result to the screen
            shell=True  # Use shell to interpret the command
        )

    #### Processes
    gazebo_run = ExecuteProcess(cmd=['gz','sim','shapes.sdf','-v 1'])

    return LaunchDescription(
            [
                mode_arg,
                print_env,
                set_env_vars1,
                use_rviz_arg,
                rviz_config_arg,
                set_env_vars,
                gazebo_run,
                diff_drive_controller_spawner,
                joint_state_broadcaster_spawner,
                ros_gz_bridge,
                robot_state_publisher_node,
                spawn_entity,
                rviz_node,
                #joint_state_publisher_gui_node
                ]
            )


