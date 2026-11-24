from ament_index_python.packages import get_package_share_path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration

from launch_ros.actions import Node, PushRosNamespace
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # Rename to rb_description_path.
    rb_description_path = get_package_share_path("rb_description")
    # Rename to default_urdf_path.
    default_urdf_path = rb_description_path / "urdf/rb.urdf" # TODO change to default xacro.
    default_rviz_config_path = rb_description_path / "rviz/urdf.rviz"

    declare_urdf_param = DeclareLaunchArgument(
        name="urdf",
        default_value=str(default_urdf_path),
        description="Absolute path to robot urdf file",
    )
    rviz_arg = DeclareLaunchArgument(
        name="rvizconfig",
        default_value=str(default_rviz_config_path),
        description="Absolute path to rviz config file",
    )

    sim_param = DeclareLaunchArgument(
            name="sim",
            default_value="false",
            description="Load simulation version of URDF",
            )

    # Form the command to get the processed URDF
    description_command = Command(["xacro ",
                 LaunchConfiguration("urdf"), 
                 ' sim:=', LaunchConfiguration("sim")
                 ])

    print(description_command)

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": ParameterValue(description_command,
                                                         value_type=str)},
                    {"use_sim_time":False}],
    )

    # Depending on gui parameter, either launch joint_state_publisher or joint_state_publisher_gui
    joint_state_publisher_node = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        parameters=[{'use_sim_time' : False}],
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", LaunchConfiguration("rvizconfig")],
    )

    return LaunchDescription(
        [
            declare_urdf_param,
            sim_param,
            rviz_arg,
            joint_state_publisher_node,
            robot_state_publisher_node,
        ]
    )
