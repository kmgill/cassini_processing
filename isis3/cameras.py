from isis3._core import isis_command
import os

def spiceinit(from_cube, is_ringplane=False):
    params = {
        "from": from_cube
    }
    # web=yes ckpredicted=true cknadir=true spkpredicted=true
    if is_ringplane is True:
        params["shape"] = "ringplane"

    s = isis_command("spiceinit", params)
    return s


def cam2map(from_cube, to_cube, projection="equirectangular", map=None, resolution="CAMERA"):

    if map is None:
        map = "%s/../data/base/templates/maps/%s.map"%(os.environ["ISISROOT"], projection)

    params = {
        "from": from_cube,
        "to": to_cube,
        "map": map
    }

    if resolution == "MAP":
        params["pixres"] = "map"

    s = isis_command("cam2map", params)
    return s


def caminfo(from_cube, to_pvl, isislabel=True, originallabel=True):
    cmd = "caminfo"
    params = {
        "from": from_cube,
        "to": to_pvl,
        "isislabel": ("yes" if isislabel is True else "no"),
        "originallabel": ("yes" if originallabel is True else "no")
    }
    s = isis_command(cmd, params)
    return s


def cam2cam(from_cube, to_cube, match_cube, interp="CUBICCONVOLUTION"):
    params = {
        "from": from_cube,
        "to": to_cube,
        "match": match_cube,
        "interp": interp
    }
    s = isis_command("cam2cam", params)
    return s