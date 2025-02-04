import sys
import os
import numpy as np
from libtiff import TIFFimage
from PIL import Image
import cv2

BAND_HEIGHT = 128

INPAINT_MASK_RED = "junocam_inpaint_mask_pj32_v1_red.png"
INPAINT_MASK_GREEN = "junocam_inpaint_mask_pj32_v1_green.png"
INPAINT_MASK_BLUE = "junocam_inpaint_mask_pj32_v1_blue.png"

BLUE_TOP = 0
BLUE_BOTTOM = 128
GREEN_TOP = 1 * 128
GREEN_BOTTOM = 2 * 128
RED_TOP = 2 * 128
RED_BOTTOM = 3 * 128

def open_image(img_path):
    img = Image.open(img_path)
    data = np.copy(np.asarray(img, dtype=np.uint8))
    img.close()
    return data

def load_inpaint_mask(inpaint_mask_path, verbose=False):
    if verbose is True:
        print("Loading inpaint mask", inpaint_mask_path)
    mask = cv2.imread(inpaint_mask_path, 0)
    mask = np.copy(np.asarray(mask, dtype=np.uint8))
    return mask

def apply_inpaint_fix(data, inpaint_mask_path):
    mask = load_inpaint_mask(inpaint_mask_path)
    dst = cv2.inpaint(data, mask, 3, cv2.INPAINT_TELEA)
    return dst



def process_inpaint_fill(img_data, verbose=False):
    inpaint_mask_red = load_inpaint_mask("%s/%s"%(os.path.dirname(__file__), INPAINT_MASK_RED), verbose)
    inpaint_mask_green = load_inpaint_mask("%s/%s"%(os.path.dirname(__file__), INPAINT_MASK_GREEN), verbose)
    inpaint_mask_blue = load_inpaint_mask("%s/%s"%(os.path.dirname(__file__), INPAINT_MASK_BLUE), verbose)

    img_height = img_data.shape[0]
    bands_per_image = int((img_height / 128 / 3))
    triplet_height = 128 * 3

    for triplet_num in range(0, bands_per_image):
        top = triplet_num * triplet_height
        bottom = top + triplet_height

        if verbose is True:
            print("Triplet Number:", triplet_num)
            print("     Triplet top/bottom:", top, bottom)
        triplet_data = img_data[top:bottom]
        if verbose is True:
            print("     Triplet Shape:", triplet_data.shape)

        img_data[top+BLUE_TOP:top+BLUE_BOTTOM] = cv2.inpaint(triplet_data[BLUE_TOP:BLUE_BOTTOM], inpaint_mask_blue, 3, cv2.INPAINT_TELEA)
        img_data[top+GREEN_TOP:top+GREEN_BOTTOM] = cv2.inpaint(triplet_data[GREEN_TOP:GREEN_BOTTOM], inpaint_mask_green, 3, cv2.INPAINT_TELEA)
        img_data[top+RED_TOP:top+RED_BOTTOM] = cv2.inpaint(triplet_data[RED_TOP:RED_BOTTOM], inpaint_mask_red, 3, cv2.INPAINT_TELEA)
    return img_data


if __name__ == "__main__":
    img_data = open_image(sys.argv[1])
    process_inpaint_fill(img_data, True)

    cv2.imwrite("test.png", img_data)
