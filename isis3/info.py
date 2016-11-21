import re
import datetime
from isis3._core import isis_command
from isis3.scripting import getkey as get_field_value
from isis3.metadata import load_pvl

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
    p = load_pvl(file_name)
    pid = None

    if file_name[-3:].upper() in ("LBL", "IMQ"):
        if "PRODUCT_ID" in p:
            pid = p["PRODUCT_ID"]
        elif "IMAGE_ID" in p:
            pid = p["IMAGE_ID"]
    elif file_name[-3:].upper() in ("CUB", ):
        pid = p["IsisCube"]["Archive"]["ProductId"]
    else:
        raise Exception(__UNSUPPORTED_UNRECOGNIZED__)

    if type(pid) == str:
        pid = pid.replace("+", "_")

    return pid



def get_target(file_name):
    p = load_pvl(file_name
                 )
    if file_name[-3:].upper() in ("LBL", "IMQ"):
        return p["TARGET_NAME"].replace(" ", "_")
    elif file_name[-3:].upper() in ("CUB", ):
        return p["IsisCube"]["Instrument"]["TargetName"].upper()
    else:
        raise Exception(__UNSUPPORTED_UNRECOGNIZED__)


def get_filters(file_name):
    p = load_pvl(file_name)

    if file_name[-3:].upper() in ("LBL", "IMQ"):
        filters = p["FILTER_NAME"]
        pattern = re.compile(r"^(?P<f1>[A-Z0-9]*)\, (?P<f2>[A-Z0-9]*)")
    elif file_name[-3:].upper() in ("CUB", ):
        filters = p["IsisCube"]["BandBin"]["FilterName"]
        pattern = re.compile(r"^(?P<f1>[A-Z0-9]*)/(?P<f2>[A-Z0-9]*)")
    else:
        raise Exception(__UNSUPPORTED_UNRECOGNIZED__)

    if type(filters) == list:
        return filters

    match = pattern.match(filters)
    if match is not None:
        filter1 = match.group("f1")
        filter2 = match.group("f2")
    else:
        filter1 = filter2 = filters
    return filter1, filter2


def get_image_time(file_name):
    p = load_pvl(file_name)

    if file_name[-3:].upper() in ("LBL", "IMQ"):
        if "IMAGE_TIME" in p:
            image_time = p["IMAGE_TIME"]
        elif "START_TIME" in p:
            image_time = p["START_TIME"]

    elif file_name[-3:].upper() in ("CUB",):

        try:
            image_time = p["IsisCube"]["Instrument"]["ImageTime"]
        except:
            image_time = p["IsisCube"]["Instrument"]["StartTime"]

    else:
        raise Exception(__UNSUPPORTED_UNRECOGNIZED__)

    return image_time


def get_num_lines(file_name):
    p = load_pvl(file_name)
    if file_name[-3:].upper() in ("LBL", "IMQ"):
        return p["IMAGE"]["LINES"]
    elif file_name[-3:].upper() in ("CUB", ):
        return p["IsisCube"]["Core"]["Dimensions"]["Lines"]
    else:
        raise Exception(__UNSUPPORTED_UNRECOGNIZED__)


def get_num_line_samples(file_name):
    p = load_pvl(file_name)

    if file_name[-3:].upper() in ("LBL", "IMQ"):
        return p["IMAGE"]["LINE_SAMPLES"]
    elif file_name[-3:].upper() in ("CUB",):
        return p["IsisCube"]["Core"]["Dimensions"]["Samples"]
    else:
        raise Exception(__UNSUPPORTED_UNRECOGNIZED__)


def get_sample_bits(file_name):
    p = load_pvl(file_name)

    if file_name[-3:].upper() in ("LBL", "IMQ"):
        return p["IMAGE"]["SAMPLE_BITS"]
    elif file_name[-3:].upper() in ("CUB", ):
        return 32  # Note: Don't assume this, Kevin. Use the byte type field
    else:
        raise Exception(__UNSUPPORTED_UNRECOGNIZED__)


def get_instrument_id(file_name):
    p = load_pvl(file_name)

    if file_name[-3:].upper() in ("LBL", "IMQ"):
        if "INSTRUMENT_ID" in p:
            return p["INSTRUMENT_ID"]
        elif "INSTRUMENT_NAME" in p:
            return p["INSTRUMENT_NAME"]
    elif file_name[-3:].upper() in ("CUB", ):
        return p["IsisCube"]["Instrument"]["InstrumentId"]
    else:
        raise Exception(__UNSUPPORTED_UNRECOGNIZED__)


