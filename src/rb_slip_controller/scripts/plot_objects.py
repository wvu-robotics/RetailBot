import numpy as np
from time import sleep
from twist_slip_msg.msg import TwistSlipStamped
from control_msgs.msg import DynamicJointState
import matplotlib.pyplot as plt
# from sensor_msgs.msg import JointState


class MessageBuffer():
    def __init__(self,length):
        self.data = np.recarray(length,dtype=int)

    # Copy in ros2 message and convert to the record array.
    def set_data(self,msg):
        ...

    # Copy over data from record array to Line2D objects.
    def update_lines(self):
        ...

class TwistSlipStampedBuffer(MessageBuffer):
    def __init__(self,length):
        # self.data_arr = np.zeros(5,length)
        self.length = length
        self.fields = np.array(['time','fl_wheel','br_wheel','bl_wheel','fr_wheel'])
        self.data = {label: np.zeros(length) for label in self.fields}
        self.lines = None
        self.start = 0 # Rotating buffer pointers
        self.end = 0


    def get_ax_lims(self,margin=0.15):
        # Find smallest value in array
        time_min = 0.0
        time_max = 0.0
        data_min = 0.0
        data_max = 0.0

        stacked_data = np.vstack([self.data[field] for field in self.fields if field != "time"])

        # Find the overall minimum and maximum
        data_min = np.min(stacked_data)
        data_max = np.max(stacked_data)
        data_range = data_max - data_min
        data_min -= margin * data_range
        data_max += margin * data_range

        time_min = np.min(self.data['time'])
        time_max = np.max(self.data['time'])
        time_range = time_max - time_min
        time_min -= margin * time_range
        time_max += margin * time_range

        return (time_min,time_max),(data_min,data_max)

    def create_lines(self,ax):
        # Dict of {label_name: Line2D}
        self.lines = {field: ax.plot([],[],label=field)[0] for field in
            self.fields if field != "time"}
        return self.lines

    # Update data from ros2 message.
    def update_data(self,msg: TwistSlipStamped):
        self.data['time'][self.end] = msg.header.stamp.sec
        self.data['fl_wheel'][self.end] =  msg.fl_wheel
        self.data['fr_wheel'][self.end] =  msg.fr_wheel
        self.data['br_wheel'][self.end] =  msg.br_wheel
        self.data['bl_wheel'][self.end] =  msg.bl_wheel

            # Check if the buffer is full.
        if self.end == self.start and self.end != 0:
            self.start = (self.start + 1) % self.length

        self.end = (self.end + 1) % self.length # Always increment end pointer.
        # print(f"{self.start=}, {self.end=}")

    # Draw data to lines.
    def update_lines(self):

        if self.start < self.end:
            # Case 1: No wrap-around, data is contiguous
            time_values = self.data['time'][self.start:self.end]
        else:
            # Case 2: Wrap-around, data is split into two sections
            time_values = np.concatenate((self.data['time'][self.start:], self.data['time'][:self.end]))

        # time_values = np.concatenate((self.data['time'][self.start:], self.data['time'][:self.start]))
        for line in self.lines:
            if self.start < self.end:
                # Case 1: No wrap-around
                values = self.data[line][self.start:self.end]
            else:
                # Case 2: Wrap-around
                values = np.concatenate((self.data[line][self.start:], self.data[line][:self.end]))

            # values = np.concatenate((self.data[line][self.start:], self.data[line][:self.start]))
            # self.lines[line].set_data(self.data['time'],values)
            self.lines[line].set_data(time_values,values)
        return list(self.lines.values())

# This would be our ROS node.
def test1():

    fig,ax = plt.subplots()
    twist_buff = TwistSlipStampedBuffer(50)
    twist_buff.create_lines(ax)

    ax.set_xlim(0,10)
    ax.set_ylim(0,10)
    ax.legend()

    # Simulate a subscriber callback.
    msg = TwistSlipStamped()
    for idx in range(300):
        msg.header.stamp.sec = idx
        msg.bl_wheel = np.random.uniform(0,5)
        twist_buff.update_data(msg)
        twist_buff.update_lines()
        time_lim, data_lim = twist_buff.get_ax_lims()
        ax.set_xlim(time_lim)
        ax.set_ylim(data_lim)
        plt.pause(0.1)
    print(twist_buff.data)


    plt.show()


if __name__ == "__main__":
    test1()
