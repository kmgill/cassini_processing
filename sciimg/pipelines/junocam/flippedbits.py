import numpy as np
import itertools as it
from scipy import signal
from scipy.interpolate import interp1d

def fix_flipped_bits(image_data):

    print("Creating median filter...")
    md = signal.medfilt2d(image_data, kernel_size=3)

    print("Testing pixels for variance...")
    for a, b in it.product(range(1, image_data.shape[0] - 1), range(1, image_data.shape[1] - 1)):
        if abs(image_data[a][b] - md[a][b]) > 10.0:
            image_data[a][b] = np.nan

    print("Filling identified pixels...")
    for a in range(1, image_data.shape[0] - 1):
        x = image_data[a]
        not_nan = np.logical_not(np.isnan(x))
        indices = np.arange(len(x))
        interp = interp1d(indices[not_nan], x[not_nan])
        image_data[a] = np.interp(indices, indices[not_nan], x[not_nan])
