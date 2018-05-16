#!/usr/bin/env python
import os
import sys
import argparse
import numpy as np

from sciimg.isis3 import utils
from sciimg.isis3 import info
from sciimg.isis3 import _core
import sciimg.isis3.importexport as importexport
import sciimg.isis3.mathandstats as mathandstats
from sciimg.processes.match import compose_rgb

def get_target_filename_portion(red_lbl_file, green_lbl_file, blue_lbl_file):
    target_red = info.get_target(red_lbl_file)
    target_green = info.get_target(green_lbl_file)
    target_blue = info.get_target(blue_lbl_file)

    targets = np.unique([target_red, target_green, target_blue])

    return "_".join(targets)


if __name__ == "__main__":

    try:
        _core.is_isis3_initialized()
    except:
        print "ISIS3 has not been initialized. Please do so. Now."
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--red", help="Data label for the red channel", required=True, type=str)
    parser.add_argument("-g", "--green", help="Data label for the green channel", required=True, type=str)
    parser.add_argument("-b", "--blue", help="Data label for the blue channel", required=True, type=str)
    parser.add_argument("-m", "--match", help="Force matching stretch values", action="store_true")
    parser.add_argument("-v", "--verbose", help="Verbose output (includes ISIS3 command output)", action="store_true")
    parser.add_argument("-o", "--output", help="Output file name", required=True, type=str)
    args = parser.parse_args()

    is_verbose = args.verbose

    match_stretch = args.match

    cub_file_red = args.red
    cub_file_green = args.green
    cub_file_blue = args.blue
    output_file_name = args.output

    compose_rgb(cub_file_red, cub_file_green, cub_file_blue, output_tiff_file=output_file_name, match_stretch=match_stretch, is_verbose=is_verbose)

