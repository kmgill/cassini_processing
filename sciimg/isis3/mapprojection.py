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