#!/bin/bash

sudo openocd -f interface/cmsis-dap.cfg -f target/rp2040.cfg -c "adapter speed 5000" -c "program build/imu_pico.elf verify reset exit"
