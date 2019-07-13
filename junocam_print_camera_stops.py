#!/usr/bin/env python2

import sys
import os
import argparse
from sciimg.isis3.junocam import jcspice
from sciimg.isis3.junocam import modeling
from sciimg.isis3 import _core
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
    parser.add_argument("-s", "--scale", help="Mesh Scalar", required=False, type=float, default=1.0)
    parser.add_argument("-d", "--data", help="Source PDS datasets", required=True, type=str, nargs='+')

    args = parser.parse_args()

    scalar = args.scale

    data_homes = args.data
    kernelbase = args.kernelbase
    allow_predicted = args.predicted

    jcspice.load_kernels(kernelbase, allow_predicted)

    vecs = modeling.get_image_locations(data_homes, scalar)

    print(json.dumps(vecs, indent=4))