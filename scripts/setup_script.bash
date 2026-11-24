#!/bin/bash

# setup_script.bash
# By: Nathan Adkins 
# email: npa00003@mix.wvu.edu
# WVU IRL 

# Run this file to install of the dependencies required to properly run retailbot
# For any questions email: npa00003@mix.wvu.edu

UYellow='\033[4;33m'
Color_Off='\033[0m'
headersrt="setup_script.bash:"


printf "${UYellow}$headersrt${Color_Off} Installing python and python packages\n"
sudo apt install python3
sudo apt install python3-pip
python3 -m pip install pyserial numpy pyqtgraph


printf "${UYellow}$headersrt${Color_Off} Importing ROS Packages\n"
vcs import src < repos.yaml --recursive


printf "${UYellow}$headersrt${Color_Off} Installing ROS Packages \n"
sudo apt install ros-humble-navigation2
sudo apt install ros-humble-nav2-bringup
sudo apt-get install ros-humble-velodyne

sudo apt-get install ros-humble-perception-pcl

sudo add-apt-repository ppa:sweptlaser/python3-pcl
sudo apt update
sudo apt install python3-pcl

sudo add-apt-repository ppa:borglab/gtsam-release-4.0
sudo apt install libgtsam-dev libgtsam-unstable-dev
sudo apt-get install libboost-all-dev


printf "${UYellow}$headersrt${Color_Off} Installing Dependencies for ROS Packages\n"
sudo apt install python3-rosdep2
rosdep update
rosdep install --from-paths src --ignore-src -r -y