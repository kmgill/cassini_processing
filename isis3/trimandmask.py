from isis3._core import isis_command


def trim(from_cube, to_cube, top=2, bottom=2, left=2, right=2):
    s = isis_command("trim", {
        "from": from_cube,
        "to": to_cube,
        "top": top,
        "bottom": bottom,
        "left": left,
        "right": right
    })
    return s

def circle(from_cube, to_cube, rad=None):
    params = {
        "from": from_cube,
        "to": to_cube,
    }

    if rad is not None:
        params["rad"] = rad

    s = isis_command("circle", params)
    return s