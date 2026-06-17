# ur5e_2f85_bringup

ROS 2 Humble packages integrating a Universal Robots UR5e with a Robotiq 2F-85 adaptive gripper, with MoveIt 2 motion planning.

## Packages

- **ur5e_85_description** -- combined URDF (UR5e + 2F-85), RViz config, and bringup launch with mock hardware.
- **ur5e_85_moveit_config** -- MoveIt 2 configuration: SRDF with two planning groups (ur_manipulator, gripper), kinematics, controllers, and named poses (home, ready, open, close).

## Dependencies

Tested on Ubuntu 22.04 + ROS 2 Humble + MoveIt 2.

    sudo apt install ros-humble-desktop ros-humble-moveit \
                     ros-humble-moveit-setup-assistant \
                     ros-humble-joint-state-publisher-gui \
                     ros-humble-ros2-control ros-humble-ros2-controllers

## Setup

    mkdir -p ~/ur5e_2f85/src && cd ~/ur5e_2f85/src

    # This repo
    git clone <YOUR-REPO-URL> ur5e_2f85_bringup

    # Upstream dependencies
    git clone -b humble https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver.git
    git clone -b ros2   https://github.com/UniversalRobots/Universal_Robots_ROS2_Description.git
    git clone -b humble https://github.com/PickNikRobotics/ros2_robotiq_gripper.git
    git clone -b ros2   https://github.com/tylerjw/serial.git

    cd ~/ur5e_2f85
    rosdep install --ignore-src --from-paths src -y -r
    colcon build --symlink-install
    source install/setup.bash

## Usage

View the robot model in RViz:

    ros2 launch ur5e_85_description view_robot.launch.py

MoveIt with mock hardware:

    ros2 launch ur5e_85_description ur5e_85_bringup.launch.py

This starts the controller manager with mock UR and Robotiq hardware, spawns joint_state_broadcaster, scaled_joint_trajectory_controller, and gripper_controller, and brings up MoveIt's move_group + RViz.

In RViz, use the MotionPlanning panel to plan and execute trajectories for either group.

## Roadmap

- [x] Combined UR5e + 2F-85 URDF
- [x] MoveIt 2 configuration with two planning groups
- [x] Mock-hardware bringup with working Plan & Execute
- [ ] Real-hardware bringup (UR driver + Robotiq driver)
- [ ] Unity to ROS 2 action bridge for teleoperation

## License

Apache-2.0
