.PHONY: defult all build pkg clean rosdep

default: build

##################################################
# ROS2 workspace building targets.
##################################################
build:
	colcon build --continue-on-error --symlink-install --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

# Build a specific package by name.
pkg:
	@echo "Building package: $(pkg)"
	colcon build --packages-select $(pkg) --continue-on-error --symlink-install --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

rosdep:
	rosdep update && rosdep install --from-paths src --ignore-src -r -y

# Clean the colcon build.
clean:
	rm -rf build/ install/ log/


##################################################
# Dev devcontainer.
##################################################
# Run dev container and VSCodium
vs:
	devpod up --devcontainer-path .container/devcontainer.json --open-ide=true --ide=vscode .

# Stop and rerun container. Keeps container's ephemeral file system.
vs_restart:
	devpod up --devcontainer-path .container/devcontainer.json --open-ide=true --ide=vscode .

# Stop and rerun container. DELETES EPHEMERAL FILESYSTEM.
vs_reset:
	devpod up --devcontainer-path .container/devcontainer.json --open-ide=true --ide=vscode .

dev_up:
	devpod up --devcontainer-path .container/devcontainer.json --open-ide=false .

dev_restart:
	devpod up --devcontainer-path .container/devcontainer.json --open-ide=false --recreate .

dev_reset:
	devpod up --devcontainer-path .container/devcontainer.json --open-ide=false --reset .

##################################################
# Compose Container.
##################################################
cont:
	docker compose -f .container/compose.yml up -d rb-gpu 

cont_restart:
	docker compose -f .container/compose.yml restart rb-gpu 

cont_build:
	docker compose -f .container/compose.yml build 

##################################################
# Robot Compose Container.
##################################################
# Spawns container with SSH server running.
robot_cont:
	docker compose -f .container/compose.yml up -d rb-robot 

robot_cont_restart:
	docker compose -f .container/compose.yml restart rb-robot 

robot_cont_build:
	docker compose -f .container/compose.yml build 


##################################################
# Robot devcontainer.
##################################################
# # Make targets for running on the robot
# robot_cont:
# 	devpod up --devcontainer-path .container/robot-devcontainer.json --open-ide=false --ide=none .

# # Run the container and rebuild if devcontainer.json or Dockerfile is changed. Auto volumes are unaffected.
# robot_cont_recreate:
# 	devpod up --devcontainer-path .container/robot-devcontainer.json --open-ide=false --recreate .

# # Run container, wipe auto volumes and rebuild image if needed.
# robot_cont_reset:
# 	devpod up --devcontainer-path .container/robot-devcontainer.json --open-ide=false --reset .

# # Run container and VSCodium
# robot_vs:
# 	devpod up --devcontainer-path .container/robot-devcontainer.json --open-ide=true --ide=vscode .


##################################################
# Workspace setup.
##################################################
get_devpod:
	@echo "Installing devpod..."
	curl -L -o devpod "https://github.com/loft-sh/devpod/releases/latest/download/devpod-linux-amd64" && \
		sudo install -m 0755 devpod /usr/local/bin/devpod && \
		rm -f devpod && \
		( devpod provider list | grep -E '(^|\*)\s*docker(\s|$$)' >/dev/null || devpod provider add docker ) && \
		devpod provider use docker

# Run after sourcing system and workspace overlays.
venv:
	python3 -m venv .venv   --system-site-packages --symlinks
setup_workspace: get_devpod
	echo "Building and running container..."
	devpod up --devcontainer-path .devcontainer/devcontainer.json --ide=vscode .

robot_setup_workspace: get_devpod
	echo "Building and running container..."
	devpod up --devcontainer-path .devcontainer/robot-devcontainer.json --ide=vscode .
