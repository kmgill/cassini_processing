

import os
from sciimg.isis3 import importexport
from sciimg.pipelines.junocam.utils import json_to_lbl
from PIL import Image
import numpy as np
from sciimg.pipelines.junocam.fillpixels import fillpixels
from sciimg.pipelines.junocam.decompanding import decompand
from sciimg.pipelines.junocam.decompanding import SQROOT
from sciimg.pipelines.junocam.flatfield import apply_flat
from libtiff import TIFFimage
import sys

def create_label(output_base, metadata_json_path):
    output_lbl_path = "%s.lbl"%output_base
    output_img_path = "%s.img"%output_base
    lbl_data = json_to_lbl(metadata_json_path, output_img_path)

    with open(output_lbl_path, "w") as f:
        f.write(lbl_data)

    return output_lbl_path


def create_pds(output_base, img_file, samples, lines):
    output_cub = "%s.cub"%output_base
    output_img = "%s.img"%output_base

    importexport.raw2isis(img_file, output_cub, samples, lines, bittype="real", byteorder="lsb")
    importexport.isis2pds(output_cub, output_img, labtype="fixed", bittype="32bit")

    os.unlink(output_cub)

    return output_img



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


def save_image_raw(image_data, path):
    image_data.tofile(path, format="d")

def apply_weight_to_band(data, band_num, weight, band_height=BAND_HEIGHT):
    top = band_num * band_height
    bottom = top + band_height

    data[top:bottom] *= weight


def apply_weights(img_data, r, g, b, verbose=False):
    img_height = img_data.shape[0]

    if verbose:
        print("Image height: %s"%img_height)

    bands_per_image = (img_height / BAND_HEIGHT / 3)

    if verbose:
        print("Detected %s RGB bands"% bands_per_image)

    for band in range(0, int(bands_per_image)):
        if verbose:
            print("Applying weights to RGB band triplet #%s"%band)
        apply_weight_to_band(img_data, band * 3 + 0, b, band_height=BAND_HEIGHT)
        apply_weight_to_band(img_data, band * 3 + 1, g, band_height=BAND_HEIGHT)
        apply_weight_to_band(img_data, band * 3 + 2, r, band_height=BAND_HEIGHT)


def round_ints(img_data):
    for a in range(0, len(img_data)):
        for b in range(0, len(img_data[a])):
            img_data[a][b] = round(img_data[a][b])


def convert_to_srgb(img_data):
    for a in range(0, len(img_data)):
        for b in range(0, len(img_data[a])):
            c = img_data[a][b]
            if c < 0.0031308:
                c = c * 12.92
            else:
                c = c ** (1.0 / 2.4) * 1.055 - 0.055
            img_data[a][b] = c

def png_to_img(img_file, metadata, fill_dead_pixels=True, do_decompand=True, do_flat_fields=False, verbose=False, doSRGB=True, use_red_weight=0.902, use_green_weight=1.0, use_blue_weight=1.8879):
    image_data = open_image(img_file)

    if fill_dead_pixels:
        if verbose:
            print("User requested to fill dead pixels. So that's what I'll do...")
        fillpixels(image_data, verbose=verbose)

    if do_decompand:
        if verbose:
            print("Decompanding pixel values...")
        decompand(image_data, verbose=verbose)

    if do_flat_fields:
        if verbose:
            print("Applying flat fields for RGB bands...")
        apply_flat(image_data, apply_filling=fill_dead_pixels, verbose=verbose)

    if verbose:
        print("Applying filter weights...")
    apply_weights(image_data, use_red_weight, use_green_weight, use_blue_weight, verbose=verbose)

    # 5436
    max_value = (float(SQROOT[-1]) * np.array([use_red_weight, use_green_weight, use_blue_weight]).max())


    if doSRGB is True:
        if verbose:
            print("Applying sRGB Conversion...")
        image_data /= max_value
        convert_to_srgb(image_data)
        image_data *= max_value

    output_base = img_file[:-4]
    output_base = "%s-adjusted" % output_base
    img_file = "%s.raw" % (img_file[0:-4])

    if verbose:
        print("Creating raw image file...")
    save_image_raw(image_data, img_file)

    if verbose:
        print("Creating label file...")
    label_file = create_label(output_base, metadata)

    if verbose:
        print("Creating PDS file...")

    img_file = create_pds(output_base, img_file, lines=image_data.shape[0], samples=image_data.shape[1])

    return label_file, img_file, max_value

