#!/usr/bin/env python
"""
    Simplified MSL MAHLI debayering and color correction routines using
    JPEG-compressed public raw images.

    References:

    Edgett, K.S., Yingst, R.A., Ravine, M.A. et al.
    Curiosity’s Mars Hand Lens Imager (MAHLI) Investigation.
    Space Sci Rev 170, 259–317 (2012).
    https://doi.org/10.1007/s11214-012-9910-4

    Edgett, K. S., M. A. Caplinger, J. N. Maki, M. A. Ravine, F. T. Ghaemi, S. McNair, K. E. Herkenhoff,
    B. M. Duston, R. G. Willson, R. A. Yingst, M. R. Kennedy, M. E. Minitti, A. J. Sengstacken, K. D. Supulver,
    L. J. Lipkaman, G. M. Krezoski, M. J. McBride, T. L. Jones, B. E. Nixon, J. K. Van Beek, D. J. Krysak, and R. L. Kirk
    (2015) Curiosity’s robotic arm-mounted Mars Hand Lens Imager (MAHLI): Characterization and calibration status,
    MSL MAHLI Technical Report 0001 (version 1: 19 June 2015; version 2: 05 October 2015).
    doi:10.13140/RG.2.1.3798.5447
    https://doi.org/10.13140/RG.2.1.3798.5447

    Bell, J. F. et al. (2017), The Mars Science Laboratory Curiosity rover
    Mastcam instruments: Preflight and in‐flight calibration, validation,
    and data archiving, Earth and Space Science, 4, 396– 452,
    doi:10.1002/2016EA000219.
    https://doi.org/10.1002/2016EA000219
"""

import numpy as np
import cv2
import sys
from PIL import Image
import argparse
import sys
import os


DEFAULT_RAD_MULTIPLE_RED = 1.0 #1.16
DEFAULT_RAD_MULTIPLE_GREEN = 1.0
DEFAULT_RAD_MULTIPLE_BLUE = 1.0 #1.05

MAHLI_INPAINT_MASK_PATH = "%s/%s"%(os.path.dirname(__file__), "cal/MSL_MAHLI_INPAINT_Sol2904_V1.png")
MAHLI_FLAT_PATH = "%s/%s"%(os.path.dirname(__file__), "cal/MSL_MAHLI_FLAT_Sol2904_V1.png")

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

def load_image(infile):
    img = Image.open(infile)
    img = np.copy(np.asarray(img, dtype=np.float32))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = check_crop(img)
    return img

def load_flat_field(infile):
    img = Image.open(infile)
    img = np.copy(np.asarray(img, dtype=np.float32))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = check_crop(img)
    return img


def load_inpaint_mask(inpaint_mask_path):
    mask = cv2.imread(inpaint_mask_path, 0)
    mask = np.copy(np.asarray(mask, dtype=np.uint8))
    mask = check_crop(mask)
    return mask

"""
Applies OpenCV inpaint using a left or right eye mask image. Similar to using
content-aware fill in Photoshop.
"""
def apply_inpaint_fix(data, inpaint_mask_path=MAHLI_INPAINT_MASK_PATH):
    mask = load_inpaint_mask(inpaint_mask_path)
    data = np.copy(np.asarray(data, dtype=np.uint8))
    data = cv2.inpaint(data, mask, 3, cv2.INPAINT_TELEA)
    data = np.copy(np.asarray(data, dtype=np.float32))
    return data


def apply_flat_field_on_channel(data, flat, channel):
    d = data[::,:,channel]
    f = flat[::,:,channel]
    m = f.mean()
    r = (d * m) / f
    return r

def apply_flat_field(data, mask_file_path=MAHLI_FLAT_PATH):
    flat = load_image(mask_file_path)
    flat = apply_inpaint_fix(flat)
    flat = apply_lut(flat)
    r = apply_flat_field_on_channel(data, flat, 0)
    g = apply_flat_field_on_channel(data, flat, 1)
    b = apply_flat_field_on_channel(data, flat, 2)
    a = np.stack((r, g, b), axis=-1)
    return a

def scale_to_uint16(data):
    prescale_max = 2033.0
    data = data / prescale_max
    data = data * 65535.0
    data = np.around(data)
    data = np.copy(np.asarray(data, dtype=np.uint16))
    return data

def write_image(data, tofile):
    cv2.imwrite(tofile, data)

"""
Crop to 1584x1184x3 minus border crop of 3 pixels
"""
def check_crop(data, border_crop=3):
    if data.shape[0] == 1200 and data.shape[1] == 1632:
        data = data[16:1200,32:1616]
    data = data[border_crop:data.shape[0]-(border_crop*2),border_crop:data.shape[1]-(border_crop*2)]
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

def process_image(image_path, rad_corr_mult_red, rad_corr_mult_green, rad_corr_mult_blue):
    print("Processing", image_path)

    if not os.path.exists(image_path):
        print("ERROR: Image not found:", image_path)
        return

    data = load_image(image_path)
    data = apply_inpaint_fix(data)
    data = apply_lut(data)
    data = apply_flat_field(data)
    data = apply_rad_multiple(data, rad_corr_mult_red, rad_corr_mult_green, rad_corr_mult_blue)

    data = scale_to_uint16(data)

    # rjcal == Raw JPEG Calibrated. Need to differentiate this from
    # a fully calibrated image (RDR) derived from the full
    # science data using the full MSL pipeline.
    # This script is hack-calibration.
    write_image(data, "%s-rjcal.png"%(input_image[:-4]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", help="Input MAHLI raw image(s)", required=True, type=str, nargs='+')
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
