# imports
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.signal import resample
from neurodsp.spectral import compute_spectrum
from neurodsp.plts import plot_power_spectra

# settings
FNAME_IN = 'data/temp.csv'
FNAME_OUT = 'figures/temp'
FS = 100

if __name__ == '__main__':
	# import data
	data = pd.read_csv(FNAME_IN)
	
	# plot signal time-series
	fig, ax = plt.subplots()
	ax.plot(data['time'], data['value'])
	ax.set(xlabel='time (s)', ylabel='value')
	fig.savefig(f"{FNAME_OUT}_timeseries.png")

    # resmple signal and plot
	duration = data['time'].iloc[-1] - data['time'].iloc[0]
	signal = resample(data['value'], int(duration*FS))
	time = np.linspace(0, len(signal)/FS, len(signal))
	fig, ax = plt.subplots()
	ax.plot(time, signal)
	ax.set(xlabel='time (s)', ylabel='value')
	fig.savefig(f"{FNAME_OUT}_timeseries_resampled.png")
	
	# compute and plot signal power spectrum
	freqs, powers = compute_spectrum(signal, FS)
	plot_power_spectra(freqs, powers, log_powers=True)
	plt.savefig(f"{FNAME_OUT}_spectrum.png")
	
	plt.close('all')
	
