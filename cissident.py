#!/usr/bin/env python
import os
import sys
import re
import subprocess
import datetime
import glob
import argparse
import numpy as np

from isis3 import utils
from isis3 import info

def printInfo(lbl_file_name):
    target = info.get_target(lbl_file_name)
    filter1, filter2 = info.get_filters(lbl_file_name)
    image_time = info.get_image_time(lbl_file_name)
    num_lines = info.get_num_lines(lbl_file_name)
    num_line_samples = info.get_num_line_samples(lbl_file_name)
    sample_bits = info.get_sample_bits(lbl_file_name)
    camera = "Narrow" if info.get_instrument_id(lbl_file_name) == "ISSNA" else "Wide"
    print "%25s|%5s|%5s|%22s|%5s|%5s|%4s|%8s| %s"%(target,
                                                filter1,
                                                filter2,
                                                image_time.strftime('%Y-%m-%d_%H.%M.%S'),
                                                num_lines,
                                                num_line_samples,
                                                sample_bits,
                                                camera,
                                                lbl_file_name)



if __name__ == "__main__":
    try:
        utils.is_isis3_initialized()
    except:
        print "ISIS3 has not been initialized. Please do so. Now."
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="PDS Label Files", required=False, type=str, nargs='+')
    args = parser.parse_args()

    data = args.data if args.data is not None else os.listdir(".")
    for file_name in data:
        if file_name[-3:].upper() in ("LBL", "CUB"):
            printInfo(file_name)
