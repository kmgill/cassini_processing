from isis3._core import isis_command


def catlab(from_file):
    s = isis_command("catlab", {"from": from_file})
    return s

