import os
import sys
import pvl
from sciimg.isis3.scripting import getkey
import tempfile
import traceback
import sciimg.isis3.utility
from sciimg.isis3 import voyager

__METADATA_CACHE__ = {}

def __read_invalid_voyager_label(img_file):
    f = open(img_file, "r")
    lines = []
    for line in f.readlines():
        line = line.strip()

        try:
            i = line.index("/*")
            if line[-2:] != "*/":
                line += " */"
        except:
            pass

        lines.append(line)
        if line == "END":
            break
    lab = "\n".join(lines)
    return lab

def __pvl_string_from_imq(imq_file, verbose=False):
    tf = tempfile.mkstemp(suffix=".img")

    p = None
    lab = None
    try:
        voyager.vdcomp(imq_file, tf[1])
        p = load_pvl(tf[1])
    except:
        if verbose is True:
            traceback.print_exc(file=sys.stdout)
        lab = __read_invalid_voyager_label(tf[1])
    finally:
        os.close(tf[0])
        os.unlink(tf[1])

    if lab is not None:
        try:
            p = pvl.loads(lab)
        except:
            traceback.print_exc(file=sys.stdout)

    return p

def load_pvl(from_file, verbose=False):
    if from_file in __METADATA_CACHE__:
        if verbose:
            print("File %s already loaded in cache."%from_file)
        return __METADATA_CACHE__[from_file]

    p = None

    if from_file[-3:].upper() == "IMQ":
        p = __pvl_string_from_imq(from_file, verbose)
    else:
        p = pvl.load(from_file)

    __METADATA_CACHE__[from_file] = p

    return p


