from sciimg.isis3._core import isis_command


def junocam2isis(from_file, to_file, fullccd=False):

    params = {
        "from": from_file,
        "to": to_file
    }

    if fullccd is True:
        params["fullccd"] = "yes"

    s = isis_command("junocam2isis", params)
    return s
