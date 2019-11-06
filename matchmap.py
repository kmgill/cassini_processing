#!/usr/bin/env python2
import sys
import os
import argparse
import traceback

from sciimg.isis3 import cameras
from sciimg.isis3 import _core

if __name__ == "__main__":

    try:
        _core.is_isis3_initialized()
    except:
        print("ISIS3 has not been initialized. Please do so. Now.")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Source cube file", required=True, type=str, nargs='+')
    parser.add_argument("-m", "--map", help="Input map", required=False, type=str)
    parser.add_argument("-o", "--output", help="Output Directory", required=True, type=str)
    parser.add_argument("-r", "--rings", help="Data is of ring plane", action="store_true")
    parser.add_argument("-s", "--skipexisting", help="Skip processing if output already exists", action="store_true")
    parser.add_argument("-p", "--reproject", help="Input files are already map projected", action="store_true")
    parser.add_argument("-b", "--bbox", help="bounding box as nn,nn,nn,nn (tl lon, lat; br lon, lat)", required=False, default=None)
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    args = parser.parse_args()

    source = args.data
    map = args.map
    output = args.output
    rings = args.rings
    skip_existing = args.skipexisting
    reprojecting = args.reproject
    bbox = args.bbox
    verbose = args.verbose

    if bbox is not None:
        bbox = bbox.split(",")
        # TODO: Seriously, start adding some error checking. And comment your damn code. For fuck's sake, Kevin!
    else:
        bbox = (None, None, None, None)

    for file_name in source:
        if file_name[-3:].upper() != "CUB":
            print("Not a ISIS cube file file. Skipping '%s'"%file_name)
        else:
            out_file = "%s/%s" % (output, file_name)
            if skip_existing and os.path.exists(out_file) :
                print("Output exists, skipping.")
            else:
                if reprojecting:
                    try:
                        s = cameras.map2map(file_name, out_file, map=map, minlat=bbox[3], maxlat=bbox[1], minlon=bbox[0], maxlon=bbox[2])
                        if verbose:
                            print(s)
                    except:
                        print("Reprojecting", file_name, "failed")
                        if verbose:
                            traceback.print_exc(file=sys.stdout)
                else:
                    try:
                        if not rings:
                            s = cameras.cam2map(file_name, out_file, map=map, resolution="MAP", minlat=bbox[3], maxlat=bbox[1], minlon=bbox[0], maxlon=bbox[2])
                        else:
                            s = cameras.ringscam2map(file_name, out_file, map=map, resolution="MAP")

                        if verbose:
                            print(s)
                    except:
                        print("Processing", file_name, "failed")
                        if verbose:
                            traceback.print_exc(file=sys.stdout)