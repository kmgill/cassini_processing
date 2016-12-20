#!/usr/bin/env python
import sys
import os
import argparse

from isis3 import utils
from isis3 import cameras
from isis3 import _core
from isis3 import utility



def match_cam(from_cube, match_cube, output_dir, pad=2000):
    source_dirname = os.path.dirname(from_cube)
    if source_dirname == "":
        source_dirname = "."

    work_dir = "%s/work" % source_dirname
    if not os.path.exists(work_dir):
        os.mkdir(work_dir)

    padded_match_file = "%s/__padded__%s" % (work_dir, match_cube)
    padded_file = "%s/%s" % (work_dir, file_name)
    out_file = "%s/%s" % (output_dir, file_name)

    utility.pad(from_cube, padded_file, top=pad, right=pad, bottom=pad, left=pad)
    utility.pad(match_cube, padded_match_file, top=pad, right=pad, bottom=pad, left=pad)

    cameras.cam2cam(padded_file, out_file, padded_match_file)

    os.unlink(padded_file)
    os.unlink(padded_match_file)


if __name__ == "__main__":

    try:
        _core.is_isis3_initialized()
    except:
        print "ISIS3 has not been initialized. Please do so. Now."
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Source cube file", required=True, type=str, nargs='+')
    parser.add_argument("-m", "--match", help="Input cube to match", required=False, type=str)
    parser.add_argument("-o", "--output", help="Output Directory", required=True, type=str)
    parser.add_argument("-p", "--padding", help="Cube padding (pixels)", required=False, type=int, default=2000)
    args = parser.parse_args()

    source = args.data
    match = args.match
    output = args.output
    padding = args.padding

    for file_name in source:
        if file_name[-3:].upper() != "CUB":
            print "Not a ISIS cube file file. Skipping '%s'"%file_name
        else:
            match_cam(file_name, match, output, padding)
