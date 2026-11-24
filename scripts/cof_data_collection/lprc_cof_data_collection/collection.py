import csv
from datetime import datetime
from matplotlib import animation 
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np 
import datetime as dt


def playback_data(played_file: str, animation_file_name: str ):

    column_names = ['type', 'X_val', 'Y_val', 'CoF_val', 'time','name']
    save_dir = 'scripts/cof_data_collection/lprc_cof_data_collection/csv_data/07_28_23/'
    data = pd.read_csv(save_dir + played_file, header=None, names=column_names)

    data['time'] = pd.to_datetime(data['time'])
    data.sort_values('time', inplace=True)
    fig, ax = plt.subplots()

    def update(num):
        ax.clear()
        ax.scatter(data['Y_val'].iloc[:num], data['X_val'].iloc[:num], c=data['CoF_val'].iloc[:num], cmap='gray_r', vmin=0, vmax=1)
        ax.set_ylim([data['Y_val'].min(), data['Y_val'].max()])
        ax.set_xlim([data['X_val'].min(), data['X_val'].max()])
        plt.gca().set_title('Time: {}'.format(data['time'].iloc[num]))

    ani = FuncAnimation(fig, update, frames=range(len(data)), repeat=False)
    ani.save(animation_file_name, writer='pillow')
    plt.show()


def playback_data_grayscale(csv_file, save_as):
    data = pd.read_csv(csv_file, header=None)
    data.columns = ['CoF type', 'X Position', 'Y Position', 'CoF', 'Time', 'Name']
    data['Time'] = pd.to_datetime(data['Time'], format='%m/%d/%Y %H:%M:%S')
    data['Timestamp'] = data['Time'].map(dt.datetime.timestamp)
    
    unique_timestep_diff = data['Timestamp'].diff().dropna().min()
    fig, ax = plt.subplots()
    scat = ax.scatter([], [], c=[], cmap='gray', vmin=0, vmax=1)

    def init():
        ax.set_xlim([data['X Position'].min(), data['X Position'].max()])
        ax.set_ylim([data['Y Position'].min(), data['Y Position'].max()])
        return scat,

    def animate(i):
        current_data = data[data['Timestamp'] <= i]
        scat.set_offsets(np.c_[current_data['X Position'], current_data['Y Position']])
        scat.set_array(current_data['CoF'])
        return scat,

    ani = animation.FuncAnimation(fig, animate, frames=np.arange(0, data['Timestamp'].max(), unique_timestep_diff), 
                                  interval=200, repeat=False, init_func=init, blit=True)
    
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
    ani.save(save_as, writer=writer)

    print(f'Video saved as {save_as}')


def record_data(static_file_path: str, dynamic_file_path: str):

    dir = 'scripts/cof_data_collection/lprc_cof_data_collection/csv_data/'

    while True:
        
        CoF_Type = input("CoF Type:\n")
        X_val = input("x value:\n")
        Y_val = input("y value:\n")
        CoF_val = input("CoF value:\n")
        person_recording = input("Person:\n")
        time = datetime.now().strftime('%m/%d/%Y %H:%M:%S')

        written_line = [CoF_Type, X_val , Y_val, CoF_val, time, person_recording]

        if CoF_Type.upper().startswith("S"):
            file_path: str= static_file_path
        elif CoF_Type.upper().startswith("D"):
            file_path: str= dynamic_file_path
        else:
            file_path: str = "backup_data.csv"

        with open(dir + file_path,"a+",newline='') as file:
            file_writer = csv.writer(file)
            file_writer.writerow(written_line)
            print(f"Data was written: {written_line}")


def main():
    # static_file: str = 'static_data.csv'
    # dynamic_file: str = 'dynamic_data.csv'
    # record_data(static_file, dynamic_file)

    saved_file_name: str = 'hi.mp4'
    played_file_path: str = 'scripts/cof_data_collection/lprc_cof_data_collection/csv_data/07_28_23/static_data.csv'
    playback_data_grayscale(played_file_path, saved_file_name)


if __name__ == '__main__':
    main()