from control_msgs.msg import DynamicJointState
import matplotlib.pyplot as plt
import numpy as np

def data_dict():
    ... 

def unpack_twist_slip(msg):
    return {
        "time": msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9,
        "fl_wheel": msg.fl_wheel,
        "bl_wheel": msg.bl_wheel,
        "br_wheel": msg.br_wheel,
        "fr_wheel": msg.fr_wheel,
        "linear_x": msg.twist.linear.x,
        "angular_z": msg.twist.angular.z,
    }    

def plot_process(queue):
    # Initialize plot
    fig, ax = plt.subplots()
    line1, = ax.plot([], [], 'b-')  # Create an empty line
    line2, = ax.plot([], [], 'b-')  # Create an empty line
    line3, = ax.plot([], [], 'b-')  # Create an empty line
    line4, = ax.plot([], [], 'b-')  # Create an empty line
    
    # Set axis limits
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 5)

    # wheel_vels = np.empty((4,1000))
    # bl_wheel_vel = []
    # br_wheel_vel = []
    # fr_wheel_vel = []
    # fl_wheel_vel = []
    time = []
    index = 0
    
    plt.ion()  # Turn on interactive mode
    plt.show()
    
    while True:
        if not queue.empty():
            data = queue.get()  # Get data from the queue
            if data is None:
                break  # Exit if None is received
            data = unpack_twist_slip(data)
            
            # if len(time) > 1:
            #     ax.set_xlim(min(time) - 1, max(time) + 1)
            #     ax.set_ylim(min(bl_wheel) - 1, max(bl_wheel) + 1)

            # Update plot
            # x, y = data
            # Weird race condition.

            # x_data.append(x)
            # y_data.append(y)

            time.append(data.time)
            # wheel_vels[:,index] = np.array(

            line.set_data(x_data, y_data)
            # ax.relim()
            # ax.autoscale_view()
            plt.draw()
            plt.pause(0.01)  # Pause to refresh the plot

            index += 1
