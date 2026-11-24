#!/bin/bash
colcon build --symlink-install --continue-on-error --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

if [ $? -eq 0 ]; then
	echo "Build successful, sourcing setup.bash..."
	source install/setup.bash
else
	echo "Build failed!"
fi

