#!/usr/bin/python
import os
import sys
import re
import subprocess
import datetime
import glob
import argparse

from isis3 import utils

def printProgress (iteration, total, prefix = '', suffix = '', decimals = 1, barLength = 100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    formatStr       = "{0:." + str(decimals) + "f}"
    percents        = formatStr.format(100 * (iteration / float(total)))
    filledLength    = int(round(barLength * iteration / float(total)))
    bar             = '*' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

def guess_from_filename_prefix(filename):
    if os.path.exists(filename):
        return filename
    if os.path.exists("%s.LBL"%filename):
        return "%s.LBL"%filename
    if os.path.exists("%s_1.LBL"%filename):
        return "%s_1.LBL"%filename



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
    source = guess_from_filename_prefix(source)

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

    # Now, we start actually doing stuff
    work_dir = "%s/work"%source_dirname
    if not os.path.exists(work_dir):
        os.mkdir(work_dir)

    cmd_runner = subprocess.call if is_verbose else subprocess.check_output


    if is_verbose:
        print "Importing to cube..."
    else:
        printProgress(0, 9)
    s = utils.import_to_cube(source, "%s/__%s_raw.cub"%(work_dir, product_id))
    if is_verbose:
        print s


    if is_verbose:
        print "Filling in Gaps..."
    else:
        printProgress(1, 9)
    s = utils.fill_gaps("%s/__%s_raw.cub"%(work_dir, product_id),
                        "%s/__%s_fill0.cub"%(work_dir, product_id))
    if is_verbose:
        print s



    if is_verbose:
        print "Initializing Spice..."
    else:
        printProgress(2, 9)
    s = utils.init_spice("%s/__%s_fill0.cub"%(work_dir, product_id), is_ringplane)
    if is_verbose:
        print s


    if is_verbose:
        print "Calibrating cube..."
    else:
        printProgress(3, 9)
    s = utils.calibrate_cube("%s/__%s_fill0.cub"%(work_dir, product_id),
                            "%s/__%s_cal.cub"%(work_dir, product_id))
    if is_verbose:
        print s


    if is_verbose:
        print "Running Noise Filter..."
    else:
        printProgress(4, 9)
    s = utils.noise_filter("%s/__%s_cal.cub"%(work_dir, product_id),
                            "%s/__%s_stdz.cub"%(work_dir, product_id))
    if is_verbose:
        print s

    if is_verbose:
        print "Filling in Nulls..."
    else:
        printProgress(5, 9)
    s = utils.fill_nulls("%s/__%s_stdz.cub"%(work_dir, product_id),
                        "%s/__%s_fill.cub"%(work_dir, product_id))
    if is_verbose:
        print s


    if is_verbose:
        print "Removing Frame-Edge Noise..."
    else:
        printProgress(6, 9)
    s = utils.trim_edges("%s/__%s_fill.cub"%(work_dir, product_id),
                        "%s/%s"%(work_dir, out_file_cub))
    if is_verbose:
        print s


    if is_verbose:
        print "Exporting TIFF..."
    else:
        printProgress(7, 9)
    s = utils.export_tiff_grayscale("%s/%s"%(work_dir, out_file_cub),
                                    "%s/%s"%(work_dir, out_file_tiff))
    if is_verbose:
        print s


    if is_verbose:
        print "Cleaning up..."
    else:
        printProgress(8, 9)
    map(os.unlink, glob.glob('%s/__%s*.cub'%(work_dir, product_id)))

    if not is_verbose:
        printProgress(9, 9)

    print "Done"
