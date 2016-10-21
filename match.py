
import os
import sys
import subprocess
import numpy as np
from os import listdir

minimum = 10000000000000
maximum = -10000000000000


cubNameFilter = []

for n in range(1, len(sys.argv)):
    filt = sys.argv[n]
    cubNameFilter.append(filt)


def matchesFilter(f):
    if len(cubNameFilter) == 0:
        return True
    for filt in cubNameFilter:
        if filt in f:
            return True
    return False


values = []
for f in listdir("."):
    if f[-3:] == "cub" and matchesFilter(f):
        out = subprocess.check_output(["stats", "from="+f])
        parts = out.split("\n")
        _min = float(parts[9].split("=")[1])
        _max = float(parts[10].split("=")[1])
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
        subprocess.call(["isis2std", "from="+f, "to="+totiff, "format=tiff", "bittype=u16bit", "stretch=manual", "minimum=%f"%minimum, "maximum=%f"%maximum])
