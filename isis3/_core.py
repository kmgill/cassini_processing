import subprocess
import sys
import os


def isis_command(cmd, params):
    proc_cmd = [cmd] + ["%s=%s"%(k, params[k]) for k in params.keys()]
    s = subprocess.check_output(proc_cmd)
    return s

