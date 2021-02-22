#!/usr/bin/env python

import sys
import argparse

from sciimg.isis3 import _core

from sciimg.processes.match import match

if __name__ == "__main__":

    try:
        _core.is_isis3_initialized()
    except:
        print("ISIS3 has not been initialized. Please do so. Now.")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Source PDS dataset(s)", required=True, type=str, nargs='+')
    parser.add_argument("-b", "--band", help="Data band", required=False, type=int, default=1)
    args = parser.parse_args()

    band = args.band
    files = args.data

    match(files, band)
