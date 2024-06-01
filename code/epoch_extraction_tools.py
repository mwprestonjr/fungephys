"""
Epoch extraction tools.

This module contains functions for extracting epochs from a signal based on
threshold crossings. 

Functions:
----------
plot_epochs : Plots a signal over time, with annotations for epochs.
find_segments : Find segments of a signal that are above/below a threshold.
join_epochs_with_gap : Joins together epochs that have a gap shorter than a given minimum duration between them.
drop_short_epochs : Drop epochs shorter than a given duration.
get_inverse_epochs : Get inverse epochs from a given epoch array and signal.
get_epoch_times : Get epoch times based on the signal, threshold, minimum gap, and minimum duration.

"""


# imports
import numpy as np
import matplotlib.pyplot as plt


def get_epoch_times(signal, threshold, min_gap, min_duration, fs=1, plot=False):

    # id epochs above threshold
    epochs_above, epochs_below = get_epochs(signal, threshold=threshold, return_below=True)

    # join epochs
    epochs_above = join_epochs_with_gap(epochs_above/fs, min_gap=min_gap)
    epochs_below = join_epochs_with_gap(epochs_below/fs, min_gap=min_gap)

    # drop short epochs
    epochs_above = drop_short_epochs(epochs_above, min_duration=min_duration)
    epochs_below = drop_short_epochs(epochs_below, min_duration=min_duration)

    # plot epochs
    if plot:
        plot_epochs(signal, np.arange(len(signal))/fs, epochs_above, threshold)

    return epochs_above.astype(int), epochs_below.astype(int)


def plot_epochs(signal, time, epochs, threshold=None):
    """Plots a signal over time, with annotations for epochs.

    Parameters
    ----------
    signal : numpy array
        Signal to be plotted.
    time : numpy array
        Time stamps for the signal.
    epochs : 2D numpy array
        Epochs to annotate.
    threshold : float, optional
        Horizontal line at given value.

    Returns
    -------
    fig, ax : matplotlib Figure, Axes
        Figure and axes for the plot.
    """

    # plot signal
    fig, ax = plt.subplots(figsize=[20,4])
    ax.plot(time, signal)

    # annotate threshold
    if threshold is not None:
        ax.axhline(threshold, color='k')

    # annotate epochs
    # for t_start in np.array(epochs[:,0]):
    #     ax.axvline(t_start, color='b')
    # for t_stop in np.array(epochs[:,1]):
    #     ax.axvline(t_stop, color='r')
    for t_start, t_stop in epochs:
        ax.axvspan(t_start, t_stop, color='gray', alpha=0.5)

    return fig, ax


def get_epochs(signal, threshold, return_below=False):
    """
    Find segments of a signal that are above/below a threshold.
    
    Parameters
    ----------
        signal : array-like
            The signal to search for segments.
        threshold : float
            Threshold value to search for segments.
        return_below : bool, optional
            If True, return segments below threshold. Default is False.
            
    Returns
    -------
        epoch_times : array-like
            Start and end times of segments.
    """

    # get indices of segments above threshold
    above_threshold = np.where(signal > threshold)[0]
    if len(above_threshold) == 0:
        if return_below:
            return np.array([]), np.array([0, len(signal) - 1])
        else:
            return np.array([])

    # get start and end of segments
    starts = above_threshold[np.where(np.diff(above_threshold) != 1)[0] + 1]
    ends = above_threshold[np.where(np.diff(above_threshold) != 1)[0]]

    starts = np.insert(starts, 0, above_threshold[0])
    ends = np.append(ends, above_threshold[-1])

    # join epoch times as array
    epoch_times = np.array([starts, ends]).T

    # print number of epochs dropped
    print(f'Identified {epoch_times.shape[0]} epochs')

    # return segments below threshold if requested
    if return_below:
        if epoch_times[0][0] == 0:
            below_starts = ends
            below_ends = starts[1:]
        else:
            below_starts = np.insert(ends, 0, 0)
            below_ends = starts

        if epoch_times[-1][-1] == len(signal) - 1:
            below_starts = below_starts[:-1]
        else:
            below_ends = np.append(below_ends, len(signal) - 1)

        epochs_below = np.vstack([below_starts, below_ends]).T

        return epoch_times, epochs_below

    else:
        return epoch_times


def join_epochs_with_gap(epochs, min_gap):
    """
    Joins together epochs that have a gap shorter than a given minimum duration between them.

    Parameters
    ----------
    epochs : numpy array
        Nx2 array containing start and end times of each epoch. 
    min_gap : float
        Minimum duration of gap between epochs.

    Returns
    -------
    epochs_clean : numpy array
        Nx2 array containing the start and end times of the remaining epochs.
    """

    epochs_clean = []
    for ii in range(epochs.shape[0] - 1):
        gap = epochs[ii+1, 0] - epochs[ii, 1]

        # if gap is less than the minimun duration
        if gap < min_gap:
            # treat first differenctly
            if epochs_clean==[]:
                epochs_clean.append([epochs[ii, 0], epochs[ii+1, 1]])
            else:
                # check previous entry
                if epochs_clean[-1][1] == epochs[ii, 1]:
                    epochs_clean[-1][1] = epochs[ii+1, 1]
                else:
                    epochs_clean.append([epochs[ii, 0], epochs[ii+1, 1]])

        # if gap is long enough
        else:
            # treat first differenctly
            if epochs_clean==[]:
                epochs_clean.append(epochs[ii])
            else:
                # check previous entry
                if epochs_clean[-1][1] == epochs[ii, 1]:
                    continue
                else:
                    epochs_clean.append(epochs[ii])

    if len(epochs_clean) > 0:
        if epochs_clean[-1][1] == epochs[-1, 1]:
            pass
        else:
            epochs_clean.append(epochs[-1])

    epochs_clean = np.array(epochs_clean)

    # print number of epochs dropped
    print(f'Joined {epochs.shape[0] - epochs_clean.shape[0]} / {epochs.shape[0]} epochs')

    return epochs_clean


def drop_short_epochs(epochs, min_duration):
    """
    Drop epochs shorter than a given duration

    Parameters
    ----------
    epochs : ndarray
        2D array of epochs, of shape (n_epochs, 2).
    min_duration : float
        Minimum duration of epochs to keep.

    Returns
    -------
    epochs_clean : ndarray
        2D array of epochs, with epochs shorter than `min_duration` removed.
    """
    # handle cases of missing epochs
    if len(epochs)==0:
        return epochs

    # get duration of epochs
    duration = np.ravel(np.diff(epochs, axis=1))

    # drop epochs below threshold
    epochs_clean = epochs[duration > min_duration]

    # print number of epochs dropped
    print(f'Dropped {epochs.shape[0] - epochs_clean.shape[0]} / {epochs.shape[0]} epochs')

    return epochs_clean


def get_inverse_epochs(epochs, signal, fs=1):
    """
    Get inverse epochs from a given epoch array and signal.

    Parameters
    ----------
    epochs : array_like
        2-dimensional array of start and stop times of regular epochs.
    signal : array_like
        Signal array representing the signal being analyzed.

    Returns
    -------
    epochs_inv : array_like
        2-dimensional array of start and stop times of the inverse epochs.
    """

    # swap start and stop times
    start_times = np.insert(epochs[:,1], 0, 0) # insert 0 at the beginning
    stop_times = np.append(epochs[:,0], (len(signal)-1)/fs) # append last time point

    # if first epoch start on first time point, drop first stop time
    if epochs[0,0] == 0:
        start_times = start_times[1:]
        stop_times = stop_times[1:]

    # if last epoch ends on last time point
    if epochs[-1,1] == (len(signal)-1)/fs:
        start_times = start_times[:-1]
        stop_times = stop_times[:-1]

    # combine epoch times
    epochs_inv = np.vstack([start_times, stop_times]).T

    return epochs_inv
