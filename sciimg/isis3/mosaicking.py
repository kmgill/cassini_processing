from sciimg.isis3._core import isis_command


class Priority:
    ONTOP = "ONTOP"
    BENEATH = "BENEATH"
    BAND = "BAND"
    AVERAGE = "AVERAGE"

class Grange:
    AUTO = "AUTO"
    USER = "USER"

def automos(from_list, to_file, priority=Priority.ONTOP, grange=Grange.AUTO, minlat=None, maxlat=None, minlon=None, maxlon=None):

    params = {
        "fromlist": from_list,
        "mosaic": to_file,
        "priority": priority
    }

    if grange == Grange.USER:
        params["grange"] = Grange.USER
        if minlat is not None:
            params["minlat"] = minlat
        if maxlat is not None:
            params["maxlat"] = maxlat
        if minlon is not None:
            params["minlon"] = minlon
        if maxlon is not None:
            params["maxlon"] = maxlon

    s = isis_command("automos", params)
    return s
