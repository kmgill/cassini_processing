import re
import datetime
from isis3._core import isis_command
from isis3.scripting import getkey as get_field_value

__UNSUPPORTED_UNRECOGNIZED__ = "Unrecognized/Unsupported file"

def has_keyword(file_name, keyword, objname=None, grpname=None):
    try:
        v = get_field_value(file_name, keyword, objname, grpname)
        return v is not None
    except:
        return False


def time_string_matches_format(s, format):
    try:
        datetime.datetime.strptime(s, format)
        return True
    except:
        return False


def get_product_id(file_name):
    if file_name[-3:].upper() in ("LBL",):
        if has_keyword(file_name, "PRODUCT_ID"):
            return get_field_value(file_name, "PRODUCT_ID").replace("+", "_")
        elif has_keyword(file_name, "IMAGE_ID"):
            return get_field_value(file_name, "IMAGE_ID").replace("+", "_")
    elif file_name[-3:].upper() in ("CUB", "IMQ"):
        return get_field_value(file_name, keyword="ProductId", grpname="Archive").replace("+", "_")
    else:
        raise Exception(__UNSUPPORTED_UNRECOGNIZED__)



def get_target(file_name):
    if file_name[-3:].upper() in ("LBL", ):
        return get_field_value(file_name, "TARGET_NAME").replace(" ", "_")
    elif file_name[-3:].upper() in ("CUB", "IMQ"):
        return get_field_value(file_name, keyword="TargetName", grpname="Instrument").upper()
    else:
        raise Exception(__UNSUPPORTED_UNRECOGNIZED__)


def get_filters(file_name):
    if file_name[-3:].upper() in ("LBL",):
        filters = get_field_value(file_name, "FILTER_NAME")
        pattern = re.compile(r"^(?P<f1>[A-Z0-9]*)\, (?P<f2>[A-Z0-9]*)")
    elif file_name[-3:].upper() in ("CUB", "IMQ"):
        filters = get_field_value(file_name, keyword="FilterName", grpname="BandBin")
        pattern = re.compile(r"^(?P<f1>[A-Z0-9]*)/(?P<f2>[A-Z0-9]*)")
    else:
        raise Exception(__UNSUPPORTED_UNRECOGNIZED__)
    match = pattern.match(filters)
    if match is not None:
        filter1 = match.group("f1")
        filter2 = match.group("f2")
    else:
        filter1 = filter2 = filters
    return filter1, filter2


def get_image_time(file_name):
    if file_name[-3:].upper() in ("LBL", ):
        if has_keyword(file_name, "IMAGE_TIME"):
            image_time = get_field_value(file_name, "IMAGE_TIME")
        elif has_keyword(file_name, "START_TIME"):
            image_time = get_field_value(file_name, "START_TIME")
    elif file_name[-3:].upper() in ("CUB", "IMQ"):
        if has_keyword(file_name, "ImageTime", grpname="Instrument"):
            image_time = get_field_value(file_name, "ImageTime", grpname="Instrument")
        elif has_keyword(file_name, "StartTime", grpname="Instrument"):
            image_time = get_field_value(file_name, "StartTime", grpname="Instrument")
    else:
        raise Exception(__UNSUPPORTED_UNRECOGNIZED__)

    if time_string_matches_format(image_time, '%Y-%jT%H:%M:%S.%f'):
        return datetime.datetime.strptime(image_time, '%Y-%jT%H:%M:%S.%f')
    elif time_string_matches_format(image_time, '%Y-%m-%dT%H:%M:%S.%f'):
        return datetime.datetime.strptime(image_time, '%Y-%m-%dT%H:%M:%S.%f')
    elif time_string_matches_format(image_time, '%Y-%m-%dT%H:%M:%SZ'):
        return datetime.datetime.strptime(image_time, '%Y-%m-%dT%H:%M:%SZ')


def get_num_lines(file_name):
    if file_name[-3:].upper() in ("LBL",):
        return int(get_field_value(file_name, "LINES", objname="IMAGE"))
    elif file_name[-3:].upper() in ("CUB", "IMQ"):
        return int(get_field_value(file_name, "Lines", objname="IsisCube", grpname="Dimensions"))
    else:
        raise Exception(__UNSUPPORTED_UNRECOGNIZED__)


def get_num_line_samples(file_name):
    if file_name[-3:].upper() in ("LBL",):
        return int(get_field_value(file_name, "LINE_SAMPLES", objname="IMAGE"))
    elif file_name[-3:].upper() in ("CUB", "IMQ"):
        return int(get_field_value(file_name, "Samples", objname="IsisCube", grpname="Dimensions"))
    else:
        raise Exception(__UNSUPPORTED_UNRECOGNIZED__)


def get_sample_bits(file_name):
    if file_name[-3:].upper() in ("LBL",):
        return int(get_field_value(file_name, "SAMPLE_BITS", objname="IMAGE"))
    elif file_name[-3:].upper() in ("CUB", "IMQ"):
        return 32  # Note: Don't assume this, Kevin. Use the byte type field
    else:
        raise Exception(__UNSUPPORTED_UNRECOGNIZED__)


def get_instrument_id(file_name):
    if file_name[-3:].upper() in ("LBL",):
        if has_keyword(file_name, "INSTRUMENT_ID"):
            return get_field_value(file_name, "INSTRUMENT_ID")
        elif has_keyword(file_name, "INSTRUMENT_NAME"):
            return get_field_value(file_name, "INSTRUMENT_NAME")
    elif file_name[-3:].upper() in ("CUB", "IMQ"):
        return get_field_value(file_name, "InstrumentId", grpname="Instrument")
    else:
        raise Exception(__UNSUPPORTED_UNRECOGNIZED__)


