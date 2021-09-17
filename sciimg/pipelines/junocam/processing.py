import os
import shutil
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

def print_r(*args):
    s = ' '.join(map(str, args))
    print(s)


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



def initspice_for_cube(args):
    cub_file = args["cub_file"]
    if "verbose" in args:
        verbose = args["verbose"]
    else:
        verbose = False

    if verbose is True:
        print_r("Initializing spice on cube file:", cub_file)

    s = cameras.spiceinit(cub_file)#, spk="/home/kevinmgill/anaconda3/envs/isis3/data/juno/kernels/spk/spk_pre_201231_210720_210407_otm33_f.bsp")

    if verbose is True:
        print_r(s)

    return s




def get_coord_range_from_cube(cub_file):
    min_lat = float(scripting.getkey(cub_file, "MinimumLatitude", grpname="Mapping"))
    max_lat = float(scripting.getkey(cub_file, "MaximumLatitude", grpname="Mapping"))
    min_lon = float(scripting.getkey(cub_file, "MinimumLongitude", grpname="Mapping"))
    max_lon = float(scripting.getkey(cub_file, "MaximumLongitude", grpname="Mapping"))
    return (min_lat, max_lat, min_lon, max_lon)

def map_project_cube(args):
    cub_file = args["cub_file"]
    out_file = args["out_file"]
    map_file = args["map"]
    if "verbose" in args:
        verbose = args["verbose"]
    else:
        verbose = False

    if verbose is True:
        print_r("Map projecting cube file", cub_file)

    try:
        s = cameras.cam2map(cub_file, out_file, map=map_file, resolution="MAP")
        if verbose is True:
            print_r(s)
        r = get_coord_range_from_cube(out_file)
        return r
    except:
        return None #Just eat the exception for now.


"""
    JunoCam additional options:
    projection=<projection>
    vt=<number>
    histeq=true|false
"""
def process_pds_data_file(from_file_name, is_verbose=False, skip_if_cub_exists=False, init_spice=True, nocleanup=False, additional_options={}, num_threads=multiprocessing.cpu_count(), max_value=None, limit_longitude=False):
    #out_file = output_filename(from_file_name)
    #out_file_tiff = "%s.tif" % out_file
    #out_file_cub = "%s.cub" % out_file

    num_steps = 17

    if "projection" in additional_options:
        projection = additional_options["projection"]
    else:
        projection = "jupiterequirectangular"

    if "st" in additional_options: # st means "Skip Triplets.
        skip_triplets = int(additional_options["st"])
        if is_verbose:
            print("Skipping first and last", skip_triplets, "triplets")
    else:
        skip_triplets = None

    if "tgt_trip" in additional_options:
        base_map_triplet = int(additional_options["tgt_trip"])
        if is_verbose:
            print("Using triplet number %s for mapping base"%base_map_triplet)
    else:
        base_map_triplet = None

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

    if "color" in additional_options:
        trueColor = additional_options["color"] == "true"
    else:
        trueColor = False


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

        init_spice_params = [{"cub_file": cub_file, "verbose": is_verbose} for cub_file in cub_files]
        p = multiprocessing.Pool(num_threads)
        xs = p.map(initspice_for_cube, init_spice_params)


    if base_map_triplet is None:
        mid_num = int(round(len(glob.glob('%s/__%s_raw_*.cub' % (work_dir, product_id))) / 3.0 / 2.0))
    else:
        mid_num = base_map_triplet

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

    cub_files_blue = glob.glob('%s/__%s_raw_BLUE_*.cub' % (work_dir, product_id))
    cub_files_green = glob.glob('%s/__%s_raw_GREEN_*.cub' % (work_dir, product_id))
    cub_files_red = glob.glob('%s/__%s_raw_RED_*.cub' % (work_dir, product_id))

    if skip_triplets is not None:
        cub_files_blue.sort()
        cub_files_blue = cub_files_blue[skip_triplets:-skip_triplets]
        cub_files_green.sort()
        cub_files_green = cub_files_green[skip_triplets:-skip_triplets]
        cub_files_red.sort()
        cub_files_red = cub_files_red[skip_triplets:-skip_triplets]
    cub_files = cub_files_blue + cub_files_green + cub_files_red


    params = [{"cub_file": cub_file, "out_file": "%s/%s"%(mapped_dir, os.path.basename(cub_file)), "map": map_file, "verbose": is_verbose} for cub_file in cub_files]
    p = multiprocessing.Pool(num_threads)
    xs = p.map(map_project_cube, params)

    if len(xs) > 0:
        min_lat = np.min([l[0] for l in xs if l is not None])
        max_lat = np.max([l[1] for l in xs if l is not None])
        min_lon = np.min([l[2] for l in xs if l is not None])
        max_lon = np.max([l[3] for l in xs if l is not None])
    else:
        min_lat = 0
        max_lat = 0
        min_lon = 0
        max_lon = 0


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


    if is_verbose:
        print("Exporting Color Map Projected Cube...")
    else:
        printProgress(10, num_steps, prefix="%s: " % from_file_name)

    out_file_map_rgb_cube_inputs = "%s/%s_Mosaic_RGB.txt" % (source_dirname, product_id)
    out_file_map_rgb_cube = "%s/%s_Mosaic_RGB.cub" % (source_dirname, product_id)

    f = open(out_file_map_rgb_cube_inputs, "w")
    f.write("%s\n"%out_file_red)
    f.write("%s\n" % out_file_green)
    f.write("%s\n" % out_file_blue)
    f.close()

    full_map_cube = "trim_tmp.cub"
    
    s = utility.cubeit(out_file_map_rgb_cube_inputs, full_map_cube)
    if is_verbose:
        print(s)

    if is_verbose:
        print("Limiting global coordinates...")
    else:
        printProgress(11, num_steps, prefix="%s: " % from_file_name)

    if limit_longitude is True and max_lon - min_lon > 360:
        # This is prone to failure (see JNCE_2021245_36C00053_V01)
        try:
            s = mapprojection.maptrim(full_map_cube, out_file_map_rgb_cube, "both")
            if is_verbose:
                print(s)
        except:
            if is_verbose:
                traceback.print_exc(file=sys.stdout)
            print("Failed to trim cube. Trying to continue with map as-is...")
            shutil.move(full_map_cube, out_file_map_rgb_cube)
    else:
        shutil.move(full_map_cube, out_file_map_rgb_cube)

    if is_verbose:
        print("Exporting Color Map Projected Tiff...")
    else:
        printProgress(12, num_steps, prefix="%s: " % from_file_name)

    out_file_map_rgb_tiff = "%s/%s_Mosaic_RGB.tif" % (source_dirname, product_id)

    if trueColor is True:
        s = importexport.isis2std_rgb(from_cube_red="%s+1"%out_file_map_rgb_cube,
                                      from_cube_green="%s+3"%out_file_map_rgb_cube,
                                      from_cube_blue="%s+5"%out_file_map_rgb_cube,
                                      to_tiff=out_file_map_rgb_tiff,
                                      match_stretch=True,
                                      minimum=0,
                                      maximum=max_value)
    else:
        s = importexport.isis2std_rgb(from_cube_red="%s+1"%out_file_map_rgb_cube,
                                      from_cube_green="%s+3"%out_file_map_rgb_cube,
                                      from_cube_blue="%s+5"%out_file_map_rgb_cube,
                                      to_tiff=out_file_map_rgb_tiff)
    if is_verbose:
        print(s)

    if nocleanup is False:
        if is_verbose:
            print("Cleaning up...")
        else:
            printProgress(13, num_steps, prefix="%s: " % from_file_name)

        clean_dir(work_dir, product_id)
        clean_dir(mapped_dir, product_id)

        if os.path.exists(out_file_red):
            os.unlink(out_file_red)
        if os.path.exists(out_file_green):
            os.unlink(out_file_green)
        if os.path.exists(out_file_blue):
            os.unlink(out_file_blue)
        if os.path.exists(out_file_map_rgb_cube_inputs):
            os.unlink(out_file_map_rgb_cube_inputs)
        if os.path.exists(full_map_cube):
            os.unlink(full_map_cube)

        dirname = os.path.dirname(out_file_red)
        if len(dirname) > 0:
            dirname += "/"
        print ("%sprint.prt"%dirname)
        if os.path.exists("%sprint.prt"%dirname):
            os.unlink("%sprint.prt"%dirname)

    else:
        if is_verbose:
            print("Skipping clean up...")
        else:
            printProgress(14, num_steps, prefix="%s: " % from_file_name)

    if not is_verbose:
        printProgress(17, num_steps, prefix="%s: "%from_file_name)

    return out_file_map_rgb_tiff
