#!/usr/bin/env python
"""
There's probably a much better way to do this. But it works so I'm using it for now...

"""



import os
import sys
import argparse
import traceback
from isis3 import importexport

from isis3.junocam.utils import json_to_lbl



def create_label(output_base, metadata_json_path):
    output_lbl_path = "%s.lbl"%output_base
    lbl_data = json_to_lbl(metadata_json_path)

    with open(output_lbl_path, "w") as f:
        f.write(lbl_data)


def create_pds(output_base, png_file):
    output_cub = "%s.cub"%output_base
    output_img = "%s.img"%output_base

    importexport.std2isis(png_file, output_cub, mode=importexport.ColorMode.GRAYSCALE)
    importexport.isis2pds(output_cub, output_img, labtype="fixed", bittype="u16bit")

    os.unlink(output_cub)


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




