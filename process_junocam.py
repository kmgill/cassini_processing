#!/usr/bin/env python2
import os
import sys
import re
import argparse
from glob import glob
import json
import zipfile
from shutil import copyfile
from sciimg.isis3 import info
from sciimg.isis3 import _core
from sciimg.processes.junocam_conversions import png_to_img
from sciimg.pipelines.junocam import processing
from sciimg.pipelines.junocam import jcspice
from sciimg.pipelines.junocam import modeling
import multiprocessing

def print_if_verbose(s, is_verbose=True):
    if is_verbose:
        print(s)



def extract(file):
    zip_ref = zipfile.ZipFile(file, 'r')
    zip_ref.extractall(".")
    zip_ref.close()


def decompress_and_copy_file(archive_glob_pattern, file_glob_pattern, verbose=False):
    zipfile_list = glob(archive_glob_pattern)
    if len(zipfile_list) == 0:
        print("Archive file not found")
        sys.exit(1)
    if verbose:
        print("Extracting file '%s'"%zipfile_list[0])
    extract(zipfile_list[0])

    file_list = glob(file_glob_pattern)
    if len(file_list) == 0:
        print("Extracted file not found")
        sys.exit(1)
    if verbose:
        print("Copying file '%s'"%file_list[0])
    copyfile(file_list[0], "./%s"%(os.path.basename(file_list[0])))
    return os.path.basename(file_list[0])


def decompress_image_set(verbose=False):
    png_file = decompress_and_copy_file("*ImageSet.zip", "ImageSet/*raw.png", verbose)
    if verbose:
        print("Found raw PNG file: %s"%png_file)
    return png_file

def decompress_metadata(verbose=False):
    metadata_file = decompress_and_copy_file("*Data.zip", "DataSet/*-Metadata.json", verbose)
    if verbose:
        print("Found metadata file: %s"%metadata_file)
    return metadata_file





if __name__ == "__main__":

    try:
        _core.is_isis3_initialized()
    except:
        print("ISIS3 has not been initialized. Please do so. Now.")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    parser.add_argument("-o", "--option", help="Mission-specific option(s)", required=False, type=str, nargs='+')
    parser.add_argument("-n", "--nocleanup", help="Don't clean up, leave temp files", action="store_true")
    parser.add_argument("-f", "--fill", help="Fill dead pixels", action="store_true")
    parser.add_argument("-d", "--decompand", help="Decompand pixel values", action="store_true")
    parser.add_argument("-F", "--flat", help="Apply flat fields (Don't use)", action="store_true")
    parser.add_argument("-r", "--redweight", help="Apply a weight for the red band", type=float, default=0.902)  # 0.510
    parser.add_argument("-g", "--greenweight", help="Apply a weight for the green band", type=float,
                        default=1.0)  # 0.630
    parser.add_argument("-b", "--blueweight", help="Apply a weight for the blue band", type=float,
                        default=1.8879)  # 1.0
    parser.add_argument("-k", "--kernelbase", help="Base directory for spice kernels", required=False, type=str,
                        default=os.environ["ISIS3DATA"])
    parser.add_argument("-p", "--predicted", help="Utilize predicted kernels", action="store_true")
    parser.add_argument("-s", "--scale", help="Mesh Scalar", required=False, type=float, default=1.0)
    parser.add_argument("-S", "--skipexisting", help="Skip steps if output files already exist", action="store_true")
    parser.add_argument("-t", "--threads", help="Number of threads to use", required=False, type=int, default=multiprocessing.cpu_count())

    args = parser.parse_args()

    is_verbose = args.verbose
    nocleanup = args.nocleanup
    fill_dead_pixels = args.fill
    do_decompand = args.decompand
    do_flat_fields = args.flat

    use_red_weight = args.redweight
    use_green_weight = args.greenweight
    use_blue_weight = args.blueweight
    kernelbase = args.kernelbase
    allow_predicted = args.predicted
    scalar = args.scale
    skip_existing = args.skipexisting
    num_threads = args.threads

    additional_options = {}

    if is_verbose:
        print("Loading spice kernels...")
    jcspice.load_kernels(kernelbase, allow_predicted)

    if type(args.option) == list:
        for option in args.option:
            if re.match("^[0-9a-zA-Z]+=[0-9a-zA-Z]+$", option) is not None:
                parts = option.split("=")
                additional_options[parts[0]] = parts[1]
            else:
                print("Invalid option format:", option)
                sys.exit(1)

    png_file = decompress_image_set(is_verbose)
    metadata_file = decompress_metadata(is_verbose)

    predicted_product_id = png_file[0:25]
    predicted_label_file = "%s-raw-adjusted.lbl"%predicted_product_id
    predicted_img_file ="%s-raw-adjusted.img"%predicted_product_id


    if skip_existing and os.path.exists(predicted_label_file) and os.path.exists(predicted_img_file):
        label_file = predicted_label_file
        img_file = predicted_img_file
    else:
        label_file, img_file = png_to_img(png_file, metadata_file,
                                           fill_dead_pixels=fill_dead_pixels,
                                           do_decompand=do_decompand,
                                           do_flat_fields=do_flat_fields,
                                           use_red_weight=use_red_weight,
                                           use_green_weight=use_green_weight,
                                           use_blue_weight=use_blue_weight,
                                           verbose=is_verbose)

    if is_verbose:
        print("Label file created: %s"%label_file)
        print("PDS IMG file created: %s"%img_file)

    if is_verbose:
        print("Processing...")

    #label_file = predicted_label_file
    #img_file = predicted_img_file





    product_id = info.get_product_id(label_file)
    cube_file_red = "%s_%s_Mosaic.cub" % (product_id, "RED")

    out_file_map_rgb_tiff = "%s_Mosaic_RGB.tif" % product_id
    if not (skip_existing and os.path.exists(cube_file_red) and os.path.exists(out_file_map_rgb_tiff)):
        out_file_map_rgb_tiff = processing.process_pds_data_file(label_file, is_verbose=is_verbose, skip_if_cub_exists=False, init_spice=True, nocleanup=nocleanup, additional_options=additional_options, num_threads=num_threads)

    if is_verbose:
        print("Creating output model...")

    obj_file_path = "%s_model.obj"%product_id
    model_spec_file_path = "%s_model-spec.json" % product_id
    if is_verbose:
        print("Creating Wavefront OBJ file: %s"%obj_file_path)

    model_spec_dict = modeling.create_obj(label_file, cube_file_red, obj_file_path, scalar=scalar, verbose=is_verbose)

    model_spec_dict["rgb_map_tiff"] = out_file_map_rgb_tiff
    model_spec_dict["obj_file"] = obj_file_path

    f = open(model_spec_file_path, "w")
    f.write(json.dumps(model_spec_dict, indent=4))
    f.close()



