
import glob
import os
import traceback
import sys
from isis3 import info
from isis3 import voyager
from isis3 import cameras
from isis3 import filters
from isis3 import mathandstats
from isis3 import trimandmask
from isis3 import scripting
from isis3 import utility
from isis3 import geometry
from isis3 import importexport
from isis3._core import printProgress

__VOYAGER_1__ = "VOYAGER_1"
__VOYAGER_2__ = "VOYAGER_2"


def output_filename(file_name):
    dirname = os.path.dirname(file_name)
    if len(dirname) > 0:
        dirname += "/"
    target = info.get_target(file_name)
    filter1, filter2 = info.get_filters(file_name)
    image_time = info.get_image_time(file_name)
    spacecraft = info.get_spacecraft_name(file_name)
    image_id = file_name[:file_name.index(".")]
    camera = info.get_instrument_id(file_name)

    if camera is not None and len(camera) > 0:
        camera = "NAC" if camera == "NARROW_ANGLE_CAMERA" else "WAC"
    else:
        camera = "UNK"

    sc = "Vg1" if spacecraft == "VOYAGER_1" else "Vg2"

    out_file = "{dirname}{image_id}_{spacecraft}_{camera}_{target}_{filter1}_{image_date}".format(dirname=dirname,
                                                                                        image_id=image_id,
                                                                                        spacecraft=sc,
                                                                                        camera=camera,
                                                                                        target=target,
                                                                                        filter1=filter1,
                                                                                        image_date=image_time.strftime('%Y-%m-%d_%H.%M.%S'))
    return out_file

def is_supported_file(file_name):
    if file_name[-3:].upper() in ("CUB", "IMQ"):
        value = info.get_field_value(file_name,  "SpacecraftName", grpname="Instrument")
        return value == __VOYAGER_1__ or value == __VOYAGER_2__
    else:
        return False



def process_pds_data_file(from_file_name, is_verbose=False, skip_if_cub_exists=False, init_spice=True,  nocleanup=False, additional_options={}):
    product_id = info.get_product_id(from_file_name)

    out_file_tiff = "%s.tif" % output_filename(from_file_name)
    out_file_cub = "%s.cub" % output_filename(from_file_name)

    if skip_if_cub_exists and os.path.exists(out_file_cub):
        print "File %s exists, skipping processing" % out_file_cub
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
        print "Importing to cube..."
    else:
        printProgress(0, 11, prefix="%s: "%from_file_name)
    s = voyager.voy2isis(from_file_name, "%s/__%s_raw.cub"%(work_dir, product_id))
    if is_verbose:
        print s

    if is_verbose:
        print "Finding Reseaus..."
    else:
        printProgress(1, 11, prefix="%s: "%from_file_name)
    s = geometry.findrx("%s/__%s_raw.cub"%(work_dir, product_id))
    if is_verbose:
        print s

    if is_verbose:
        print "Removing Reseaus..."
    else:
        printProgress(2, 11, prefix="%s: "%from_file_name)
    s = geometry.remrx("%s/__%s_raw.cub"%(work_dir, product_id),
                       "%s/__%s_remrx.cub" % (work_dir, product_id),
                       action="BILINEAR")
    if is_verbose:
        print s

    try:
        if init_spice is True:
            if is_verbose:
                print "Initializing Spice..."
            else:
                printProgress(3, 11, prefix="%s: "%from_file_name)
            s = cameras.spiceinit("%s/__%s_remrx.cub" % (work_dir, product_id), is_ringplane)
            if is_verbose:
                print s

        if is_verbose:
            print "Calibrating cube..."
        else:
            printProgress(4, 11, prefix="%s: "%from_file_name)
        s = voyager.voycal("%s/__%s_raw.cub"%(work_dir, product_id),
                                "%s/__%s_cal.cub"%(work_dir, product_id))
        if is_verbose:
            print s

        # TODO: Determine when to run this (on Io approach) and do so
        #if is_verbose:
        #    print "Plasma torus irradiation correction..."
        #else:
        #    printProgress(4, 11, prefix="%s: "%from_file_name)
        #s = voyager.voycal("%s/__%s_cal.cub"%(work_dir, product_id),
        #                        "%s/__%s_ramp.cub"%(work_dir, product_id))

        #if is_verbose:
        #    print s

        last_cube = "%s/__%s_cal.cub"%(work_dir, product_id)
    except:
        if is_verbose:
            traceback.print_exc(file=sys.stdout)
        last_cube = "%s/__%s_remrx.cub" % (work_dir, product_id)

    if is_verbose:
        print "Filling in Gaps..."
    else:
        printProgress(5, 11, prefix="%s: "%from_file_name)
    s = mathandstats.fillgap(last_cube,
                       "%s/__%s_fill.cub" % (work_dir, product_id))
    if is_verbose:
        print s

    if is_verbose:
        print "Stretch Fix..."
    else:
        printProgress(5, 11, prefix="%s: "%from_file_name)
    s = utility.stretch("%s/__%s_fill.cub" % (work_dir, product_id),
                       "%s/__%s_stretch.cub" % (work_dir, product_id))
    if is_verbose:
        print s

    if is_verbose:
        print "Running Noise Filter..."
    else:
        printProgress(6, 11, prefix="%s: "%from_file_name)
    s = filters.noisefilter("%s/__%s_stretch.cub"%(work_dir, product_id),
                            "%s/__%s_stdz.cub"%(work_dir, product_id))
    if is_verbose:
        print s

    if is_verbose:
        print "Filling in Nulls..."
    else:
        printProgress(7, 11, prefix="%s: "%from_file_name)
    s = filters.lowpass("%s/__%s_stdz.cub"%(work_dir, product_id),
                        "%s/__%s_fill0.cub"%(work_dir, product_id))
    if is_verbose:
        print s

    if is_verbose:
        print "Removing Frame-Edge Noise..."
    else:
        printProgress(8, 11, prefix="%s: "%from_file_name)
    s = trimandmask.trim("%s/__%s_fill0.cub"%(work_dir, product_id),
                         out_file_cub,
                         top=2,
                         right=2,
                         bottom=2,
                         left=2)
    if is_verbose:
        print s

    """
    if is_verbose:
        print "Trimming Corners..."
    else:
        printProgress(9, 11, prefix="%s: "%from_file_name)
    s = trimandmask.circle("%s/__%s_noise.cub" % (work_dir, product_id),
                        out_file_cub,
                        rad=500)
    if is_verbose:
        print s
    """

    if is_verbose:
        print "Exporting TIFF..."
    else:
        printProgress(9, 11, prefix="%s: "%from_file_name)
    s = importexport.isis2std_grayscale("%s"%(out_file_cub),
                                    "%s"%(out_file_tiff))
    if is_verbose:
        print s

    if nocleanup is False:
        if is_verbose:
            print "Cleaning up..."
        else:
            printProgress(10, 11, prefix="%s: "%from_file_name)
        map(os.unlink, glob.glob('%s/__%s*.cub'%(work_dir, product_id)))
    else:
        if is_verbose:
            print "Skipping clean up..."
        else:
            printProgress(10, 11, prefix="%s: "%from_file_name)

    dirname = os.path.dirname(out_file_tiff)
    if len(dirname) > 0:
        dirname += "/"
    if os.path.exists("%sprint.prt"%dirname):
        os.unlink("%sprint.prt"%dirname)


    if not is_verbose:
        printProgress(11, 11, prefix="%s: "%from_file_name)
