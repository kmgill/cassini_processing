

import os
from sciimg.isis3 import importexport
from sciimg.isis3.junocam.utils import json_to_lbl


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