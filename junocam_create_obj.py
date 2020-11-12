#!/usr/bin/env python

import sys
import os
import spiceypy as spice
import math
import numpy as np
import argparse
import glob
from sciimg.pipelines.junocam import jcspice
from sciimg.pipelines.junocam import modeling
from sciimg.isis3 import _core

if __name__ == "__main__":

    try:
        _core.is_isis3_initialized()
    except:
        print("ISIS3 has not been initialized. Please do so. Now.")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--label", help="Input JunoCam Label File (PVL formatted)", required=True, type=str)
    parser.add_argument("-r", "--red", help="Input Projected JunoCam Image for red (cube formatted)", required=True,
                        type=str)
    parser.add_argument("-k", "--kernelbase", help="Base directory for spice kernels", required=False, type=str,
                    default=os.environ["ISISDATA"])
    parser.add_argument("-p", "--predicted", help="Utilize predicted kernels", action="store_true")
    parser.add_argument("-o", "--output", help="Output file path", required=True, type=str, default=None)
    parser.add_argument("-s", "--scale", help="Mesh Scalar", required=False, type=float, default=1.0)
    parser.add_argument("-t", "--minlat", help="Minimum Latitude", required=False, type=float, default=None)
    parser.add_argument("-T", "--maxlat", help="Maximum Latitude", required=False, type=float, default=None)
    parser.add_argument("-n", "--minlon", help="Minimum Longitude", required=False, type=float, default=None)
    parser.add_argument("-N", "--maxlon", help="Maximum Longitude", required=False, type=float, default=None)
    args = parser.parse_args()

    lbl_file = args.label
    cube_file_red = args.red
    kernelbase = args.kernelbase
    allow_predicted = args.predicted
    output_file_path = args.output
    scalar = args.scale
    minlat = args.minlat
    maxlat = args.maxlat
    minlon = args.minlon
    maxlon = args.maxlon

    jcspice.load_kernels(kernelbase, allow_predicted)
    modeling.create_obj(lbl_file,
                        cube_file_red,
                        output_file_path,
                        allow_predicted=allow_predicted,
                        scalar=scalar,
                        minlat=minlat,
                        maxlat=maxlat,
                        minlon=minlon,
                        maxlon=maxlon)
