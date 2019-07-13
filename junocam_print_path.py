#!/usr/bin/env python2

import sys
import os
import spiceypy as spice
import argparse
from sciimg.isis3 import _core
from sciimg.isis3.junocam import jcspice
from sciimg.isis3.junocam import modeling
import json

if __name__ == "__main__":
    try:
        _core.is_isis3_initialized()
    except:
        print("ISIS3 has not been initialized. Please do so. Now.")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--kernelbase", help="Base directory for spice kernels", required=False, type=str,
                        default=os.environ["ISIS3DATA"])
    parser.add_argument("-p", "--predicted", help="Utilize predicted kernels", action="store_true")
    parser.add_argument("-b", "--begin", help="Beginning Time", required=True, type=str, default=None)
    parser.add_argument("-e", "--end", help="Ending Time", required=True, type=str, default=None)
    parser.add_argument("-s", "--scale", help="Mesh Scalar", required=False, type=float, default=1.0)
    parser.add_argument("-n", "--num", help="Number of points", required=False, type=int, default=250)
    args = parser.parse_args()

    scalar = args.scale
    begin = args.begin
    end = args.end
    num_points = args.num
    kernelbase = args.kernelbase
    allow_predicted = args.predicted

    jcspice.load_kernels(kernelbase, allow_predicted)

    begin_time = spice.str2et(begin)
    end_time = spice.str2et(end)

    vecs = modeling.get_perijove_path(begin_time, end_time, num_points, scalar)

    print(json.dumps(vecs, indent=4))

