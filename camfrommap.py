#!/usr/bin/env python
import sys
import os
import argparse

from isis3 import utils
from isis3 import cameras
from isis3 import _core
from isis3 import utility


def map2cam(file_name, cam_file, output_dir):
    out_file = "%s/%s" % (output_dir, file_name)
    cameras.map2cam(file_name, out_file, cam_file)
    pass

if __name__ == "__main__":

    try:
        _core.is_isis3_initialized()
    except:
        print "ISIS3 has not been initialized. Please do so. Now."
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Source cube file", required=True, type=str, nargs='+')
    parser.add_argument("-m", "--match", help="Input cube to match", required=False, type=str)
    parser.add_argument("-o", "--output", help="Output Directory", required=True, type=str)
    args = parser.parse_args()

    source = args.data
    match = args.match
    output = args.output
    padding = args.padding

    for file_name in source:
        if file_name[-3:].upper() != "CUB":
            print "Not a ISIS cube file file. Skipping '%s'"%file_name
        else:
            map2cam(file_name, match, output, padding)