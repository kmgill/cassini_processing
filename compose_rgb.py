#!/usr/bin/env python
import os
import sys
import re
import subprocess
import datetime
import glob
import argparse
import numpy as np

from isis3 import utils
from isis3 import info
import isis3.importexport as importexport
import isis3.mathandstats as mathandstats

def get_target_filename_portion(red_lbl_file, green_lbl_file, blue_lbl_file):
    target_red = info.get_target(red_lbl_file)
    target_green = info.get_target(green_lbl_file)
    target_blue = info.get_target(blue_lbl_file)

    targets = np.unique([target_red, target_green, target_blue])

    return "_".join(targets)

def process_file(input_name):

    cub_file = None
    if input_name[-3:].upper() == "CUB":
        if not os.path.exists(input_name):
            print "File %s does not exist"%input_name
            raise Exception("File %s does not exist"%input_name)
        cub_file = input_name
    else:
        lbl_file = utils.guess_from_filename_prefix(input_name)
        if not os.path.exists(lbl_file):
            print "File %s does not exist"%lbl_file
            raise Exception("File %s does not exist"%lbl_file)
        else:
            print "Processing", lbl_file

        utils.process_pds_data_file(lbl_file, is_ringplane=False, is_verbose=is_verbose, skip_if_cub_exists=True)
        cub_file = utils.output_cub_from_label(lbl_file)
        
    min_value, max_value = mathandstats.get_data_min_max(cub_file)
    return cub_file, min_value, max_value



if __name__ == "__main__":

    try:
        utils.is_isis3_initialized()
    except:
        print "ISIS3 has not been initialized. Please do so. Now."
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--red", help="Data label for the red channel", required=True, type=str)
    parser.add_argument("-g", "--green", help="Data label for the green channel", required=True, type=str)
    parser.add_argument("-b", "--blue", help="Data label for the blue channel", required=True, type=str)
    parser.add_argument("-m", "--match", help="Force matching stretch values", action="store_true")
    parser.add_argument("-v", "--verbose", help="Verbose output (includes ISIS3 command output)", action="store_true")
    args = parser.parse_args()

    is_verbose = args.verbose

    match_stretch = args.match

    red_cub_file, r_min, r_max = process_file(args.red)
    green_cub_file, g_min, g_max = process_file(args.green)
    blue_cub_file, b_min, b_max = process_file(args.blue)

    a = np.array([r_min, r_max, g_min, g_max, b_min, b_max])
    min = np.min(a)
    max = np.max(a)

    print "Max:", max
    print "Min:", min

    red_product_id = info.get_product_id(red_cub_file)
    green_product_id = info.get_product_id(green_cub_file)
    blue_product_id = info.get_product_id(blue_cub_file)
    targets = get_target_filename_portion(red_cub_file, green_cub_file, blue_cub_file)

    output_tiff = "%s_%s_%s_%s_RGB-composed.tif"%(red_product_id, green_product_id, blue_product_id, targets)

    s = importexport.isis2std_rgb(red_cub_file, green_cub_file, blue_cub_file, output_tiff, minimum=min, maximum=max, match_stretch=match_stretch)

    if is_verbose:
        print s
