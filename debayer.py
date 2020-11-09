"""
    Simplified MSL MastCam debayering and color correction routines using
    JPEG-compressed public raw images.

    References:
    Bell, J. F., Godber, A., McNair, S., Caplinger, M. A., Maki, J. N., Lemmon, M. T.,
    Van Beek, J., Malin, M. C., Wellington, D., Kinch, K. M., & Madsen, M. B. (2017).
    The Mars Science Laboratory Curiosity rover Mast Camera (Mastcam) instruments:
    Pre‐flight and in‐flight calibration, validation, and data archiving.
    Earth and Space Science, 4(7), 396– 452.

    Retrieved from: https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2016EA000219

"""


import numpy as np
import cv2
import sys
from PIL import Image
import argparse

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
    data = np.copy(np.asarray(img, dtype=np.uint16))
    return data

def apply_lut(data, ctable=LUT):
    ctable = LUT
    for a in range(0, len(data)):
        for b in range(0, len(data[a])):
            data[a][b] = ctable[int(round(data[a][b]))]
    return data

def apply_debayer(data):
    data = cv2.cvtColor(data, cv2.COLOR_BAYER_BG2BGR)
    return data

def scale_to_uint16(data, no_lut=False):
    data = np.copy(np.asarray(data, dtype=np.float32))

    prescale_max = 2033.0 if no_lut is False else 255

    data = data / prescale_max
    data = data * 65535.0
    data = np.copy(np.asarray(data, dtype=np.uint16))
    return data

"""
    Applies white balance coefficients [J. F. Bell, et al]
"""
def apply_white_balance(data):
    WB = np.array([1.2, 1.0, 1.26])
    for a in range(0, len(data)):
        for b in range(0, len(data[a])):
            data[a][b] = data[a][b] * WB
    return data

def write_image(data, tofile):
    cv2.imwrite(tofile, data)

def process_image(input_image, no_lut=False, white_balance=False):
    print("Processing", input_image)
    data = load_image(input_image)
    if not no_lut == True:
        data = apply_lut(data)
    data = apply_debayer(data)
    if white_balance is True:
        data = apply_white_balance(data)
    data = scale_to_uint16(data, no_lut)
    write_image(data, "%s.png"%(input_image[:-4]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", help="Input bayer patterned image(s)", required=True, type=str, nargs='+')
    parser.add_argument("-r", "--raw", help="Do not apply lookup table (raw debayered)", action="store_true")
    parser.add_argument("-w", "--white_balance", help="Apply white balance multiplication", action="store_true")
    args = parser.parse_args()
    input_images = args.image
    no_lut = args.raw
    white_balance = args.white_balance

    for input_image in input_images:
        process_image(input_image, no_lut, white_balance)
