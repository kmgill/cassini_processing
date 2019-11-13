import numpy as np
import spiceypy as spice
import math
from sciimg.pipelines.junocam import jcspice




JUNO_JUNOCAM_METHANE = -61504
JUNO_JUNOCAM_BLUE = -61501
JUNO_JUNOCAM = -61500
JUNO_JUNOCAM_GREEN = -61502
JUNO_JUNOCAM_RED = -61503

SENSOR_PIXELS_H = 1648
SENSOR_PIXELS_V = 1214

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


class SurfaceNotFoundException(Exception):
    pass

class Camera:
    __CAMERAS = {}

    def __init__(self, camera_id=JUNO_JUNOCAM):
        print_r("Creating camera with id ", camera_id)
        self.id = camera_id
        self.shape, self.obsref, self.bsight, self.n, self.bounds = self.getfov()

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


    def distortion_by_camera_id(self):
        if self.id == JUNO_JUNOCAM:
            k1 = INS_61500_DISTORTION_K1
            k2 = INS_61500_DISTORTION_K2
            cx = INS_61500_DISTORTION_X
            cy = INS_61500_DISTORTION_Y
        elif self.id == JUNO_JUNOCAM_METHANE:
            k1 = INS_61504_DISTORTION_K1
            k2 = INS_61504_DISTORTION_K2
            cx = INS_61504_DISTORTION_X
            cy = INS_61504_DISTORTION_Y
        elif self.id == JUNO_JUNOCAM_BLUE:
            k1 = INS_61501_DISTORTION_K1
            k2 = INS_61501_DISTORTION_K2
            cx = INS_61501_DISTORTION_X
            cy = INS_61501_DISTORTION_Y
        elif self.id == JUNO_JUNOCAM_GREEN:
            k1 = INS_61502_DISTORTION_K1
            k2 = INS_61502_DISTORTION_K2
            cx = INS_61502_DISTORTION_X
            cy = INS_61502_DISTORTION_Y
        elif self.id == JUNO_JUNOCAM_RED:
            k1 = INS_61503_DISTORTION_K1
            k2 = INS_61503_DISTORTION_K2
            cx = INS_61503_DISTORTION_X
            cy = INS_61503_DISTORTION_Y
        else:
            raise Exception("Invalid camera identifier: %s"%self.id)

        fl = PIXEL_SIZE
        return k1, k2, cx, cy, fl

    def sensor_top_by_camera_id(self):
        if self.id == JUNO_JUNOCAM:
            top = 0
        elif self.id == JUNO_JUNOCAM_METHANE:
            top = 291
        elif self.id == JUNO_JUNOCAM_BLUE:
            top = 456
        elif self.id == JUNO_JUNOCAM_GREEN:
            top = 611
        elif self.id == JUNO_JUNOCAM_RED:
            top = 766
        else:
            raise Exception("Invalid camera identifier: %s"%self.id)
        return top


    # https://naif.jpl.nasa.gov/pub/naif/JUNO/kernels/ik/juno_junocam_v03.ti
    def undistort(self, c):
        [k1, k2, cx, cy, fl] = self.distortion_by_camera_id()
        xd, yd = c[0], c[1]
        for i in range(5):  # fixed number of iterations for simplicity
            r2 = (xd ** 2 + yd ** 2)
            dr = 1 + k1 * r2 + k2 * r2 * r2
            xd = c[0] / dr
            yd = c[1] / dr
        return [xd, yd]


    # https://naif.jpl.nasa.gov/pub/naif/JUNO/kernels/ik/juno_junocam_v03.ti
    def distort(self, c):
        [k1, k2, cx, cy, fl] = self.distortion_by_camera_id()
        xd, yd = c[0], c[1]
        r2 = (xd ** 2 + yd ** 2)
        dr = 1 + k1 * r2 + k2 * r2 * r2
        xd *= dr
        yd *= dr
        return [xd, yd]


    def xy_coords_to_ref_frame_vector(self, x, y):
        [k1, k2, cx, cy, fl] = self.distortion_by_camera_id()
        cam = [0, 0]
        cam[0] = x - cx
        cam[1] = y - cy
        cam = self.undistort(cam)
        v = [cam[0], cam[1], fl]
        return v


    def strip_xy_to_sensor_vector(self, x, y):
        xy_distorted = self.xy_coords_to_ref_frame_vector(x, y)
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

    def getfov(self):
        shape, obsref, bsight, n, bounds = spice.getfov(self.id, 4, 32, 32)
        return shape, obsref, bsight, n, bounds

    def sincpt_for_sensor_xy(self, et, x, y):
        dvec = self.strip_xy_to_sensor_vector(x, y)
        try:
            spoint, etemit, srfvec = spice.sincpt("Ellipsoid", 'JUPITER', et, 'IAU_JUPITER', 'LT+S', 'JUNO', self.obsref, dvec)
        except:
            raise SurfaceNotFoundException()
        return spoint, etemit, srfvec

    def illumf(self, et, spoint):
        trgepc, srfvec, phase, solar, emissn, visibl, lit = spice.illumf("Ellipsoid", 'JUPITER', 'SUN', et, 'IAU_JUPITER', 'LT+S', 'JUNO', spoint)
        return trgepc, srfvec, phase, solar, emissn, visibl, lit

    def illumf_for_sensor_xy(self, et, x, y):
        spoint, etemit, srfvec = self.sincpt_for_sensor_xy(et, x, y)
        trgepc, srfvec, phase, solar, emissn, visibl, lit = self.illumf(et, spoint)
        return trgepc, srfvec, phase, solar, emissn, visibl, lit

    def surface_coords_for_surface_point(self, spoint):
        radius, lon, lat = spice.reclat(spoint)
        lon = math.degrees(lon)
        lat = math.degrees(lat)

        return radius, lon, lat

    def surface_coords_for_sensor_xy(self, et, x, y):
        spoint, etemit, srfvec = self.sincpt_for_sensor_xy(et, x, y)
        return self.surface_coords_for_surface_point(spoint)
