from isis3._core import isis_command


def voy2isis(from_file, to_file):
    s = isis_command("voy2isis", {"from": from_file, "to": to_file})
    return s


def voycal(from_file, to_file):
    s = isis_command("voycal", {"from": from_file, "to": to_file})
    return s
