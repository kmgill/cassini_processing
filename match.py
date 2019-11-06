#!/usr/bin/env python2

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
    parser.add_argument("-f", "--filters", help="Require filter(s) or exit", required=False, type=str, nargs='+')
    parser.add_argument("-t", "--targets", help="Require target(s) or exit", required=False, type=str, nargs='+')
    parser.add_argument("-w", "--width", help="Require width or exit", required=False, type=str, nargs='+')
    parser.add_argument("-H", "--height", help="Require height or exit", required=False, type=str, nargs='+')
    parser.add_argument("-b", "--band", help="Data band", required=False, type=int, default=-1)
    args = parser.parse_args()

    filters = args.filters if args.filters is not None else []
    targets = args.targets if args.targets is not None else []

    require_height = args.height if args.height is not None else []
    require_width = args.width if args.width is not None else []

    filters = [f.upper() for f in filters]
    targets = [t.upper() for t in targets]

    band = args.band

    files = args.data

    match(files, targets, filters, require_width, require_height, band)