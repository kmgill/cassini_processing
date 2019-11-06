#!/usr/bin/env python2


import os
import sys
import re
import numpy as np
from PIL import Image
import argparse
#from libtiff import TIFFimage
try:
   import cPickle as pickle
except:
   import pickle

BAND_HEIGHT = 128


def open_image(img_path):
    img = Image.open(img_path)
    data = np.copy(np.asarray(img, dtype=np.float32))
    img.close()
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", help="Input Image", required=True, type=str)
    parser.add_argument("-o", "--output", help="Output Pickle Image", required=True, type=str)
    args = parser.parse_args()

    input_image = args.input
    output_file = args.output

    pixels = open_image(input_image)
    avg_matrix = np.zeros(((BAND_HEIGHT * 3), pixels.shape[1]))
    print(avg_matrix.shape)

    img_height = pixels.shape[0]

    bands_per_image = int((img_height / BAND_HEIGHT / 3))

    skip_bands = (5, 6, 7, 8, 9, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25)
    for band in range(0, bands_per_image):
        if band not in skip_bands:
            top = band * (BAND_HEIGHT * 3)
            bottom = top + (BAND_HEIGHT * 3)

            R = pixels[top:bottom]
            avg_matrix += R


    blue_pixels = avg_matrix[0:BAND_HEIGHT]
    blue_pixels /= (bands_per_image - len(skip_bands))
    blue_pixels_t = np.copy(np.asarray(blue_pixels, dtype=np.uint16))
    #tiff = TIFFimage(blue_pixels_t, description='')
    #tiff.write_file(blue_pixels_t, compression='none', verbose=False)

    green_pixels = avg_matrix[BAND_HEIGHT:(BAND_HEIGHT * 2)]
    green_pixels /= (bands_per_image - len(skip_bands))
    green_pixels_t = np.copy(np.asarray(green_pixels, dtype=np.uint16))
    #tiff = TIFFimage(green_pixels_t, description='')
    #tiff.write_file(green_pixels_t, compression='none', verbose=False)

    red_pixels = avg_matrix[(BAND_HEIGHT * 2):(BAND_HEIGHT * 3)]
    red_pixels /= (bands_per_image - len(skip_bands))
    red_pixels_t = np.copy(np.asarray(red_pixels, dtype=np.uint16))
    #tiff = TIFFimage(red_pixels_t, description='')
    #tiff.write_file(red_pixels_t, compression='none', verbose=False)

    flats = {
        "red": red_pixels,
        "green": green_pixels,
        "blue": blue_pixels
    }

    with open(output_file, "w") as out_pkl_file:
        pickle.dump(flats, out_pkl_file)
        out_pkl_file.close()