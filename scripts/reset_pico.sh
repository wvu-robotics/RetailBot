#!/bin/bash
echo '3-2.2' | sudo tee /sys/bus/usb/drivers/usb/unbind
sleep 1
echo '3-2.2' | sudo tee /sys/bus/usb/drivers/usb/bind
