import os
import sys
import time
from multiprocessing import Process, Queue
import numpy as np


# current_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.join(current_dir, "rp2daq"))
from current_pico.rp2daq import rp2daq

# Wrapper func to be run as a process.
def start_capture(*args, **kwargs):
    adc_reader = ADCReader(*args, **kwargs)
    adc_reader.start_capture()


class ADCReader:
    def __init__(self, data_queue, ksps_total=72, channels=[1, 2],
                 num_samples=180, required_device_id=""):
        self.ksps_total = ksps_total
        self.channels = channels
        self.num_samples = num_samples
        self.prev_etime_us = 0
        self.data_queue = data_queue # Ensure it holds only the latest data
        self.rp = rp2daq.Rp2daq(required_device_id=required_device_id)

    def adc_callback(self, **kwargs):
        """Handles incoming ADC data and updates the queue."""
        data = np.array(kwargs['data'])

        # self.data_queue.put((1))
        try:
            channel0 = np.sum(data[0::2]) / self.num_samples
            channel1 = np.sum(data[1::2]) / self.num_samples
            processed_data = np.array((channel0, channel1))

            # Ensure only latest data is kept
            if not self.data_queue.empty():
                self.data_queue.get_nowait()
            self.data_queue.put(processed_data)

        except Exception as e:
            print(f"ADC_callback error: {e}")

        # print("Packet received", len(data),
        #       -kwargs['start_time_us'] + kwargs['end_time_us'],
        #       -self.prev_etime_us + kwargs['start_time_us'])

        self.prev_etime_us = kwargs['end_time_us']

    def start_capture(self):
        """Starts ADC capture and processes data asynchronously."""
        print("Starting ADC...")

        self.rp.adc(
            channel_mask=sum(2 ** ch for ch in self.channels),
            blocksize=self.num_samples * len(self.channels),
            infinite=1,
            clkdiv=int(48000 // self.ksps_total),
            _callback=self.adc_callback
        )

        try:
            while True:
                time.sleep(1)  # Keeps the process alive
        except KeyboardInterrupt:
            print("ADC capture stopped.")

# Initialize and start ADC reader
if __name__ == "__main__":
    adc_reader = ADCReader()
    adc_reader.start_capture()

