from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    declared_args = [
        DeclareLaunchArgument("ros_ip", default_value="0.0.0.0",
                              description="IP address to bind the ROS-TCP-Endpoint server to"),
        DeclareLaunchArgument("ros_tcp_port", default_value="10000",
                              description="Port for the ROS-TCP-Endpoint server"),
    ]

    ros_ip = LaunchConfiguration("ros_ip")
    ros_tcp_port = LaunchConfiguration("ros_tcp_port")

    desc_pkg = FindPackageShare("ur5e_85_description")
    actions_pkg = FindPackageShare("ur5e_moveit_actions")

    # 1. Core robot + MoveIt + RViz
    base_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([desc_pkg, "launch", "ur5e_85_bringup.launch.py"])
        ),
    )

    # 2. Custom action server + Python bridge (delayed so MoveIt's move_group is ready)
    action_layer = TimerAction(
        period=8.0,
        actions=[IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([actions_pkg, "launch", "action_server.launch.py"])
            ),
        )],
    )

    # 3. ROS-TCP-Endpoint for Unity (delayed slightly)
    tcp_endpoint = TimerAction(
        period=10.0,
        actions=[Node(
            package="ros_tcp_endpoint",
            executable="default_server_endpoint",
            name="ros_tcp_endpoint",
            output="screen",
            parameters=[{"ROS_IP": ros_ip, "ROS_TCP_PORT": ros_tcp_port}],
        )],
    )

    return LaunchDescription(declared_args + [base_bringup, action_layer, tcp_endpoint])
