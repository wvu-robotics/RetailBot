#!/bin/bash
#mkdir -p output

onshape-to-robot .

# Add xacro include. Hacky and bad but so is everything XML.
#sed -i '0,/<robot /s/<robot /<robot xmlns:xacro="http:\/\/www.ros.org\/wiki\/xacro" /' rb.urdf

# Fix paths for meshes. No way to turn off merged/ output dir right now.
sed -i 's|meshes/merged/|meshes/|g' rb.urdf

# Install output. Overwrite what's there.
cp rb.urdf ../urdf/
cp -r meshes/merged/* ../meshes/

