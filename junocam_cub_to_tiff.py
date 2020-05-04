#!/usr/bin/env python

import sys
import argparse
from sciimg.isis3 import _core
from sciimg.isis3 import importexport
from sciimg.pipelines.junocam.decompanding import SQROOT
import numpy as np
from sciimg.processes.match import get_files_min_max_values




def calc_min_max(data_input, is_verbose=False):
    min_value, max_value = get_files_min_max_values(["%s+1"%data_input, "%s+3"%data_input, "%s+5"%data_input], is_verbose=is_verbose)
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

    # These values will be overridden if calcminmax is true
    max_value = (float(SQROOT[-1]) * np.array([use_red_weight, use_green_weight, use_blue_weight]).max())
    if use_max is not None:
        max_value = use_max


    for data_input in data_inputs:
        output_tiff = "%s.tif"%data_input[:-4]
        print("Converting %s to %s..."%(data_input, output_tiff))

        if calcminmax is True:
            min_value, max_value = calc_min_max(data_input, is_verbose)

        if true_color is True:
            s = importexport.isis2std_rgb(from_cube_red="%s+1"%data_input,
                                          from_cube_green="%s+3"%data_input,
                                          from_cube_blue="%s+5"%data_input,
                                          to_tiff=output_tiff,
                                          match_stretch=True,
                                          minimum=0,
                                          maximum=max_value)
        else:
            s = importexport.isis2std_rgb(from_cube_red="%s+1"%data_input,
                                          from_cube_green="%s+3"%data_input,
                                          from_cube_blue="%s+5"%data_input,
                                          to_tiff=output_tiff)



