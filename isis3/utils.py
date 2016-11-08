#!/usr/bin/python
import os
import sys
import re
import subprocess
import datetime
import glob
import numpy as np

"""
I stole this from someone on stackexchange.
"""
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

"""
Note: Probably need a better check than just looking at two environment variables
"""
def is_isis3_initialized():
    if not "ISISROOT" in os.environ:
        raise Exception("ISISROOT not set!")
    if not "ISIS3DATA" in os.environ:
        raise Exception("ISIS3DATA not set!")
    return True


def get_field_value(lbl_file_name, keyword, objname=None, grpname=None):
    try:
        cmd = ["getkey", "from=%s"%lbl_file_name, "keyword=%s"%keyword]
        if objname is not None:
            cmd += ["objname=%s"%objname]
        if grpname is not None:
            cmd += ["grpname=%s"%grpname]
        s = subprocess.check_output(cmd)
        return s.strip()
    except:
        return None

def get_product_id(file_name):
    if file_name[-3:].upper() == "LBL":
        return get_field_value(file_name, "PRODUCT_ID")[2:-4]
    elif file_name[-3:].upper() == "CUB":
        return get_field_value(file_name, keyword="ProductId", grpname="Archive")[2:-4]
    else:
        raise Exception("Unrecognized/Unsupported file")

def get_target(file_name):
    if file_name[-3:].upper() == "LBL":
        return get_field_value(file_name, "TARGET_NAME").replace(" ", "_")
    elif file_name[-3:].upper() == "CUB":
        return get_field_value(file_name, keyword="TargetName", grpname="Instrument")
    else:
        raise Exception("Unrecognized/Unsupported file")

def get_filters(file_name):
    if file_name[-3:].upper() == "LBL":
        filters = get_field_value(file_name, "FILTER_NAME")
        pattern = re.compile(r"^(?P<f1>[A-Z0-9]*)\, (?P<f2>[A-Z0-9]*)")
    elif file_name[-3:].upper() == "CUB":
        filters = get_field_value(file_name, keyword="FilterName", grpname="BandBin")
        pattern = re.compile(r"^(?P<f1>[A-Z0-9]*)/(?P<f2>[A-Z0-9]*)")
    else:
        raise Exception("Unrecognized/Unsupported file")
    match = pattern.match(filters)
    if match is not None:
        filter1 = match.group("f1")
        filter2 = match.group("f2")
    else:
        filter1 = filter2 = "UNK"
    return filter1, filter2

def get_image_time(file_name):
    if file_name[-3:].upper() == "LBL":
        image_time = get_field_value(file_name, "IMAGE_TIME")
    elif file_name[-3:].upper() == "CUB":
        image_time = get_field_value(file_name, "ImageTime", grpname="Instrument")
    else:
        raise Exception("Unrecognized/Unsupported file")
    return datetime.datetime.strptime(image_time, '%Y-%jT%H:%M:%S.%f')


def get_num_lines(file_name):
    if file_name[-3:].upper() == "LBL":
        return int(get_field_value(file_name, "LINES", objname="IMAGE"))
    elif file_name[-3:].upper() == "CUB":
        return int(get_field_value(file_name, "Lines", objname="IsisCube", grpname="Dimensions"))
    else:
        raise Exception("Unrecognized/Unsupported file")

def get_num_line_samples(file_name):
    if file_name[-3:].upper() == "LBL":
        return int(get_field_value(file_name, "LINE_SAMPLES", objname="IMAGE"))
    elif file_name[-3:].upper() == "CUB":
        return int(get_field_value(file_name, "Samples", objname="IsisCube", grpname="Dimensions"))
    else:
        raise Exception("Unrecognized/Unsupported file")

def get_sample_bits(file_name):
    if file_name[-3:].upper() == "LBL":
        return int(get_field_value(file_name, "SAMPLE_BITS", objname="IMAGE"))
    elif file_name[-3:].upper() == "CUB":
        return 32
    else:
        raise Exception("Unrecognized/Unsupported file")

def get_instrument_id(file_name):
    if file_name[-3:].upper() == "LBL":
        return get_field_value(file_name, "INSTRUMENT_ID")
    elif file_name[-3:].upper() == "CUB":
        return get_field_value(file_name, "InstrumentId", grpname="Instrument")
    else:
        raise Exception("Unrecognized/Unsupported file")   

def output_filename_from_label(lbl_file_name):
    product_id = get_product_id(lbl_file_name)
    target = get_target(lbl_file_name)
    filter1, filter2 = get_filters(lbl_file_name)
    image_time = get_image_time(lbl_file_name)
    out_file = "{product_id}_{target}_{filter1}_{filter2}_{image_date}".format(product_id=product_id,
                                                                                        target=target,
                                                                                        filter1=filter1,
                                                                                        filter2=filter2,
                                                                                        image_date=image_time.strftime('%Y-%m-%d_%H.%M.%S'))
    return out_file


def output_tiff_from_label(lbl_file_name):
    out_file_base = output_filename_from_label(lbl_file_name)
    out_file_tiff = "%s.tif"%out_file_base
    return out_file_tiff

def output_cub_from_label(lbl_file_name):
    out_file_base = output_filename_from_label(lbl_file_name)
    out_file_cub = "%s.cub"%out_file_base
    return out_file_cub

def import_to_cube(lbl_file_name, to_cube):
    s = subprocess.check_output(["ciss2isis",
                                "from=%s"%lbl_file_name,
                                "to=%s"%to_cube])
    return s

def fill_gaps(from_cube, to_cube):
    s = subprocess.check_output(["fillgap",
                    "from=%s"%from_cube,
                    "to=%s"%to_cube,
                    "interp=cubic",
                    "direction=sample"])
    return s

def init_spice(from_cube, is_ringplane=False):
    s = subprocess.check_output(["spiceinit",
                    "from=%s"%from_cube,
                    "shape=%s"%("ringplane" if is_ringplane else "system")]) #ringplane, "ellipsoid"
    return s

def calibrate_cube(from_cube, to_cube):
    s = subprocess.check_output(["cisscal",
                    "from=%s"%from_cube,
                    "to=%s"%to_cube,
                    "units=intensity"])
    return s

def noise_filter(from_cube, to_cube):
    s = subprocess.check_output(["noisefilter",
                    "from=%s"%from_cube,
                    "to=%s"%to_cube,
                    "toldef=stddev",
                    "tolmin=2.5",
                    "tolmax=2.5",
                    "replace=null",
                    "samples=5",
                    "lines=5"])
    return s

def fill_nulls(from_cube, to_cube):
    s = subprocess.check_output(["lowpass",
                    "from=%s"%from_cube,
                    "to=%s"%to_cube,
                    "samples=3",
                    "lines=3",
                    "filter=outside",
                    "null=yes",
                    "hrs=no",
                    "his=no",
                    "lrs=no",
                    "replacement=center"
                    ])
    return s

def trim_edges(from_cube, to_cube):
    s = subprocess.check_output(["trim",
                    "from=%s"%from_cube,
                    "to=%s"%to_cube,
                    "top=2",
                    "bottom=2",
                    "left=2",
                    "right=2"
                    ])
    return s

def export_tiff_grayscale(from_cube, to_tiff, minimum=None, maximum=None):
    cmd = ["isis2std",
                    "from=%s"%from_cube,
                    "to=%s"%to_tiff,
                    "format=tiff",
                    "bittype=u16bit"
                    ]

    if minimum is not None and maximum is not None:
        cmd += ["stretch=manual", "minimum=%f"%minimum, "maximum=%f"%maximum]
    else:
        cmd.append("maxpercent=99.999")

    s = subprocess.check_output(cmd)
    return s


def export_tiff_rgb(from_cube_red, from_cube_green, from_cube_blue, to_tiff, minimum=None, maximum=None, match_stretch=False):
    cmd = ["isis2std",
                    "red=%s"%from_cube_red,
                    "green=%s"%from_cube_green,
                    "blue=%s"%from_cube_blue,
                    "to=%s"%to_tiff,
                    "format=tiff",
                    "bittype=u16bit",
                    "mode=rgb"
                    ]
    if match_stretch and minimum is not None and maximum is not None:
        cmd += ["stretch=manual", "rmin=%f"%minimum, "rmax=%f"%maximum]
        cmd += ["gmin=%f"%minimum, "gmax=%f"%maximum]
        cmd += ["bmin=%f"%minimum, "bmax=%f"%maximum]
    else:
        cmd.append("maxpercent=99.999")

    s = subprocess.check_output(cmd)
    return s


def get_data_min_max(from_cube):
    out = subprocess.check_output(["stats", "from=%s"%from_cube])

    min = 0
    max = 0

    pattern = re.compile(r"^ *(?P<key>[a-zA-Z0-9]*)[ =]+(?P<value>[\-A-Z0-9.]*)")
    for line in out.split("\n"):
        match = pattern.match(line)
        if match is not None:
            key = match.group("key")
            value = match.group("value")
            if key == "Minimum":
                min = float(value)
            elif key == "Maximum":
                max = float(value)
    return min, max



"""
    Simplistic method for allowing a user to just specify the first part of a file if they're (read: me) being lazy
"""
def guess_from_filename_prefix(filename):
    if os.path.exists(filename):
        return filename
    if os.path.exists("%s.LBL"%filename):
        return "%s.LBL"%filename
    if os.path.exists("%s_1.LBL"%filename):
        return "%s_1.LBL"%filename


def process_pds_data_file(lbl_file_name, is_ringplane=False, is_verbose=False, skip_if_cub_exists=False):
    product_id = get_product_id(lbl_file_name)

    out_file_tiff = output_tiff_from_label(lbl_file_name)
    out_file_cub = output_cub_from_label(lbl_file_name)

    if skip_if_cub_exists and os.path.exists(out_file_cub):
        print "File %s exists, skipping processing"%out_file_cub
        return

    source_dirname = os.path.dirname(lbl_file_name)
    if source_dirname == "":
        source_dirname = "."

    work_dir = "%s/work"%source_dirname
    if not os.path.exists(work_dir):
        os.mkdir(work_dir)


    if is_verbose:
        print "Importing to cube..."
    else:
        printProgress(0, 9, prefix="%s: "%lbl_file_name)
    s = import_to_cube(lbl_file_name, "%s/__%s_raw.cub"%(work_dir, product_id))
    if is_verbose:
        print s


    if is_verbose:
        print "Filling in Gaps..."
    else:
        printProgress(1, 9, prefix="%s: "%lbl_file_name)
    s = fill_gaps("%s/__%s_raw.cub"%(work_dir, product_id),
                        "%s/__%s_fill0.cub"%(work_dir, product_id))
    if is_verbose:
        print s



    if is_verbose:
        print "Initializing Spice..."
    else:
        printProgress(2, 9, prefix="%s: "%lbl_file_name)
    s = init_spice("%s/__%s_fill0.cub"%(work_dir, product_id), is_ringplane)
    if is_verbose:
        print s


    if is_verbose:
        print "Calibrating cube..."
    else:
        printProgress(3, 9, prefix="%s: "%lbl_file_name)
    s = calibrate_cube("%s/__%s_fill0.cub"%(work_dir, product_id),
                            "%s/__%s_cal.cub"%(work_dir, product_id))
    if is_verbose:
        print s


    if is_verbose:
        print "Running Noise Filter..."
    else:
        printProgress(4, 9, prefix="%s: "%lbl_file_name)
    s = noise_filter("%s/__%s_cal.cub"%(work_dir, product_id),
                            "%s/__%s_stdz.cub"%(work_dir, product_id))
    if is_verbose:
        print s

    if is_verbose:
        print "Filling in Nulls..."
    else:
        printProgress(5, 9, prefix="%s: "%lbl_file_name)
    s = fill_nulls("%s/__%s_stdz.cub"%(work_dir, product_id),
                        "%s/__%s_fill.cub"%(work_dir, product_id))
    if is_verbose:
        print s


    if is_verbose:
        print "Removing Frame-Edge Noise..."
    else:
        printProgress(6, 9, prefix="%s: "%lbl_file_name)
    s = trim_edges("%s/__%s_fill.cub"%(work_dir, product_id),
                        "%s"%(out_file_cub))
    if is_verbose:
        print s


    if is_verbose:
        print "Exporting TIFF..."
    else:
        printProgress(7, 9, prefix="%s: "%lbl_file_name)
    s = export_tiff_grayscale("%s"%(out_file_cub),
                                    "%s"%(out_file_tiff))
    if is_verbose:
        print s


    if is_verbose:
        print "Cleaning up..."
    else:
        printProgress(8, 9, prefix="%s: "%lbl_file_name)
    map(os.unlink, glob.glob('%s/__%s*.cub'%(work_dir, product_id)))

    if not is_verbose:
        printProgress(9, 9, prefix="%s: "%lbl_file_name)
