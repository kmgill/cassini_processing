import re
import datetime
from isis3._core import isis_command
from isis3.scripting import getkey as get_field_value


def get_product_id(file_name):
    if file_name[-3:].upper() == "LBL":
        return get_field_value(file_name, "PRODUCT_ID")[2:-4]
    elif file_name[-3:].upper() == "CUB":
        return get_field_value(file_name, keyword="ProductId", grpname="Archive")[2:-4]
    else:
        raise Exception("Unrecognized/Unsupported file")

def get_target(file_name):
    if file_name[-3:].upper() == "LBL":
        return get_field_value(file_name, "TARGET_NAME").replace(" ", "_")
    elif file_name[-3:].upper() == "CUB":
        return get_field_value(file_name, keyword="TargetName", grpname="Instrument")
    else:
        raise Exception("Unrecognized/Unsupported file")

def get_filters(file_name):
    if file_name[-3:].upper() == "LBL":
        filters = get_field_value(file_name, "FILTER_NAME")
        pattern = re.compile(r"^(?P<f1>[A-Z0-9]*)\, (?P<f2>[A-Z0-9]*)")
    elif file_name[-3:].upper() == "CUB":
        filters = get_field_value(file_name, keyword="FilterName", grpname="BandBin")
        pattern = re.compile(r"^(?P<f1>[A-Z0-9]*)/(?P<f2>[A-Z0-9]*)")
    else:
        raise Exception("Unrecognized/Unsupported file")
    match = pattern.match(filters)
    if match is not None:
        filter1 = match.group("f1")
        filter2 = match.group("f2")
    else:
        filter1 = filter2 = "UNK"
    return filter1, filter2

def get_image_time(file_name):
    if file_name[-3:].upper() == "LBL":
        image_time = get_field_value(file_name, "IMAGE_TIME")
    elif file_name[-3:].upper() == "CUB":
        image_time = get_field_value(file_name, "ImageTime", grpname="Instrument")
    else:
        raise Exception("Unrecognized/Unsupported file")
    return datetime.datetime.strptime(image_time, '%Y-%jT%H:%M:%S.%f')


def get_num_lines(file_name):
    if file_name[-3:].upper() == "LBL":
        return int(get_field_value(file_name, "LINES", objname="IMAGE"))
    elif file_name[-3:].upper() == "CUB":
        return int(get_field_value(file_name, "Lines", objname="IsisCube", grpname="Dimensions"))
    else:
        raise Exception("Unrecognized/Unsupported file")

def get_num_line_samples(file_name):
    if file_name[-3:].upper() == "LBL":
        return int(get_field_value(file_name, "LINE_SAMPLES", objname="IMAGE"))
    elif file_name[-3:].upper() == "CUB":
        return int(get_field_value(file_name, "Samples", objname="IsisCube", grpname="Dimensions"))
    else:
        raise Exception("Unrecognized/Unsupported file")

def get_sample_bits(file_name):
    if file_name[-3:].upper() == "LBL":
        return int(get_field_value(file_name, "SAMPLE_BITS", objname="IMAGE"))
    elif file_name[-3:].upper() == "CUB":
        return 32
    else:
        raise Exception("Unrecognized/Unsupported file")

def get_instrument_id(file_name):
    if file_name[-3:].upper() == "LBL":
        return get_field_value(file_name, "INSTRUMENT_ID")
    elif file_name[-3:].upper() == "CUB":
        return get_field_value(file_name, "InstrumentId", grpname="Instrument")
    else:
        raise Exception("Unrecognized/Unsupported file")


