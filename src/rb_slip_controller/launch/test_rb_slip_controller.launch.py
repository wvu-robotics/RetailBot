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
    rb_slip_controller_path = get_package_share_path('rb_slip_controller')

    urdf_contents = Command(['xacro ',str(urdf_path), ' mode:=', 'real'])
    robot_state_publisher_node = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                'use_sim_time': False,
                'robot_description':ParameterValue(urdf_contents,value_type=str)
            }]
    )

    ros2_control_conf_path = rb_slip_controller_path/"config/test_ros2_control.yaml"

    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[ros2_control_conf_path], # run hw_interface, register controllers.
        output="both",
        remappings=[
            ("~/robot_description", "/robot_description"),
        ],
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    # diff_drive_controller_spawner = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     #arguments=["rb_base_controller", "--controller-manager", "/controller_manager"],
    #     arguments=["diff_drive_controller"],
    # )

    rb_slip_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        #arguments=["rb_base_controller", "--controller-manager", "/controller_manager"],
        arguments=["rb_slip_controller"],
    )

    rviz_config = rb_slip_controller_path/"config/test.rviz"
    # rviz_config_arg = DeclareLaunchArgument(
    #         name='rviz_config',
    #         default_value=str(rviz_config),
    #         description="rviz config file")
    # rviz_config = LaunchConfiguration('rviz_config')
    #
    rviz_node = Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=["-d", str(rviz_config)],
            )

    vicon_tf_node = Node(
        package="rb_tf_broadcasters",
        executable="vicon_tf",
    )

    vicon_odom_pubber = Node(
        package="rb_tf_broadcasters",
        executable="vicon_odom_pubber",
    )

    yaml_launch_file = os.path.join(
        get_package_share_directory('rb_bringup'),
        'launch',
        'vrpn.launch.yaml'
    )

    vrpn_launch = IncludeLaunchDescription( yaml_launch_file)

    # vrpn_mocap_launch = LaunchDescription(
    #     package='rb_bringup',
    #     executable='
    # )

    return LaunchDescription(
        [
            ros2_control_node,
            robot_state_publisher_node,
            joint_state_broadcaster_spawner,
            rb_slip_controller_spawner,
            rviz_node,
            # vicon_tf_node,
            # vicon_odom_pubber,
            # vrpn_launch
        ]
    )
