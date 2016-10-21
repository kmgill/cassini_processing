#!/usr/bin/python
import os
import sys
import re
import subprocess
import datetime
import glob
import argparse

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


def get_field_value(lbl_file_name, keyword, objname=None):
    cmd = ["getkey", "from=%s"%lbl_file_name, "keyword=%s"%keyword]
    if objname is not None:
        cmd += ["objname=%s"%objname]
    s = subprocess.check_output(cmd)
    return s.strip()


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

    target = get_field_value(source, "TARGET_NAME").replace(" ", "_")
    print "Target:", target

    product_id = get_field_value(source, "PRODUCT_ID")[2:-4]
    print "Product Id:", product_id

    print "Ringplane shape:", ("Yes" if is_ringplane else "No")

    filters = get_field_value(source, "FILTER_NAME")
    pattern = re.compile(r"^(?P<f1>[A-Z0-9]*)\, (?P<f2>[A-Z0-9]*)")
    match = pattern.match(filters)
    if match is not None:
        filter1 = match.group("f1")
        filter2 = match.group("f2")
    else:
        filter1 = filter2 = "UNK"

    print "Filter #1:", filter1
    print "Filter #2:", filter2

    lines = get_field_value(source, "LINES", objname="IMAGE")
    print "Lines:", lines

    line_samples = get_field_value(source, "LINE_SAMPLES", objname="IMAGE")
    print "Samples per line:", line_samples

    sample_bits = get_field_value(source, "SAMPLE_BITS", objname="IMAGE")
    print "Bits per sample:", sample_bits

    image_date = datetime.datetime.strptime(get_field_value(source, "IMAGE_TIME"), '%Y-%jT%H:%M:%S.%f')
    print "Image Date:", image_date

    out_file_tiff = "{product_id}_{target}_{filter1}_{filter2}_{image_date}.tif".format(product_id=product_id,
                                                                                        target=target,
                                                                                        filter1=filter1,
                                                                                        filter2=filter2,
                                                                                        image_date=image_date.strftime('%Y-%m-%d_%H.%M.%S'))
    print "Target TIFF:", out_file_tiff

    out_file_cub = "{product_id}_{target}_{filter1}_{filter2}_{image_date}.cub".format(product_id=product_id,
                                                                                        target=target,
                                                                                        filter1=filter1,
                                                                                        filter2=filter2,
                                                                                        image_date=image_date.strftime('%Y-%m-%d_%H.%M.%S'))
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
    cmd_runner(["ciss2isis",
                    "from=%s"%source,
                    "to=%s/__%s_raw.cub"%(work_dir, product_id)])

    if is_verbose:
        print "Filling in Gaps..."
    else:
        printProgress(1, 9)
    cmd_runner(["fillgap",
                    "from=%s/__%s_raw.cub"%(work_dir, product_id),
                    "to=%s/__%s_fill0.cub"%(work_dir, product_id),
                    "interp=cubic",
                    "direction=sample"])

    if is_verbose:
        print "Initializing Spice..."
    else:
        printProgress(2, 9)
    cmd_runner(["spiceinit",
                    "from=%s/__%s_fill0.cub"%(work_dir, product_id),
                    "shape=%s"%("ringplane" if is_ringplane else "system")]) #ringplane, "ellipsoid"

    if is_verbose:
        print "Calibrating cube..."
    else:
        printProgress(3, 9)
    cmd_runner(["cisscal",
                    "from=%s/__%s_fill0.cub"%(work_dir, product_id),
                    "to=%s/__%s_cal.cub"%(work_dir, product_id),
                    "units=intensity"])

    if is_verbose:
        print "Running Noise Filter..."
    else:
        printProgress(4, 9)
    cmd_runner(["noisefilter",
                    "from=%s/__%s_cal.cub"%(work_dir, product_id),
                    "to=%s/__%s_stdz.cub"%(work_dir, product_id),
                    "toldef=stddev",
                    "tolmin=2.5",
                    "tolmax=2.5",
                    "replace=null",
                    "samples=5",
                    "lines=5"])

    if is_verbose:
        print "Filling in Nulls..."
    else:
        printProgress(5, 9)
    cmd_runner(["lowpass",
                    "from=%s/__%s_stdz.cub"%(work_dir, product_id),
                    "to=%s/__%s_fill.cub"%(work_dir, product_id),
                    "samples=3",
                    "lines=3",
                    "filter=outside",
                    "null=yes",
                    "hrs=no",
                    "his=no",
                    "lrs=no",
                    "replacement=center"
                    ])

    if is_verbose:
        print "Removing Frame-Edge Noise..."
    else:
        printProgress(6, 9)
    cmd_runner(["trim",
                    "from=%s/__%s_fill.cub"%(work_dir, product_id),
                    "to=%s/%s"%(work_dir, out_file_cub),
                    "top=2",
                    "bottom=2",
                    "left=2",
                    "right=2"
                    ])

    if is_verbose:
        print "Exporting TIFF..."
    else:
        printProgress(7, 9)
    cmd_runner(["isis2std",
                    "from=%s/%s"%(work_dir, out_file_cub),
                    "to=%s/%s"%(work_dir, out_file_tiff),
                    "format=tiff",
                    "bittype=u16bit",
                    "maxpercent=99.999"
                    ])
    #subprocess.call(["isis2std", "from="+f, "to="+totiff, "format=tiff", "bittype=u16bit", "stretch=manual", "minimum=%f"%minimum, "maximum=%f"%maximum])

    if is_verbose:
        print "Cleaning up..."
    else:
        printProgress(8, 9)
    map(os.unlink, glob.glob('%s/__%s*.cub'%(work_dir, product_id)))

    if not is_verbose:
        printProgress(9, 9)

    print "Done"
