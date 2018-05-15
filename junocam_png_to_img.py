#!/usr/bin/env python
"""
There's probably a much better way to do this. But it works so I'm using it for now...

"""


import argparse

from sciimg.processes.junocam_conversions import create_label
from sciimg.processes.junocam_conversions import create_pds


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--metadata", help="Input JunoCam Metadata JSON File", required=True, type=str)
    parser.add_argument("-p", "--png", help="Input JunoCam PNG File", required=True, type=str)
    args = parser.parse_args()

    metadata = args.metadata
    png_file = args.png

    output_base = png_file[:-4]

    create_label(output_base, metadata)
    create_pds(output_base, png_file)




