""" Time utility functions """

# imports
from time import time


def get_start_time():

    return time()


def print_time_elapsed(t_start, prefix='Time elapsed: '):
    from time import time

    day, hour, min, sec = convert_seconds(time() - t_start)
    print(f"{prefix}{day} day {hour} hour, {min} min, and {sec :0.1f} s")


def print_duration(signal, fs):
    from time import time

    n_seconds = len(signal) / fs
    day, hour, min, sec = convert_seconds(n_seconds)
    print(f"{day} day {hour} hour, {min} min, and {sec :0.1f} s")


def convert_seconds(duration):
    """
    Convert duration in seconds to hours, minutes, and seconds.

    Parameters
    ----------
    duration : float
        Duration in seconds.

    Returns
    -------
    dayr, hour, min, sec : int
        Duration in days, hours, minutes, and seconds.
    """

    day = int(duration // 86400)
    hour = int(duration // 3600)
    min = int(duration % 3600 // 60)
    sec = int(duration % 60)
    
    return day, hour, min, sec