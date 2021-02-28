#!/usr/bin/env python
"""
    Simplified Mars 2020 MastCam-Z decompanding color correction routines using
    PNG-formatted public raw images.

    References:

    Bell, J. F. et al. (2017), The Mars Science Laboratory Curiosity rover
    Mastcam instruments: Preflight and in‐flight calibration, validation,
    and data archiving, Earth and Space Science, 4, 396– 452,
    doi:10.1002/2016EA000219.
    https://doi.org/10.1002/2016EA000219


    Hayes, A.G., Corlies, P., Tate, C. et al.
    Pre-Flight Calibration of the Mars 2020 Rover Mastcam Zoom (Mastcam-Z)
    Multispectral, Stereoscopic Imager. Space Sci Rev 217, 29 (2021).
    https://doi.org/10.1007/s11214-021-00795-x

"""

import numpy as np
import cv2
import sys
from PIL import Image
import argparse
import os

DEFAULT_RAD_MULTIPLE_RED = 1.0 #1.0797812675266405
DEFAULT_RAD_MULTIPLE_GREEN = 1.0
DEFAULT_RAD_MULTIPLE_BLUE = 1.0 #0.932978126752664

INPAINT_MASK_RIGHT_PATH = "cal/M20_MCZ_RIGHT_INPAINT_MASK_V1.png"
INPAINT_MASK_LEFT_PATH = "cal/M20_MCZ_LEFT_INPAINT_MASK_V1.png"

LEFT_EYE = "L"
RIGHT_EYE = "R"

# 8bit to 11bit DN inverse lookup table (Table 0), Bell, et al 2017
LUT = np.array((0, 2, 3, 3, 4, 5, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16,
                18, 19, 20, 22, 24, 25, 27, 29, 31, 33, 35, 37, 39, 41,
                43, 46, 48, 50, 53, 55, 58, 61, 63, 66, 69, 72, 75, 78,
                81, 84, 87, 90, 94, 97, 100, 104, 107, 111, 115, 118, 122,
                126, 130, 134, 138, 142, 146, 150, 154, 159, 163, 168, 172,
                177, 181, 186, 191, 196, 201, 206, 211, 216, 221, 226, 231,
                236, 241, 247, 252, 258, 263, 269, 274, 280, 286, 292, 298,
                304, 310, 316, 322, 328, 334, 341, 347, 354, 360, 367, 373,
                380, 387, 394, 401, 408, 415, 422, 429, 436, 443, 450, 458,
                465, 472, 480, 487, 495, 503, 510, 518, 526, 534, 542, 550,
                558, 566, 575, 583, 591, 600, 608, 617, 626, 634, 643, 652,
                661, 670, 679, 688, 697, 706, 715, 724, 733, 743, 752, 761,
                771, 781, 790, 800, 810, 819, 829, 839, 849, 859, 869, 880,
                890, 900, 911, 921, 932, 942, 953, 964, 974, 985, 996, 1007,
                1018, 1029, 1040, 1051, 1062, 1074, 1085, 1096, 1108, 1119,
                1131, 1142, 1154, 1166, 1177, 1189, 1201, 1213, 1225, 1237,
                1249, 1262, 1274, 1286, 1299, 1311, 1324, 1336, 1349, 1362,
                1374, 1387, 1400, 1413, 1426, 1439, 1452, 1465, 1479, 1492,
                1505, 1519, 1532, 1545, 1559, 1573, 1586, 1600, 1614, 1628,
                1642, 1656, 1670, 1684, 1698, 1712, 1727, 1741, 1755, 1770,
                1784, 1799, 1814, 1828, 1843, 1858, 1873, 1888, 1903, 1918,
                1933, 1948, 1963, 1979, 1994, 2009, 2025, 2033), dtype=np.float32)

"""
Loads M20 PNG formatted Mastcam-Z images into a numpy array. Images appear to
be BGR arranged, so they are swapped to standard RGB.
"""
def load_image(infile):
    img = Image.open(infile)
    img = np.copy(np.asarray(img, dtype=np.uint8))
    data = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return data

"""
Performs LUT conversion from 8bit to 11bit DN values. Completes this through
numpy vectorization of the image array.
"""
def apply_lut(data):
    lut_conv = lambda t: LUT[int(t)]
    lut_conv_func = np.vectorize(lut_conv)
    data = lut_conv_func(data)
    return data

"""
Applies a color channel radiance multiple. Supplying all 1.0 values will result
in no change.
"""
def apply_rad_multiple(data, rad_corr_mult_red=DEFAULT_RAD_MULTIPLE_RED, rad_corr_mult_green=DEFAULT_RAD_MULTIPLE_GREEN, rad_corr_mult_blue=DEFAULT_RAD_MULTIPLE_BLUE):
    data[::,:,0] *= rad_corr_mult_red
    data[::,:,1] *= rad_corr_mult_green
    data[::,:,2] *= rad_corr_mult_blue
    return data

"""
Normalizes the 11bit DN LUT-derived values (0-2033) to 16bit value range of 0-65525.
"""
def scale_to_uint16(data):
    prescale_max = 2033.0
    data = data / prescale_max
    data = data * 65535.0
    data = np.copy(np.asarray(data, dtype=np.uint16))
    return data

def load_inpaint_mask(inpaint_mask_path):
    mask = cv2.imread(inpaint_mask_path, 0)
    mask = np.copy(np.asarray(mask, dtype=np.uint8))
    return mask

"""
Applies OpenCV inpaint using a left or right eye mask image. Similar to using
content-aware fill in Photoshop.
"""
def apply_inpaint_fix(data, inpaint_mask_path=INPAINT_MASK_RIGHT_PATH):
    mask = load_inpaint_mask(inpaint_mask_path)
    dst = cv2.inpaint(data, mask, 3, cv2.INPAINT_TELEA)
    return dst

def write_image(data, tofile):
    cv2.imwrite(tofile, data)

def get_left_or_right(input_image):
    bn = os.path.basename(input_image)
    return bn[1]

"""
Runs the image conversion routines.
"""
def process_image(input_image, rad_corr_mult_red=DEFAULT_RAD_MULTIPLE_RED, rad_corr_mult_green=DEFAULT_RAD_MULTIPLE_GREEN, rad_corr_mult_blue=DEFAULT_RAD_MULTIPLE_BLUE):
    print("Processing", input_image)

    if not os.path.exists(input_image):
        print("ERROR: Image not found:", input_image)
        return

    eye_code = get_left_or_right(input_image)

    inpaint_mask_base_name = None
    if eye_code == RIGHT_EYE:
        inpaint_mask_base_name = INPAINT_MASK_RIGHT_PATH
    elif eye_code == LEFT_EYE:
        inpaint_mask_base_name = INPAINT_MASK_LEFT_PATH

    inpaint_mask_path = "%s/%s"%(os.path.dirname(__file__), inpaint_mask_base_name)
    
    data = load_image(input_image)
    data = apply_inpaint_fix(data, inpaint_mask_path=inpaint_mask_path)
    data = apply_lut(data)
    data = apply_rad_multiple(data, rad_corr_mult_red, rad_corr_mult_green, rad_corr_mult_blue)


    # Images will be saved as 16bit PNG files, so need to be scaled to that
    # color range while preserving proportional luminosity.
    data = scale_to_uint16(data)
    write_image(data, "%s-decompanded.png"%(input_image[:-4]))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", help="Input bayer patterned image(s)", required=True, type=str, nargs='+')
    parser.add_argument("-R", "--red", help="Radiance correction multiple, red channel", type=float, default=DEFAULT_RAD_MULTIPLE_RED)
    parser.add_argument("-G", "--green", help="Radiance correction multiple, green channel", type=float, default=DEFAULT_RAD_MULTIPLE_GREEN)
    parser.add_argument("-B", "--blue", help="Radiance correction multiple, blue channel", type=float, default=DEFAULT_RAD_MULTIPLE_BLUE)

    args = parser.parse_args()
    input_images = args.image
    rad_corr_mult_red = args.red
    rad_corr_mult_green = args.green
    rad_corr_mult_blue = args.blue

    for input_image in input_images:
        process_image(input_image, rad_corr_mult_red, rad_corr_mult_green, rad_corr_mult_blue)
