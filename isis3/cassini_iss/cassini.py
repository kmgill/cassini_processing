
from isis3.info import get_field_value


def is_supported_file(file_name):
    if not file_name[-3:].upper() == "LBL":
        return False

    value = get_field_value(file_name,  "INSTRUMENT_HOST_NAME")
    return value == "CASSINI ORBITER"