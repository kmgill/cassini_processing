#!/usr/bin/env python
import os
import sys
import subprocess
import numpy as np
from os import listdir
import argparse


from isis3 import utils

if __name__ == "__main__":

    try:
        utils.is_isis3_initialized()
    except:
        print "ISIS3 has not been initialized. Please do so. Now."
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Source PDS dataset(s)", required=True, type=str, nargs='+')
    parser.add_argument("-f", "--filters", help="Require filter(s) or exit", required=False, type=str, nargs='+')
    parser.add_argument("-t", "--targets", help="Require target(s) or exit", required=False, type=str, nargs='+')
    args = parser.parse_args()

    filters = args.filters if args.filters is not None else []
    targets = args.targets if args.targets is not None else []

    filters = [f.upper() for f in filters]
    targets = [t.upper() for t in targets]

    matching_files = []

    for f in args.data:
        if f[-3:].upper() != "CUB":
            print "File %s is not supported, skipping"%f
            continue
        target = utils.get_target(f)
        filter1, filter2 = utils.get_filters(f)
        if len(targets) > 0 and  target.upper() not in targets:
            continue
        elif len(filters) > 0 and (filter1.upper() not in filters and filter2.upper() not in filters):
            continue
        else:
            matching_files.append(f)

    values = []
    for f in matching_files:
        _min, _max = utils.get_data_min_max(f)
        values.append(_min)
        values.append(_max)
        print _min, _max


    minimum = np.min(values)
    maximum = np.max(values)

    #maximum -= ((maximum - minimum) * 0.45)
    #minimum += ((maximum - minimum) * 0.35)

    for f in matching_files:
        totiff = f[:-4]+".tif"
        print totiff
        utils.export_tiff_grayscale(f, totiff, minimum=minimum, maximum=maximum)
