ARG DOCKER_REPO=ros
ARG ROS_DISTRO=jazzy
ARG IMAGE_SUFFIX= 

FROM $DOCKER_REPO:$ROS_DISTRO$IMAGE_SUFFIX AS rb-base

ARG USERNAME=rb
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Change from /bin/sh to using bash. Affects RUN,CMD,ENTRYPOINT.
SHELL ["/bin/bash", "-c"]

# Prevent warnings about pip as root and apt asking for input.
ENV PIP_ROOT_USER_ACTION=ignore
ENV TZ=Etc/UTC 
ENV DEBIAN_FRONTEND=noninteractive

ENV SHELL=/bin/bash

# Delete existing user if there's conflict.
RUN if id -u $USER_UID ; then userdel `id -un $USER_UID` ; fi
# Create the user. Set their default shell for SSH here.
RUN groupadd --gid $USER_GID $USERNAME \
	&& useradd --gid $USER_UID --uid $USER_GID -m $USERNAME -s $SHELL

# Make a home for our user and give them password-less sudo.
RUN echo ${USERNAME} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USERNAME} \
	&& chmod 0440 /etc/sudoers.d/${USERNAME} \
	&& mkdir -p /home/${USERNAME} \
	&& chown -R ${USER_UID}:${USER_GID} /home/${USERNAME}

# Give them permissions.
RUN usermod -aG video  $USERNAME && usermod -aG dialout  $USERNAME

RUN --mount=type=cache,target=/var/cache/apt \
	--mount=type=cache,target=/var/lib/apt/lists \
	apt-get update -y && apt-get install -y --no-install-recommends \
	ca-certificates curl

# Install general use packages that won't change often.
RUN --mount=type=cache,target=/var/cache/apt \
	--mount=type=cache,target=/var/lib/apt/lists \
	apt-get update -y && apt-get install -y --no-install-recommends \ 
	sudo \
	git \
	tmux \
	gdb \
	gdb-multiarch \
	curl \
	g++ \
	gcc \
	gcc-arm-none-eabi \
	clangd \
	clang \
	clang-format \
	make \
	cmake \
	npm \
	python3 \
	python-is-python3 \
	python3-pip \
	python3-numpy \
	python3-matplotlib \
	python3-pynvim \
	python3-venv \
	python3-clang \
	python3-tk \
	python3-colcon-common-extensions \
	python3-pynvim \
	python3-pandas \
	bash-completion \
	ytree \
	libboost-all-dev \
	apt-utils \
	lsb-release \
	wget \
	ssh \
	gnupg \
	openssh-server \
	xorg \
	x11-apps \
	xauth \
	libx11-dev \
	libx11-xcb1 \
	libxcb-icccm4 \
	libxcb-image0 \
	libxcb-keysyms1 \
	libxcb-randr0 \
	libxcb-render-util0 \
	libxcb-xinerama0 \
	libgl1 \
	libglx-mesa0 \
	automake \
	autoconf \
	build-essential \
	texinfo \
	libtool \
	libftdi-dev \
	libusb-1.0-0-dev \
	libhidapi-dev \
	jupyter-notebook \
	xclip \
	tree-sitter-cli \
	unzip \
	ripgrep \
	fd-find \
	libstdc++-arm-none-eabi-newlib \
	openocd \
	ncurses-bin \
	neovim

# ROS pkgs that won't change often.
RUN --mount=type=cache,target=/var/cache/apt \
	--mount=type=cache,target=/var/lib/apt/lists \
	apt-get update -y \
	&& apt-get install -y --no-install-recommends \
	ros-${ROS_DISTRO}-micro-ros-msgs \
	ros-${ROS_DISTRO}-rqt-graph \
	ros-${ROS_DISTRO}-gz-ros2-control \
	ros-${ROS_DISTRO}-ros2-control \
	ros-${ROS_DISTRO}-ros2-controllers \
	ros-${ROS_DISTRO}-robot-localization \
	ros-${ROS_DISTRO}-rviz-imu-plugin \
	ros-${ROS_DISTRO}-navigation2 \
	ros-${ROS_DISTRO}-nav2-bringup \
	ros-${ROS_DISTRO}-velodyne \
	ros-${ROS_DISTRO}-perception-pcl \
	ros-${ROS_DISTRO}-ros-gz \
	ros-${ROS_DISTRO}-gazebo-* \
	ros-${ROS_DISTRO}-teleop-twist-joy \
	ros-${ROS_DISTRO}-joint-state-publisher \
	ros-${ROS_DISTRO}-ros-gz* \
	ros-${ROS_DISTRO}-joint-state-publisher-gui \
	ros-${ROS_DISTRO}-gz-* \
	ros-${ROS_DISTRO}-teleop-twist-keyboard \
	ros-${ROS_DISTRO}-vrpn-mocap \
	ros-${ROS_DISTRO}-tf-transformations \
	ros-${ROS_DISTRO}-rosbag2-py \
	ros-${ROS_DISTRO}-rosbag2 

# Quicker build package adding...
RUN --mount=type=cache,target=/var/cache/apt \
	--mount=type=cache,target=/var/lib/apt/lists \
	apt-get update -y && apt-get install -y --no-install-recommends \ 
	python3-pyqtgraph \
	python3-scipy \
	python3-vcstool \
	python3-serial 
  # ros-${ROS_DISTRO}-zed_wrapper



# NPM Packages.
RUN npm install -g tree-sitter-cli

# TODO Fix version conflict with numpy and ... .
RUN pip install --break-system-packages \
	basedpyright \
	onshape-to-robot


# Set where user shell will be on container start.
WORKDIR /home/${USERNAME}/

# Act as $USER for rest of the build.
USER ${USERNAME}

# Run commands for every new shell opened in container. Usually bind mount over these later anyway.
COPY --chmod=0755 .container/entrypoint.sh /home/$USERNAME/.entrypoint.sh
COPY --chmod=0755 .container/env.sh /home/$USERNAME/.env.sh
RUN echo "source ~/.env.sh" >> /home/${USERNAME}/.bashrc
RUN echo "source ~/.bashrc" >> /home/${USERNAME}/.bash_profile

ENV SHELL=/bin/bash
# ENTRYPOINT ["/bin/bash","-c "]
# CMD ["/bin/bash", "-c"]
CMD ["sleep", "infinity"]
