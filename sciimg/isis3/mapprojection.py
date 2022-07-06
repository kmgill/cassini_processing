from sciimg.isis3._core import isis_command
import re


#maptrim from=JNCE_2018144_13C00051_V01_RED_Mosaic.cub to=JNCE_2018144_13C00051_V01_RED_Mosaic.trimmed.cub mode=crop minlat=-90 maxlat=90 minlon=-180 maxlon=180
def maptrim(from_cube, to_cube, mode="crop", minlat=-90, maxlat=90, minlon=-180, maxlon=180):
    s = isis_command("maptrim", {
        "from": from_cube,
        "to": to_cube,
        "mode": mode,
        "minlat": minlat,
        "maxlat": maxlat,
        "minlon": minlon,
        "maxlon": maxlon
    })
    return s


def map2map(from_cube, to_cube, map, minlat=None, maxlat=None, minlon=None, maxlon=None):
    params = {
        "from": from_cube,
        "to": to_cube,
        "map": map
    }
    if minlat is not None:
        params["minlat"] = minlat
    if maxlat is not None:
        params["maxlat"] = maxlat    

    if minlon is not None:
        params["minlon"] = minlon
    if maxlon is not None:
        params["maxlon"] = maxlon

    s = isis_command("map2map", params)
    return s