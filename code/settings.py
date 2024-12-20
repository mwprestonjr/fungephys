"""
Global settings for project.

"""

import numpy as np

COLORS = ["#1b9e77", "#d95f02", "#7570b3", "#e7298a"]

SPECPARAM_SETTINGS = {
    'peak_width_limits' :   [2, np.inf], # default : (0.5, 12.0) - recommends at least frequency resolution * 2
    'min_peak_height'   :   0, # default : 0
    'max_n_peaks'       :   4, # default : inf
    'peak_threshold'    :   3 # default : 2.0
}
N_JOBS = -1 # for parallelization
