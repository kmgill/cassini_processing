#!/usr/bin/python
import os
import sys
import re
import subprocess
import datetime
import glob
import argparse

from isis3 import utils






if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Source PDS dataset", required=True, type=str)
    parser.add_argument("-r", "--ringplane", help="Input data is of a ring plane", action="store_true")
    parser.add_argument("-m", "--metadata", help="Print metadata and exit", action="store_true")
    parser.add_argument("-f", "--filter", help="Require filter or exit", required=False, type=str, nargs='+')
    parser.add_argument("-t", "--target", help="Require target or exit", required=False, type=str)
    parser.add_argument("-s", "--skipexisting", help="Skip processing if output already exists", action="store_true")
    parser.add_argument("-v", "--verbose", help="Verbose output (includes ISIS3 command output)", action="store_true")
    args = parser.parse_args()

    source = args.data
    source = utils.guess_from_filename_prefix(source)

    is_ringplane = args.ringplane
    metadata_only = args.metadata

    require_filters = args.filter
    require_target = args.target

    skip_existing = args.skipexisting

    is_verbose = args.verbose

    source_dirname = os.path.dirname(source)
    if source_dirname == "":
        source_dirname = "."

    if not os.path.exists(source):
        print "File %s does not exist"%source
    else:
        print "Processing", source

    target = utils.get_target(source)
    print "Target:", target

    product_id = utils.get_product_id(source)
    print "Product Id:", product_id

    print "Ringplane shape:", ("Yes" if is_ringplane else "No")

    filter1, filter2 = utils.get_filters(source)

    print "Filter #1:", filter1
    print "Filter #2:", filter2

    lines = utils.get_num_lines(source)
    print "Lines:", lines

    line_samples = utils.get_num_line_samples(source)
    print "Samples per line:", line_samples

    sample_bits = utils.get_sample_bits(source)
    print "Bits per sample:", sample_bits

    image_date = utils.get_image_time(source)
    print "Image Date:", image_date

    out_file_base = utils.output_filename_from_label(source)

    out_file_tiff = "%s.tif"%out_file_base
    print "Target TIFF:", out_file_tiff

    out_file_cub = "%s.cub"%out_file_base
    print "Target ISIS3 cube:", out_file_cub

    if metadata_only:
        sys.exit(0)

    if skip_existing and os.path.exists(out_file_cub) and os.path.exists(out_file_tiff):
        print "Output exists, skipping."
        sys.exit(0)

    if require_target is not None and not require_target.upper() == target.upper():
        print "Target mismatch, exiting."
        sys.exit(0)

    if require_filters is not None and not (filter1 in require_filters or filter2 in require_filters):
        print "Filter mismatch, exiting."
        sys.exit(0)

    utils.process_pds_data_file(source, is_ringplane=is_ringplane, is_verbose=is_verbose)

    print "Done"
