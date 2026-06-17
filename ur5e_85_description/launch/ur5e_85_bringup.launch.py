from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, IncludeLaunchDescription, RegisterEventHandler, TimerAction
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    declared_args = [
        DeclareLaunchArgument("ur_type", default_value="ur5e"),
        DeclareLaunchArgument("use_fake_hardware", default_value="true"),
    ]

    ur_type = LaunchConfiguration("ur_type")
    use_fake_hardware = LaunchConfiguration("use_fake_hardware")

    desc_pkg   = FindPackageShare("ur5e_85_description")
    moveit_pkg = FindPackageShare("ur5e_85_moveit_config")

    # ---- robot_description (URDF from our xacro) ----
    robot_description_content = Command([
        PathJoinSubstitution([FindExecutable(name="xacro")]), " ",
        PathJoinSubstitution([desc_pkg, "urdf", "ur5e_85.urdf.xacro"]), " ",
        "ur_type:=", ur_type, " ",
        "use_fake_hardware:=", use_fake_hardware,
    ])
    robot_description = {
        "robot_description": ParameterValue(value=robot_description_content, value_type=str)
    }

    # ---- ros2_control_node (controller manager) ----
    ros2_controllers_yaml = PathJoinSubstitution([
        moveit_pkg, "config", "ros2_controllers.yaml"
    ])
    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description, ros2_controllers_yaml],
        output="screen",
    )

    # ---- robot_state_publisher ----
    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description],
    )

    # ---- spawners ----
    jsb_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )
    arm_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["scaled_joint_trajectory_controller",
                   "--controller-manager", "/controller_manager"],
    )
    gripper_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["gripper_controller",
                   "--controller-manager", "/controller_manager"],
    )

    # ---- MoveIt move_group + RViz, delayed so controllers come up first ----
    move_group = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([moveit_pkg, "launch", "move_group.launch.py"])
        ),
    )
    moveit_rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([moveit_pkg, "launch", "moveit_rviz.launch.py"])
        ),
    )
    delayed_moveit = TimerAction(period=5.0, actions=[move_group, moveit_rviz])

    return LaunchDescription(declared_args + [
        rsp, control_node,
        jsb_spawner, arm_spawner, gripper_spawner,
        delayed_moveit,
    ])
