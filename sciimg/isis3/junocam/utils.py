import sys
import json
import types
import re


def is_number(value):
    if re.match("^-*[0-9]+[.]?[0-9e+]*$", value) is not None:
        return True
    elif re.match("[0-9]+\.[0-9\e+]+ <[\w]+>", value) is not None:
        return True
    else:
        return False



def json_to_lbl(input_json_path):
    fp = open(input_json_path, "r")
    data = fp.read()
    fp.close()

    label_data = json.loads(data)

    s = ""

    s += "PDS_VERSION_ID                = PDS3\n"
    s += "\n"
    s += "^IMAGE                        = \"%s.IMG\"\n" % (label_data["FILE_NAME"][:-4])
    s += "\n"

    for key in label_data:
        value = label_data[key]
        if (isinstance(value, types.StringType) or isinstance(value, types.UnicodeType)) and not is_number(value):
            value = "\"%s\"" % value
        if isinstance(value, types.ListType):
            value = str(map(str, value)).replace("[", "(").replace("]", ")")
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
  SAMPLE_BITS                = 16
  SAMPLE_BIT_MASK            = 2#1111111111111111#
  SAMPLE_TYPE                = LSB_UNSIGNED_INTEGER
  CORE_NULL                  = 0
  CORE_LOW_REPR_SATURATION   = 1
  CORE_LOW_INSTR_SATURATION  = 1
  CORE_HIGH_REPR_SATURATION  = 65535
  CORE_HIGH_INSTR_SATURATION = 65535
END_OBJECT                    = IMAGE
END\n""".format(lines=label_data["LINES"],
                  line_samples=label_data["LINE_SAMPLES"])
    return s
