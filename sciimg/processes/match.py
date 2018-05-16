import sys
import numpy as np
import os
from sciimg.isis3 import info
import sciimg.isis3.importexport as importexport
import sciimg.isis3.mathandstats as mathandstats
from sciimg.isis3 import utils


def get_file_min_max_values(cub_file, is_verbose=False):
    min_value, max_value = mathandstats.get_data_min_max(cub_file)
    return min_value, max_value


def get_files_min_max_values(file_names, is_verbose=False):
    data_limits = []

    for file_name in file_names:
        min_value, max_value = get_file_min_max_values(file_name, is_verbose=is_verbose)
        data_limits += [min_value, max_value]

    files_min = float(np.array(data_limits).min())
    files_max = float(np.array(data_limits).max())

    return files_min, files_max



def match(files, targets, filters, require_width, require_height):
    matching_files = []

    for f in files:
        if f[-3:].upper() != "CUB":
            print "File %s is not supported, skipping" % f
            continue
        target = None
        try:
            target = info.get_target(f)
        except:
            pass

        filter1, filter2 = None, None
        try:
            filter1, filter2 = info.get_filters(f)
        except:
            pass

        width = info.get_num_line_samples(f)
        height = info.get_num_lines(f)

        if len(targets) > 0 and target.upper() not in targets:
            continue
        elif len(filters) > 0 and (filter1.upper() not in filters and filter2.upper() not in filters):
            continue
        elif len(require_width) > 0 and str(width) not in require_width:
            continue
        elif len(require_height) > 0 and str(height) not in require_height:
            continue
        else:
            matching_files.append(f)

    values = []
    for f in matching_files:
        _min, _max = mathandstats.get_data_min_max(f)
        values.append(_min)
        values.append(_max)
        print _min, _max

    minimum = np.min(values)
    maximum = np.max(values)

    print "Minimun:", minimum, "Maximum:", maximum
    # maximum -= ((maximum - minimum) * 0.45)
    # minimum += ((maximum - minimum) * 0.35)

    for f in matching_files:
        totiff = f[:-4] + ".tif"
        print totiff
        importexport.isis2std_grayscale(f, totiff, minimum=minimum, maximum=maximum)



def compose_rgb(cub_file_red, cub_file_green, cub_file_blue, output_tiff_file, match_stretch=False, is_verbose=False):
    files = [cub_file_red, cub_file_green, cub_file_blue]

    min, max = get_files_min_max_values(files, is_verbose=is_verbose)

    if is_verbose:
        print "Max:", max
        print "Min:", min

    s = importexport.isis2std_rgb(cub_file_red,
                                  cub_file_green,
                                  cub_file_blue,
                                  output_tiff_file,
                                  minimum=min,
                                  maximum=max,
                                  match_stretch=match_stretch)

    if is_verbose:
        print s