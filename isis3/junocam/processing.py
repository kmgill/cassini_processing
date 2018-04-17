import os
import sys
import glob
import shutil
from isis3 import info
from isis3 import juno
from isis3 import cameras
from isis3 import filters
from isis3 import mathandstats
from isis3 import trimandmask
from isis3 import geometry
from isis3 import importexport
from isis3 import mosaicking
from isis3._core import printProgress



def output_filename(file_name):
    dirname = os.path.dirname(file_name)
    if len(dirname) > 0:
        dirname += "/"


def is_supported_file(file_name):
    if file_name[-3:].upper() in ("CUB",):
        value = info.get_field_value(file_name,  "SpacecraftName", grpname="Instrument")
        return value == "JUNO"
    elif file_name[-3:].upper() in ("LBL", ):
        value = info.get_field_value(file_name, "SPACECRAFT_NAME")
        return value == "JUNO"
    else:
        return False


def assemble_mosaic(color, source_dirname, product_id, is_verbose=False):
    mapped_dir = "%s/work/mapped" % source_dirname
    list_file = "%s/work/mapped/cubs_%s.lis" % (source_dirname, product_id)
    cub_files = glob.glob('%s/__%s_raw_%s_*.cub' % (mapped_dir, product_id, color.upper()))

    f = open(list_file, "w")
    for cub_file in cub_files:
        f.write(cub_file)
        f.write("\n")
    f.close()

    mosaic_out = "%s/%s_%s_Mosaic.cub" % (source_dirname, product_id, color.upper())
    s = mosaicking.automos(list_file, mosaic_out, priority=mosaicking.Priority.AVERAGE)
    if is_verbose:
        print s

    return mosaic_out


def export(out_file_cub, is_verbose=False):
    out_file_tiff = "%s.tif"%out_file_cub[:-3]
    s = importexport.isis2std_grayscale("%s+1" % (out_file_cub),
                                        "%s" % (out_file_tiff))
    if is_verbose:
        print s


def clean_dir(dir, product_id):
    files = glob.glob('%s/*%s*' % (dir, product_id))
    for file in files:
        os.unlink(file)

def process_pds_data_file(from_file_name, is_ringplane=False, is_verbose=False, skip_if_cub_exists=False, init_spice=True, **args):
    #out_file = output_filename(from_file_name)
    #out_file_tiff = "%s.tif" % out_file
    #out_file_cub = "%s.cub" % out_file

    source_dirname = os.path.dirname(from_file_name)
    if source_dirname == "":
        source_dirname = "."

    work_dir = "%s/work" % source_dirname
    if not os.path.exists(work_dir):
        os.mkdir(work_dir)

    product_id = info.get_product_id(from_file_name)
    mapped_dir = "%s/work/mapped" % source_dirname
    if not os.path.exists(mapped_dir):
        os.mkdir(mapped_dir)


    if is_verbose:
        print "Importing to cube..."
    else:
        printProgress(0, 9, prefix="%s: "%from_file_name)

    try: # Noticing a weird exception in junocam2isis. Eating the exception for now.
        s = juno.junocam2isis(from_file_name, "%s/__%s_raw.cub"%(work_dir, product_id))
        if is_verbose:
            print s
    except:
        pass

    if init_spice is True:
        if is_verbose:
            print "Initializing Spice..."
        else:
            printProgress(1, 9, prefix="%s: "%from_file_name)
        cub_files = glob.glob('%s/__%s_raw_*.cub'%(work_dir, product_id))

        for cub_file in cub_files:
            s = cameras.spiceinit(cub_file, is_ringplane=is_ringplane)
            if is_verbose:
                print s




    mid_file = "%s/__%s_raw_GREEN_0030.cub"%(work_dir, product_id)
    map_file = "%s/__%s_map.cub"%(work_dir, product_id)

    if is_verbose:
        print "Starting Map..."
    else:
        printProgress(2, 9, prefix="%s: " % from_file_name)

    s = cameras.cam2map(mid_file, map_file, projection="equirectangular")
    if is_verbose:
        print s


    if is_verbose:
        print "Map Projecting Stripes..."
    else:
        printProgress(3, 9, prefix="%s: " % from_file_name)

    cub_files = glob.glob('%s/__%s_raw_*.cub' % (work_dir, product_id))
    for cub_file in cub_files:
        try: # Not all of them will work.
            bn = os.path.basename(cub_file)
            out_file = "%s/%s"%(mapped_dir, bn)
            s = cameras.cam2map(cub_file, out_file, map=map_file, resolution="MAP")
            if is_verbose:
                print s
        except:
            pass # Probably shouldn't eat the exception here.



    if is_verbose:
        print "Assembling Red Mosaic..."
    else:
        printProgress(4, 9, prefix="%s: " % from_file_name)

    out_file_red = assemble_mosaic("RED", source_dirname, product_id, is_verbose)


    if is_verbose:
        print "Assembling Green Mosaic..."
    else:
        printProgress(5, 9, prefix="%s: " % from_file_name)

    out_file_green = assemble_mosaic("GREEN", source_dirname, product_id, is_verbose)

    if is_verbose:
        print "Assembling Blue Mosaic..."
    else:
        printProgress(6, 9, prefix="%s: " % from_file_name)

    out_file_blue = assemble_mosaic("BLUE", source_dirname, product_id, is_verbose)


    if is_verbose:
        print "Exporting Tiffs..."
    else:
        printProgress(7, 9, prefix="%s: " % from_file_name)

    export(out_file_red, is_verbose)
    export(out_file_green, is_verbose)
    export(out_file_blue, is_verbose)



    if is_verbose:
        print "Cleaning up..."
    else:
        printProgress(8, 9, prefix="%s: " % from_file_name)

    clean_dir(work_dir, product_id)
    clean_dir(mapped_dir, product_id)

    dirname = os.path.dirname(out_file_red)
    if len(dirname) > 0:
        dirname += "/"
    if os.path.exists("%sprint.prt"%dirname):
        os.unlink("%sprint.prt"%dirname)

    if not is_verbose:
        printProgress(9, 9, prefix="%s: "%from_file_name)