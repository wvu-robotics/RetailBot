#!/bin/bash

# setup_script.bash
# By: Nathan Adkins 
# email: npa00003@mix.wvu.edu
# WVU IRL

# This file is to prevent any crashes on retailbot while building the workspace's packages 
# To run this file, type the following into your terminal (ignore the '#'):
# ./colcon_build.bash

UYellow='\033[4;33m'
Color_Off='\033[0m'

headersrt="colcon_build.bash:"

printf "${UYellow}$headersrt${Color_Off} Building robot_localization\n"
colcon build --packages-select robot_localization 

printf "${UYellow}$headersrt${Color_Off} Building robot_localization\n"
colcon build --packages-select graph_based_slam 

printf "${UYellow}$headersrt${Color_Off} Building all packages\n"
BUILDFLAGS=-j4 colcon build --continue-on-error --parallel-workers 2 