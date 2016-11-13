from isis3._core import isis_command


def isis2std_grayscale(from_cube, to_tiff, format="tiff", bittype="u16bit", minimum=None, maximum=None, maxpercent=9.999):
    cmd = "isis2std"
    params = {
        "from": from_cube,
        "to": to_tiff,
        "format": format,
        "bittype": bittype
    }

    if minimum is not None and maximum is not None:
        params["stretch"] = "manual"
        params["minimum"] = minimum,
        params["maximum"] = maximum
    else:
        params["maxpercent"] = maxpercent

    s = isis_command(cmd, params)

    return s

def isis2std_rgb(from_cube_red, from_cube_green, from_cube_blue, to_tiff, minimum=None, maximum=None, match_stretch=False, format="tiff", bittype="u16bit", maxpercent=99.999):
    cmd = "isis2std"
    params = {
        "red": from_cube_red,
        "green": from_cube_green,
        "blue": from_cube_blue,
        "to": to_tiff,
        "format": format,
        "bittype": bittype,
        "mode": "rgb"
    }

    if match_stretch and minimum is not None and maximum is not None:
        params += {
            "stretch": "manual",
            "rmin": minimum,
            "rmax": maximum,
            "gmin": minimum,
            "gmax": maximum,
            "bmin": minimum,
            "bmax": maximum
        }
    else:
        params += {"maxpercent": maxpercent}

    s = isis_command(cmd, params)
    return s