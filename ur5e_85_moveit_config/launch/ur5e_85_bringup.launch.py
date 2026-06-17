from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    declared_args = [
        DeclareLaunchArgument("ur_type", default_value="ur5e"),
        DeclareLaunchArgument("robot_ip", default_value="0.0.0.0"),
        DeclareLaunchArgument("use_fake_hardware", default_value="true"),
        DeclareLaunchArgument("launch_rviz", default_value="true"),
    ]

    ur_type           = LaunchConfiguration("ur_type")
    robot_ip          = LaunchConfiguration("robot_ip")
    use_fake_hardware = LaunchConfiguration("use_fake_hardware")
    launch_rviz       = LaunchConfiguration("launch_rviz")

    desc_pkg    = FindPackageShare("ur5e_85_description")
    moveit_pkg  = FindPackageShare("ur5e_85_moveit_config")

    # 1) UR driver control stack: ros2_control_node + spawners + robot_state_publisher
    ur_control = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("ur_robot_driver"),
                "launch", "ur_control.launch.py",
            ])
        ),
        launch_arguments={
            "ur_type": ur_type,
            "robot_ip": robot_ip,
            "use_fake_hardware": use_fake_hardware,
            "launch_rviz": "false",  # we launch MoveIt's RViz instead
            # Use OUR combined URDF instead of the UR driver's default
            "description_package": "ur5e_85_description",
            "description_file": "ur5e_85.urdf.xacro",
        }.items(),
    )

    # 2) MoveIt move_group + RViz (delay so robot_state_publisher is up first)
    moveit_rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([moveit_pkg, "launch", "moveit_rviz.launch.py"])
        ),
    )
    move_group = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([moveit_pkg, "launch", "move_group.launch.py"])
        ),
    )

    delayed_moveit = TimerAction(
        period=4.0,
        actions=[move_group, moveit_rviz],
    )

    return LaunchDescription(declared_args + [ur_control, delayed_moveit])