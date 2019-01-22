#!/usr/bin/env python2

import sys
import os
import spiceypy as spice
import argparse
import glob
from sciimg.isis3 import info
from sciimg.isis3 import scripting
from sciimg.isis3 import importexport
from sciimg.isis3 import _core
import json
import glob

def load_kernels(kernelbase, allow_predicted=False):
    kernels = [
        "%s/juno/kernels/pck/pck00010.tpc"%kernelbase,
        "%s/juno/kernels/fk/juno_v12.tf"%kernelbase,
        "%s/juno/kernels/ik/juno_junocam_v02.ti"%kernelbase,
        "%s/juno/kernels/lsk/naif0012.tls"%kernelbase,
        "%s/juno/kernels/sclk/JNO_SCLKSCET.00074.tsc"%kernelbase,
        "%s/juno/kernels/tspk/de436s.bsp"%kernelbase,
        "%s/juno/kernels/tspk/jup310.bsp"%kernelbase,
        "%s/juno/kernels/spk/juno_struct_v04.bsp"%kernelbase
    ]

    kernel_prefix = "spk_rec_" if not allow_predicted else ""
    for file in glob.glob("%s/juno/kernels/spk/%s*bsp"%(kernelbase, kernel_prefix)):
        kernels.append(file)

    kernel_prefix = "juno_sc_rec_" if not allow_predicted else ""
    for file in glob.glob("%s/juno/kernels/ck/%s*bc"%(kernelbase, kernel_prefix)):
        kernels.append(file)

    for kernel in kernels:
        spice.furnsh(kernel)


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

    load_kernels(kernelbase, allow_predicted)

    vecs = []

    for data_home in data_homes:
        lbl_files = glob.glob('%s/*.lbl'%data_home)
        for lbl_file in lbl_files:
            image_time = spice.str2et(info.get_field_value(lbl_file, "IMAGE_TIME"))
            stop_name = info.get_field_value(lbl_file, "PRODUCT_ID")
            spacecraft_vec, lt = spice.spkpos('JUNO_SPACECRAFT', image_time, 'IAU_JUPITER', 'NONE', 'JUPITER')
            stop_spec = {
                "name": stop_name,
                "vec": ((spacecraft_vec[0] * scalar), (spacecraft_vec[1] * scalar), (spacecraft_vec[2] * scalar))
            }
            vecs.append(stop_spec)

    print(json.dumps(vecs, indent=4))