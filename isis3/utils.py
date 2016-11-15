#!/usr/bin/python
import os
import sys
import glob

import isis3.info as info
import isis3.cassini as cissisis
import isis3.cameras as cameras
import isis3.filters as filters
import isis3.trimandmask as trimandmask
import isis3.mathandstats as mathandstats
import isis3.importexport as importexport

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


def output_filename_from_label(lbl_file_name):
    dirname = os.path.dirname(lbl_file_name)
    if len(dirname) > 0:
        dirname += "/"
    product_id = info.get_product_id(lbl_file_name)
    target = info.get_target(lbl_file_name)
    filter1, filter2 = info.get_filters(lbl_file_name)
    image_time = info.get_image_time(lbl_file_name)
    out_file = "{dirname}{product_id}_{target}_{filter1}_{filter2}_{image_date}".format(dirname=dirname,
                                                                                        product_id=product_id,
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
    return cissisis.ciss2isis(lbl_file_name, to_cube)

def calibrate_cube(from_cube, to_cube):
    return cissisis.cisscal(from_cube, to_cube, units="intensity")




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
    if os.path.exists("%s_2.LBL"%filename):
        return "%s_2.LBL"%filename


def process_pds_data_file(lbl_file_name, is_ringplane=False, is_verbose=False, skip_if_cub_exists=False):
    product_id = info.get_product_id(lbl_file_name)

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
    s = mathandstats.fillgap("%s/__%s_raw.cub"%(work_dir, product_id),
                        "%s/__%s_fill0.cub"%(work_dir, product_id))
    if is_verbose:
        print s



    if is_verbose:
        print "Initializing Spice..."
    else:
        printProgress(2, 9, prefix="%s: "%lbl_file_name)
    s = cameras.spiceinit("%s/__%s_fill0.cub"%(work_dir, product_id), is_ringplane)
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
    s = filters.noisefilter("%s/__%s_cal.cub"%(work_dir, product_id),
                            "%s/__%s_stdz.cub"%(work_dir, product_id))
    if is_verbose:
        print s

    if is_verbose:
        print "Filling in Nulls..."
    else:
        printProgress(5, 9, prefix="%s: "%lbl_file_name)
    s = filters.lowpass("%s/__%s_stdz.cub"%(work_dir, product_id),
                        "%s/__%s_fill.cub"%(work_dir, product_id))
    if is_verbose:
        print s


    if is_verbose:
        print "Removing Frame-Edge Noise..."
    else:
        printProgress(6, 9, prefix="%s: "%lbl_file_name)
    s = trimandmask.trim("%s/__%s_fill.cub"%(work_dir, product_id),
                        "%s"%(out_file_cub))
    if is_verbose:
        print s


    if is_verbose:
        print "Exporting TIFF..."
    else:
        printProgress(7, 9, prefix="%s: "%lbl_file_name)
    s = importexport.isis2std_grayscale("%s"%(out_file_cub),
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
