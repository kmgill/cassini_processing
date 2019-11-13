import numpy as np
import spiceypy as spice
import os
import sys
from libtiff import TIFFimage
from PIL import Image
import math
from sciimg.isis3.junocam import jcspice
from sciimg.isis3 import _core
import argparse

JUNO = -61

JUNO_JUNOCAM_METHANE = -61504
JUNO_JUNOCAM_BLUE = -61501
JUNO_JUNOCAM = -61500
JUNO_JUNOCAM_GREEN = -61502
JUNO_JUNOCAM_RED = -61503

SENSOR_PIXELS_H = 1648
SENSOR_PIXELS_V = 1214

#JUNOCAM_STRIP_TRUE_WIDTH = 1648
JUNOCAM_STRIP_TRUE_HEIGHT = 155

JUNOCAM_STRIP_WIDTH = 1648
JUNOCAM_STRIP_HEIGHT = 128

FOCAL_LENGTH = 10.997
PIXEL_SIZE = 0.0074

INS_61504_DISTORTION_K1 = -5.9624209455667325e-08
INS_61504_DISTORTION_K2 = 2.7381910042256151e-14
INS_61504_DISTORTION_X = 814.21
INS_61504_DISTORTION_Y = 315.48

INS_61501_DISTORTION_K1 = -5.9624209455667325e-08
INS_61501_DISTORTION_K2 = 2.7381910042256151e-14
INS_61501_DISTORTION_X = 814.21
INS_61501_DISTORTION_Y = 158.48

INS_61500_DISTORTION_K1 = -5.9624209455667325e-08
INS_61500_DISTORTION_K2 = 2.7381910042256151e-14
INS_61500_DISTORTION_X = 814.21
INS_61500_DISTORTION_Y = 78.48

INS_61502_DISTORTION_K1 = -5.9624209455667325e-08
INS_61502_DISTORTION_K2 = 2.7381910042256151e-14
INS_61502_DISTORTION_X = 814.21
INS_61502_DISTORTION_Y = 3.48

INS_61503_DISTORTION_K1 = -5.9624209455667325e-08
INS_61503_DISTORTION_K2 = 2.7381910042256151e-14
INS_61503_DISTORTION_X = 814.21
INS_61503_DISTORTION_Y = -151.52

LL = 0
LR = 1
UR = 2
UL = 3

JUNOCAM_CHANNEL_RED = 2
JUNOCAM_CHANNEL_GREEN = 1
JUNOCAM_CHANNEL_BLUE = 0


def print_r(*args):
    s = ' '.join(map(str, args))
    print(s)


class Camera:
    __CAMERAS = {}

    def __init__(self, camera_id=JUNO_JUNOCAM):
        print_r("Creating camera with id ", camera_id)
        self.id = camera_id
        self.shape, self.frame, self.bsight, self.n, self.bounds = spice.getfov(camera_id, 4, 32, 32)

        self.ul = np.array(self.bounds[UL])
        self.ll = np.array(self.bounds[LL])
        self.ur = np.array(self.bounds[UR])
        self.lr = np.array(self.bounds[LR])


    @staticmethod
    def get_camera(camera_id):
        if not camera_id in Camera.__CAMERAS:
            camera = Camera(camera_id)
            Camera.__CAMERAS[camera_id] = camera

        return Camera.__CAMERAS[camera_id]


def distortion_by_camera_id(cam_id):
    if cam_id == JUNO_JUNOCAM:
        k1 = INS_61500_DISTORTION_K1
        k2 = INS_61500_DISTORTION_K2
        cx = INS_61500_DISTORTION_X
        cy = INS_61500_DISTORTION_Y
    elif cam_id == JUNO_JUNOCAM_METHANE:
        k1 = INS_61504_DISTORTION_K1
        k2 = INS_61504_DISTORTION_K2
        cx = INS_61504_DISTORTION_X
        cy = INS_61504_DISTORTION_Y
    elif cam_id == JUNO_JUNOCAM_BLUE:
        k1 = INS_61501_DISTORTION_K1
        k2 = INS_61501_DISTORTION_K2
        cx = INS_61501_DISTORTION_X
        cy = INS_61501_DISTORTION_Y
    elif cam_id == JUNO_JUNOCAM_GREEN:
        k1 = INS_61502_DISTORTION_K1
        k2 = INS_61502_DISTORTION_K2
        cx = INS_61502_DISTORTION_X
        cy = INS_61502_DISTORTION_Y
    elif cam_id == JUNO_JUNOCAM_RED:
        k1 = INS_61503_DISTORTION_K1
        k2 = INS_61503_DISTORTION_K2
        cx = INS_61503_DISTORTION_X
        cy = INS_61503_DISTORTION_Y
    else:
        raise Exception("Invalid camera identifier: %s"%cam_id)

    fl = PIXEL_SIZE
    return (k1, k2, cx, cy, fl)


def sensor_top_by_camera_id(cam_id):
    if cam_id == JUNO_JUNOCAM:
        top = 0
    elif cam_id == JUNO_JUNOCAM_METHANE:
        top = 291
    elif cam_id == JUNO_JUNOCAM_BLUE:
        top = 456
    elif cam_id == JUNO_JUNOCAM_GREEN:
        top = 611
    elif cam_id == JUNO_JUNOCAM_RED:
        top = 766
    else:
        raise Exception("Invalid camera identifier: %s"%cam_id)
    return top


# https://naif.jpl.nasa.gov/pub/naif/JUNO/kernels/ik/juno_junocam_v03.ti
def undistort(cam_id, c):
    [k1, k2, cx, cy, fl] = distortion_by_camera_id(cam_id)
    xd, yd = c[0], c[1]
    for i in range(5):  # fixed number of iterations for simplicity
        r2 = (xd ** 2 + yd ** 2)
        dr = 1 + k1 * r2 + k2 * r2 * r2
        xd = c[0] / dr
        yd = c[1] / dr
    return [xd, yd]


# https://naif.jpl.nasa.gov/pub/naif/JUNO/kernels/ik/juno_junocam_v03.ti
def distort(cam_id, c):
    [k1, k2, cx, cy, fl] = distortion_by_camera_id(cam_id)
    xd, yd = c[0], c[1]
    r2 = (xd ** 2 + yd ** 2)
    dr = 1 + k1 * r2 + k2 * r2 * r2
    xd *= dr
    yd *= dr
    return [xd, yd]


def xy_coords_to_ref_frame_vector(cam_id, x, y):
    [k1, k2, cx, cy, fl] = distortion_by_camera_id(cam_id)
    cam = [0, 0]
    cam[0] = x - cx
    cam[1] = y - cy
    cam = undistort(cam_id, cam)
    v = [cam[0], cam[1], fl]
    return v


def strip_xy_to_sensor_vector(cam_id, x, y):
    xy_distorted = xy_coords_to_ref_frame_vector(cam_id, x, y)
    x_dist = xy_distorted[0]
    y_dist = xy_distorted[1] * -1.0

    o = x_dist * PIXEL_SIZE
    ang_x_rad = math.atan(o / FOCAL_LENGTH)

    o = y_dist * PIXEL_SIZE
    ang_y_rad = math.atan(o / FOCAL_LENGTH)

    v = spice.rotvec([0, 0, 1], ang_x_rad, 1)
    v = spice.rotvec(v, ang_y_rad, 2)

    v2 = [0, 0, 0]
    v2[0] = v[1]
    v2[1] = v[0]
    v2[2] = v[2]

    return v2


def calc_light_for_band(data, et,  band_num, camera, band_height=JUNOCAM_STRIP_HEIGHT):
    top = band_num * band_height
    bottom = top + band_height

    shape, obsref, bsight, n, bounds = spice.getfov(camera.id, 4, 32, 32)

    strip_data = np.zeros((JUNOCAM_STRIP_HEIGHT, JUNOCAM_STRIP_WIDTH))
    for y in range(0, JUNOCAM_STRIP_HEIGHT):
        for x in range(0, JUNOCAM_STRIP_WIDTH):
            try:
                dvec = strip_xy_to_sensor_vector(camera.id, x, y)
                spoint, etemit, srfvec = spice.sincpt("Ellipsoid", 'JUPITER', et, 'IAU_JUPITER', 'LT+S', 'JUNO', obsref, dvec)
                trgepc, srfvec, phase, solar, emissn, visibl, lit = spice.illumf("Ellipsoid", 'JUPITER', 'SUN', et,'IAU_JUPITER', 'LT+S', 'JUNO', spoint)

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

    camera_red = Camera.get_camera(JUNO_JUNOCAM_RED)
    camera_green = Camera.get_camera(JUNO_JUNOCAM_GREEN)
    camera_blue = Camera.get_camera(JUNO_JUNOCAM_BLUE)
    et_start = spice.str2et(start_date)

    light_data = np.ones(img_data.shape)

    num_exposures = height / JUNOCAM_STRIP_HEIGHT / 3
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



