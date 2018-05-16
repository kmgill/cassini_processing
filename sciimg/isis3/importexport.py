from sciimg.isis3._core import isis_command
import os


def pds2isis(from_file, to_file):
    s = isis_command("pds2isis", {"from": from_file, "to": to_file})
    return s


class ColorMode:
    AUTO="auto"
    GRAYSCALE="grayscale"
    RGB="rgb"
    RGBA="rgba"

def std2isis(from_file, to_file, mode=ColorMode.AUTO):
    params = {
        "from": from_file,
        "to": to_file,
    }

    if mode != ColorMode.AUTO:
        params["mode"] = mode

    s = isis_command("std2isis", params)
    return s



def isis2pds(from_file, to_file, labtype="fixed", bittype="32bit", pdsversion="pds3"):
    params = {
        "from": from_file,
        "to": to_file,
        "labtype": labtype,
        "bittype": bittype,
        "pdsversion": pdsversion
    }

    s = isis_command("isis2pds", params)
    return s


def isis2std_grayscale(from_cube, to_tiff, format="tiff", bittype="u16bit", minimum=None, maximum=None, maxpercent=99.999, cleanup_print_file=True):
    cmd = "isis2std"
    params = {
        "from": "%s+1"%from_cube,
        "to": to_tiff,
        "format": format,
        "bittype": bittype
    }

    if minimum is not None and maximum is not None:
        params["stretch"] = "manual"
        params["minimum"] = minimum
        params["maximum"] = maximum
    else:
        params["maxpercent"] = maxpercent

    s = isis_command(cmd, params)

    if cleanup_print_file:
        dirname = os.path.dirname(to_tiff)
        if len(dirname) > 0:
            dirname += "/"
        if os.path.exists("%sprint.prt" % dirname):
            os.unlink("%sprint.prt" % dirname)

    return s


def isis2std_rgb(from_cube_red, from_cube_green, from_cube_blue, to_tiff, minimum=None, maximum=None, match_stretch=False, format="tiff", bittype="u16bit", maxpercent=99.999, cleanup_print_file=True):
    cmd = "isis2std"
    params = {
        "red": "%s+1"%from_cube_red,
        "green": "%s+1"%from_cube_green,
        "blue": "%s+1"%from_cube_blue,
        "to": to_tiff,
        "format": format,
        "bittype": bittype,
        "mode": "rgb"
    }

    if match_stretch and minimum is not None and maximum is not None:
        params.update({
            "stretch": "manual",
            "rmin": minimum,
            "rmax": maximum,
            "gmin": minimum,
            "gmax": maximum,
            "bmin": minimum,
            "bmax": maximum
        })
    else:
        params["maxpercent"] = maxpercent

    s = isis_command(cmd, params)

    if cleanup_print_file:
        dirname = os.path.dirname(to_tiff)
        if len(dirname) > 0:
            dirname += "/"
        if os.path.exists("%sprint.prt" % dirname):
            os.unlink("%sprint.prt" % dirname)

    return s