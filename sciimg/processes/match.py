import sys
import numpy as np
import os
from sciimg.isis3 import info
import sciimg.isis3.importexport as importexport
import sciimg.isis3.mathandstats as mathandstats
from sciimg.isis3 import utils


def get_file_min_max_values(cub_file, is_verbose=False):
    min_value, max_value = mathandstats.get_data_min_max(cub_file)
    if is_verbose is True:
        print("File %s min/max: %d, %d"%(cub_file, min_value, max_value))
    return min_value, max_value


def get_files_min_max_values(file_names, is_verbose=False):
    data_limits = []

    for file_name in file_names:
        min_value, max_value = get_file_min_max_values(file_name, is_verbose=is_verbose)
        data_limits += [min_value, max_value]

    files_min = float(np.array(data_limits).min())
    files_max = float(np.array(data_limits).max())

    return files_min, files_max



def match(files, band=1):
    values = []
    for f in files:
        _min, _max = mathandstats.get_data_min_max(f, band)
        values.append(_min)
        values.append(_max)
        print(_min, _max)

    minimum = np.min(values)
    maximum = np.max(values)

    print("Minimun:", minimum, "Maximum:", maximum)
    # maximum -= ((maximum - minimum) * 0.45)
    # minimum += ((maximum - minimum) * 0.35)

    for f in files:
        totiff = f[:-4] + ".tif"
        print(totiff)
        importexport.isis2std_grayscale(f, totiff, minimum=minimum, maximum=maximum, band=band)



def compose_rgb(cub_file_red, cub_file_green, cub_file_blue, output_tiff_file, match_stretch=False, is_verbose=False):
    files = [cub_file_red, cub_file_green, cub_file_blue]

    min, max = get_files_min_max_values(files, is_verbose=is_verbose)

    if is_verbose:
        print("Max:", max)
        print("Min:", min)

    s = importexport.isis2std_rgb(cub_file_red,
                                  cub_file_green,
                                  cub_file_blue,
                                  output_tiff_file,
                                  minimum=min,
                                  maximum=max,
                                  match_stretch=match_stretch)

    if is_verbose:
        print(s)
