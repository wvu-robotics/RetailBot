# import rp2daq
from current_pico.rp2daq import rp2daq
import time
import threading
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from multiprocessing import Process, Queue
import numpy as np
from plotter import animate

# Modifying code from https://github.com/FilipDominec/rp2daq/blob/main/example_ADC_async.py

ADC_channel_names = {0:"GPIO 26", 1:"GPIO 27", 2:"GPIO 28", 3:"ref V", 4:"builtin thermo"}
channels = [1,2]
kSPS_total = 72 # Will be divided by len(channels).

# Shared to plotting process.
data_queue = Queue(maxsize=1)

rp = rp2daq.Rp2daq()
# rp = rp2daq.Rp2daq(required_device_id='rp2daq_231005_E6612483CB58C423')
# rp = rp2daq.Rp2daq(required_device_id='E6612483CB58C423')

all_data = []
received_time = []
delayed = []


# Called from other thread whenever data come from RP2.
prev_etime_us = 0
def ADC_callback(**kwargs):  # Should be **kwargs?
    global t0, prev_etime_us, data_queue #?
    data = np.array(kwargs['data'])
    print(data.shape)

    try:
        # Get each channels data by alternate offsets
        num_samples = 1000
        # channel0 = sum(kwargs['data'][0::2])/num_samples
        # channel1 = sum(kwargs['data'][1::2])/num_samples
        channel0 = np.sum(data[0::2])/num_samples
        channel1 = np.sum(data[1::2])/num_samples
        print(f"{channel0=}, {channel1=}")

        data = np.array((channel0, channel1))
        data_queue.put(data) # Use np to divide list by int?
        # all_data.extend([data])

    except Exception as e:
        print(f"{e=}")

    print("Packet received", len(all_data), len(data),
            -kwargs['start_time_us']+ kwargs['end_time_us'],
            -prev_etime_us + kwargs['start_time_us'],
            rp._i.report_queue.qsize(), 
            (" DELAYED" if kwargs['block_delayed_by_usb'] else "") )
    prev_etime_us = kwargs['end_time_us']
    received_time.extend([time.time()]*(len(kwargs['data'])//len(channels)))



t0 = None
print("Starting ADC...")
rp.adc(channel_mask=sum(2**ch for ch in channels), 
        blocksize=1000*len(channels), 
       infinite=1,
       clkdiv=int(48000//kSPS_total), 
       _callback=ADC_callback)


print("Starting plotter process...")
anim_proc = Process(target=animate, args=(data_queue, channels))
anim_proc.start()

time.sleep(1000)


