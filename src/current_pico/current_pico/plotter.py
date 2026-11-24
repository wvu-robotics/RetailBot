import rp2daq
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from multiprocessing import Process, Queue
import numpy as np

ADC_channel_names = {0:"GPIO 26", 1:"GPIO 27", 2:"GPIO 28", 3:"ref V", 4:"builtin thermo"}

def animate(queue, channels=[1,2]):
    fig, ax = plt.subplots()
    ax.set_xlim(0, 100)
    ax.set_ylim(-3, 3)
    ax.set_xlabel("Time(sec)")
    ax.set_ylabel("Motor Current(Amps)")
    line1, = ax.plot([], [], 'b', lw=2, label='ADC27 Current')
    line2, = ax.plot([], [], 'r', lw=2, label='ADC28 Current')
    ax.set_title('Motor Currents 12kHz PWM Sampled at 20ksps, ~10bit resolution')
    txt_title = ax.text(1, 1.3, '', ha='center', fontsize=12)
    fig.legend()
    start_t = time.time()
    window_size = 50 # How many samples to show in the plot.
    right_margin = 20 # White space ahead of signal.


    data = [[],[]] #TODO Make of same size as len(channels).
    times = []

    # Will this work with lists?
    def calc_amps(val):
        print(f"{val=}")
        volts =  val / (4096.0 / 3.2) 
        amps = (volts - 1.48) / 0.528
        return amps

    def update(frame):
        try:
            # Data for ADC channels is interleaved into one list.
            # TODO Have start/stop times in queue objects as well.
            while not queue.empty():
                dat = queue.get_nowait()
            print(dat)
            amps = calc_amps(dat)
            # print(type(amps))

            elapsed_time = time.time() - start_t
            times.extend([elapsed_time])

            for idx, channel in enumerate(channels):
                data[idx].extend([amps[idx]])

            line1.set_data(times, data[0])
            line2.set_data(times, data[1])

            if elapsed_time - window_size > ax.get_xlim()[0]:
                ax.set_xlim(elapsed_time - window_size, elapsed_time + right_margin)

            # xlim = (elapsed_time - window_size, elapsed_time + right_margin)
            # ax.set_xlim(xlim[0], xlim[1])
            # txt_title.set_position((xlim[0] + (xlim[1] - xlim[0]) / 2, 3 * 0.85))
        except Exception as e:
            print(f"Plot updating: {e=}")
            return line1, line2, txt_title

        return line1, line2, txt_title

    # Blocking
    anim = FuncAnimation(fig, update, interval=0, blit=True)
    plt.show()

