import numpy as np
import spiceypy as spice
import os
import sys
from libtiff import TIFFimage
from PIL import Image
import math
from sciimg.pipelines.junocam import jcspice
from sciimg.isis3 import _core
import argparse
from sciimg.pipelines.junocam import junocam
import traceback

JUNO = -61


def print_r(*args):
    s = ' '.join(map(str, args))
    print(s)




def calc_light_for_band(data, et, band_num, camera, band_height=junocam.JUNOCAM_STRIP_HEIGHT):
    top = band_num * band_height
    bottom = top + band_height

    strip_data = np.zeros((junocam.JUNOCAM_STRIP_HEIGHT, junocam.JUNOCAM_STRIP_WIDTH))
    for y in range(0, junocam.JUNOCAM_STRIP_HEIGHT):
        for x in range(0, junocam.JUNOCAM_STRIP_WIDTH):
            try:
                trgepc, srfvec, phase, solar, emissn, visibl, lit = camera.illumf_for_sensor_xy(et, x, y)

                if math.cos(solar) <= 0.0:
                    lum = 0.0
                else:
                    lum = abs(math.cos(solar)) ** 0.875 # h/t Bjorn Jonsson
                strip_data[y][x] = lum
            except:
                pass

    data[top:bottom] = strip_data


def open_image(img_path):
    img = Image.open(img_path)
    data = np.copy(np.asarray(img, dtype=np.float32))
    img.close()
    return data


def delambert(img_data, start_date, interframe_delay, verbose=False):
    height = img_data.shape[0]

    camera_red = junocam.Camera.get_camera(junocam.JUNO_JUNOCAM_RED)
    camera_green = junocam.Camera.get_camera(junocam.JUNO_JUNOCAM_GREEN)
    camera_blue = junocam.Camera.get_camera(junocam.JUNO_JUNOCAM_BLUE)
    et_start = spice.str2et(start_date)

    light_data = np.ones(img_data.shape)

    num_exposures = height / junocam.JUNOCAM_STRIP_HEIGHT / 3
    if verbose:
        print_r("Number of triplets (exposures):", num_exposures)

    start_time_bias = 0.06188
    interframe_delay_bias = 0.0010347187388880883

    for exposure in range(0, num_exposures):
    #for exposure in range(8, 12):
    #if True:
    #    exposure = 7
        frame_0 = exposure * 3
        frame_1 = exposure * 3 + 1
        frame_2 = exposure * 3 + 2

        et = et_start + start_time_bias + (exposure) * (interframe_delay + interframe_delay_bias)

        if verbose:
            utcstr = spice.et2utc( et, "C", 3)
            print_r("Processing triplet", (exposure + 1), "of", num_exposures, "on date/time:", utcstr)

        if verbose:
            print_r("   Exposure #", (exposure + 1), ", Blue...")
        calc_light_for_band(light_data, et, frame_0, camera_blue)

        if verbose:
            print_r("   Exposure #", (exposure + 1), ", Green...")
        calc_light_for_band(light_data, et, frame_1, camera_green)

        if verbose:
            print_r("   Exposure #", (exposure + 1), ", Red...")
        calc_light_for_band(light_data, et, frame_2, camera_red)

    #light_data = 1.0 - light_data
    img_data[:] = light_data
    #img_data *= light_data
    return img_data


# For testing
if __name__ == "__main__":

    try:
        _core.is_isis3_initialized()
    except:
        print_r("ISIS3 has not been initialized. Please do so. Now.")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    parser.add_argument("-k", "--kernelbase", help="Base directory for spice kernels", required=False, type=str,
                        default=os.environ["ISIS3DATA"])
    parser.add_argument("-p", "--predicted", help="Utilize predicted kernels", action="store_true")
    parser.add_argument("-d", "--data", help="Source PDS dataset", required=True, type=str)
    parser.add_argument("-s", "--start", help="Start Date", required=True, type=str)
    parser.add_argument("-i", "--delay", help="Interframe Delay", required=True, type=float)
    args = parser.parse_args()

    is_verbose = args.verbose
    kernelbase = args.kernelbase
    allow_predicted = args.predicted
    source = args.data
    start_date = args.start
    interframe_delay = args.delay

    if is_verbose:
        print_r("Loading spice kernels...")
    jcspice.load_kernels(kernelbase, allow_predicted)

    print_r("Loading Image Data...")
    data = open_image(source)

    delambert(data, start_date, interframe_delay, is_verbose)

    data /= data.max()
    data *= 65535.0
    data_matrix = data.astype(np.uint16)

    tiff = TIFFimage(data_matrix, description='')
    tiff.write_file("test_data.tif", compression='none')



