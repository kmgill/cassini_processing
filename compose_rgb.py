#!/usr/bin/python
import os
import sys
import re
import subprocess
import datetime
import glob
import argparse
import numpy as np

from isis3 import utils


def get_target_filename_portion(red_lbl_file, green_lbl_file, blue_lbl_file):
    target_red = utils.get_target(red_lbl_file)
    target_green = utils.get_target(green_lbl_file)
    target_blue = utils.get_target(blue_lbl_file)

    targets = np.unique([target_red, target_green, target_blue])

    return "_".join(targets)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-r", "--red", help="Data label for the red channel", required=True, type=str)
    parser.add_argument("-g", "--green", help="Data label for the green channel", required=True, type=str)
    parser.add_argument("-b", "--blue", help="Data label for the blue channel", required=True, type=str)
    parser.add_argument("-v", "--verbose", help="Verbose output (includes ISIS3 command output)", action="store_true")
    args = parser.parse_args()

    is_verbose = args.verbose

    red_lbl_file = args.red
    red_lbl_file = utils.guess_from_filename_prefix(red_lbl_file)
    if not os.path.exists(red_lbl_file):
        print "File (red) %s does not exist"%red_lbl_file
    else:
        print "Processing", red_lbl_file



    green_lbl_file = args.green
    green_lbl_file = utils.guess_from_filename_prefix(green_lbl_file)
    if not os.path.exists(green_lbl_file):
        print "File (green) %s does not exist"%green_lbl_file
    else:
        print "Processing", green_lbl_file

    blue_lbl_file = args.blue
    blue_lbl_file = utils.guess_from_filename_prefix(blue_lbl_file)
    if not os.path.exists(blue_lbl_file):
        print "File (blue) %s does not exist"%blue_lbl_file
    else:
        print "Processing", blue_lbl_file


    utils.process_pds_date_file(red_lbl_file, is_ringplane=False, is_verbose=is_verbose, skip_if_cub_exists=True)
    red_cub_file = utils.output_cub_from_label(red_lbl_file)
    r_min, r_max = utils.get_data_min_max(red_cub_file)

    utils.process_pds_date_file(green_lbl_file, is_ringplane=False, is_verbose=is_verbose, skip_if_cub_exists=True)
    green_cub_file = utils.output_cub_from_label(green_lbl_file)
    g_min, g_max = utils.get_data_min_max(green_cub_file)

    utils.process_pds_date_file(blue_lbl_file, is_ringplane=False, is_verbose=is_verbose, skip_if_cub_exists=True)
    blue_cub_file = utils.output_cub_from_label(blue_lbl_file)
    b_min, b_max = utils.get_data_min_max(blue_cub_file)

    a = np.array([r_min, r_max, g_min, g_max, b_min, b_max])
    min = np.min(a)
    max = np.max(a)

    print "Max:", max
    print "Min:", min

    red_product_id = utils.get_product_id(red_lbl_file)
    green_product_id = utils.get_product_id(green_lbl_file)
    blue_product_id = utils.get_product_id(blue_lbl_file)
    targets = get_target_filename_portion(red_lbl_file, green_lbl_file, blue_lbl_file)

    output_tiff = "%s_%s_%s_%s_RGB-composed.tif"%(red_product_id, green_product_id, blue_product_id, targets)

    s = utils.export_tiff_rgb(red_cub_file, green_cub_file, blue_cub_file, output_tiff, minimum=None, maximum=None)

    if is_verbose:
        print s
