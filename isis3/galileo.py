from isis3._core import isis_command

def gllssi2isis(from_file, to_file):
    s = isis_command("gllssi2isis", {"from": from_file, "to": to_file})
    return s


def gllssical(from_file, to_file):
    s = isis_command("gllssical", {"from": from_file, "to": to_file})
    return s
