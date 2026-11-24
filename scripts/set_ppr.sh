#!/bin/bash

# Define devices and baud rate
LEFT_DEVICE="/dev/left_roboteq"
RIGHT_DEVICE="/dev/right_roboteq"
BAUDRATE=9600
PPR_VALUE=1454

# Function to send a query or command using picocom
send_command() {
    local device=$1
    local command=$2
    echo -e "$command\r" > "$device"
    sleep 1
}

# Function to handle a specific device (query, set, and verify PPR)
handle_device() {
    local device=$1
    echo "Connecting to $device at $BAUDRATE baud rate..."
    picocom -b "$BAUDRATE" "$device" &

    # Wait a bit for picocom to establish the connection
    sleep 2

    # Step 1: Query the PPR configuration for both channels
    echo "Querying the current PPR values on $device..."
    send_command "$device" "~EPPR"

    # Step 2: Set the PPR values for both channels
    echo "Setting PPR values to $PPR_VALUE on $device..."
    send_command "$device" "^EPPR 0 $PPR_VALUE"
    send_command "$device" "^EPPR 1 $PPR_VALUE"

    # Step 3: Query again to verify the changes
    echo "Verifying the PPR values on $device..."
    send_command "$device" "~EPPR"

    # Step 4: Exit picocom (this sends Ctrl+A and then Ctrl+X to exit)
    killall picocom

    echo "Done with $device!"
}

# Handle both left and right devices
handle_device "$LEFT_DEVICE"
handle_device "$RIGHT_DEVICE"

echo "Process completed for both devices!"

