from ament_index_python.packages import get_package_share_path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration

from launch_ros.actions import Node, PushRosNamespace
from launch_ros.parameter_descriptions import ParameterValue


"""
Publish the robot_description topic. Accepts arg mode=[mock|sim|real]. Xacro
used to pass these to include gz and ros2_control tags conditionally.
"""


def generate_launch_description():
    # -----------------------------------------------------------------------------
    # Paths
    # -----------------------------------------------------------------------------
    rb_description_path = get_package_share_path("rb_description")

    default_rviz_config_path = rb_description_path / "config" / "rb_description.rviz"

    # -----------------------------------------------------------------------------
    # Launch Arguments
    # -----------------------------------------------------------------------------
    declare_cfg_path = DeclareLaunchArgument(
        name="cfg_path",
        description="Config file to be used by all nodes",
        default_value=str(rb_description_path / "config" / "rb_description.yaml"),  # TODO
    )
    cfg_path = LaunchConfiguration(variable_name="cfg_path")

    declare_urdf_path = DeclareLaunchArgument(
        name="urdf_path",
        default_value=str(rb_description_path / "urdf" / "rb.urdf"),
        description="Absolute path to robot urdf file",
    )
    urdf_path = LaunchConfiguration(variable_name="urdf_path")

    declare_rviz_cfg_path = DeclareLaunchArgument(
        name="rviz_cfg_path",
        default_value=str(default_rviz_config_path),
        description="Absolute path to rviz config file",
    )
    rviz_cfg_path = LaunchConfiguration(variable_name="rviz_cfg_path")

    # Flag to turn RViz on/off
    declare_rviz_flag = DeclareLaunchArgument(
        "rviz_flag",
        default_value="true",
        description="Whether to launch RViz",
    )
    rviz_flag = LaunchConfiguration("rviz_flag")

    declare_urdf_mode = DeclareLaunchArgument(
        name="urdf_mode",
        default_value="sim",
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

    # -----------------------------------------------------------------------------
    # LaunchDescriptionEntities
    # -----------------------------------------------------------------------------
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            cfg_path,
            {"robot_description": urdf_str},
        ],
    )

    # Depending on gui parameter, either launch joint_state_publisher or joint_state_publisher_gui
    joint_state_publisher_node = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        parameters=[
            cfg_path,
        ],
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_cfg_path],
        parameters=[cfg_path],
        condition=IfCondition(rviz_flag),
    )

    # -----------------------------------------------------------------------------
    # Return final LaunchDescription.
    # -----------------------------------------------------------------------------
    return LaunchDescription(
        [
            declare_cfg_path,
            declare_urdf_path,
            declare_urdf_mode,
            declare_rviz_cfg_path,
            declare_rviz_flag,
            joint_state_publisher_node,
            robot_state_publisher_node,
            rviz_node
        ]
    )
