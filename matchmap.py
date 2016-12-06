#!/usr/bin/env python
import sys
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

    args = parser.parse_args()

    source = args.data
    map = args.map
    output = args.output

    for file_name in source:
        if file_name[-3:].upper() != "CUB":
            print "Not a ISIS cube file file. Skipping '%s'"%file_name
        else:
            out_file = "%s/%s" % (output, file_name)
            cameras.cam2map(file_name, out_file, map=map, resolution="MAP")