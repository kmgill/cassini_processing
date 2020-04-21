
import json
import types
import re
from six import string_types


def is_number(value):
    if re.match("^-*[0-9]+[.]?[0-9e+]*$", value) is not None:
        return True
    elif re.match("[0-9]+\.[0-9e+]+ <[\w]+>", value) is not None:
        return True
    else:
        return False



def json_to_lbl(input_json_path, img_file):
    fp = open(input_json_path, "r")
    data = fp.read()
    fp.close()

    label_data = json.loads(data)

    s = ""

    s += "PDS_VERSION_ID                = PDS3\n"
    s += "\n"
    s += "^IMAGE                        = \"%s\"\n" % (img_file)
    s += "\n"

    for key in label_data:
        value = label_data[key]
        if isinstance(value, string_types) and not is_number(value):
            value = "\"%s\"" % value
        if type(value) == list or type(value) == map:
            value = "(%s)" % ','.join(["'%s'" % f for f in value])
        lbl_line = "%-30s= %s" % (key, value)
        s += "%s\n"%lbl_line

    s += """
OBJECT                        = IMAGE
  LINES                       = {lines}
  LINE_SAMPLES                = {line_samples}
  BANDS                      = 1
  FILTER_NAME                = Gray
  BAND_STORAGE_TYPE          = BAND_SEQUENTIAL
  OFFSET                     = 0.0
  SCALING_FACTOR             = 1.0
  SAMPLE_BITS                = 32
  SAMPLE_BIT_MASK            = 2#1111111111111111#
  SAMPLE_TYPE                = PC_REAL
  CORE_NULL                  = 0
  CORE_LOW_REPR_SATURATION   = 1
  CORE_LOW_INSTR_SATURATION  = 1
  CORE_HIGH_REPR_SATURATION  = 65535
  CORE_HIGH_INSTR_SATURATION = 65535
END_OBJECT                    = IMAGE
END\n""".format(lines=label_data["LINES"],
                  line_samples=label_data["LINE_SAMPLES"])
    return s
