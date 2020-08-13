import os
import numpy as np
from PIL import Image
from sciimg.pipelines.junocam.decompanding import decompand

"""
Note: This stuff isn't even close to correct and reflects some messing around. Don't use it. 

"""

DARK_IMG_PATH_RED = os.path.join(os.path.dirname(__file__), 'juno-dark-red.tif')
DARK_IMG_PATH_GREEN = os.path.join(os.path.dirname(__file__), 'juno-dark-green.tif')
DARK_IMG_PATH_BLUE = os.path.join(os.path.dirname(__file__), 'juno-dark-blue.tif')

FLAT_IMG_PATH_RED = os.path.join(os.path.dirname(__file__), 'junocam_rgb_flatfield_v3_2.png')
FLAT_IMG_PATH_GREEN = os.path.join(os.path.dirname(__file__), 'junocam_rgb_flatfield_v3_1.png')
FLAT_IMG_PATH_BLUE = os.path.join(os.path.dirname(__file__), 'junocam_rgb_flatfield_v3_0.png')


BAND_HEIGHT = 128


def open_image(img_path):
    img = Image.open(img_path)
    data = np.copy(np.asarray(img, dtype=np.float32))
    img.close()
    return data

def open_dark_field_image(band_id, apply_filling=False):
    if band_id == 0:
        path = DARK_IMG_PATH_BLUE
    elif band_id == 1:
        path = DARK_IMG_PATH_GREEN
    elif band_id == 2:
        path = DARK_IMG_PATH_RED
    else:
        raise Exception("Invalid band identifier specified. Cannot select dark image")

    data = open_image(path)
    #f apply_filling:
    #    fill_dead_pixel(data, 0, band_id,  band_height=BAND_HEIGHT)

    return data

def open_flat_field_image(band_id, apply_filling=False):
    if band_id == 0:
        path = FLAT_IMG_PATH_BLUE
    elif band_id == 1:
        path = FLAT_IMG_PATH_GREEN
    elif band_id == 2:
        path = FLAT_IMG_PATH_RED
    else:
        raise Exception("Invalid band identifier specified. Cannot select flatfield image")

    data = open_image(path)
    #f apply_filling:
    #    fill_dead_pixel(data, 0, band_id,  band_height=BAND_HEIGHT)

    return data


def is_invalid(value):
    return np.isnan(value) or np.isinf(value)


def apply_flat_for_band(data, band_num, band_id, apply_filling=False, band_height=BAND_HEIGHT):
    top = band_num * band_height
    bottom = top + band_height

    F = open_flat_field_image(band_id, apply_filling)
    F = F / 65535.0

    #F = decompand(F, normalize=False, verbose=False)

    #D = open_dark_field_image(band_id, apply_filling)

    #print(F.min(), F.max())

    R = data[top:bottom]

    #m = F.mean()
    m = F#(F - D).mean()
    #D = np.zeros(R.shape)
    #G = m / (F - D)
    #C = (R - D) * G
    #print(G.min(), G.max(), F.min(), F.max(), D.min(), D.max(), R.min(), R.max())
    C = R / F
    print(R.min(), R.max(), F.min(), F.max(), C.min(), C.max())
    data[top:bottom] = C


def apply_flat(img_data, apply_filling=False, verbose=False):
    img_height = img_data.shape[0]

    if verbose:
        print("Image height:", img_height)

    bands_per_image = int((img_height / BAND_HEIGHT / 3))

    if verbose:
        print("Detected", bands_per_image, "RGB bands")

    for band in range(0, bands_per_image):
        if verbose:
            print("Applying flat field for RGB band triplet #", band)

        apply_flat_for_band(img_data, band * 3 + 0, 0, apply_filling=apply_filling, band_height=BAND_HEIGHT)
        apply_flat_for_band(img_data, band * 3 + 1, 1, apply_filling=apply_filling, band_height=BAND_HEIGHT)
        apply_flat_for_band(img_data, band * 3 + 2, 2, apply_filling=apply_filling, band_height=BAND_HEIGHT)

    # Correcting and normalizing
    #img_data[np.isnan(img_data)] = 0.0
    #img_data[np.isinf(img_data)] = 0.0
    #img_data /= img_data.max()
    #img_data *= 255.0