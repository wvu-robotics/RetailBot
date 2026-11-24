#!/bin/bash
# This is source'd by .bashrc

source /opt/ros/jazzy/setup.bash
echo "Sourced ROS jazzy"

export TERM=xterm-256color
export SHELL=/bin/bash

export ROS_DOMAIN_ID=96

alias ls='ls --color=auto'

if [[ "$(hostname)" == *robot* ]]; then
    export PS1="\[\e[1;34m\]\u@\h:\w\$ \[\e[0m\]"
else
    export PS1="\[\e[0;32m\]\u@\h:\w\$ \[\e[0m\]"
fi


if [[ -f "${ROS_WS}/install/setup.bash" ]] then
	echo "Sourcing workspace..."
	source ${ROS_WS}/install/setup.bash
fi

alias p="python3"
alias s="source ${ROS_WS}/install/setup.bash"
export XDG_CONFIG_HOME=~/.config
export FASTDDS_BUILTIN_TRANSPORTS=UDPv4
