#!/bin/bash

#sudo openocd -f interface/cmsis-dap.cfg -f target/rp2040.cfg -c "adapter speed 5000"

# Start OpenOCD in the background
sudo openocd -f interface/cmsis-dap.cfg -f target/rp2040.cfg -c "adapter speed 5000" 

# Wait a few seconds for OpenOCD to initialize
#sleep 2

# Start GDB and connect to the target
#gdb-multiarch build/imu_pico.elf -ex "target remote localhost:3333" -ex "monitor reset init"

