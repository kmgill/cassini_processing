
from isis3._core import isis_command

def getkey(from_file_name, keyword, objname=None, grpname=None):
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
        return None