import os
from pathlib import Path
import launch
import launch_ros
import launch_ros.descriptions
import launch_ros.actions

from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg_share = get_package_share_directory("scara_description")
    xacro_file  = str(Path(pkg_share) / "urdf" / "scara.urdf.xacro")
    rviz_config = str(Path(pkg_share) / "rviz" / "scara.rviz")

    gui_arg = launch.actions.DeclareLaunchArgument(
        name="gui",
        default_value="true",
        description="Abrir joint_state_publisher_gui (sliders de junta)",
    )

    robot_state_publisher = launch_ros.actions.Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
            "robot_description": launch_ros.descriptions.ParameterValue(
                launch.substitutions.Command(["xacro ", xacro_file]),
                value_type=str,
            )
        }],
    )

    joint_state_publisher_gui = launch_ros.actions.Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        condition=launch.conditions.IfCondition(
            launch.substitutions.LaunchConfiguration("gui")
        ),
    )

    # Verifica se o arquivo .rviz existe. Se não existir, abre o RViz em branco.
    rviz_args = []
    if os.path.exists(rviz_config):
        rviz_args = ["-d", rviz_config]

    rviz2 = launch_ros.actions.Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        arguments=rviz_args,
    )

    return launch.LaunchDescription([
        gui_arg,
        robot_state_publisher,
        joint_state_publisher_gui,
        rviz2,
    ])