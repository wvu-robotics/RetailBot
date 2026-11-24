from ament_index_python.packages import get_package_share_path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration

from launch_ros.actions import Node, PushRosNamespace
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    rb_description_path = get_package_share_path("rb_description")

    # Just in case we want to look at another URDF.
    declare_urdf_path = DeclareLaunchArgument(
        name="urdf_path",
        default_value=str(rb_description_path / "urdf" / "rb.urdf"),
        description="Absolute path to robot urdf file",
    )
    urdf_path = LaunchConfiguration(variable_name="urdf_path")

    # use_sim_time_declare = DeclareLaunchArgument(
    #         name="use_sim_time",
    #         default_value="false",
    #         description="Whether to use system time or /clock.",
    #         )
    # use_sim_time_arg = LaunchConfiguration('use_sim_time')

    declare_urdf_mode = DeclareLaunchArgument(
        name="urdf_mode",
        default_value="real",
        description="Load simulation version of URDF",
    )
    urdf_mode = LaunchConfiguration(variable_name="urdf_mode")

    # Form the command to get the processed URDF.
    xacro_command = Command(
        command=[
            "xacro ",
            urdf_path,
            " mode:=",
            urdf_mode,
        ]
    )
    # A string of the final processed URDF.
    urdf_str = ParameterValue(xacro_command, value_type=str)

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[
            {
                "robot_description": ParameterValue(robot_desc, value_type=str),
            }
        ],
    )
    # Skip this if using the gui version.
    # joint_state_publisher_node = Node(
    #     package="joint_state_publisher",
    #     executable="joint_state_publisher",
    #     parameters=[{'use_sim_time' : use_sim_time_arg}],
    # )

    joint_state_publisher_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        parameters=[{"use_sim_time": use_sim_time_arg}],
    )

    default_rviz_config_path = rb_description_path / "config/urdf.rviz"
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", str(default_rviz_config_path)],
    )

    return LaunchDescription(
        [
            urdf_arg_declare,
            use_sim_time_declare,
            mode_declare,
            robot_state_publisher_node,
            joint_state_publisher_gui_node,
            # joint_state_publisher_node,
            rviz_node,
        ]
    )
