import subprocess
import sys
import os

"""
Note: Probably need a better check than just looking at two environment variables
"""
def is_isis3_initialized():
    if not "ISISROOT" in os.environ:
        raise Exception("ISISROOT not set!")
    if not "ISIS3DATA" in os.environ:
        raise Exception("ISIS3DATA not set!")
    return True


"""
I stole this from someone on stackexchange.
"""
def printProgress (iteration, total, prefix = '', suffix = '', decimals = 1, barLength = 100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    formatStr       = "{0:." + str(decimals) + "f}"
    percents        = formatStr.format(100 * (iteration / float(total)))
    filledLength    = int(round(barLength * iteration / float(total)))
    bar             = '*' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def isis_command(cmd, params):
    proc_cmd = [cmd] + ["%s=%s"%(k, params[k]) for k in params.keys()]
    s = subprocess.check_output(proc_cmd, stderr=subprocess.STDOUT)
    return s

