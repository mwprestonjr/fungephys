



# import
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from time_utils import convert_seconds


def import_data(fname, ch_names=None, zero_nan=True, return_labels=False,
               end_time=None, verbose=True):

    # import data
    if ch_names is None:
        df = pd.read_csv(fname)
    else:
        df = pd.read_csv(fname, skiprows=1, names=ch_names)

    # convert HH:MM:SS to seconds
    df = df.rename(columns={df.columns[0]: 'time'})
    df['time'] = pd.to_datetime(df['time']).dt.time
    df['time'] = pd.to_timedelta(df['time'].astype(str)).dt.total_seconds()

    # drop end of signal (trailing rows of NaN)
    if end_time is not None:
        df = df.loc[df['time'] <= end_time]

    # print info
    if verbose:
        total_time = df['time'].iloc[-1] - df['time'].iloc[0]
        day, hour, min, sec = convert_seconds(total_time)
        print(f"\tFilename: {fname}")
        print(f"\tDuration: {day} days, {hour} hours, {min} minutes, {sec} seconds")
        print(f"\tColumns: {df.columns.to_list()}")

    # set nan to 0
    if zero_nan:
        if verbose:
            n_nan = df.isna().sum().sum()
            total_values = df.shape[0] * df.shape[1]
            perc = n_nan / total_values * 100
            print(f"\tCleaning: {n_nan} NaN values were set to zero ({perc:0.0f}%)")
        df = df.fillna(0)

    # convert to numpy
    signals = df.iloc[:, 1:].to_numpy().T
    time = df['time'].to_numpy()
    labels = df.columns[1:]

    # return
    if return_labels:
        return signals, time, labels
    else:
        return signals, time
