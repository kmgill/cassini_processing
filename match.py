#!/usr/bin/python
import os
import sys
import subprocess
import numpy as np
from os import listdir

from isis3 import utils

def matchesFilter(f):
    if len(cubNameFilter) == 0:
        return True
    for filt in cubNameFilter:
        if filt in f:
            return True
    return False

if __name__ == "__main__":

    try:
        utils.is_isis3_initialized()
    except:
        print "ISIS3 has not been initialized. Please do so. Now."
        sys.exit(1)

    cubNameFilter = []

    for n in range(1, len(sys.argv)):
        filt = sys.argv[n]
        cubNameFilter.append(filt)

    values = []
    for f in listdir("."):
        if f[-3:] == "cub" and matchesFilter(f):
            _min, _max = utils.get_data_min_max(f)
            values.append(_min)
            values.append(_max)
            print _min, "%f"%_max


    minimum = np.min(values)
    maximum = np.max(values)

    #maximum -= ((maximum - minimum) * 0.45)
    #minimum += ((maximum - minimum) * 0.35)

    for f in listdir("."):
        if f[-3:] == "cub" and matchesFilter(f):
            totiff = f[:-4]+".tif"
            print totiff
            utils.export_tiff_grayscale(f, totiff, minimum=minimum, maximum=maximum)
