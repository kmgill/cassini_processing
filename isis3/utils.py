#!/usr/bin/python
import os
import sys
import re
import subprocess
import datetime
import glob



def get_field_value(lbl_file_name, keyword, objname=None):
    cmd = ["getkey", "from=%s"%lbl_file_name, "keyword=%s"%keyword]
    if objname is not None:
        cmd += ["objname=%s"%objname]
    s = subprocess.check_output(cmd)
    return s.strip()

def get_product_id(lbl_file_name):
    return get_field_value(lbl_file_name, "PRODUCT_ID")[2:-4]

def get_target(lbl_file_name):
    return get_field_value(lbl_file_name, "TARGET_NAME").replace(" ", "_")

def get_filters(lbl_file_name):
    filters = get_field_value(lbl_file_name, "FILTER_NAME")
    pattern = re.compile(r"^(?P<f1>[A-Z0-9]*)\, (?P<f2>[A-Z0-9]*)")
    match = pattern.match(filters)
    if match is not None:
        filter1 = match.group("f1")
        filter2 = match.group("f2")
    else:
        filter1 = filter2 = "UNK"
    return filter1, filter2

def get_image_time(lbl_file_name):
    image_time = datetime.datetime.strptime(get_field_value(lbl_file_name, "IMAGE_TIME"), '%Y-%jT%H:%M:%S.%f')
    return image_time

def get_num_lines(lbl_file_name):
    return int(get_field_value(lbl_file_name, "LINES", objname="IMAGE"))

def get_num_line_samples(lbl_file_name):
    return int(get_field_value(lbl_file_name, "LINE_SAMPLES", objname="IMAGE"))

def get_sample_bits(lbl_file_name):
    return int(get_field_value(lbl_file_name, "SAMPLE_BITS", objname="IMAGE"))

def output_filename_from_label(lbl_file_name):
    product_id = get_product_id(lbl_file_name)
    target = get_target(lbl_file_name)
    filter1, filter2 = get_filters(lbl_file_name)
    image_time = get_image_time(lbl_file_name)
    out_file = "{product_id}_{target}_{filter1}_{filter2}_{image_date}".format(product_id=product_id,
                                                                                        target=target,
                                                                                        filter1=filter1,
                                                                                        filter2=filter2,
                                                                                        image_date=image_time.strftime('%Y-%m-%d_%H.%M.%S'))
    return out_file





def import_to_cube(lbl_file_name, to_cube):
    s = subprocess.check_output(["ciss2isis",
                                "from=%s"%lbl_file_name,
                                "to=%s"%to_cube])
    return s

def fill_gaps(from_cube, to_cube):
    s = subprocess.check_output(["fillgap",
                    "from=%s"%from_cube,
                    "to=%s"%to_cube,
                    "interp=cubic",
                    "direction=sample"])
    return s

def init_spice(from_cube, is_ringplane=False):
    s = subprocess.check_output(["spiceinit",
                    "from=%s"%from_cube,
                    "shape=%s"%("ringplane" if is_ringplane else "system")]) #ringplane, "ellipsoid"
    return s

def calibrate_cube(from_cube, to_cube):
    s = subprocess.check_output(["cisscal",
                    "from=%s"%from_cube,
                    "to=%s"%to_cube,
                    "units=intensity"])
    return s

def noise_filter(from_cube, to_cube):
    s = subprocess.check_output(["noisefilter",
                    "from=%s"%from_cube,
                    "to=%s"%to_cube,
                    "toldef=stddev",
                    "tolmin=2.5",
                    "tolmax=2.5",
                    "replace=null",
                    "samples=5",
                    "lines=5"])
    return s

def fill_nulls(from_cube, to_cube):
    s = subprocess.check_output(["lowpass",
                    "from=%s"%from_cube,
                    "to=%s"%to_cube,
                    "samples=3",
                    "lines=3",
                    "filter=outside",
                    "null=yes",
                    "hrs=no",
                    "his=no",
                    "lrs=no",
                    "replacement=center"
                    ])
    return s

def trim_edges(from_cube, to_cube):
    s = subprocess.check_output(["trim",
                    "from=%s"%from_cube,
                    "to=%s"%to_cube,
                    "top=2",
                    "bottom=2",
                    "left=2",
                    "right=2"
                    ])
    return s

def export_tiff_grayscale(from_cube, to_tiff, minimum=None, maximum=None):
    cmd = ["isis2std",
                    "from=%s"%from_cube,
                    "to=%s"%to_tiff,
                    "format=tiff",
                    "bittype=u16bit"
                    ]

    if minimum is not None and maximum is not None:
        cmd += ["stretch=manual", "minimum=%f"%minimum, "maximum=%f"%maximum]
    else:
        cmd.append("maxpercent=99.999")

    s = subprocess.check_output(cmd)
    return s

def get_data_min_max(from_cube):
    out = subprocess.check_output(["stats", "from=%s"%from_cube])
    parts = out.split("\n")
    _min = float(parts[9].split("=")[1])
    _max = float(parts[10].split("=")[1])
    return _min, _max
