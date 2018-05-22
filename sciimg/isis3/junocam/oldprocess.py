import sys
import os
import numpy as np
from libtiff import TIFFimage
from PIL import Image
from sciimg.isis3.junocam.corrections import DEAD_PIXEL_MAP

BAND_HEIGHT = 128

class SourceRawImage:

    def __init__(self, path):
        img = Image.open(path)
        self.data = np.copy(np.asarray(img, dtype=np.uint16))

        if self.data.max() > 255: # BAD ASSUMPTION! BAD!
            self.__byte_depth = 16
        else:
            self.__byte_depth = 8

        img.close()
        self.width = self.data.shape[1]
        self.height = self.data.shape[0]

    def get_byte_depth(self):
        return self.__byte_depth

    def get_band(self, band_num, band_height=BAND_HEIGHT):
        top = band_num * band_height
        bottom = top + band_height
        im = self.data[top:bottom]
        return im



class DestImage:
    def __init__(self, width, height, band_height=BAND_HEIGHT):
        self.width = width
        self.height = height
        self.band_height = band_height
        self.data = np.empty((height, width))
        self.data[:] = np.NAN

    def set_band(self, band, band_num, band_overlap=10, byte_depth=8):
        start_y = (band_num * (self.band_height - band_overlap))

        for y in range(0, self.band_height):
            for x in range(0, self.width):

                if byte_depth == 8:
                    value = round((float(band[y][x]) / 255.0) * 65535.0)
                elif byte_depth == 16:
                    value = float(band[y][x])
                else:
                    raise Exception("Unexpected byte depth '%s'"%byte_depth)

                if y <= band_overlap and not np.isnan(self.data[start_y + y][x]) and not np.isnan(value):
                    f = float(y) / float(band_overlap)
                    d = self.data[start_y + y][x]
                    v = (f * value) + ((1.0 - f) * d)
                    self.data[start_y + y][x] = v
                else:
                    self.data[start_y + y][x] = value

    def save(self, path):
        data_matrix = self.data.astype(np.uint16)
        tiff = TIFFimage(data_matrix, description='')
        tiff.write_file(path, compression='none', verbose=False)

    def calc_minmax(self):
        mn = np.nanmin(self.data)
        mx = np.nanmax(self.data)
        return mn, mx

    def normalize_within_minmax(self, pixel_min, pixel_max):
        self.data -= pixel_min
        self.data /= (pixel_max - pixel_min)
        self.data[self.data < pixel_min] = pixel_min
        self.data *= 65535.0


    def graylevel(self):
        im = self.data
        im2 = 65535.0 * (im / 65535.0) ** 2.0  # squared
        self.data = im2

    def histeq(self, nbr_bins=65536):
        im = self.data
        imhist, bins = np.histogram(im.flatten(), nbr_bins, normed=True)
        cdf = imhist.cumsum()  # cumulative distribution function
        cdf = 65535 * cdf / cdf[-1]  # normalize

        # use linear interpolation of cdf to find new pixel values
        im2 = np.interp(im.flatten(), bins[:-1], cdf)
        im2 = im2.reshape(im.shape)

        self.data = im2

    def replace_nan(self):
        inds = np.where(np.isnan(self.data))
        self.data[inds] = np.nanmin(self.data)

    def apply_weight(self, weight=1.0):
        self.data *= weight


def linear_interpolate(v0, v1, f):
    v = (v0 * f) + (v1 * (1.0 - f))
    return v


def fill_dead_pixel(band, band_num):
    dead_pixels = DEAD_PIXEL_MAP[band_num]

    for dead_pixel in dead_pixels:
        cx = dead_pixel[0]
        cy = dead_pixel[1]
        radius = dead_pixel[2]

        for y in range(-radius, radius):
            for x in range(-radius, radius):
                x0 = band[cy + y][cx - radius]
                x1 = band[cy + y][cx + radius]
                y0 = band[cy - radius][cx + x]
                y1 = band[cy + radius][cx + x]

                fx = ((x + radius) / (radius*2.0))
                fy = ((y + radius) / (radius*2.0))

                ix = linear_interpolate(x0, x1, fx)
                iy = linear_interpolate(y0, y1, fy)

                v = np.mean([ix, iy])

                band[cy + y][cx + x] = v


def save_band(band, band_num, filter_num):
    img = np.copy(band)

    inds = np.where(np.isnan(img))
    img[inds] = np.nanmin(img)

    data_matrix = img #.astype(np.uint16)
    tiff = TIFFimage(data_matrix, description='')
    if not os.path.exists("bands"):
        os.mkdir("bands")
    tiff.write_file("bands/band_%d_%d.tif"%(filter_num, band_num), compression='none', verbose=False)


def process_band(source, filter_num, band_height=BAND_HEIGHT, band_overlap=10, save_bands=False, fill_dead_pixels=False):
    bands_per_image = (source.height / band_height / 3)
    img0 = DestImage(source.width, bands_per_image * band_height, band_height=band_height)

    byte_depth = source.get_byte_depth()

    for b in range(0, bands_per_image):
        b0 = (b * 3) + filter_num
        band = source.get_band(b0, band_height=band_height)
        if fill_dead_pixels is True:
            fill_dead_pixel(band, filter_num)
        if save_bands is True:
            save_band(band, b, filter_num)
        img0.set_band(band, b, band_overlap=band_overlap, byte_depth=byte_depth)

    img0.replace_nan()
    return img0, bands_per_image


def process(input_file,
            use_band_height=BAND_HEIGHT,
            band_overlap=10,
            save_bands=False,
            fill_dead_pixels=False,
            apply_hist_eq=False,
            apply_graylevel=False,
            match_intensity_levels=False,
            blue_weight=1.0,
            green_weight=1.0,
            red_weight=1.0):
    source = SourceRawImage(input_file)
    limits = []

    b0, num_bands = process_band(source,
                                 0,
                                 band_height=use_band_height,
                                 band_overlap=band_overlap,
                                 save_bands=save_bands,
                                 fill_dead_pixels=fill_dead_pixels)

    b1, num_bands = process_band(source,
                                 1,
                                 band_height=use_band_height,
                                 band_overlap=band_overlap,
                                 save_bands=save_bands,
                                 fill_dead_pixels=fill_dead_pixels)

    b2, num_bands = process_band(source,
                                 2,
                                 band_height=use_band_height,
                                 band_overlap=band_overlap,
                                 save_bands=save_bands,
                                 fill_dead_pixels=fill_dead_pixels)

    b0.apply_weight(weight=blue_weight)
    b1.apply_weight(weight=green_weight)
    b2.apply_weight(weight=red_weight)

    if apply_hist_eq:
        b0.histeq()
        b1.histeq()
        b2.histeq()

    if apply_graylevel:
        b0.graylevel()
        b1.graylevel()
        b2.graylevel()

    if match_intensity_levels:
        limits += b0.calc_minmax()
        limits += b1.calc_minmax()
        limits += b2.calc_minmax()

        b0.normalize_within_minmax(np.min(limits), np.max(limits))
        b1.normalize_within_minmax(np.min(limits), np.max(limits))
        b2.normalize_within_minmax(np.min(limits), np.max(limits))

    red_file_name = "%s-red.tif"%input_file[:input_file.rindex(".")]
    green_file_name = "%s-green.tif" % input_file[:input_file.rindex(".")]
    blue_file_name = "%s-blue.tif" % input_file[:input_file.rindex(".")]

    b0.save(blue_file_name)
    b1.save(green_file_name)
    b2.save(red_file_name)

    return red_file_name, green_file_name, blue_file_name