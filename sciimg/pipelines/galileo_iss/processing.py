
import os
import glob
from sciimg.isis3 import info
from sciimg.isis3 import galileo
from sciimg.isis3 import cameras
from sciimg.isis3 import filters
from sciimg.isis3 import trimandmask
from sciimg.isis3 import importexport
from sciimg.isis3._core import printProgress
from traceback import print_exc


def output_filename(file_name):
    dirname = os.path.dirname(file_name)
    if len(dirname) > 0:
        dirname += "/"
    product_id = str(info.get_product_id(file_name)).replace("+", "_")
    target = info.get_target(file_name)
    filter1, filter2 = info.get_filters(file_name)
    image_time = info.get_image_time(file_name)
    image_id = file_name[:file_name.index(".")]

    out_file = "{dirname}{image_id}_{product_id}_{target}_{filter1}_{image_date}".format(dirname=dirname,
                                                                                        image_id=image_id,
                                                                                        product_id=product_id,
                                                                                        target=target,
                                                                                        filter1=filter1,
                                                                                        image_date=image_time.strftime('%Y-%m-%d_%H.%M.%S'))
    return out_file

def is_supported_file(file_name):
    try:
        if file_name[-3:].upper() in ("CUB",):
            value = info.get_field_value(file_name,  "SpacecraftName", grpname="Instrument")
            return value == "Galileo Orbiter"
        elif file_name[-3:].upper() in ("LBL", ):
            value = info.get_field_value(file_name, "SPACECRAFT_NAME")
            return value == "GALILEO ORBITER"
        else:
            return False
    except:
        return False

def process_pds_data_file(from_file_name, is_verbose=False, skip_if_cub_exists=False, init_spice=True, nocleanup=False, additional_options={}):
    product_id = str(info.get_product_id(from_file_name)).replace("+", "_")

    out_file_tiff = "%s.tif" % output_filename(from_file_name)
    out_file_cub = "%s.cub" % output_filename(from_file_name)

    if skip_if_cub_exists and os.path.exists(out_file_cub):
        print("File %s exists, skipping processing" % out_file_cub)
        return

    if "ringplane" in additional_options:
        is_ringplane = additional_options["ringplane"].upper() in ("TRUE", "YES")
    else:
        is_ringplane = False

    source_dirname = os.path.dirname(from_file_name)
    if source_dirname == "":
        source_dirname = "."

    work_dir = "%s/work" % source_dirname
    if not os.path.exists(work_dir):
        os.mkdir(work_dir)

    if is_verbose:
        print("Importing to cube...")
    else:
        printProgress(0, 9, prefix="%s: "%from_file_name)
    s = galileo.gllssi2isis(from_file_name, "%s/__%s_raw.cub"%(work_dir, product_id))
    if is_verbose:
        print(s)

    if init_spice is True:
        if is_verbose:
            print("Initializing Spice...")
        else:
            printProgress(1, 9, prefix="%s: " % from_file_name)
        s = cameras.spiceinit("%s/__%s_raw.cub" % (work_dir, product_id), is_ringplane)
        if is_verbose:
            print(s)

    if is_verbose:
        print("Calibrating cube...")
    else:
        printProgress(2, 9, prefix="%s: " % from_file_name)
    s = galileo.gllssical("%s/__%s_raw.cub" % (work_dir, product_id),
                       "%s/__%s_cal.cub" % (work_dir, product_id))
    if is_verbose:
        print(s)

    if is_verbose:
        print("Running Noise Filter...")
    else:
        printProgress(3, 9, prefix="%s: "%from_file_name)
    s = filters.noisefilter("%s/__%s_cal.cub"%(work_dir, product_id),
                            "%s/__%s_stdz.cub"%(work_dir, product_id))
    if is_verbose:
        print(s)

    if is_verbose:
        print("Filling in Nulls...")
    else:
        printProgress(4, 9, prefix="%s: "%from_file_name)
    s = filters.lowpass("%s/__%s_stdz.cub"%(work_dir, product_id),
                        "%s/__%s_fill0.cub"%(work_dir, product_id))
    if is_verbose:
        print(s)

    if is_verbose:
        print("Removing Frame-Edge Noise...")
    else:
        printProgress(5, 9, prefix="%s: "%from_file_name)
    s = trimandmask.trim("%s/__%s_fill0.cub"%(work_dir, product_id),
                        "%s"%(out_file_cub))
    if is_verbose:
        print(s)

    if is_verbose:
        print("Exporting TIFF...")
    else:
        printProgress(6, 9, prefix="%s: "%from_file_name)
    s = importexport.isis2std_grayscale("%s"%(out_file_cub),
                                    "%s"%(out_file_tiff))
    if is_verbose:
        print(s)

    if nocleanup is False:
        if is_verbose:
            print("Cleaning up...")
        else:
            printProgress(7, 9, prefix="%s: "%from_file_name)
        map(os.unlink, glob.glob('%s/__%s*.cub'%(work_dir, product_id)))
    else:
        if is_verbose:
            print("Skipping clean up...")
        else:
            printProgress(7, 9, prefix="%s: "%from_file_name)

    if not is_verbose:
        printProgress(9, 9, prefix="%s: "%from_file_name)

    return out_file_cub

