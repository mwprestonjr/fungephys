"""
Plotting functions

"""

# impots
import numpy as np
import matplotlib.pyplot as plt


def beautify_ax(ax):
    """
    Beautify axis by removing top and right spines.
    """
    
    # remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def plot_signals(signals, time, ax=None, labels=None, title=None, ylabel=None, 
                 save_path=None):
    """
    Plot signals from a dataframe

    Parameters
    ----------
    signals : numpy.ndarray
        Signals to plot. Can be 1D or 2D
    time : numpy.ndarray
        Time values for the signals
    ax : matplotlib.axes.Axes, optional
        Axis to plot on. If None, a new figure is created
    labels : list, optional
        Labels for the signals
    title : str, optional
        Title of the plot
    ylabel : str, optional
        Label for the y-axis. If None, defaults to "voltage (uV)"
    save_path : str, optional
        Path to save the plot, by default None

    Returns
    -------
    fig, ax
        Matplotlib figure and axis objects
    """

    # Init figure
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 6))

    # plot single signal
    if signals.ndim == 1:
        ax.plot(time, signals)

    # plot multiple signals
    elif signals.ndim == 2:
        for i, signal in enumerate(signals):
            if labels is None:
                ax.plot(time, signal, label=f"signal {i}", alpha=0.7)
            else:
                ax.plot(time, signal, label=labels[i])
        ax.legend()
    else:
        raise ValueError(f"signals must be 1D or 2D. Shape of signals: {signals.ndim}")
        
    # label figure
    ax.set_xlabel("time (s)")
    if title:
        ax.set_title(title)
    if ylabel:
        ax.set_ylabel(ylabel)
    else:
        ax.set_ylabel("voltage (uV)")

    # save figure
    if save_path:
        plt.savefig(save_path)


def plot_signals_df(df, title=None, ylabel=None, save_path=None):
    """
    Plot signals from a dataframe

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe containing signals to plot
    title : str, optional
        Title of the plot
    ylabel : str, optional
        Label for the y-axis. If None, defaults to "voltage (uV)"
    save_path : str, optional
        Path to save the plot, by default None

    Returns
    -------
    fig, ax
        Matplotlib figure and axis objects
    """

    # plot signals
    fig, ax = plt.subplots(figsize=(12, 6))
    for col in df.columns[1:]:
        ax.plot(df['time'], df[col], label=col)

    # label figure
    ax.legend()
    ax.set_xlabel("time (s)")
    if title:
        ax.set_title(title)
    if ylabel:
        ax.set_ylabel(ylabel)
    else:
        ax.set_ylabel("voltage (uV)")

    # save figure
    if save_path:
        plt.savefig(save_path)

    return fig, ax


def plot_spectra(spectra, freqs, ax=None, shade_sem=True, plot_each=False,
                 y_units='\u03BCV\u00b2/Hz', title=None, fname=None, **kwargs):
    
    """
    Plot power spectra. 

    Parameters
    ----------
    spectra : 2d array
        Power spectra [n_spectra x n_frequencies].
    freqs : 1d array
        Frequency values corresponding to PSD values.
    ax : matplotlib axis, optional
        Axis to plot on. The default is None.
    shade_sem : bool, optional
        Whether to shade SEM. The default is True.
    plot_each : bool, options
        Whether to plot each spectra. The default is False.
    y_units : str, optional
        Units for y-axis. The default is '\u03BCV\u00b2/Hz' (microvolts).
    title : str, optional
        Title for plot. The default is None.
    fname : str, optional
        File name to save figure. The default is None.
    **kwargs : dict
        Additional keyword arguments for plotting.

    Returns
    -------
    fig, ax : matplotlib figure and axis
        Figure and axis.
    """

    # check axis
    if ax is None:
        fig, ax = plt.subplots(1,1, figsize=[6,4])

    # check psds are 2d
    if not spectra.ndim == 2:
        raise ValueError('PSD must be 2d arrays.')
    
    # remove rows containing all nans
    spectra = spectra[~np.isnan(spectra).all(axis=1)]

    # plot mean spectra for each condition
    ax.loglog(freqs, np.mean(spectra, axis=0), **kwargs)
    
    # shade between SEM of spectra for each condition
    if shade_sem and not plot_each:
        lower = np.mean(spectra, 0) - (np.std(spectra, 0)/np.sqrt(spectra.shape[0]))
        upper = np.mean(spectra, 0) + (np.std(spectra, 0)/np.sqrt(spectra.shape[0]))
        ax.fill_between(freqs, lower, upper, alpha=0.5, edgecolor=None, **kwargs)

    if plot_each:
        for i_spec in range(len(spectra)):
            ax.loglog(freqs, spectra[i_spec], alpha=0.5)

    # set axes ticks and labels
    ax.set_ylabel(f'power ({y_units})')
    ax.set_xlabel('frequency (Hz)')

    # add title
    if title is None:
        ax.set_title('Power spectra')
    else:
        ax.set_title(title)

    # add grid
    ax.grid(True, which='major', axis='both', linestyle='--', linewidth=0.5)
    
    # return
    if fname is not None:
        plt.savefig(fname)


