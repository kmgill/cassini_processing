#!/usr/bin/env python
import os
import sys
import re
import subprocess
import datetime
import glob
import argparse
import traceback

from isis3 import utils
from isis3 import info
from isis3 import _core

def print_if_verbose(s, is_verbose=True):
    if is_verbose:
        print s

def process_data_file(lbl_file_name, is_ringplane, require_target, require_filters, require_width, require_height, metadata_only, is_verbose, skip_existing, init_spice, projection, nocleanup):
    source = utils.guess_from_filename_prefix(lbl_file_name)
    source_dirname = os.path.dirname(source)
    if source_dirname == "":
        source_dirname = "."

    if not os.path.exists(source):
        print "File %s does not exist"%source
    else:
        print_if_verbose("Processing %s"%source, is_verbose)

    target = info.get_target(source)
    print_if_verbose("Target: %s"%target, is_verbose)

    product_id = info.get_product_id(source)
    print_if_verbose("Product ID: %s"%product_id, is_verbose)

    print_if_verbose("Ringplace Shape: %s"%("Yes" if is_ringplane else "No"), is_verbose)

    try:
        filter1, filter2 = info.get_filters(source)
    except:
        filter1, filter2 = (None, None)
    print_if_verbose("Filter #1: %s"%filter1, is_verbose)
    print_if_verbose("Filter #2: %s"%filter2, is_verbose)

    width = info.get_num_line_samples(source)
    height = info.get_num_lines(source)

    lines = info.get_num_lines(source)
    print_if_verbose("Lines: %s"%lines, is_verbose)

    line_samples = info.get_num_line_samples(source)
    print_if_verbose("Samples per line: %s"%line_samples, is_verbose)

    image_date = info.get_image_time(source)
    print_if_verbose("Image Date: %s"%image_date, is_verbose)

    out_file_base = utils.output_filename(source)

    out_file_tiff = "%s.tif"%out_file_base
    print_if_verbose("Output Tiff: %s"%out_file_tiff, is_verbose)

    out_file_cub = "%s.cub"%out_file_base
    print_if_verbose("Output Cube: %s"%out_file_cub, is_verbose)

    if metadata_only:
        return

    if skip_existing and os.path.exists(out_file_cub) and os.path.exists(out_file_tiff):
        print "Output exists, skipping."
        return

    if require_target is not None and not require_target.upper() == target.upper():
        print "Target mismatch, exiting."
        return

    if require_filters is not None and not (filter1 in require_filters or filter2 in require_filters):
        print "Filter mismatch, exiting."
        return

    if require_height is not None and not (str(height) in require_height):
        print "Height filter mismatch, exiting"

    if require_width is not None and not (str(width) in require_width):
        print "Width filter mismatch, exiting"

    utils.process_pds_data_file(source, is_ringplane=is_ringplane, is_verbose=is_verbose, init_spice=init_spice, projection=projection, nocleanup=nocleanup)


if __name__ == "__main__":

    try:
        _core.is_isis3_initialized()
    except:
        print "ISIS3 has not been initialized. Please do so. Now."
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Source PDS dataset", required=True, type=str, nargs='+')
    parser.add_argument("-r", "--ringplane", help="Input data is of a ring plane", action="store_true")
    parser.add_argument("-m", "--metadata", help="Print metadata and exit", action="store_true")
    parser.add_argument("-f", "--filter", help="Require filter or exit", required=False, type=str, nargs='+')
    parser.add_argument("-t", "--target", help="Require target or exit", required=False, type=str)
    parser.add_argument("-s", "--skipexisting", help="Skip processing if output already exists", action="store_true")
    parser.add_argument("-v", "--verbose", help="Verbose output (includes ISIS3 command output)", action="store_true")
    parser.add_argument("-w", "--width", help="Require width or exit", required=False, type=str, nargs='+')
    parser.add_argument("-H", "--height", help="Require height or exit", required=False, type=str, nargs='+')
    parser.add_argument("-S", "--skipspice", help="Skip spice initialization", required=False, action="store_true")
    parser.add_argument("-p", "--projection", help="Map projection (Juno)", required=False, type=str)
    parser.add_argument("-n", "--nocleanup", help="Don't clean up, leave temp files", required=False, type=str)
    args = parser.parse_args()

    source = args.data

    is_ringplane = args.ringplane
    metadata_only = args.metadata

    require_filters = args.filter
    require_target = args.target
    require_height = args.height
    require_width = args.width

    skip_existing = args.skipexisting
    skip_spice = args.skipspice
    is_verbose = args.verbose
    nocleanup = args.nocleanup

    projection = args.projection

    for lbl_file_name in source:
        if lbl_file_name[-3:].upper() not in ("LBL", "BEL", "IMQ"):  # Note: 'BEL' is for .LBL_label via atlas wget script
            print "Not a PDS label file. Skipping '%s'"%lbl_file_name
        else:
            try:
                process_data_file(lbl_file_name, is_ringplane, require_target, require_filters, require_width, require_height, metadata_only, is_verbose, skip_existing, not skip_spice, projection=projection, nocleanup=nocleanup)
            except Exception as ex:
                print "Error processing '%s'"%lbl_file_name
                if is_verbose:
                    traceback.print_exc(file=sys.stdout)


    print_if_verbose("Done", is_verbose)
