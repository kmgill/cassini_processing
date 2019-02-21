import os
import sys
import glob
from sciimg.isis3 import info
from sciimg.isis3 import juno
from sciimg.isis3 import cameras
from sciimg.isis3 import mathandstats
from sciimg.isis3 import trimandmask
from sciimg.isis3 import importexport
from sciimg.isis3 import mosaicking
from sciimg.isis3._core import printProgress
from sciimg.isis3 import utility
from sciimg.isis3 import scripting
from sciimg.isis3 import mapprojection
import multiprocessing
import numpy as np
import traceback

def output_filename(file_name):
    dirname = os.path.dirname(file_name)
    if len(dirname) > 0:
        dirname += "/"


def is_supported_file(file_name):
    if file_name is None:
        return False

    if file_name[-3:].upper() in ("CUB",):
        value = info.get_field_value(file_name,  "SpacecraftName", grpname="Instrument")
        return value is not None and value.decode('UTF-8') == "JUNO"
    elif file_name[-3:].upper() in ("LBL", ):
        value = info.get_field_value(file_name, "SPACECRAFT_NAME")
        return value is not None and value.decode('UTF-8') == "JUNO"
    else:
        return False


def assemble_mosaic(color, source_dirname, product_id, min_lat, max_lat, min_lon, max_lon, is_verbose=False):
    mapped_dir = "%s/work/mapped" % source_dirname
    list_file = "%s/work/mapped/cubs_%s.lis" % (source_dirname, product_id)
    cub_files = glob.glob('%s/__%s_raw_%s_*.cub' % (mapped_dir, product_id, color.upper()))

    f = open(list_file, "w")
    for cub_file in cub_files:
        f.write(cub_file)
        f.write("\n")
    f.close()

    mosaic_out = "%s/%s_%s_Mosaic.cub" % (source_dirname, product_id, color.upper())
    s = mosaicking.automos(list_file,
                           mosaic_out,
                           priority=mosaicking.Priority.AVERAGE,
                           grange=mosaicking.Grange.USER,
                           minlat=min_lat,
                           maxlat=max_lat,
                           minlon=min_lon,
                           maxlon=max_lon)
    if is_verbose:
        print(s)

    return mosaic_out


def export(out_file_cub, is_verbose=False):
    out_file_tiff = "%s.tif"%out_file_cub[:-4]
    s = importexport.isis2std_grayscale("%s" % (out_file_cub),
                                        "%s" % (out_file_tiff))
    if is_verbose:
        print(s)


def clean_dir(dir, product_id):
    files = glob.glob('%s/*%s*' % (dir, product_id))
    for file in files:
        os.unlink(file)


def trim_vertical(cub_file, trim_pixels=2):
    trim_file = "%s_trim.cub"%cub_file[:-4]
    trimandmask.trim(cub_file, trim_file, top=trim_pixels, bottom=trim_pixels, left=0, right=0)
    os.unlink(cub_file)
    os.rename(trim_file, cub_file)

def trim_cube(args):
    cub_file = args["cub_file"]
    trim_pixels = args["trim_pixels"]
    trim_vertical(cub_file, trim_pixels)

def trim_cubes(work_dir, product_id, trim_pixels=2, num_threads=multiprocessing.cpu_count()):
    cub_files = glob.glob('%s/__%s_raw_*.cub' % (work_dir, product_id))

    params = [{"cub_file":cub_file, "trim_pixels": trim_pixels} for cub_file in cub_files]
    p = multiprocessing.Pool(num_threads)
    xs = p.map(trim_cube, params)


def histeq_cube(cub_file, work_dir, product_id):
    hist_file = "%s/__%s_hist.cub" % (work_dir, product_id)
    mathandstats.histeq("%s+1"%cub_file, hist_file, minper=0.0, maxper=100.0)
    os.unlink(cub_file)
    os.rename(hist_file, cub_file)



def initspice_for_cube(cub_file):
    s = cameras.spiceinit(cub_file)
    return s


def map_project_cube(args):
    cub_file = args["cub_file"]
    out_file = args["out_file"]
    map_file = args["map"]

    try:
        s = cameras.cam2map(cub_file, out_file, map=map_file, resolution="MAP")
        min_lat = float(scripting.getkey(out_file, "MinimumLatitude", grpname="Mapping"))
        max_lat = float(scripting.getkey(out_file, "MaximumLatitude", grpname="Mapping"))
        min_lon = float(scripting.getkey(out_file, "MinimumLongitude", grpname="Mapping"))
        max_lon = float(scripting.getkey(out_file, "MaximumLongitude", grpname="Mapping"))
        return (min_lat, max_lat, min_lon, max_lon)
    except:
        return None #Just eat the exception for now.


"""
    JunoCam additional options:
    projection=<projection>
    vt=<number>
    histeq=true|false
"""
def process_pds_data_file(from_file_name, is_verbose=False, skip_if_cub_exists=False, init_spice=True, nocleanup=False, additional_options={}, num_threads=multiprocessing.cpu_count()):
    #out_file = output_filename(from_file_name)
    #out_file_tiff = "%s.tif" % out_file
    #out_file_cub = "%s.cub" % out_file

    num_steps = 16

    if "projection" in additional_options:
        projection = additional_options["projection"]
    else:
        projection = "equirectangular"

    source_dirname = os.path.dirname(from_file_name)
    if source_dirname == "":
        source_dirname = "."

    work_dir = "%s/work" % source_dirname
    if not os.path.exists(work_dir):
        os.mkdir(work_dir)




    product_id = info.get_product_id(from_file_name)
    sub_spacecraft_longitude = info.get_property(from_file_name, "SUB_SPACECRAFT_LONGITUDE")
    print("Product Id:", product_id)
    print("Sub Spacecraft Longitude:", sub_spacecraft_longitude)


    mapped_dir = "%s/work/mapped" % source_dirname
    if not os.path.exists(mapped_dir):
        os.mkdir(mapped_dir)

    if is_verbose:
        print("Importing to cube...")
    else:
        printProgress(0, num_steps, prefix="%s: "%from_file_name)

    s = juno.junocam2isis(from_file_name, "%s/__%s_raw.cub"%(work_dir, product_id))
    if is_verbose:
        print(s)


    if "vt" in additional_options:
        trim_pixels = int(additional_options["vt"])
        if is_verbose:
            print("Trimming Framelets...")
            print("Vertical trimming: %d pixels"%trim_pixels)
        else:
            printProgress(1, num_steps, prefix="%s: "%from_file_name)

        trim_cubes(work_dir, product_id, trim_pixels=trim_pixels, num_threads=num_threads)


    if init_spice is True:
        if is_verbose:
            print("Initializing Spice...")
        else:
            printProgress(2, num_steps, prefix="%s: "%from_file_name)
        cub_files = glob.glob('%s/__%s_raw_*.cub'%(work_dir, product_id))
        p = multiprocessing.Pool(num_threads)
        xs = p.map(initspice_for_cube, cub_files)
    

    mid_num = int(round(len(glob.glob('%s/__%s_raw_*.cub' % (work_dir, product_id))) / 3.0 / 2.0))

    mid_file = "%s/__%s_raw_GREEN_%04d.cub"%(work_dir, product_id, mid_num)
    map_file = "%s/__%s_map.cub"%(work_dir, product_id)


    if is_verbose:
        print("Starting Map...")
    else:
        printProgress(3, num_steps, prefix="%s: " % from_file_name)

    s = cameras.cam2map(mid_file, map_file, projection=projection)
    if is_verbose:
        print(s)

    if is_verbose:
        print("Map Projecting Stripes...")
    else:
        printProgress(4, num_steps, prefix="%s: " % from_file_name)
    

    cub_files = glob.glob('%s/__%s_raw_*.cub' % (work_dir, product_id))

    params = [{"cub_file": cub_file, "out_file": "%s/%s"%(mapped_dir, os.path.basename(cub_file)), "map": map_file} for cub_file in cub_files]
    p = multiprocessing.Pool(num_threads)
    xs = p.map(map_project_cube, params)

    min_lat = np.min([l[0] for l in xs if l is not None])
    max_lat = np.max([l[1] for l in xs if l is not None])
    min_lon = np.min([l[2] for l in xs if l is not None])
    max_lon = np.max([l[3] for l in xs if l is not None])

    if is_verbose:
        print("Assembling Red Mosaic...")
    else:
        printProgress(5, num_steps, prefix="%s: " % from_file_name)

    out_file_red = assemble_mosaic("RED", source_dirname, product_id, min_lat, max_lat, min_lon, max_lon, is_verbose)

    if is_verbose:
        print("Assembling Green Mosaic...")
    else:
        printProgress(6, num_steps, prefix="%s: " % from_file_name)

    out_file_green = assemble_mosaic("GREEN", source_dirname, product_id, min_lat, max_lat, min_lon, max_lon, is_verbose)

    if is_verbose:
        print("Assembling Blue Mosaic...")
    else:
        printProgress(7, num_steps, prefix="%s: " % from_file_name)

    out_file_blue = assemble_mosaic("BLUE", source_dirname, product_id, min_lat, max_lat, min_lon, max_lon, is_verbose)


    if "histeq" in additional_options and additional_options["histeq"].upper() in ("TRUE", "YES"):
        if is_verbose:
            print("Running histogram equalization on map projected cubes...")
        else:
            printProgress(8, num_steps, prefix="%s: " % from_file_name)
        histeq_cube(out_file_red, work_dir, product_id)
        histeq_cube(out_file_green, work_dir, product_id)
        histeq_cube(out_file_blue, work_dir, product_id)

    if is_verbose:
        print("Exporting Map Projected Tiffs...")
    else:
        printProgress(9, num_steps, prefix="%s: " % from_file_name)

    export(out_file_red, is_verbose)
    export(out_file_green, is_verbose)
    export(out_file_blue, is_verbose)



    if is_verbose:
        print("Exporting Color Map Projected Tiff...")
    else:
        printProgress(10, num_steps, prefix="%s: " % from_file_name)

    out_file_map_rgb_tiff = "%s/%s_Mosaic_RGB.tif" % (source_dirname, product_id)
    s = importexport.isis2std_rgb(from_cube_red=out_file_red, from_cube_green=out_file_green, from_cube_blue=out_file_blue, to_tiff=out_file_map_rgb_tiff)
    if is_verbose:
        print(s)





    if is_verbose:
        print("Camera Projecting Mosaics...")
    else:
        printProgress(11, num_steps, prefix="%s: " % from_file_name)

    pad_file = "%s/__%s_raw_GREEN_00%d_padded.cub"%(work_dir, product_id, mid_num)

    utility.pad(mid_file, pad_file, top=2300, right=0, bottom=2300, left=0)

    out_file_red_cam = "%s/%s_%s_Recammed.cub" % (source_dirname, product_id, "RED")
    cameras.map2cam(out_file_red, out_file_red_cam, pad_file)

    out_file_green_cam = "%s/%s_%s_Recammed.cub" % (source_dirname, product_id, "GREEN")
    cameras.map2cam(out_file_green, out_file_green_cam, pad_file)

    out_file_blue_cam = "%s/%s_%s_Recammed.cub" % (source_dirname, product_id, "BLUE")
    cameras.map2cam(out_file_blue, out_file_blue_cam, pad_file)


    if "histeq" in additional_options and additional_options["histeq"].upper() in ("TRUE", "YES"):
        if is_verbose:
            print("Running histogram equalization on camera projected cubes...")
        else:
            printProgress(12, num_steps, prefix="%s: " % from_file_name)
        histeq_cube(out_file_red_cam, work_dir, product_id)
        histeq_cube(out_file_green_cam, work_dir, product_id)
        histeq_cube(out_file_blue_cam, work_dir, product_id)


    if is_verbose:
        print("Exporting Camera Projected Tiffs...")
    else:
        printProgress(13, num_steps, prefix="%s: " % from_file_name)

    export(out_file_red_cam, is_verbose)
    export(out_file_green_cam, is_verbose)
    export(out_file_blue_cam, is_verbose)


    if is_verbose:
        print("Exporting Color Camera Projected Tiff...")
    else:
        printProgress(14, num_steps, prefix="%s: " % from_file_name)

    out_file_cam_rgb_tiff = "%s/%s_RGB.tif" % (source_dirname, product_id)
    s = importexport.isis2std_rgb(from_cube_red=out_file_red_cam, from_cube_green=out_file_green_cam, from_cube_blue=out_file_blue_cam, to_tiff=out_file_cam_rgb_tiff)
    if is_verbose:
        print(s)

    if nocleanup is False:
        if is_verbose:
            print("Cleaning up...")
        else:
            printProgress(15, num_steps, prefix="%s: " % from_file_name)

        clean_dir(work_dir, product_id)
        clean_dir(mapped_dir, product_id)

        dirname = os.path.dirname(out_file_red)
        if len(dirname) > 0:
            dirname += "/"
        if os.path.exists("%sprint.prt"%dirname):
            os.unlink("%sprint.prt"%dirname)
    else:
        if is_verbose:
            print("Skipping clean up...")
        else:
            printProgress(15, num_steps, prefix="%s: " % from_file_name)

    if not is_verbose:
        printProgress(16, num_steps, prefix="%s: "%from_file_name)

    return out_file_map_rgb_tiff