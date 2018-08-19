import numpy as np
import spiceypy as spice
import jcspice
import os
import sys
from libtiff import TIFFimage
from PIL import Image
import math

JUNO = -61

JUNO_JUNOCAM_METHANE = -61504
JUNO_JUNOCAM_BLUE = -61501
JUNO_JUNOCAM = -61500
JUNO_JUNOCAM_GREEN = -61502
JUNO_JUNOCAM_RED = -61503

JUNOCAM_STRIP_WIDTH = 1648
JUNOCAM_STRIP_TRUE_HEIGHT = 155
JUNOCAM_STRIP_HEIGHT = 128


LL = 0
LR = 1
UR = 2
UL = 3

JUNOCAM_CHANNEL_RED = 2
JUNOCAM_CHANNEL_GREEN = 1
JUNOCAM_CHANNEL_BLUE = 0



class Camera:
    __CAMERAS = {}

    def __init__(self, camera_id=JUNO_JUNOCAM):
        print "Creating camera with id ", camera_id
        self.id = camera_id
        self.shape, self.frame, self.bsight, self.n, self.bounds = spice.getfov(camera_id, 4, 32, 32)

        self.ul = np.array(self.bounds[UL])
        self.ll = np.array(self.bounds[LL])
        self.ur = np.array(self.bounds[UR])
        self.lr = np.array(self.bounds[LR])

    def intercept_at_time(self, et, radii=None):
        return Intercept(et, camera=self, radii=radii)


    @staticmethod
    def get_camera(camera_id):
        if not camera_id in Camera.__CAMERAS:
            camera = Camera(camera_id)
            Camera.__CAMERAS[camera_id] = camera

        return Camera.__CAMERAS[camera_id]



class SurfacePoint:

    def __init__(self, radius=0.0, lon=0.0, lat=0.0, range=None):
        self.radius = radius
        self.lon = lon
        self.lat = lat
        self.range = range


class Intercept:

    def __init__(self, et, camera, radii=None):
        self.et = et
        self.camera = camera
        if radii is not None:
            self.radii = radii
        else:
            n, radii = spice.bodvrd("JUPITER", "RADII", 64)
            self.radii = radii

        try:
            self.spoint, self.etemit, self.srfvec = spice.sincpt("Ellipsoid", "JUPITER", et, "IAU_JUPITER", "CN+S", "JUNO", camera.frame, camera.bsight)
            self.bs_surface_point = self.surface_point_for_point(self.spoint)
            self.found = True
        except:
            self.found = False
            self.bs_surface_point = None

    def surface_point_for_point(self, spoint):
        radius, lon, lat = spice.reclat(spoint)
        lon = math.degrees(lon)
        lat = math.degrees(lat)

        return SurfacePoint(radius, lon, lat)

    def surface_point_for_vector(self, dvec):
        rotate = spice.pxfrm2(self.camera.frame, "IAU_JUPITER", self.et, self.etemit)
        pmgsmr = spice.vsub(self.spoint, self.srfvec)
        bndvec = spice.mxv(rotate, dvec)
        try:
            spoint = spice.surfpt(pmgsmr, bndvec, self.radii[0], self.radii[1], self.radii[2])
            return self.surface_point_for_point(spoint)
        except:
            return None

    def surface_point_for_vector_lt(self, dvec):
        try:
            spoint, trgepc, srfvec = spice.sincpt("Ellipsoid", "JUPITER", self.et, "IAU_JUPITER", "CN+S", "JUNO", self.camera.frame, dvec)
            return self.surface_point_for_point(spoint)
        except:
            return None

    def surface_point_for_sensor_xy(self, x, y):
        num_crosstalk_pixels = JUNOCAM_STRIP_TRUE_HEIGHT - JUNOCAM_STRIP_HEIGHT
        half_num_crosstalk_pixels = num_crosstalk_pixels / 2.0

        fX = float(x) / JUNOCAM_STRIP_WIDTH
        fY = (float(y) + half_num_crosstalk_pixels) / JUNOCAM_STRIP_TRUE_HEIGHT

        x0 = self.camera.ur * fX + (self.camera.ul * (1.0 - fX))
        x1 = self.camera.lr * fX + (self.camera.ll * (1.0 - fX))

        dvec = x0 * fY + (x1 * (1.0 - fY))

        if self.found:
            return self.surface_point_for_vector(dvec)
        else:
            return self.surface_point_for_vector_lt(dvec)


    def illumination_for_vector(self, dvec):
        trgepc, srfvec, phase, solar, emissn = spice.ilumin("Ellipsoid", "JUPITER", self.et, "IAU_JUPITER", "LT+S", "JUNO", dvec)

        phase = math.degrees(phase)
        solar = math.degrees(solar)
        emissn = math.degrees(emissn)

        return phase, solar, emissn


    def determine_middle_pixel_resolution(self):
        midX = int(round(JUNOCAM_STRIP_WIDTH / 2.0))
        midY = int(round(JUNOCAM_STRIP_HEIGHT / 2.0))

        midL = self.surface_point_for_sensor_xy(midX - .5, midY - .5)
        midR = self.surface_point_for_sensor_xy(midX + .5, midY + .5)

        latRes = abs(midR.lat - midL.lat)
        lonRes = abs(midR.lon - midL.lon)

        return latRes, lonRes



    def determine_coordinate_extents(self):
        spUL = self.surface_point_for_vector(self.camera.bounds[UL])
        spLL = self.surface_point_for_vector(self.camera.bounds[LL])
        spUR = self.surface_point_for_vector(self.camera.bounds[UR])
        spLR = self.surface_point_for_vector(self.camera.bounds[LR])

        lats = []
        lons = []

        for sp in (spUL, spLL, spUR, spLR):
            if sp is not None:
                lats.append(sp.lat)
                lons.append(sp.lon)

        lats = np.array(lats)
        lons = np.array(lons)

        if len(lats) > 0 and len(lons) > 0:
            maxLat = lats.max()
            maxLon = lons.max()

            minLat = lats.min()
            minLon = lons.min()

            bounds = {
                "lats": {
                    "min": minLat,
                    "max": maxLat
                },
                "lons": {
                    "min": minLon,
                    "max": maxLon
                }
            }

            return bounds
        else:
            return None

def get_intercept_surface_point(intercept, x, y):
    sp = intercept.surface_point_for_sensor_xy(x, y)
    return sp

def calc_surface_normal(v0, v1, v2):
    v0 = np.array(v0)
    v1 = np.array(v1)
    v2 = np.array(v2)

    U = v1 - v0
    V = v2 - v1

    N = np.cross(U, V)
    return N

def calc_light_for_band(data, et,  band_num, camera, band_height=JUNOCAM_STRIP_HEIGHT):
    top = band_num * band_height
    bottom = top + band_height

    intercept = camera.intercept_at_time(et)

    jupiter_vec, lt = spice.spkpos('JUPITER', et, 'IAU_SUN', 'NONE', 'SUN')
    jupiter_vec, vmag = spice.unorm(jupiter_vec)
    jupiter_vec = np.array(jupiter_vec)

    strip_data = np.zeros((JUNOCAM_STRIP_HEIGHT, JUNOCAM_STRIP_WIDTH))
    for y in range(0, JUNOCAM_STRIP_HEIGHT):
        for x in range(0, JUNOCAM_STRIP_WIDTH):
            sp = intercept.surface_point_for_sensor_xy(x, y)
            continue
            if sp is not None:
                lon = math.radians(sp.lon)
                lat = math.radians(sp.lat)

                lonp1 = math.radians(sp.lon + 0.01)
                latm1 = math.radians(sp.lat - 0.01)
                ulVector = np.array(spice.srfrec(599, lon, lat))
                llVector = np.array(spice.srfrec(599, lon, latm1))
                urVector = np.array(spice.srfrec(599, lonp1, lat))

                dvec = calc_surface_normal(ulVector, llVector, urVector)
                dvec, dmag = spice.unorm(dvec)
                dot = spice.vdot(dvec, jupiter_vec)
                illum = np.max(np.array((0.0, dot)))
                strip_data[y][x] = illum
                #phase, solar, emissn = intercept.illumination_for_vector(dvec)

                #norm = spice.srfnrm("DSK/UNPRIORITIZED", "JUPITER", et, "IAU_JUPITER", (dvec,))
                #print phase, solar, emissn

    data[top:bottom] = strip_data
    #data[top:bottom] /= flat_data


def open_image(img_path):
    img = Image.open(img_path)
    data = np.copy(np.asarray(img, dtype=np.float32))
    img.close()
    return data

# For testing
if __name__ == "__main__":

    img_path = sys.argv[1]

    """
    illum_path = sys.argv[2]

    data = open_image(img_path)
    light = open_image(illum_path)

    data /= data.max()
    light /= light.max()

    light = 1.0 - light

    data = light * data
    data /= data.max()
    data *= 65535.0
    data_matrix = data.astype(np.uint16)

    tiff = TIFFimage(data_matrix, description='')
    tiff.write_file("test_data.tif", compression='none')


    sys.exit(0)
    """
    start_time = sys.argv[2]
    interframe_delay = float(sys.argv[3])

    print "Loading SPICE..."
    jcspice.load_kernels("/Users/kgill/ISIS/data")

    print "Loading Image Data..."
    data = open_image(img_path)
    height = data.shape[0]
    width = data.shape[1]

    camera_red = Camera.get_camera(JUNO_JUNOCAM_RED)
    camera_green = Camera.get_camera(JUNO_JUNOCAM_GREEN)
    camera_blue = Camera.get_camera(JUNO_JUNOCAM_BLUE)
    et_start = spice.str2et(start_time)

    light_data = np.zeros(data.shape)


    num_exposures = height / JUNOCAM_STRIP_HEIGHT / 3
    for exposure in range(0, num_exposures):
        frame_0 = exposure * 3
        frame_1 = exposure * 3 + 1
        frame_2 = exposure * 3 + 2
        et = et_start + interframe_delay * exposure

        print "Exposure #", exposure, ", Blue..."
        calc_light_for_band(light_data, et, frame_0, camera_blue)

        print "Exposure #", exposure, ", Green..."
        calc_light_for_band(light_data, et, frame_1, camera_green)

        print "Exposure #", exposure, ", Red..."
        calc_light_for_band(light_data, et, frame_2, camera_red)

    light_data = 1.0 - light_data
    data = data * light_data
    data /= data.max()
    data *= 65535.0
    data_matrix = data.astype(np.uint16)

    tiff = TIFFimage(data_matrix, description='')
    tiff.write_file("test_data.tif", compression='none')



