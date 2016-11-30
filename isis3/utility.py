from isis3._core import isis_command


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
