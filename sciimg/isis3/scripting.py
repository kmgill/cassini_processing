import tempfile
import os
import sys
from sciimg.isis3 import voyager
from sciimg.isis3._core import isis_command
import traceback
import pvl


"""
Note: Exceptions may cause the temp files to not be deleted...
"""

def __getkey_voy2isis(from_file_name, keyword, objname=None, grpname=None, verbose=False):
    tf = tempfile.mkstemp(suffix=".cub")
    try:
        voyager.voy2isis(from_file_name, tf[1])
        value = getkey(tf[1], keyword, objname, grpname, verbose)
    finally:
        os.close(tf[0])
        os.unlink(tf[1])
    return value


def __getkey_vdcomp(from_file_name, keyword, objname=None, grpname=None, verbose=False):

    tf = tempfile.mkstemp(suffix=".img")
    try:
        voyager.vdcomp(from_file_name, tf[1])
        value = getkey(tf[1], keyword, objname, grpname, verbose)
        return value
    except:
        if verbose is True:
            traceback.print_exc(file=sys.stdout)
        return __getkey_voy2isis(from_file_name, keyword, objname, grpname, verbose)
    finally:
        os.close(tf[0])
        os.unlink(tf[1])



def getkey(from_file_name, keyword, objname=None, grpname=None, verbose=False):
    if from_file_name[-3:].upper() == "IMQ":
        return __getkey_voy2isis(from_file_name, keyword, objname, grpname, verbose)
    else:
        try:
            cmd = "getkey"
            params = {
                "from" : from_file_name,
                "keyword": keyword
            }

            if objname is not None:
                params["objname"] = objname

            if grpname is not None:
                params["grpname"] = grpname

            s = isis_command(cmd, params)
            return s.strip()
        except:
            if verbose is True:
                traceback.print_exc(file=sys.stdout)
            return None
