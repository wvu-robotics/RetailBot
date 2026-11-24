# Data Analysis


## Launching a Jupyter Notebook
It is recommended to run this from inside the container so that you can use the
ROS2 libraries and import custom messages from our workspace. It is also
recommended to use a virtual env which can be created from the requirements.txt
file like so,

`python3 -m venv .venv && source .venv/bin/activate && pip install -r
requirements.txt`

Then run the `./run_jup.sh` script. Copying the addresses which are printed to
your browser will open the jupyter browser.

File paths will be relative to the top level of the repo. E.g a path for a bag
file would be something like 

`bag_path =
"logging/2025_2_16_rosbags/2025_2_16__17_35_4130RPMback_60RPMfront_v2.bag/2025_2_16__17_35_4130RPMback_60RPMfront_v2.bag_0.mcap"`
