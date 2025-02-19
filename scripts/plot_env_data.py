"""
Plot environmental data from CSV files.

Option to take path input from command line or use default path.


"""

# imports
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import argparse

# settings
INTERVAL = 60000


def main():

    # parse command line arguments
    parser = argparse.ArgumentParser(description='Plot environmental data.')
    parser.add_argument('--path', type=str, default='data/environment/', 
                        help='Path to the data folder')
    args = parser.parse_args()
    path = args.path

    # plot
    datalog, eventlog = import_data(path)
    fig, axes = init_fig()
    plot_sensor_data(datalog, eventlog, axes)
    anim = FuncAnimation(fig, update_plot, interval=INTERVAL, fargs=(path, axes),
                            cache_frame_data=False)
    plt.show()


def update_plot(frame, path, axes):
    datalog, eventlog = import_data(path)
    plot_sensor_data(datalog, eventlog, axes)


def import_data(path):
    # Read in the datalog 
    datalog = pd.read_csv(f"{path}/datalog.csv")
    datalog, start_time = create_time_column(datalog)
    datalog.rename(columns={'temperature': 'temperature_c'}, inplace=True)
    datalog.insert(3, 'temperature', datalog['temperature_c'] * 9/5 + 32)

    # Read in the eventlog
    eventlog = pd.read_csv(f"{path}/eventlog.csv")
    eventlog, _ = create_time_column(eventlog, start_time)

    return datalog, eventlog


def create_time_column(df, start_time=None):
    # convert datetime column to create seconds column
    df.rename(columns={'time': 'datetime'}, inplace=True)
    df['datetime'] = pd.to_datetime(df['datetime'])
    if start_time is None:
        df.insert(1, 'time', (df['datetime'] - df['datetime'].min()).dt.total_seconds())
        start_time = df['datetime'].min()
    else:
        df.insert(1, 'time', (df['datetime'] - start_time).dt.total_seconds())

    return df, start_time


def get_event_times(datalog, eventlog):
    start_times = eventlog.loc[eventlog['command'] == 'H', 'time'].values
    end_times = eventlog.loc[eventlog['command'] == 'h', 'time'].values

    # make sure the first event is a start event and the last event is an end event
    if len(start_times) > 0 and len(end_times) > 0:
        if end_times[0] < start_times[0]:
            start_times = np.insert(start_times, 0, 0)
        if len(start_times) > len(end_times):
            end_times = np.append(end_times, datalog['time'].max())

    # convert to datetime
    start_times = pd.to_datetime(datalog['datetime'].min() + pd.to_timedelta(start_times, unit='s'))
    end_times = pd.to_datetime(datalog['datetime'].min() + pd.to_timedelta(end_times, unit='s'))

    return start_times, end_times


def plot_sensor_data(datalog, eventlog, axes):
    # plot environmental data
    features = ['temperature', 'humidity', 'light']
    title = ['Temperature', 'Humidity', 'Light']
    ylabels = ['temperature (°F)', 'humidity (%)', 'light (ON/OFF)']
    for ax, feature, title, ylabel in zip(axes, features, title, ylabels):
        ax.plot(datalog['datetime'], datalog[feature], color='k', linewidth=3)
        ax.set_ylabel(ylabel)
        ax.set_title(title)

    # plot events (shade times when devices are ON)
    start_times, end_times = get_event_times(datalog, eventlog)
    for ax in axes[:2]:
        for start, end in zip(start_times, end_times):
            ax.axvspan(start, end, color='b', alpha=0.3)

    # annotate xticks every hour (top of every hour i.e. 1:00, 2:00 etc.)
    first_hour = datalog['datetime'].min().floor('h')
    last_hour = datalog['datetime'].max().ceil('h')
    xticks = pd.date_range(start=first_hour, end=last_hour, freq='h')
    xtick_labels = [f"{t.hour}:00" for t in xticks]
    axes[2].set_xticks(xticks)
    axes[2].set_xticklabels(xtick_labels)
    axes[2].set_xlabel('Time')

    # label
    axes[2].set_yticks([0, 1], ['OFF', 'ON'])

    # format and show
    plt.tight_layout()


def init_fig():
    # create figure
    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

    # color background of ideal ranges
    axes[0].axhspan(65, 75, color='g', alpha=0.2)
    axes[0].axhspan(60, 65, color='y', alpha=0.2)
    axes[0].axhspan(75, 80, color='y', alpha=0.2)
    axes[0].axhline(80, color='r', linewidth=5, alpha=0.2)
    axes[0].axhline(60, color='r', linewidth=5, alpha=0.2)
    axes[1].axhspan(90, 100, color='g', alpha=0.2)
    axes[1].axhspan(85, 90, color='y', alpha=0.2)
    axes[1].axhline(85, color='r', linewidth=5, alpha=0.2)
    axes[2].axhspan(-0.5, 0.5, color='grey', alpha=0.2)
    axes[2].axhspan(0.5, 1.5, color='grey', alpha=0.1)

    return fig, axes


if __name__ == "__main__":
    main()