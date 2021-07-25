#!/usr/bin/env python

import sys
import argparse
from sciimg.isis3 import _core
from sciimg.isis3 import importexport
from sciimg.pipelines.junocam.decompanding import SQROOT
import numpy as np
from sciimg.processes.match import get_files_min_max_values



def calc_min_max_multi_cubs(data_inputs, bands=[1, 3, 5], is_verbose=False):
    check_bands = []
    for data_input in data_inputs:
        for band in bands:
            check_bands.append("%s+%s"%(data_input, band))
    min_value, max_value = get_files_min_max_values(check_bands, is_verbose=is_verbose)
    return min_value, max_value

def calc_min_max(data_input, bands=[1, 3, 5], is_verbose=False):
    min_value, max_value = calc_min_max_multi_cubs((data_input,), bands, is_verbose)
    return min_value, max_value


if __name__ == "__main__":

    try:
        _core.is_isis3_initialized()
    except:
        print("ISIS3 has not been initialized. Please do so. Now.")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    parser.add_argument("-d", "--data", help="Source PDS datasets", required=True, type=str, nargs='+')
    parser.add_argument("-t", "--truecolor", help="Export for true color", action="store_true")
    parser.add_argument("-r", "--redweight", help="Apply a weight for the red band", type=float, default=0.902)  # 0.510
    parser.add_argument("-g", "--greenweight", help="Apply a weight for the green band", type=float,
                        default=1.0)  # 0.630
    parser.add_argument("-b", "--blueweight", help="Apply a weight for the blue band", type=float,
                        default=1.8879)  # 1.0
    parser.add_argument("-m", "--minvalue", help="Use specific output minimum", type=float, default=0.0)  # 1.0
    parser.add_argument("-M", "--maxvalue", help="Use specific output maximum", type=float, default=None)  # 1.0
    parser.add_argument("-c", "--calcminmax", help="Calculate dataset min/max", action="store_true")
    parser.add_argument("-p", "--perband", help="Calculate dataset band min/max separately", action="store_true")
    parser.add_argument("-f", "--format", help="Format (tif, jpeg, png)", type=str, default="tif", choices=("jpeg", "tif", "png"))  # 1.0

    args = parser.parse_args()

    is_verbose = args.verbose
    data_inputs = args.data
    true_color = args.truecolor
    use_red_weight = args.redweight
    use_green_weight = args.greenweight
    use_blue_weight = args.blueweight
    use_max = args.maxvalue
    use_min = args.minvalue
    calcminmax = args.calcminmax
    perband = args.perband
    format = args.format

    # These values will be overridden if calcminmax is true
    max_value = (float(SQROOT[-1]) * np.array([use_red_weight, use_green_weight, use_blue_weight]).max())
    if use_max is not None:
        max_value = use_max

    if calcminmax is True and perband is False:
        min_value, max_value = calc_min_max_multi_cubs(data_inputs, bands=[1, 3, 5], is_verbose=is_verbose)
        red_min = min_value
        red_max = max_value
        green_min = min_value
        green_max = max_value
        blue_min = min_value
        blue_max = max_value
    elif calcminmax is True and perband is True:
        min_value, max_value = calc_min_max_multi_cubs(data_inputs, bands=(1,), is_verbose=is_verbose)
        red_min = min_value
        red_max = max_value
        min_value, max_value = calc_min_max_multi_cubs(data_inputs, bands=(3,), is_verbose=is_verbose)
        green_min = min_value
        green_max = max_value
        min_value, max_value = calc_min_max_multi_cubs(data_inputs, bands=(5,), is_verbose=is_verbose)
        blue_min = min_value
        blue_max = max_value


    extension = "tif"
    bittype = "u16bit"
    if format == "png":
        extension = "png"
    elif format == "jpeg":
        extension = "jpg"
        bittype = "8bit"

    for data_input in data_inputs:
        output_tiff = "%s.%s"%(data_input[:-4], extension)
        print("Converting %s to %s..."%(data_input, output_tiff))

        if true_color is True:
            s = importexport.isis2std_rgb(from_cube_red="%s+1"%data_input,
                                          from_cube_green="%s+3"%data_input,
                                          from_cube_blue="%s+5"%data_input,
                                          to_tiff=output_tiff,
                                          match_stretch=True,
                                          minimum=0,
                                          maximum=max_value,
                                          format=format,
                                          bittype=bittype)
        elif calcminmax is True and perband is False:
            s = importexport.isis2std_rgb(from_cube_red="%s+1" % data_input,
                                          from_cube_green="%s+3" % data_input,
                                          from_cube_blue="%s+5" % data_input,
                                          to_tiff=output_tiff,
                                          match_stretch=True,
                                          minimum=min_value,
                                          maximum=max_value,
                                          format=format,
                                          bittype=bittype)
        elif calcminmax is True and perband is True:
            s = importexport.isis2std_rgb(from_cube_red="%s+1" % data_input,
                                          from_cube_green="%s+3" % data_input,
                                          from_cube_blue="%s+5" % data_input,
                                          to_tiff=output_tiff,
                                          minmaxperband=True,
                                          red_min=red_min,
                                          red_max=red_max,
                                          green_min=green_min,
                                          green_max=green_max,
                                          blue_min=blue_min,
                                          blue_max=blue_max,
                                          format=format,
                                          bittype=bittype)

        else:
            s = importexport.isis2std_rgb(from_cube_red="%s+1"%data_input,
                                          from_cube_green="%s+3"%data_input,
                                          from_cube_blue="%s+5"%data_input,
                                          to_tiff=output_tiff,
                                          format=format,
                                          bittype=bittype)



