#!/usr/bin/env python
import sys
import os
import argparse

from isis3 import utils
from isis3 import cameras
from isis3 import _core

if __name__ == "__main__":

    try:
        _core.is_isis3_initialized()
    except:
        print "ISIS3 has not been initialized. Please do so. Now."
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Source cube file", required=True, type=str, nargs='+')
    parser.add_argument("-m", "--map", help="Input map", required=False, type=str)
    parser.add_argument("-o", "--output", help="Output Directory", required=True, type=str)
    parser.add_argument("-r", "--rings", help="Data is of ring plane", action="store_true")
    parser.add_argument("-s", "--skipexisting", help="Skip processing if output already exists", action="store_true")
    parser.add_argument("-p", "--reproject", help="Input files are already map projected", action="store_true")

    args = parser.parse_args()

    source = args.data
    map = args.map
    output = args.output
    rings = args.rings
    skip_existing = args.skipexisting
    reprojecting = args.reproject

    for file_name in source:
        if file_name[-3:].upper() != "CUB":
            print "Not a ISIS cube file file. Skipping '%s'"%file_name
        else:
            out_file = "%s/%s" % (output, file_name)
            if skip_existing and os.path.exists(out_file) :
                print "Output exists, skipping."
            else:
                if reprojecting:
                    try:
                        cameras.map2map(file_name, out_file, map=map)
                    except:
                        print "Reprojecting", file_name, "failed"
                else:
                    try:
                        if not rings:
                            cameras.cam2map(file_name, out_file, map=map, resolution="MAP")
                        else:
                            cameras.ringscam2map(file_name, out_file, map=map, resolution="MAP")
                    except:
                        print "Processing", file_name, "failed"