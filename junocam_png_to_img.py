#!/usr/bin/env python
"""
There's probably a much better way to do this. But it works so I'm using it for now...

"""


import argparse
from PIL import Image
import numpy as np
from sciimg.isis3.junocam.fillpixels import fillpixels
from sciimg.isis3.junocam.decompanding import decompand
from sciimg.processes.junocam_conversions import create_label
from sciimg.processes.junocam_conversions import create_pds
from libtiff import TIFFimage

BAND_HEIGHT = 128

def open_image(img_path):
    img = Image.open(img_path)
    data = np.copy(np.asarray(img, dtype=np.float32))
    img.close()

    return data


def save_image(image_data, path):
    data_matrix = image_data.astype(np.uint16)
    tiff = TIFFimage(data_matrix, description='')
    tiff.write_file(path, compression='none')


def apply_weight_to_band(data, band_num, weight, band_height=BAND_HEIGHT):
    top = band_num * band_height
    bottom = top + band_height

    data[top:bottom] *= weight


def apply_weights(img_data, r, g, b, verbose=False):
    img_height = img_data.shape[0]

    if verbose:
        print "Image height:", img_height

    bands_per_image = (img_height / BAND_HEIGHT / 3)

    if verbose:
        print "Detected", bands_per_image, "RGB bands"

    for band in range(0, bands_per_image):
        if verbose:
            print "Filling pixels for RGB band triplet #", band
        apply_weight_to_band(img_data, band * 3 + 0, b, band_height=BAND_HEIGHT)
        apply_weight_to_band(img_data, band * 3 + 1, g, band_height=BAND_HEIGHT)
        apply_weight_to_band(img_data, band * 3 + 2, r, band_height=BAND_HEIGHT)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--metadata", help="Input JunoCam Metadata JSON File", required=True, type=str)
    parser.add_argument("-p", "--png", help="Input JunoCam PNG File", required=True, type=str)
    parser.add_argument("-f", "--fill", help="Fill dead pixels", action="store_true")
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    parser.add_argument("-d", "--decompand", help="Decompand pixel values", action="store_true")

    parser.add_argument("-r", "--redweight", help="Apply a weight for the red band", type=float, default=1.0) # 0.510
    parser.add_argument("-g", "--greenweight", help="Apply a weight for the green band", type=float, default=1.0) # 0.630
    parser.add_argument("-b", "--blueweight", help="Apply a weight for the blue band", type=float, default=1.0) # 1.0

    args = parser.parse_args()

    metadata = args.metadata
    img_file = args.png
    fill_dead_pixels = args.fill
    verbose = args.verbose
    do_decompand = args.decompand

    use_red_weight = args.redweight
    use_green_weight = args.greenweight
    use_blue_weight = args.blueweight

    image_data = open_image(img_file)



    if fill_dead_pixels:
        if verbose:
            print "User requested to fill dead pixels. So that's what I'll do..."
        fillpixels(image_data, verbose=verbose)

    if do_decompand:
        if verbose:
            print "Decompanding pixel values..."
        decompand(image_data, verbose=verbose)

    if verbose:
        print "Applying filter weights..."
    apply_weights(image_data, use_red_weight, use_green_weight, use_blue_weight, verbose=False)

    image_data /= image_data.max()
    image_data *= 65535.0

    img_file = "%s-adjusted.tif" % (img_file[0:-4])
    save_image(image_data, img_file)


    output_base = img_file[:-4]

    if verbose:
        print "Creating output files with basename of", output_base

    if verbose:
        print "Creating label file..."
    create_label(output_base, metadata)

    if verbose:
        print "Creating PDS file..."
    create_pds(output_base, img_file)




