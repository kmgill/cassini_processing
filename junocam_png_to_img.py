#!/usr/bin/env python
"""
There's probably a much better way to do this. But it works so I'm using it for now...

"""


import argparse
from sciimg.processes.junocam_conversions import png_to_img

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--metadata", help="Input JunoCam Metadata JSON File", required=True, type=str)
    parser.add_argument("-p", "--png", help="Input JunoCam PNG File", required=True, type=str)
    parser.add_argument("-f", "--fill", help="Fill dead pixels", action="store_true")
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    parser.add_argument("-d", "--decompand", help="Decompand pixel values", action="store_true")
    parser.add_argument("-F", "--flat", help="Apply flat fields (Don't use)", action="store_true")

    parser.add_argument("-r", "--redweight", help="Apply a weight for the red band", type=float, default=0.902) # 0.510
    parser.add_argument("-g", "--greenweight", help="Apply a weight for the green band", type=float, default=1.0) # 0.630
    parser.add_argument("-b", "--blueweight", help="Apply a weight for the blue band", type=float, default=1.8879) # 1.0

    args = parser.parse_args()

    metadata = args.metadata
    img_file = args.png
    fill_dead_pixels = args.fill
    verbose = args.verbose
    do_decompand = args.decompand
    do_flat_fields = args.flat

    use_red_weight = args.redweight
    use_green_weight = args.greenweight
    use_blue_weight = args.blueweight

    png_to_img(img_file, metadata,
               fill_dead_pixels=fill_dead_pixels,
               do_decompand=do_decompand,
               do_flat_fields=do_flat_fields,
               use_red_weight=use_red_weight,
               use_green_weight=use_green_weight,
               use_blue_weight=use_blue_weight,
               verbose=verbose)


