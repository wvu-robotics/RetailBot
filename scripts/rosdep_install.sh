#!/bin/bash
# Run rosdep through the src/ dir. Made this because I can't remember the command.
rosdep install --from-paths src -y --ignore-src
