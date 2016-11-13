import subprocess




def get_field_value(lbl_file_name, keyword, objname=None, grpname=None):
    try:
        cmd = ["getkey", "from=%s"%lbl_file_name, "keyword=%s"%keyword]
        if objname is not None:
            cmd += ["objname=%s"%objname]
        if grpname is not None:
            cmd += ["grpname=%s"%grpname]
        s = subprocess.check_output(cmd)
        return s.strip()
    except:
        return None


