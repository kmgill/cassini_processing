#!/usr/bin/env python

import sys
import argparse

from sciimg.isis3 import _core
import sciimg.isis3.importexport as importexport

if __name__ == "__main__":

    try:
        _core.is_isis3_initialized()
    except:
        print("ISIS3 has not been initialized. Please do so. Now.")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Source cube file", required=True, type=str, nargs='+')
    parser.add_argument("-b", "--band", help="Data band", required=False, type=int, default=1)

    args = parser.parse_args()

    source = args.data
    band = args.band

    for file_name in source:
        if file_name[-3:].upper() != "CUB":
            print("Not a ISIS cube file file. Skipping '%s'"%file_name)
        else:
            out_file_tiff = "%s.tif"%file_name[:-4]
            importexport.isis2std_grayscale(file_name, out_file_tiff, minimum=None, maximum=None, band=band)
