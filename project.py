#!/usr/bin/env python
import sys
import argparse

from isis3 import utils
from isis3 import cameras

if __name__ == "__main__":

    try:
        utils.is_isis3_initialized()
    except:
        print "ISIS3 has not been initialized. Please do so. Now."
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Source cube file", required=True, type=str, nargs='+')
    parser.add_argument("-p", "--projection", help="Desired map projection", required=False, type=str)
    parser.add_argument("-m", "--map", help="Input map", required=False, type=str)

    args = parser.parse_args()

    source = args.data
    projection = args.projection
    map = args.map

    if (projection is not None and map is not None) or (projection is None and map is  None):
        print "Please specify either a projection OR an input map"
        sys.exit(1)

    for file_name in source:
        if file_name[-3:].upper() != "CUB":
            print "Not a ISIS cube file file. Skipping '%s'"%file_name
        else:
            if map is None:
                out_file = "%s_%s.cub"%(file_name[0:-4], projection)
                cameras.cam2map(file_name, out_file, projection=projection)
            else:
                out_file = "%s_%s.cub" % (file_name[0:-4], "reprojected")
                cameras.cam2map(file_name, out_file, map=map, resolution="MAP")
