from sciimg.isis3._core import isis_command


def catlab(from_file):
    s = isis_command("catlab", {"from": from_file})
    return s


def stretch(from_file, to_file, null="0.0", lis="0.0"):
    params = {
        "from": from_file,
        "to": to_file,
        "null": null,
        "lis": lis
    }
    s = isis_command("stretch", params)
    return s


def pad(from_file, to_file, left=0, right=0, bottom=0, top=0):
    params = {
        "from": from_file,
        "to": to_file,
        "top": top,
        "bottom": bottom,
        "left": left,
        "right": right
    }
    s = isis_command("pad", params)
    return s


def cubeit(fromlist, to_file, proplab=None):
    params = {
        "fromlist": fromlist,
        "to": to_file
    }
    if proplab is not None:
        params["proplab"] = proplab

    s = isis_command("cubeit", params)
    return s